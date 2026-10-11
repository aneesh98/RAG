from dotenv import load_dotenv
from openai import OpenAI
import psycopg
from pgvector.psycopg import register_vector
from pgvector import Vector

load_dotenv()

client = OpenAI()

query = "How many leaves can I take in a month?"

# 1. Convert the question into an embedding
response = client.embeddings.create(
    model="text-embedding-3-small",
    input=query
)

query_vector = Vector(response.data[0].embedding)


# 2. Connect to PostgreSQL
conn = psycopg.connect(
    "postgresql://raguser:ragpassword@localhost:5432/ragdb"
)

register_vector(conn)


# 3. Ask PostgreSQL for the nearest vectors
with conn.cursor() as cur:
    cur.execute(
        """
        SELECT
            id,
            content,
            1 - (embedding <=> %s) AS similarity
        FROM documents
        ORDER BY embedding <=> %s
        LIMIT 4
        """,
        (query_vector, query_vector)
    )

    results = cur.fetchall()


for row in results:
    print(
        round(row[2], 4),
        row[1]
    )

conn.close()