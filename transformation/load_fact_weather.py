import os
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

ingestion_timestamp = datetime.now(
    ZoneInfo("America/Sao_Paulo")
)

load_dotenv()

engine = create_engine(
    f"postgresql+psycopg2://"
    f"{os.getenv('POSTGRES_USER')}:"
    f"{os.getenv('POSTGRES_PASSWORD')}@"
    f"{os.getenv('POSTGRES_HOST')}:"
    f"{os.getenv('POSTGRES_PORT')}/"
    f"{os.getenv('POSTGRES_DB')}"
)

PROCESS_NAME = "fact_weather_load"

with engine.begin() as conn:
    
    result = conn.execute(
        text("""
            SELECT last_execution
            FROM dw.etl_control
            WHERE process_name = :process_name
        """),
        {"process_name": PROCESS_NAME}
    )

    last_execution = result.scalar()
    
    print(f"Última execução: {last_execution}")
    
    if last_execution is None:
        raise ValueError("last_execution não pode ser None")
    
    query = text("""
        SELECT
            observation_time,
            temperature,
            humidity,
            wind_speed,
            ingestion_timestamp
        FROM staging.weather
        WHERE ingestion_timestamp > :last_execution      
    """)
    
    df = pd.read_sql(
        query, 
        conn, 
        params={"last_execution": last_execution}
    )

    if df.empty:
        print("Nenhum registro novo encontrado.")
        exit()
    
    df["observation_time"] = pd.to_datetime(
        df["observation_time"]
    )

    df["date_key"] = (
        df["observation_time"]
        .dt.strftime("%Y%m%d")
        .astype(int)
    )

    fact_df = df[
        [
            "date_key",
            "observation_time",
            "temperature",
            "humidity",
            "wind_speed",
            "ingestion_timestamp",
        ]
    ]

    fact_df.to_sql(
        "fact_weather",
        conn,
        schema="dw",
        if_exists="append",
        index=False,
    )

    max_ingestion = df["ingestion_timestamp"].max()
    
    conn.execute(
        text("""
            UPDATE dw.etl_control
            SET last_execution = :last_execution
            WHERE process_name = :process_name
        """),
        {
            "last_execution": max_ingestion,
            "process_name": PROCESS_NAME
        }
    )
    
    print(
        f"{len(fact_df)} registros carregados."
    )
    
    print(
        f"Controle atualizado para: {max_ingestion}"
    )
