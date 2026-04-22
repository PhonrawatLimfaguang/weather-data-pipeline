import pandas as pd
import sqlite3
import os
import glob

# =========================
# FUNCTION: LOAD DATA INTO DATA WAREHOUSE
# =========================
def load_data():
    """
    Load transformed weather data into SQLite using Star Schema

    Features:
    - Auto-detect latest CSV
    - Deduplicate dimension tables
    - Prevent duplicate fact records
    - Add indexes for performance
    - Use foreign keys
    """

    # =========================
    # PATH CONFIG
    # =========================
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    PROCESSED_PATH = os.path.join(BASE_DIR, "data", "processed")
    DB_PATH = os.path.join(BASE_DIR, "data", "weather.db")

    # =========================
    # LOAD LATEST FILE
    # =========================
    files = glob.glob(os.path.join(PROCESSED_PATH, "*.csv"))

    if not files:
        print("❌ No processed files found")
        return

    latest_file = max(files, key=os.path.getctime)
    print(f"📂 Loading file: {latest_file}")

    df = pd.read_csv(latest_file)

    # =========================
    # CONNECT DB
    # =========================
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # เปิดใช้ Foreign Key
    cursor.execute("PRAGMA foreign_keys = ON;")

    # =========================
    # CREATE TABLES
    # =========================

    # 🌍 Location
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dim_location (
        location_id INTEGER PRIMARY KEY AUTOINCREMENT,
        city TEXT,
        country TEXT,
        region TEXT
    )
    """)

    # 📅 Time
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dim_time (
        time_id INTEGER PRIMARY KEY AUTOINCREMENT,
        datetime TEXT,
        date TEXT,
        hour INTEGER
    )
    """)

    # ☁️ Weather
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dim_weather (
        weather_id INTEGER PRIMARY KEY AUTOINCREMENT,
        weather TEXT,
        weather_desc TEXT
    )
    """)

    # ⭐ Fact
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fact_weather (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        location_id INTEGER,
        time_id INTEGER,
        weather_id INTEGER,
        temperature REAL,
        humidity INTEGER,
        pressure INTEGER,
        wind_speed REAL,
        FOREIGN KEY (location_id) REFERENCES dim_location(location_id),
        FOREIGN KEY (time_id) REFERENCES dim_time(time_id),
        FOREIGN KEY (weather_id) REFERENCES dim_weather(weather_id)
    )
    """)

    conn.commit()

    # =========================
    # CREATE INDEX (🔥 เพิ่มความเร็ว)
    # =========================
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fact_time ON fact_weather(time_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fact_location ON fact_weather(location_id)")

    conn.commit()

    # =========================
    # INSERT DATA
    # =========================
    for _, row in df.iterrows():

        # ---------- LOCATION ----------
        cursor.execute("""
            SELECT location_id FROM dim_location
            WHERE city=? AND country=? AND region=?
        """, (row["city"], row["country"], row["region"]))

        result = cursor.fetchone()

        if result:
            location_id = result[0]
        else:
            cursor.execute("""
                INSERT INTO dim_location (city, country, region)
                VALUES (?, ?, ?)
            """, (row["city"], row["country"], row["region"]))
            location_id = cursor.lastrowid

        # ---------- TIME ----------
        cursor.execute("""
            SELECT time_id FROM dim_time
            WHERE datetime=? AND date=? AND hour=?
        """, (row["datetime_24h"], row["date"], row["hour"]))

        result = cursor.fetchone()

        if result:
            time_id = result[0]
        else:
            cursor.execute("""
                INSERT INTO dim_time (datetime, date, hour)
                VALUES (?, ?, ?)
            """, (row["datetime_24h"], row["date"], row["hour"]))
            time_id = cursor.lastrowid

        # ---------- WEATHER ----------
        cursor.execute("""
            SELECT weather_id FROM dim_weather
            WHERE weather=? AND weather_desc=?
        """, (row["weather"], row["weather_desc"]))

        result = cursor.fetchone()

        if result:
            weather_id = result[0]
        else:
            cursor.execute("""
                INSERT INTO dim_weather (weather, weather_desc)
                VALUES (?, ?)
            """, (row["weather"], row["weather_desc"]))
            weather_id = cursor.lastrowid

        # ---------- FACT (กัน duplicate 🔥) ----------
        cursor.execute("""
            SELECT id FROM fact_weather
            WHERE location_id=? AND time_id=? AND weather_id=?
        """, (location_id, time_id, weather_id))

        result = cursor.fetchone()

        if not result:
            cursor.execute("""
                INSERT INTO fact_weather (
                    location_id, time_id, weather_id,
                    temperature, humidity, pressure, wind_speed
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                location_id,
                time_id,
                weather_id,
                row["temperature"],
                row["humidity"],
                row["pressure"],
                row["wind_speed"]
            ))

    # =========================
    # FINALIZE
    # =========================
    conn.commit()
    conn.close()

    print("✅ Data loaded into SQLite (Star Schema - Production Ready)")


# =========================
# RUN
# =========================
if __name__ == "__main__":
    load_data()