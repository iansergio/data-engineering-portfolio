import json
import os
from pathlib import Path
from zoneinfo import ZoneInfo
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

engine = create_engine(
    f"postgresql+psycopg2://"
    f"{os.getenv('POSTGRES_USER')}:"
    f"{os.getenv('POSTGRES_PASSWORD')}@"
    f"{os.getenv('POSTGRES_HOST')}:"
    f"{os.getenv('POSTGRES_PORT')}/"
    f"{os.getenv('POSTGRES_DB')}"
)

file_path = Path("data/weather/weather.json")

with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

current = data["current"]

df = pd.DataFrame([
    {
        "observation_time": current["time"],
        "temperature": current["temperature_2m"],
        "humidity": current["relative_humidity_2m"],
        "wind_speed": current["wind_speed_10m"],
        "ingestion_timestamp": datetime.now(
            ZoneInfo("America/Sao_Paulo")
        ),
    }
])

df["observation_time"] = pd.to_datetime(
    df["observation_time"],
    utc=True
)

df.to_sql(
    "weather",
    engine,
    schema="staging",
    if_exists="append",
    index=False,
)

print("Carga staging concluída.")
