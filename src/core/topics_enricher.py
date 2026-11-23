"""Assign a canonical category and a concrete daily trend to ingested articles.

Two labels are written per document:

* `topic`    - one of the canonical `NEWS_CATEGORIES`. Derived from embedding
               similarity alone, so it costs no LLM calls, never fails on a rate
               limit, and stays comparable day over day.
* `trend`    - a concrete label for the cluster the document belongs to, named by
               the LLM ("anthropic stock market debut"). This is the day-to-day
               detail that a fixed category list cannot express.

Categories are written before any LLM call, so a rate-limited run still leaves
every document categorised instead of empty.
"""

from collections import defaultdict
from datetime import datetime
import logging
import os
import re
from typing import Dict, List, Optional, Tuple

import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from langchain.chat_models import init_chat_model
from langchain.prompts import ChatPromptTemplate

from src.core.chroma_database import ChromaDatabase, CustomEmbedder
from src.core.translator import GoogleTranslator
from src.taxonomy import NEWS_CATEGORIES, UNCLASSIFIED_CATEGORY
from src.utils.rate_limit import call_with_retry
from config import chat_configuration, chroma_configuration, mongo_configuration
from src.core.mongo_client import CustomMongoClient
from src.utils.prompts import Prompts

logger = logging.getLogger("topics_enricher")
logger.setLevel(logging.INFO)


