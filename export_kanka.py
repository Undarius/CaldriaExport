import requests
import json
import os
import zipfile
from pathlib import Path

# 🔐 Deine API-Konfiguration
API_TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiNzhjNzAxZGZiNjYzMzVlNDNiYTBlMzE0ZjU2M2IxZjFlZjNmMGRmZmRmYTIzMGZkYTZhNDkyZTkwNGExZDU1ZWFkYjMxZGRmNjkyYjgxNjAiLCJpYXQiOjE3NDg0NTMwNzQuNDg4MTUxLCJuYmYiOjE3NDg0NTMwNzQuNDg4MTU1LCJleHAiOjE3Nzk5ODkwNzQuNDgzMDcyLCJzdWIiOiIzMjM2MjkiLCJzY29wZXMiOltdfQ.W57UzUu1jiTnqi8yo1hbC-6BQOYdkE7geCNtfKvXvaOn0gJcwzYV85P6Ek0nsKlHuvjkb4ZPvGIPHgQihgkdz5UaAH-HFAGdjepBW901GINRMkfe0Y8V2vyXJLv9qQTCSq9mDK97q4uKtb9EobVyi4eYoXXZbBy-GN4c4N2OWp-f4NLntk5_TThGBCPshwIeye-54tpYxlNBtrv5TT1dDENP0TSrwglX0YlGeD5UpMKP18E3D_XXmNWRk7kspE7cdbgedgG4rrSRzpzaCAPeaoKBYI-7oMc0BW0n2Y339ckyPb8CmNn-_bZwtlaAAjEzcgf--579dPjdHfvGxqLbYOaLFNa6-DrVIyW0fm6cITuGBDgQInQCuKjxCQqI0-ep200yvCkpgvGcGfXMuKgSR03spPky396kJ3OyEklitg15cMGNtzlY4uEOl75kH9ZYD1RU-jNjBknolLdDQnnhVvPBFWnYUBtiMAtHxlOe6fJemVxNnEO_eQFf95JYUGCqia7HjP5ccGPT5kqLunvpqa5ZW2VdW5lcszQJR8yKGhrSFZtBhSl36wti_GzTf3wRlxz5_j0aj9D8K3s7bKvDLcjRZDC0I29UsXZvOjDIkyZiA6crIJ9fL7Bxl20Z8qxm8OoqYktCR1eTwGj03SZLLpYAsQHkJlelEiZ0sR7-1wU'
CAMPAIGN_ID = '316191'
BASE_URL = f'https://api.kanka.io/1.0/campaigns/{CAMPAIGN_ID}'
HEADERS = {
    'Authorization': f'Bearer {API_TOKEN}',
    'Accept': 'application/json'
}

# 📦 Die Kanka-Endpunkte, die wir abrufen wollen
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

# 🗂️ Speicherort für Export
EXPORT_DIR = Path("caldria_export_full")
ZIP_NAME = EXPORT_DIR.with_suffix('.zip')
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

# 📄 Funktion zum Abrufen aller Seiten eines Endpunkts
def fetch_all(endpoint):
    all_data = []
    page = 1
    while True:
        response = requests.get(f"{BASE_URL}/{endpoint}?page={page}", headers=HEADERS)
        if response.status_code != 200:
            print(f"❌ Fehler bei {endpoint}, Seite {page}")
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

# 👥 Zusatzfunktion: Mitglieder einer Organisation laden
def fetch_org_members(org_id):
    url = f"{BASE_URL}/organisations/{org_id}/organisation_members"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        print(f"⚠️ Fehler bei Mitgliedern für Org {org_id}")
        return []

# 🔁 Hauptloop: Alle Daten abrufen und speichern
all_data = {}
for resource in RESOURCE_TYPES:
    print(f"⬇️ Lade: {resource}")
    data = fetch_all(resource)
    all_data[resource] = data
    with open(EXPORT_DIR / f"{resource}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# 👥 Erweiterung: Organisationen mit Mitgliedern anreichern
for org in all_data.get("organisations", []):
    org_id = org.get("id")
    org["members"] = fetch_org_members(org_id)

# 💾 Speichere Organisationen mit Mitgliedern separat
with open(EXPORT_DIR / "organisations_with_members.json", "w", encoding="utf-8") as f:
    json.dump(all_data["organisations"], f, indent=2, ensure_ascii=False)

# 📦 ZIP-Archiv aller JSON-Dateien erstellen
with zipfile.ZipFile(ZIP_NAME, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for file in EXPORT_DIR.glob("*.json"):
        zipf.write(file, arcname=file.name)

print(f"✅ Export abgeschlossen: {ZIP_NAME.resolve()}")
