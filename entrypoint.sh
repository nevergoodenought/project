#!/bin/sh
DATA_DIR="${DICTIONARY_DATA_DIR:-/usr/src/app/demo_data}"

echo "Ожидание..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "PostgreSQL запущен"

if [ ! -f "$DATA_DIR/full_dictionary.csv" ] \
  && { [ -f "$DATA_DIR/demo_kerch_dictionary.csv" ] || [ -f "$DATA_DIR/kerch_dictionary.csv" ]; } \
  && { [ -f "$DATA_DIR/demo_mironov_dictionary.csv" ] || [ -f "$DATA_DIR/mironov_fb2.csv" ]; } \
  && { [ -f "$DATA_DIR/demo_pop_dictionary.csv" ] || [ -f "$DATA_DIR/pop_dictionary.csv" ]; }; then
  echo "Собираю full_dictionary.csv из CSV-словарей..."
  python idxcsv.py --data-dir "$DATA_DIR" --output "$DATA_DIR/full_dictionary.csv"
fi

python ingest_data.py
flask --app app run --host=0.0.0.0
   
