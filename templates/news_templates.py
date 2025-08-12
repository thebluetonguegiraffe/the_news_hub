

rag_rs_template = """You are a news recommender system.

Your task is to:
- Provide a brief summary of the provided context.
- Return a bullet list of the URLs found in the context. If you came to the conclusion that the context is not related to the
question, do not add the bullet list and reply using the following structure: 
"There is no relevant information about your question this week".

Format the output as a dictionary with "summary" and "articles" as keys. "Respond in strict JSON format with a 'summary' string and an 'articles' array of URLs. 
No markdown or extra formatting."


Context:
{context}

Question:
{question}

Answer:
"""

topic_categorization_template = """You are a topic classification assistant.

Given the following document, assign it **one** of the following topics:
{topics}

Document:
{document}

Topic:
"""

topic_generation_template = """You are a topic assignor.

Given the following documents, you have to propose a single topic that fits
the documents content. The topic should be a single word without containing the quote "topic:" . 
You should try to propose the following general topics but if you can not, you can propose your own topic.

The general topics are:
{initial_topics}

Documents:
{documents}

Proposed topic:
"""

topic_description_template = """You are a topic descriptor.

Given a single topic, you will provide a description of it in 10 words approx.

Topic:
{topic}

Proposed description:
"""