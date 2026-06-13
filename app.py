import os

import psycopg2
from flask import Flask, jsonify, render_template, request
from psycopg2.extras import RealDictCursor


app = Flask(__name__)


DB_CONFIG = {
    "dbname": "rusindb",
    "user": "postgres",
    "password": "toor",
    "host": "db",
    "port": "5432",
}


def get_connection():
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return psycopg2.connect(database_url)
    return psycopg2.connect(**DB_CONFIG)


def search_dictionary(term):
    results = {"kerch": [], "pop_dict": [], "mirinov": []}

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT k.idkword AS id, k.ruwordkerch AS ru, k.ruswordkerch AS rus
                FROM kerch k
                WHERE k.ruwordkerch ILIKE %s OR k.ruswordkerch ILIKE %s
                ORDER BY idkword
                LIMIT 100
                """,
                (term, term),
            )
            results["kerch"] = [dict(row) for row in cursor.fetchall()]

            cursor.execute(
                """
                SELECT p.idpopword AS id, p.ruwordpop AS ru, p.ruswordpop AS rus, p.uawordpop AS ua
                FROM pop_rus_ua_ru p
                WHERE p.ruwordpop ILIKE %s OR p.ruswordpop ILIKE %s OR p.uawordpop ILIKE %s
                ORDER BY idpopword
                LIMIT 100
                """,
                (term, term, term),
            )
            results["pop_dict"] = [dict(row) for row in cursor.fetchall()]

            cursor.execute(
                """
                SELECT m.idmword AS id, m.ruwordm AS ru, m.ruswordm AS rus
                FROM mirinov m
                WHERE m.ruwordm ILIKE %s OR m.ruswordm ILIKE %s
                ORDER BY idmword
                LIMIT 100
                """,
                (term, term),
            )
            results["mirinov"] = [dict(row) for row in cursor.fetchall()]

    return results


def find_similar_words(term):
    pattern = f"{term}%"
    words = []

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            queries = [
                (
                    "kerch",
                    """
                    SELECT ruwordkerch AS word
                    FROM kerch
                    WHERE ruwordkerch ILIKE %s
                    ORDER BY ruwordkerch
                    LIMIT 50
                    """,
                ),
                (
                    "mironov",
                    """
                    SELECT ruswordm AS word
                    FROM mirinov
                    WHERE ruswordm ILIKE %s
                    ORDER BY ruswordm
                    LIMIT 50
                    """,
                ),
                (
                    "pop",
                    """
                    SELECT ruswordpop AS word
                    FROM pop_rus_ua_ru
                    WHERE ruswordpop ILIKE %s
                    ORDER BY ruswordpop
                    LIMIT 50
                    """,
                ),
            ]

            for source, query in queries:
                cursor.execute(query, (pattern,))
                words.extend(
                    {"word": row["word"], "source": source}
                    for row in cursor.fetchall()
                    if row["word"]
                )

    return words[:100]


@app.route("/")
def index():
    term = request.args.get("term", "").strip()
    results = search_dictionary(term) if term else {"kerch": [], "pop_dict": [], "mirinov": []}
    return render_template(
        "search.html",
        search_term=term,
        search_performed=bool(term),
        results=results,
    )


@app.route("/search")
def search():
    term = request.args.get("term", "").strip()
    results = search_dictionary(term) if term else {"kerch": [], "pop_dict": [], "mirinov": []}

    if request.accept_mimetypes.best == "application/json":
        return jsonify({"results": results})

    return render_template(
        "search.html",
        search_term=term,
        search_performed=bool(term),
        results=results,
    )


@app.route("/similar")
def similar():
    term = request.args.get("term", "").strip()
    similar_words = find_similar_words(term) if term else []

    if request.accept_mimetypes.best == "application/json":
        return jsonify({"similar": similar_words})

    return render_template(
        "similar.html",
        search_term=term,
        search_performed=bool(term),
        similar_words=similar_words,
    )
