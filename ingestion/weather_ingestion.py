import os
import json
from datetime import datetime, timezone
from io import BytesIO

import pandas as pd
import requests
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient

load_dotenv()

CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = os.getenv("BRONZE_CONTAINER")

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

current = data["current"]

df = pd.DataFrame([{
    "timestamp": current["time"],
    "temperature": current["temperature_2m"],
    "humidity": current["relative_humidity_2m"],
    "wind_speed": current["wind_speed_10m"]
}])

buffer = BytesIO()
df.to_parquet(buffer, engine="pyarrow", index=False)
buffer.seek(0)

today = datetime.now(timezone.utc)
blob_path = (
    f"weather/"
    f"year={today.year}/"
    f"month={today.month:02d}/"
    f"day={today.day:02d}/"
    f"weather.parquet"
)

blob_service = BlobServiceClient.from_connection_string(
    str(CONNECTION_STRING)
)

blob_client = blob_service.get_blob_client(
    container=str(CONTAINER_NAME),
    blob=blob_path
)

blob_client.upload_blob(
    buffer,
    overwrite=True
)

print(f"Arquivo enviado para: {blob_path}")