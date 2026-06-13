import argparse
import os
from pathlib import Path

import pandas as pd


SOURCES = {
    "kerch": {
        "path": "demo_kerch_dictionary.csv",
        "fallback_path": "kerch_dictionary.csv",
        "id_column": "idkword",
        "word_column": "word",
        "output_columns": ["word", "translation"],
    },
    "mironov": {
        "path": "demo_mironov_dictionary.csv",
        "fallback_path": "mironov_fb2.csv",
        "id_column": "idmword",
        "word_column": "rusword",
        "output_columns": ["rusword", "ruword"],
    },
    "pop": {
        "path": "demo_pop_dictionary.csv",
        "fallback_path": "pop_dictionary.csv",
        "id_column": "idpopword",
        "word_column": "ruswordpop",
        "output_columns": ["ruswordpop", "uawordpop", "ruwordpop"],
    },
}


def read_source(base_dir, source_name, config):
    file_path = base_dir / config["path"]
    if not file_path.exists():
        fallback_path = base_dir / config["fallback_path"]
        if fallback_path.exists():
            file_path = fallback_path
        else:
            raise FileNotFoundError(
                f"Не найден файл {file_path}. Поместите demo CSV в demo_data "
                "или приватные CSV в private_data."
            )

    df = pd.read_csv(file_path, dtype=str).fillna("")

    missing_columns = [
        column
        for column in [config["word_column"], *config["output_columns"]]
        if column not in df.columns
    ]
    if missing_columns:
        raise ValueError(
            f"{file_path.name}: отсутствуют колонки {', '.join(missing_columns)}"
        )

    df = df[config["output_columns"]].copy()
    df.insert(0, config["id_column"], range(1, len(df) + 1))
    df["source_word"] = df[config["word_column"]].str.strip()
    df["source"] = source_name

    return df


def build_dictionary(base_dir):
    frames = [
        read_source(base_dir, source_name, config)
        for source_name, config in SOURCES.items()
    ]

    combined = pd.concat(frames, ignore_index=True, sort=False).fillna("")
    unique_words = pd.unique(combined.loc[combined["source_word"] != "", "source_word"])
    word_to_id = {word: index for index, word in enumerate(unique_words, start=1)}

    combined["idrusword"] = combined["source_word"].map(word_to_id)
    combined["X"] = combined["idrusword"]


    combined["Unnamed: 0"] = combined["idkword"]
    combined["IDIndex"] = combined["idmword"]

    for column in [
        "X",
        "idrusword",
        "idkword",
        "idmword",
        "idpopword",
        "Unnamed: 0",
        "IDIndex",
    ]:
        combined[column] = combined[column].map(format_id)

    column_order = [
        "X",
        "idrusword",
        "source",
        "source_word",
        "idkword",
        "idmword",
        "idpopword",
        "Unnamed: 0",
        "IDIndex",
        "word",
        "translation",
        "rusword",
        "ruword",
        "ruswordpop",
        "uawordpop",
        "ruwordpop",
    ]

    return combined.reindex(columns=column_order).fillna("")


def format_id(value):
    if pd.isna(value) or value == "":
        return ""
    return str(int(value))


def parse_args():
    parser = argparse.ArgumentParser(
        description="Создает full_dictionary.csv из демо-словарей или приватных CSV."
    )
    parser.add_argument(
        "--data-dir",
        default=os.getenv("DICTIONARY_DATA_DIR"),
        help="Папка с CSV. По умолчанию: DICTIONARY_DATA_DIR или папка проекта.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="full_dictionary.csv",
        help="Файл результата. По умолчанию: full_dictionary.csv",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    base_dir = Path(args.data_dir).resolve() if args.data_dir else Path(__file__).resolve().parent
    result = build_dictionary(base_dir)
    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = base_dir / output_path
    result.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"Файл успешно сохранен: {output_path.name}")
    print(f"Всего строк: {len(result)}")
    print(f"Уникальных слов: {result['idrusword'].nunique()}")
    for source_name in SOURCES:
        print(f"{source_name}: {(result['source'] == source_name).sum()}")


if __name__ == "__main__":
    main()
