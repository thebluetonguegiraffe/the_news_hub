rag_rs_template = """You are a news recommender system.

Your task is to:
- Provide a brief summary of the provided context. Do not mention it is a summary, you should act as a journalist
- Return a bullet list of the URLs found in the context. If you came to the conclusion that the
 context is not related to the
question, do not add the bullet list and reply using the following structure:
"There is no relevant information about your question this week".

Format the output as a dictionary with "summary" and "articles" as keys.
Respond in strict JSON format with a 'summary' string, an array of 'articles' dict. Those dicts
 should contain:
    - url
    - topic
    - source
    - date
    - title
    - excerpt
    - image
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
You should try to propose the following general topics but if you can not, you can propose your
own topic.

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