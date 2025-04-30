#!/bin/bash

CSV_FILE="allocine.csv"

echo "⌛ $(date): Début du scraping..." >> /var/log/cron.log

# Lancer scrapy avec un nom de fichier dynamique
scrapy crawl allocine_copy -o "$CSV_FILE" -s FEED_EXPORT_ENCODING=utf-8
if [ $? -ne 0 ]; then
    echo "❌ Scraping échoué" >> /var/log/cron.log
    exit 1
fi

echo "🛠️ Correction de l'encodage vers UTF-8 avec BOM..."

python3 - <<END
import chardet

input_file = "$CSV_FILE"

# Lire le fichier en binaire
with open(input_file, "rb") as f:
    raw_data = f.read()

# Détection de l'encodage
detected = chardet.detect(raw_data)
encoding = detected["encoding"]
print(f"🔍 Encodage détecté: {encoding}")

# Décodage + Réécriture en UTF-8 avec BOM
try:
    text = raw_data.decode(encoding)
    with open(input_file, "w", encoding="utf-8-sig") as f:
        f.write(text)
    print("✅ Encodage corrigé (UTF-8 avec BOM)")
except Exception as e:
    print(f"❌ Erreur de conversion: {e}")
    exit(1)
END

echo "✅ Scraping terminé. Upload..." >> /var/log/cron.log

# Upload du fichier corrigé
python upload_blob.py "$CSV_FILE"
