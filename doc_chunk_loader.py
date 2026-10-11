from pathlib import Path
import re

from dotenv import load_dotenv
from openai import OpenAI
import psycopg
from pgvector.psycopg import register_vector
from pgvector import Vector


load_dotenv()

client = OpenAI()

text = Path("employee_handbook.txt").read_text(
    encoding="utf-8"
)

pattern = r"={5,}\s*\n(\d+\.\s+[^\n]+)\n={5,}"

matches = list(re.finditer(pattern, text))

print(f"Found {len(matches)} sections")

sections = []

for i, match in enumerate(matches):
    heading = match.group(1)

    content_start = match.end()

    if i + 1 < len(matches):
        content_end = matches[i + 1].start()
    else:
        content_end = len(text)

    content = text[content_start:content_end].strip()

    sections.append({
        "heading": heading,
        "content": content
    })

embedding_texts = [
    f"{section['heading']}\n\n{section['content']}"
    for section in sections
]

embedding_response = client.embeddings.create(
    model="text-embedding-3-small",
    input=embedding_texts
)

conn = psycopg.connect(
    "postgresql://raguser:ragpassword@localhost:5432/ragdb"
)

register_vector(conn)

with conn.cursor() as cur:

    for index, (section, embedding_data) in enumerate(
        zip(sections, embedding_response.data)
    ):

        cur.execute(
            """
            INSERT INTO document_chunks (
                document_name,
                section_heading,
                chunk_index,
                content,
                embedding
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                "employee_handbook.txt",
                section["heading"],
                index,
                section["content"],
                Vector(embedding_data.embedding)
            )
        )

conn.commit()