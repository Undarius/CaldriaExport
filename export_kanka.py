import requests
import json
import zipfile
from pathlib import Path

# 🔐 Deine API-Konfiguration
API_TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiNzhjNzAxZGZiNjYzMzVlNDNiYTBlMzE0ZjU2M2IxZjFlZjNmMGRmZmRmYTIzMGZkYTZhNDkyZTkwNGExZDU1ZWFkYjMxZGRmNjkyYjgxNjAiLCJpYXQiOjE3NDg0NTMwNzQuNDg4MTUxLCJuYmYiOjE3NDg0NTMwNzQuNDg4MTU1LCJleHAiOjE3Nzk5ODkwNzQuNDgzMDcyLCJzdWIiOiIzMjM2MjkiLCJzY29wZXMiOltdfQ.W57UzUu1jiTnqi8yo1hbC-6BQOYdkE7geCNtfKvXvaOn0gJcwzYV85P6Ek0nsKlHuvjkb4ZPvGIPHgQihgkdz5UaAH-HFAGdjepBW901GINRMkfe0Y8V2vyXJLv9qQTCSq9mDK97q4uKtb9EobVyi4eYoXXZbBy-GN4c4N2OWp-f4NLntk5_TThGBCPshwIeye-54tpYxlNBtrv5TT1dDENP0TSrwglX0YlGeD5UpMKP18E3D_XXmNWRk7kspE7cdbgedgG4rrSRzpzaCAPeaoKBYI-7oMc0BW0n2Y339ckyPb8CmNn-_bZwtlaAAjEzcgf--579dPjdHfvGxqLbYOaLFNa6-DrVIyW0fm6cITuGBDgQInQCuKjxCQqI0-ep200yvCkpgvGcGfXMuKgSR03spPky396kJ3OyEklitg15cMGNtzlY4uEOl75kH9ZYD1RU-jNjBknolLdDQnnhVvPBFWnYUBtiMAtHxlOe6fJemVxNnEO_eQFf95JYUGCqia7HjP5ccGPT5kqLunvpqa5ZW2VdW5lcszQJR8yKGhrSFZtBhSl36wti_GzTf3wRlxz5_j0aj9D8K3s7bKvDLcjRZDC0I29UsXZvOjDIkyZiA6crIJ9fL7Bxl20Z8qxm8OoqYktCR1eTwGj03SZLLpYAsQHkJlelEiZ0sR7-1wU'
CAMPAIGN_ID = '316191'
BASE_URL = f'https://api.kanka.io/1.0/campaigns/{CAMPAIGN_ID}'
HEADERS = {'Authorization': f'Bearer {API_TOKEN}', 'Accept': 'application/json'}

EXPORT_DIR = Path("caldria_export_extended")
ZIP_NAME = EXPORT_DIR.with_suffix('.zip')
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

RESOURCE_TYPES = [
    'characters',
    'organisations',
    'locations',
    'families',
    'items',
    'journals',
    'quests',
    'events',
    'races',
    'tags'
]

# Mapping: Hauptressource → Liste von Subressourcen
SUB_RESOURCES = {
    'organisations': ['organisation_members'],
    'characters': ['relationships'],
    'items': ['abilities'],
}

def fetch_all(endpoint):
    """Seitenweise alle Daten eines Endpunkts abrufen."""
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

def fetch_subresource(resource, entry_id, sub):
    """Subressource (z. B. organisation_members) eines Elements laden."""
    url = f"{BASE_URL}/{resource}/{entry_id}/{sub}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        return []

# Alle Hauptressourcen holen
all_data = {}
for resource in RESOURCE_TYPES:
    print(f"⬇️ Lade: {resource}")
    data = fetch_all(resource)
    all_data[resource] = data
    with open(EXPORT_DIR / f"{resource}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Prüfen, ob Subressourcen existieren
    if resource in SUB_RESOURCES:
        for sub in SUB_RESOURCES[resource]:
            combined = []
            for entry in data:
                sub_data = fetch_subresource(resource, entry["id"], sub)
                combined.append({
                    "id": entry["id"],
                    "name": entry["name"],
                    "subresource": sub,
                    "entries": sub_data
                })
            with open(EXPORT_DIR / f"{resource}__{sub}.json", "w", encoding="utf-8") as f:
                json.dump(combined, f, indent=2, ensure_ascii=False)

# ZIP erstellen
with zipfile.ZipFile(ZIP_NAME, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for file in EXPORT_DIR.glob("*.json"):
        zipf.write(file, arcname=file.name)

print(f"✅ Erweiterter Export abgeschlossen: {ZIP_NAME.resolve()}")