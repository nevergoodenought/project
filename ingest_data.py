import csv
import os
from pathlib import Path

import psycopg2
from psycopg2 import sql

def sanitize_sql_string(value):
    """Безопасно обрабатывает строку для вставки в SQL-запрос"""
    if value is None:
        return None
    sanitized = ''.join(c for c in str(value) if ord(c) >= 32 or c in '\t')
    sanitized = sanitized.replace("'", "''").replace('\\', '\\\\')
    return sanitized.strip() or None

DB_CONFIG = {
    "dbname": "rusindb",
    "user": "postgres",
    "password": "toor",
    "host": "db",
    "port": "5432"
}

def create_connection():
    return psycopg2.connect(**DB_CONFIG)

def parse_csv(file_path, pop_file_path='pop_dictionary.csv'):
    data = {
        'kerch': [],
        'pop_rus_ua_ru': [],
        'mirinov': [],
        'rusword': []
    }

    rusword_map = {}

    def get_or_create_rusword(word):
        """Создаёт или возвращает id для русского слова"""
        if not word:
            return None
        if word not in rusword_map:
            rusword_id = len(rusword_map) + 1
            rusword_map[word] = rusword_id
            data['rusword'].append({
                'idrusword': rusword_id,
                'rusword': word
            })
        return rusword_map[word]

    with open(file_path, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            source = row['source']

            if source == 'kerch':
                # word = русинское слово (левый столбец словаря Керча)
                rusin_word = sanitize_sql_string(row['word'])
                if not rusin_word:
                    continue

                rusword_id = get_or_create_rusword(rusin_word)

                data['kerch'].append({
                    'idkword': int(row['Unnamed: 0']),
                    'ruwordkerch': rusin_word,
                    'ruswordkerch': sanitize_sql_string(row['translation']),
                    'idrusword': rusword_id
                })

            elif source == 'pop':
                continue

            elif source == 'mironov':
                # rusword = русское слово, ruword = русинский перевод
                rus_word = sanitize_sql_string(row['rusword'])
                if not rus_word:
                    continue

                rusword_id = get_or_create_rusword(rus_word)

                data['mirinov'].append({
                    'idmword': int(row['IDIndex']),
                    'ruswordm': rus_word,
                    'ruwordm': sanitize_sql_string(row['ruword']),
                    'idrusword': rusword_id
                })

    with open(pop_file_path, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)

        for idpopword, row in enumerate(reader, start=1):
            rus_word = sanitize_sql_string(row.get('ruswordpop'))
            if not rus_word:
                continue

            rusword_id = get_or_create_rusword(rus_word)

            data['pop_rus_ua_ru'].append({
                'idpopword': idpopword,
                'ruwordpop': sanitize_sql_string(row.get('ruwordpop')),
                'ruswordpop': rus_word,
                'uawordpop': sanitize_sql_string(row.get('uawordpop')),
                'idrusword': rusword_id
            })

    print(f"Загружено: rusword={len(data['rusword'])}, kerch={len(data['kerch'])}, "
          f"pop={len(data['pop_rus_ua_ru'])}, mirinov={len(data['mirinov'])}")
    return data

def insert_data(conn, data):
    with conn.cursor() as cursor:
        cursor.execute("""
            TRUNCATE TABLE kerch, mirinov, pop_rus_ua_ru, rusword
            RESTART IDENTITY CASCADE
        """)

        # rusword
        for item in data['rusword']:
            cursor.execute(sql.SQL("""
                INSERT INTO rusword (idrusword, rusword)
                VALUES ({}, {})
                ON CONFLICT (idrusword) DO NOTHING
            """).format(
                sql.Literal(item['idrusword']),
                sql.Literal(item['rusword'])
            ))

        # kerch
        for item in data['kerch']:
            cursor.execute(sql.SQL("""
                INSERT INTO kerch (idkword, ruwordkerch, ruswordkerch, idrusword)
                VALUES ({}, {}, {}, {})
                ON CONFLICT (idkword, idrusword) DO NOTHING
            """).format(
                sql.Literal(item['idkword']),
                sql.Literal(item['ruwordkerch']),
                sql.Literal(item['ruswordkerch']),
                sql.Literal(item['idrusword'])
            ))

        # pop_rus_ua_ru
        for item in data['pop_rus_ua_ru']:
            cursor.execute(sql.SQL("""
                INSERT INTO pop_rus_ua_ru (idpopword, ruwordpop, ruswordpop, uawordpop, idrusword)
                VALUES ({}, {}, {}, {}, {})
                ON CONFLICT (idpopword, idrusword) DO NOTHING
            """).format(
                sql.Literal(item['idpopword']),
                sql.Literal(item['ruwordpop']),
                sql.Literal(item['ruswordpop']),
                sql.Literal(item['uawordpop']),
                sql.Literal(item['idrusword'])
            ))

        # mirinov
        for item in data['mirinov']:
            cursor.execute(sql.SQL("""
                INSERT INTO mirinov (idmword, ruswordm, ruwordm, idrusword)
                VALUES ({}, {}, {}, {})
                ON CONFLICT (idmword, idrusword) DO NOTHING
            """).format(
                sql.Literal(item['idmword']),
                sql.Literal(item['ruswordm']),
                sql.Literal(item['ruwordm']),
                sql.Literal(item['idrusword'])
            ))

        conn.commit()

def main():
    default_data_dir = Path(__file__).resolve().parent / "demo_data"
    data_dir = Path(os.getenv("DICTIONARY_DATA_DIR", default_data_dir)).resolve()
    full_dictionary_path = data_dir / 'full_dictionary.csv'
    pop_dictionary_path = data_dir / 'demo_pop_dictionary.csv'
    if not pop_dictionary_path.exists():
        pop_dictionary_path = data_dir / 'pop_dictionary.csv'
    missing_files = [
        path.name
        for path in [full_dictionary_path, pop_dictionary_path]
        if not path.exists()
    ]

    if missing_files:
        print(
            "Приватные словари не загружены: отсутствуют "
            f"{', '.join(missing_files)} в {data_dir}. "
            "Приложение запустится с пустой базой; для демо-данных "
            "используйте demo_data, для полных локальных данных - private_data."
        )
        return

    conn = create_connection()
    try:
        data = parse_csv(full_dictionary_path, pop_dictionary_path)
        insert_data(conn, data)
        print("Данные успешно загружены в базу данных")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main()
