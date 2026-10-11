from dotenv import load_dotenv
from openai import OpenAI
from pgvector import Vector
from pgvector.psycopg import register_vector
import psycopg

load_dotenv()

client = OpenAI()

conn = psycopg.connect(
    "dbname=ragdb user=raguser password=ragpassword host=localhost port=5432"
)

register_vector(conn)


def retrieve(query: str, limit: int = 3):
    # Convert the user's QUESTION into one embedding
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    )

    query_embedding = Vector(response.data[0].embedding)

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                id,
                section_heading,
                content,
                1 - (embedding <=> %s) AS similarity
            FROM document_chunks
            ORDER BY embedding <=> %s
            LIMIT %s
            """,
            (
                query_embedding,
                query_embedding,
                limit
            )
        )

        return cur.fetchall()


query = "How can I reimburse my ticket to Japan?"



# print(context)

def answer_query(query: str):
    results = retrieve(query)

    context_parts = []

    for row in results:
        id, heading, content, similarity = row

        context_parts.append(
            f"""
                SECTION: {heading}

                {content}
                """.strip()
                    )

    context = "\n\n---\n\n".join(context_parts)
    prompt = f"""
    You are an employee handbook assistant.

    Answer the user's question using only the handbook
    sections provided below.

    If the provided sections do not contain enough information
    to answer the question, say that the handbook does not
    provide enough information.

    HANDBOOK SECTIONS:

    {context}

    USER QUESTION:

    {query}
    """

    response = client.responses.create(
        model="gpt-5.6-luna",
        input=prompt
    )

    return response.output_text
if __name__ == "__main__":
    query = input("Enter your question: ")
    while query.lower() != "exit":
        answer = answer_query(query)
        print(f"\nAnswer:\n{answer}\n")
        query = input("Enter your question (or type 'exit' to quit): ")