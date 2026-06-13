import csv
from pathlib import Path


DEMO_ROWS = 200
DEMO_DIR = Path(__file__).resolve().parent / "demo_data"


def write_csv(path, fieldnames, rows):
    DEMO_DIR.mkdir(exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    write_csv(
        DEMO_DIR / "demo_kerch_dictionary.csv",
        ["word", "translation"],
        [
            {
                "word": f"demo_rusin_kerch_{index:03d}",
                "translation": f"demo_russian_kerch_{index:03d}",
            }
            for index in range(1, DEMO_ROWS + 1)
        ],
    )

    write_csv(
        DEMO_DIR / "demo_mironov_dictionary.csv",
        ["IDIndex", "rusword", "ruword"],
        [
            {
                "IDIndex": index,
                "rusword": f"demo_russian_mironov_{index:03d}",
                "ruword": f"demo_rusin_mironov_{index:03d}",
            }
            for index in range(1, DEMO_ROWS + 1)
        ],
    )

    write_csv(
        DEMO_DIR / "demo_pop_dictionary.csv",
        ["ruswordpop", "uawordpop", "ruwordpop"],
        [
            {
                "ruswordpop": f"demo_russian_pop_{index:03d}",
                "uawordpop": f"demo_ukrainian_pop_{index:03d}",
                "ruwordpop": f"demo_rusin_pop_{index:03d}",
            }
            for index in range(1, DEMO_ROWS + 1)
        ],
    )

    print(f"Demo dictionaries generated in {DEMO_DIR}")


if __name__ == "__main__":
    main()
