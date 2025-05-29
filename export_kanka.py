import zipfile

import requests
import json
import os

API_TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiNzhjNzAxZGZiNjYzMzVlNDNiYTBlMzE0ZjU2M2IxZjFlZjNmMGRmZmRmYTIzMGZkYTZhNDkyZTkwNGExZDU1ZWFkYjMxZGRmNjkyYjgxNjAiLCJpYXQiOjE3NDg0NTMwNzQuNDg4MTUxLCJuYmYiOjE3NDg0NTMwNzQuNDg4MTU1LCJleHAiOjE3Nzk5ODkwNzQuNDgzMDcyLCJzdWIiOiIzMjM2MjkiLCJzY29wZXMiOltdfQ.W57UzUu1jiTnqi8yo1hbC-6BQOYdkE7geCNtfKvXvaOn0gJcwzYV85P6Ek0nsKlHuvjkb4ZPvGIPHgQihgkdz5UaAH-HFAGdjepBW901GINRMkfe0Y8V2vyXJLv9qQTCSq9mDK97q4uKtb9EobVyi4eYoXXZbBy-GN4c4N2OWp-f4NLntk5_TThGBCPshwIeye-54tpYxlNBtrv5TT1dDENP0TSrwglX0YlGeD5UpMKP18E3D_XXmNWRk7kspE7cdbgedgG4rrSRzpzaCAPeaoKBYI-7oMc0BW0n2Y339ckyPb8CmNn-_bZwtlaAAjEzcgf--579dPjdHfvGxqLbYOaLFNa6-DrVIyW0fm6cITuGBDgQInQCuKjxCQqI0-ep200yvCkpgvGcGfXMuKgSR03spPky396kJ3OyEklitg15cMGNtzlY4uEOl75kH9ZYD1RU-jNjBknolLdDQnnhVvPBFWnYUBtiMAtHxlOe6fJemVxNnEO_eQFf95JYUGCqia7HjP5ccGPT5kqLunvpqa5ZW2VdW5lcszQJR8yKGhrSFZtBhSl36wti_GzTf3wRlxz5_j0aj9D8K3s7bKvDLcjRZDC0I29UsXZvOjDIkyZiA6crIJ9fL7Bxl20Z8qxm8OoqYktCR1eTwGj03SZLLpYAsQHkJlelEiZ0sR7-1wU'
CAMPAIGN_ID = '316191'
BASE_URL = f'https://api.kanka.io/1.0/campaigns/{CAMPAIGN_ID}'
HEADERS = {
    'Authorization': f'Bearer {API_TOKEN}',
    'Accept': 'application/json'
}

# Konfigurierbare (aber erweiterbare) Ressourcentypen
RESOURCE_TYPES = [
    'characters',
    'organisations',
    'locations',
    'families',
    'items',
    'journals',
    'abilities',
    'quests',
    'races',
    'notes',
    'events',
    'tags'
]

EXPORT_DIR = "caldria_export"
ZIP_NAME = "caldria_export.zip"
os.makedirs(EXPORT_DIR, exist_ok=True)

def fetch_all(endpoint):
    print(f"⬇️  Lade: {endpoint} ...")
    all_data = []
    page = 1
    while True:
        response = requests.get(f"{BASE_URL}/{endpoint}?page={page}", headers=HEADERS)
        if response.status_code != 200:
            print(f"❌ Fehler bei {endpoint}, Seite {page}: {response.status_code}")
            break
        data = response.json()
        entries = data.get("data", [])
        if not entries:
            break
        all_data.extend(entries)
        if not data.get("links", {}).get("next"):
            break
        page += 1
    return all_data

# Daten abrufen und speichern
for resource in RESOURCE_TYPES:
    results = fetch_all(resource)
    if results:
        with open(f"{EXPORT_DIR}/{resource}.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"✅ {resource}: {len(results)} Einträge gespeichert.")
    else:
        print(f"⚠️  Keine Daten für {resource}.")

# ZIP erstellen
with zipfile.ZipFile(ZIP_NAME, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(EXPORT_DIR):
        for file in files:
            full_path = os.path.join(root, file)
            arcname = os.path.relpath(full_path, EXPORT_DIR)
            zipf.write(full_path, arcname)
print(f"📦 Export abgeschlossen: {ZIP_NAME}")