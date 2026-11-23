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

    TREND_LABEL_TEMPLATE = """You are a news desk editor naming today's story clusters.

    Below are headlines that were grouped together because they cover the same
    story. Name that specific story.

    Rules:
    - 2 to 5 words naming the concrete event, place, organisation or people
      involved. Use proper nouns when the headlines contain them.
    - Describe what actually happened, not an abstract theme.
    - Lowercase. No quotes, no markdown, no punctuation, no trailing period.
    - Never add a year or a date that the headlines do not state.
    - Output the label and nothing else.

    GOOD (concrete, names the story):
    - anthropic stock market debut
    - bangladesh election protests
    - bank of england headquarters refurbishment
    - storm claudia floods in valencia

    BAD (abstract, unusable as a label):
    - glory
    - resilience
    - empire
    - elite
    - the economy
    - important news about technology

    Headlines:
    {documents}

    Label:
    """

    TOPIC_DESCRIPTION_TEMPLATE = """
    Role: Expert Database Archivist
    Task: Summarize a topic in a single, punchy, high-level sentence.

    Constraints:
    - Length: 10-12 words.
    - Format: [Noun Phrase] + [Formal Impact/Scope].
    - Forbidden: "is a", "refers to", "when", "like", "for example".
    - Forbidden: markdown formatting (no bold, brackets, em-dashes), explanations of your
      reasoning, or any text other than the description sentence itself.

    GOOD (Noun-led, Categorical):
    - Topic: Infrastructure | Description: Foundational physical and organizational structures needed for the operation of society.
    - Topic: Logistics | Description: Strategic management of the movement and positioning of resources and goods.

    BAD (Verb-led, Informal):
    - Topic: Infrastructure | Description: Building things like roads and bridges so that people can drive.
    - Topic: Logistics | Description: This is how companies move their products from one place to another.

    Topic: {topic}
    Description (plain sentence only, no formatting or commentary):
    """  # noqa

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
