import requests
import sys

try:
    url = "https://www.jpbox-office.com/fichfilm.php?id=23503"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'
    }
    print("Envoi de la requête...")
    response = requests.get(url, headers=headers)
    print(f"Statut de la réponse: {response.status_code}")
    html_content = response.text
    
    print(f"Taille du contenu HTML: {len(html_content)} caractères")
    # Sauvegarder le HTML dans un fichier pour l'examiner
    with open('page_source.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("HTML sauvegardé dans page_source.html")
except Exception as e:
    print(f"Une erreur s'est produite: {e}", file=sys.stderr)