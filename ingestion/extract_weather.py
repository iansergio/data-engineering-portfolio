import json
from pathlib import Path

import requests

LATITUDE = -26.3044  # Joinville
LONGITUDE = -48.8487

url = (
    "https://api.open-meteo.com/v1/forecast"
    f"?latitude={LATITUDE}"
    f"&longitude={LONGITUDE}"
    "&current=temperature_2m,relative_humidity_2m,wind_speed_10m"
)

response = requests.get(url, timeout=30)
response.raise_for_status()

data = response.json()

output_dir = Path("data/weather")
output_dir.mkdir(parents=True, exist_ok=True)

output_file = output_dir / "weather.json"

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
    
print(f"Arquivo salvo em {output_file}")
