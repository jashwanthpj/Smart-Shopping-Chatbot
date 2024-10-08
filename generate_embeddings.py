import psycopg2
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

try:
    conn = psycopg2.connect(
        dbname = "shopping_data",
        user = "postgres",
        password = "Pj262001@",
        host = "Localhost"
    )

    cursor = conn.cursor()
    cursor.execute("SELECT id, pdt_desc FROM apparels LIMIT 1")
    rows = cursor.fetchall()

    for row in rows:
        id = row[0]
        description = row[1]

        embedding = model.encode(description).tolist()
        cursor.execute(
            "UPDATE apparels SET embedding = %s WHERE id = %s", (embedding, id)
        )
    conn.commit()

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    if cursor is not None:
        cursor.close()
    if conn is not None:
        conn.close()
