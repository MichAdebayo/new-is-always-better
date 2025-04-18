#!/bin/bash

CSV_FILE="allocine.csv"

echo "⌛ $(date): Début du scraping..." >> /var/log/cron.log

# Lancer scrapy avec export en UTF-8 (s'il n'est pas déjà défini dans settings.py)
scrapy crawl allocine_copy -o "$CSV_FILE" -s FEED_EXPORT_ENCODING=utf-8
if [ $? -ne 0 ]; then
    echo "❌ Scraping échoué" >> /var/log/cron.log
    exit 1
fi

# Vérification de l'encodage réel du fichier
ENCODING=$(file -bi "$CSV_FILE" | awk -F "=" '{print $2}')
echo "📦 Encodage détecté : $ENCODING"

# Si le fichier est en UTF-16, le convertir en UTF-8
if [[ "$ENCODING" == "utf-16le" || "$ENCODING" == "utf-16be" ]]; then
    echo "⚠️ Encodage UTF-16 détecté. Conversion en UTF-8..."
    iconv -f UTF-16 -t UTF-8 "$CSV_FILE" -o "${CSV_FILE}.utf8"
    mv "${CSV_FILE}.utf8" "$CSV_FILE"
    echo "✅ Conversion terminée."
fi

echo "✅ Scraping terminé. Upload..." >> /var/log/cron.log

# Passer le nom du fichier au script Python
python upload_blob.py "$CSV_FILE"
