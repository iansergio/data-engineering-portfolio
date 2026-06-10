import json
import os
from datetime import datetime
from io import BytesIO
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

load_dotenv()

file_path = Path("data/weather/weather.json")

with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)
    
current = data["current"]

df = pd.DataFrame([{
    "timestamp": current["time"],
    "temperature": current["temperature_2m"],
    "humidity": current["relative_humidity_2m"],
    "wind_speed": current["wind_speed_10m"]
}])

buffer = BytesIO()

df.to_parquet(
    buffer, 
    engine="pyarrow", 
    index=False
)

buffer.seek(0)

now = datetime.now(
    ZoneInfo("America/Sao_Paulo")
)

blob_path = (
    f"weather/"
    f"year={now.year}/"
    f"month={now.month:02d}/"
    f"day={now.day:02d}/"
    f"weather.parquet"
)

CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = os.getenv("BRONZE_CONTAINER")

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
