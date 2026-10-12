from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )


@app.route("/")
def home():
    return {
        "message": "Notes API v2 deployed automatically"
    }


@app.route("/health")
def health():
    try:
        conn = get_connection()
        conn.close()

        return {
            "status": "healthy"
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }, 500


@app.route("/init-db")
def init_db():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT
        )
    """)

    conn.commit()

    cur.close()
    conn.close()

    return {
        "message": "Database initialized"
    }


@app.route("/notes", methods=["GET"])
def get_notes():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, title, content FROM notes ORDER BY id"
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    notes = []

    for row in rows:
        notes.append({
            "id": row[0],
            "title": row[1],
            "content": row[2]
        })

    return jsonify(notes)


@app.route("/notes", methods=["POST"])
def create_note():

    body = request.get_json()

    title = body["title"]
    content = body["content"]

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO notes(title, content)
        VALUES (%s, %s)
        """,
        (title, content)
    )

    conn.commit()

    cur.close()
    conn.close()

    return {
        "message": "Note created"
    }


@app.route("/notes/<int:note_id>", methods=["PUT"])
def update_note(note_id):

    body = request.get_json()

    title = body["title"]
    content = body["content"]

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE notes
        SET title = %s,
            content = %s
        WHERE id = %s
        """,
        (title, content, note_id)
    )

    conn.commit()

    cur.close()
    conn.close()

    return {
        "message": f"Note {note_id} updated"
    }


@app.route("/notes/<int:note_id>", methods=["DELETE"])
def delete_note(note_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM notes WHERE id = %s",
        (note_id,)
    )

    conn.commit()

    cur.close()
    conn.close()

    return {
        "message": f"Note {note_id} deleted"
    }


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )