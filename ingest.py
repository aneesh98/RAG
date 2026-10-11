from dotenv import load_dotenv
from openai import OpenAI
import psycopg
from pgvector.psycopg import register_vector

load_dotenv()

client = OpenAI()

documents = [
    "The employee may request a new laptop from the IT portal.",
    "Hardware replacements require manager approval.",
    "The cafeteria serves breakfast until 10:30 AM.",
    "VPN access is available to remote employees."
]


conn = psycopg.connect(
    "postgresql://raguser:ragpassword@localhost:5432/ragdb"
)

register_vector(conn)

response = client.embeddings.create(
    model="text-embedding-3-small",
    input=documents
)

with conn.cursor() as cur:

    for document, embedding_data in zip(
        documents,
        response.data
    ):
        cur.execute(
            """
            INSERT INTO documents (content, embedding)
            VALUES (%s, %s)
            """,
            (
                document,
                embedding_data.embedding
            )
        )

conn.commit()
conn.close()