class Prompts:
    """Collection of prompts for analyzing news articles."""

    RAG_TEMPLATE = """You are an expert news journalist and recommender.

    Your task is to:
        - Write a concise, well-written news-style summary of the information provided
        in the context.
        - Use a neutral and professional tone, as if writing a short paragraph for a news article.
        - Do not mention that you are summarizing or that the information came from a context.
        - If the context does not contain any relevant information to answer the question, respond
        exactly with:
        "There is no relevant information about your question this week."

        Formatting rules:
        - Do not use markdown, bullet points, or headings.
        - Respond in plain text, as natural news prose.

        Context:
        {context}

        Question:
        {question}

        Answer:
    """
    TOPIC_CLASSIFICATION_TEMPLATE = """You are a topic classification assistant.

    Given the following document, assign it **one** of the following topics:
    {topics}

    Document:
    {document}

    Topic:
    """

    TOPIC_GENERATION_TEMPLATE = """You are a topic assignor.

    Given the following documents, you have to propose a single topic that fits
    the documents content. The topic should be a single word without containing the quote "topic:" .
    You should try to propose the following general topics but if you can not, you can propose your
    own topic.

    The general topics are:
    {cached_topics}

    Documents:
    {documents}

    Proposed topic:
    """

    TOPIC_DESCRIPTION_TEMPLATE = """You are a topic descriptor.

    Given a single topic, you will provide a description of it in 10 words approx.

    Topic:
    {topic}

    Proposed description:
    """

    asked_frecuency_template = """You are a linguistic expert.

    You should determined the time window descrived by the user in the input question.
    Examples
    - What has happen during this week? -> 7
    - What has happen today? ->  1
    If you are not sure of the anwser, say 0

    Question:
    {question}

    time_window:
    """