class TopicsEnricher:
    # Chroma Cloud rejects a get() asking for more than 300 rows.
    PAGE_SIZE = 300

    # Clustering is only meaningful with a handful of documents per cluster.
    MIN_DOCS_TO_CLUSTER = 8
    MIN_CLUSTERS = 2
    MAX_CLUSTERS = 25
    TARGET_DOCS_PER_CLUSTER = 4
    PCA_COMPONENTS = 50
    MIN_DOCS_FOR_PCA = 20

    # A document whose best category is not clearly better than the runner-up is
    # left as UNCLASSIFIED_CATEGORY rather than forced into a wrong bucket.
    MIN_CATEGORY_SIMILARITY = 0.55
    # Reported in the logs to show how many documents sat between two
    # categories. Prototypes can be retuned when this stays high.
    CONFIDENT_MARGIN = 0.02

    def __init__(self):
        self.llm = init_chat_model(
            model=chat_configuration["model"],
            model_provider="openai",
            api_key=os.getenv("MISTRAL_API_KEY"),
            base_url="https://api.mistral.ai/v1",
            max_tokens=40,
        )
        self.chroma_db = ChromaDatabase(collection_name=chroma_configuration["collection_name"])
        self.prompts = Prompts()
        self.mongo = CustomMongoClient
        self.translator = GoogleTranslator(source_lang="en")
        self._category_matrix: Optional[np.ndarray] = None
        self._category_labels: List[str] = list(NEWS_CATEGORIES.keys())

    # ------------------------------------------------------------------ reading

    def fetch_documents(
        self, date: str, overwrite: bool = False, include: Optional[List[str]] = None
    ) -> Dict[str, List]:
        """
        Page through every document ingested at `date`.

        Returns empty lists when there is nothing to do; an empty bucket is a
        normal outcome (the scrapers may not have reached it yet), not an error.
        `include` narrows what Chroma sends back: the summary pass does not need
        the embeddings, which are 1024 floats per document.
        """
        include = include or ["embeddings", "metadatas", "documents"]
        if overwrite:
            chroma_filter = {"ingestion_date": date}
        else:
            chroma_filter = {"$and": [{"ingestion_date": date}, {"topic": ""}]}

        collected = {"ids": [], "embeddings": [], "metadatas": [], "documents": []}
        offset = 0

        while True:
            batch = self.chroma_db.search_with_filter(
                chroma_filter=chroma_filter,
                include=include,
                limit=self.PAGE_SIZE,
                offset=offset,
            )
            ids = batch.get("ids") or []
            if not ids:
                # No rows left. Reaching this on the first pass simply means the
                # bucket is empty; on a later pass it means the previous page was
                # the last one, which a total that is an exact multiple of the
                # page size would otherwise hide.
                break

            collected["ids"].extend(ids)
            for field in ("embeddings", "metadatas", "documents"):
                if field in include:
                    collected[field].extend(batch[field])
            logger.info(f"fetched {len(collected['ids'])} docs so far...")

            if len(ids) < self.PAGE_SIZE:
                break
            offset += self.PAGE_SIZE

        return collected

    # --------------------------------------------------------------- categories

    def category_matrix(self) -> np.ndarray:
        """Embed the category prototypes once per process, L2-normalised."""
        if self._category_matrix is None:
            prototypes = [NEWS_CATEGORIES[label] for label in self._category_labels]
            embedder = CustomEmbedder()
            vectors = call_with_retry(
                lambda: embedder(prototypes), description="category prototype embeddings"
            )
            self._category_matrix = self._normalise(np.asarray(vectors, dtype=np.float32))
            logger.info(f"{len(self._category_labels)} category prototypes embedded")
        return self._category_matrix

    def assign_categories(self, embeddings: np.ndarray) -> Tuple[List[str], np.ndarray]:
        """
        Pick the closest canonical category for each document by cosine similarity.

        Also returns the margin between the best and second-best category. A
        small margin means the document sits between two categories, and
        `refine_categories` lets its cluster break the tie.
        """
        similarities = self._normalise(embeddings) @ self.category_matrix().T
        ordered = np.sort(similarities, axis=1)
        best_scores = ordered[:, -1]
        runner_up = ordered[:, -2] if similarities.shape[1] > 1 else np.zeros_like(best_scores)
        margins = best_scores - runner_up
        best_indices = similarities.argmax(axis=1)

        categories = []
        for index, score in zip(best_indices, best_scores):
            if score < self.MIN_CATEGORY_SIMILARITY:
                categories.append(UNCLASSIFIED_CATEGORY)
            else:
                categories.append(self._category_labels[index])
        return categories, margins

    # --------------------------------------------------------------- clustering

    def create_clusters(self, embeddings: np.ndarray) -> np.ndarray:
        """
        Group documents into story clusters and return a label per document.

        Embeddings are L2-normalised so k-means on euclidean distance behaves
        like cosine similarity, which is what the embedding model is trained for.
        """
        n_samples = len(embeddings)
        reduced = self._normalise(embeddings)

        if n_samples >= self.MIN_DOCS_FOR_PCA:
            n_components = min(self.PCA_COMPONENTS, n_samples - 1, reduced.shape[1])
            reduced = PCA(n_components=n_components, random_state=42).fit_transform(reduced)
            reduced = self._normalise(reduced)

        k_max = max(self.MIN_CLUSTERS, min(self.MAX_CLUSTERS,
                                           n_samples // self.TARGET_DOCS_PER_CLUSTER))
        # k can never exceed the number of documents: that was the ValueError
        # that failed the DAG whenever a bucket was thin.
        k_max = min(k_max, n_samples - 1)

        best_labels, best_score, best_k = None, -1.0, None
        for k in range(self.MIN_CLUSTERS, k_max + 1):
            labels = KMeans(n_clusters=k, random_state=42, n_init=10).fit_predict(reduced)
            if len(set(labels)) < 2:
                continue
            score = silhouette_score(reduced, labels)
            if score > best_score:
                best_labels, best_score, best_k = labels, score, k

        if best_labels is None:
            logger.warning("Could not form clusters; treating all documents as one cluster.")
            return np.zeros(n_samples, dtype=int)

        logger.info(f"chose k={best_k} for {n_samples} docs (silhouette {best_score:.3f})")
        return best_labels

    # ------------------------------------------------------------------ labels

    def label_cluster(self, cluster_documents: List[str]) -> Optional[str]:
        """
        Ask the LLM for a concrete label for one cluster.

        Returns None when the call cannot be completed, so the caller keeps the
        category it already assigned instead of losing the document.
        """
        headlines = "\n".join(f"- {document}" for document in cluster_documents[:12])
        prompt = ChatPromptTemplate.from_messages([("system", self.prompts.TREND_LABEL_TEMPLATE)])
        chain = prompt | self.llm

        try:
            response = call_with_retry(
                lambda: chain.invoke({"documents": headlines}),
                description="trend label",
            )
        except Exception as error:  # noqa: BLE001 - a label is never worth failing the run
            logger.error(f"Could not label cluster: {error}")
            return None

        return self._clean_label(response.content)

    MAX_LABEL_CHARS = 80

    @classmethod
    def _clean_label(cls, raw: str) -> Optional[str]:
        """Strip the markdown and filler the small model sometimes emits."""
        label = (raw or "").strip().lower()
        # The model occasionally adds a second line of commentary despite the
        # prompt; the first non-empty line is the label.
        label = next((line for line in label.splitlines() if line.strip()), "")
        label = label.replace("*", "").replace("`", "").replace('"', "").replace("'", "")
        label = re.sub(r"^(label|topic|proposed topic|trend)\s*:\s*", "", label)
        label = re.sub(r"\s+", " ", label).strip(" .,:;-")
        if not label:
            return None
        if len(label) > cls.MAX_LABEL_CHARS:
            # A loose cluster draws a wordy answer. Keep it, trimmed at a word
            # boundary, rather than dropping the only label we have.
            label = label[: cls.MAX_LABEL_CHARS].rsplit(" ", 1)[0].strip(" .,:;-")
        return label or None

    # ------------------------------------------------------------- orchestration

    def clusterize_topics(self, date: str, dry_run: bool = False, overwrite: bool = False) -> None:
        results = self.fetch_documents(date=date, overwrite=overwrite)
        ids = results["ids"]

        if not ids:
            logger.info(f"Nothing to enrich for {date}.")
            return

        embeddings = np.asarray(results["embeddings"], dtype=np.float32)
        documents = results["documents"]
        logger.info(f"{len(ids)} documents to enrich for {date}")

        # Step 1: categories. No LLM involved, so this always completes and the
        # documents are never left uncategorised by a rate-limited run.
        categories, margins = self.assign_categories(embeddings)
        undecided = int((margins < self.CONFIDENT_MARGIN).sum())
        if not dry_run:
            self._write_metadata(ids, [{"topic": category} for category in categories])
        logger.info(f"categories assigned: {self._counts(categories)}")
        # Logged rather than acted on: letting a cluster majority overrule a
        # narrow win was measured on real buckets and moved more documents to
        # the wrong category than to the right one, because the clusters are
        # story-shaped, not category-shaped.
        logger.info(f"{undecided}/{len(categories)} categories won by a narrow margin")

        if len(ids) < self.MIN_DOCS_TO_CLUSTER:
            logger.info(
                f"Only {len(ids)} documents: too few to cluster, categories only."
            )
            return

        # Step 2: clustering. Local computation, still no LLM.
        labels = self.create_clusters(embeddings)
        clusters: Dict[int, List[int]] = defaultdict(list)
        for position, label in enumerate(labels):
            clusters[int(label)].append(position)

        # Step 3: concrete trend labels per cluster. Best effort: a failure here
        # costs a trend label, never the category written in step 1.

        named, failed = 0, 0
        for cluster_id, positions in clusters.items():
            trend = self.label_cluster([documents[position] for position in positions])
            if not trend:
                failed += 1
                continue
            named += 1
            logger.info(f"cluster {cluster_id}: {trend!r} ({len(positions)} docs)")
            if not dry_run:
                self._write_metadata(
                    [ids[position] for position in positions],
                    [{"trend": trend}] * len(positions),
                )

        logger.info(f"trends named for {named} clusters, {failed} could not be labelled")

    def _write_metadata(self, ids: List[str], metadatas: List[Dict]) -> None:
        """Update Chroma in pages, since the service caps rows per request."""
        for start in range(0, len(ids), self.PAGE_SIZE):
            self.chroma_db.collection.update(
                ids=ids[start:start + self.PAGE_SIZE],
                metadatas=metadatas[start:start + self.PAGE_SIZE],
            )

    # ----------------------------------------------------------------- mongo

    def populate_topics_database(self, date: str, dry_run: bool = False) -> None:
        """Record per-category counts for `date`, plus the concrete trends seen."""
        results = self.fetch_documents(date=date, overwrite=True, include=["metadatas"])
        metadatas = results["metadatas"]
        if not metadatas:
            logger.info(f"No documents to summarise for {date}.")
            return

        categories = [md.get("topic") or UNCLASSIFIED_CATEGORY for md in metadatas]
        trends: Dict[str, Dict] = {}
        for md in metadatas:
            trend = md.get("trend")
            if not trend:
                continue
            entry = trends.setdefault(
                trend, {"docs_number": 0, "categories": defaultdict(int)}
            )
            entry["docs_number"] += 1
            entry["categories"][md.get("topic") or UNCLASSIFIED_CATEGORY] += 1

        if dry_run:
            logger.info(
                f"Dry run: would record {len(set(categories))} categories "
                f"and {len(trends)} trends for {date}."
            )
            return

        self._update_categories(categories=categories, date=date)
        self._update_trends(trends=trends, date=date)

    def _update_categories(self, categories: List[str], date: str) -> None:
        counts = self._counts(categories)
        descriptions = self._category_descriptions(sorted(counts))

        with self.mongo() as client:
            collection = client[mongo_configuration["db"]][mongo_configuration["collection"]]
            for category, docs_number in counts.items():
                # Replace any entry already recorded for this bucket instead of
                # appending a second one: the API sums every entry it finds for a
                # day, so a re-run (the catch-up pass re-visits recent buckets)
                # would otherwise double the count.
                collection.update_one(
                    filter={"_id": category},
                    update={"$pull": {"topics_per_day": {"date": date}}},
                )
                update = {
                    # Only the categories present today are touched, so the
                    # series no longer fills up with zero-count entries.
                    "$push": {"topics_per_day": {"date": date, "docs_number": docs_number}}
                }
                description = descriptions.get(category)
                if description:
                    update["$setOnInsert"] = description
                collection.update_one(filter={"_id": category}, update=update, upsert=True)
        logger.info(f"{len(counts)} categories updated in MongoDB for {date}")

    def _update_trends(self, trends: Dict[str, Dict], date: str) -> None:
        if not trends:
            logger.info("No trends to record.")
            return

        with self.mongo() as client:
            collection = client[mongo_configuration["db"]][mongo_configuration["trends_collection"]]
            for trend, data in trends.items():
                dominant = max(data["categories"].items(), key=lambda item: item[1])[0]
                collection.update_one(
                    filter={"label": trend, "date": date},
                    update={
                        "$set": {
                            "label": trend,
                            "date": date,
                            "category": dominant,
                            "docs_number": data["docs_number"],
                        }
                    },
                    upsert=True,
                )
        logger.info(f"{len(trends)} trends recorded in MongoDB for {date}")

    def _category_descriptions(self, categories: List[str]) -> Dict[str, Dict]:
        """
        Build the description/translation payload for categories not stored yet.

        Written with $setOnInsert, so a category is described once and never
        rewritten by a later run.
        """
        with self.mongo() as client:
            collection = client[mongo_configuration["db"]][mongo_configuration["collection"]]
            stored = collection.find({"_id": {"$in": categories}}, {"_id": 1})
            known = {doc["_id"] for doc in stored}

        missing = [category for category in categories if category not in known]
        if not missing:
            return {}

        descriptions = []
        for category in missing:
            try:
                descriptions.append(self.get_topic_description(topic=category))
            except Exception as error:  # noqa: BLE001
                logger.warning(f"No description for {category}: {error}")
                descriptions.append("")

        translated = {}
        for language in ("ca", "es"):
            translated["topic", language] = self.translator.translate_batch(
                missing, target_lang=language
            )
            translated["description", language] = self.translator.translate_batch(
                descriptions, target_lang=language
            )

        payload = {}
        for index, category in enumerate(missing):
            description = descriptions[index]
            payload[category] = {
                "description": description,
                "topic_ca": translated["topic", "ca"][index] or category,
                "topic_es": translated["topic", "es"][index] or category,
                "description_ca": translated["description", "ca"][index] or description,
                "description_es": translated["description", "es"][index] or description,
            }
        return payload

    def get_topic_description(self, topic: str) -> str:
        logger.info(f"Generating description for category: {topic}")
        prompt = ChatPromptTemplate.from_messages(
            [("system", self.prompts.TOPIC_DESCRIPTION_TEMPLATE)]
        )
        chain = prompt | self.llm
        response = call_with_retry(
            lambda: chain.invoke({"topic": topic}), description=f"description for {topic}"
        )
        return (response.content or "").strip().replace("*", "").lower()

    # ------------------------------------------------------------------ helpers

    @staticmethod
    def _normalise(matrix: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        return matrix / np.clip(norms, 1e-12, None)

    @staticmethod
    def _counts(values: List[str]) -> Dict[str, int]:
        counts: Dict[str, int] = defaultdict(int)
        for value in values:
            counts[value] += 1
        return dict(sorted(counts.items(), key=lambda item: -item[1]))
