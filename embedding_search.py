from dotenv import load_dotenv
from openai import OpenAI

import math


def cosine_similarity(a, b):
    dot_product = sum(x * y for x, y in zip(a, b))

    magnitude_a = math.sqrt(sum(x * x for x in a))
    magnitude_b = math.sqrt(sum(x * x for x in b))

    return dot_product / (magnitude_a * magnitude_b)

load_dotenv()

client = OpenAI()

documents = [
    "The employee may request a new laptop from the IT portal.",
    "Hardware replacements require manager approval.",
    "The cafeteria serves breakfast until 10:30 AM.",
    "VPN access is available to remote employees."
]

response = client.embeddings.create(
    model="text-embedding-3-small",
    input=documents
)

query = "What time is Matsyagandha Express leaves from LTT Station?"

query_response = client.embeddings.create(
    model="text-embedding-3-small",
    input=query
)

query_vector = query_response.data[0].embedding


print(query_response)

results = []

for i, document_vector in enumerate(response.data):
    score = cosine_similarity(
        query_vector,
        document_vector.embedding
    )

    results.append({
        "document": documents[i],
        "score": score
    })

results.sort(
    key=lambda x: x["score"],
    reverse=True
)

top_results = results[:2]

context = "\n".join(
    result["document"]
    for result in top_results
)

breakpoint()

prompt = f"""
Answer the user's question using only the provided context.

Context:
{context}

Question:
{query}

If the context does not contain enough information to answer,
say that you don't have enough information.
"""

generation_response = client.responses.create(
    model="gpt-5.6-luna",
    input=prompt
)

breakpoint()

print(generation_response.output_text)