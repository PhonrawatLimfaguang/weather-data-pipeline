import json
import pandas as pd
import glob
import os
from datetime import datetime  

# =========================
# PATH CONFIG
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_PATH = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_PATH = os.path.join(BASE_DIR, "data", "processed")

# =========================
# REGION MAP (🔥 อัปเกรด)
# =========================
REGION_MAP = {
    "Bangkok": "Central",
    "Chiang Mai": "North",
    "Chiang Rai": "North",
    "Phuket": "South",
    "Surat Thani": "South",
    "Khon Kaen": "Northeast",
    "Udon Thani": "Northeast",
    "Nakhon Ratchasima": "Northeast"
}

# =========================
# FUNCTION
# =========================
def transform_weather():

    files = glob.glob(os.path.join(RAW_PATH, "*.json"))

    if not files:
        print("❌ No raw files found")
        return

    records = []

    for file in files:
        try:
            with open(file) as f:
                data = json.load(f)

                # =========================
                # TIME
                # =========================
                dt_obj = datetime.fromtimestamp(data["dt"])

                city_name = data["name"]

                record = {
                    # 🌍 Location
                    "city": city_name,
                    "country": data["sys"]["country"],
                    "region": REGION_MAP.get(city_name, "Unknown"),

                    # 🌡 Weather
                    "temperature": data["main"]["temp"],
                    "feels_like": data["main"]["feels_like"],
                    "temp_min": data["main"]["temp_min"],
                    "temp_max": data["main"]["temp_max"],
                    "humidity": data["main"]["humidity"],
                    "pressure": data["main"]["pressure"],

                    # ☁️ Condition
                    "weather": data["weather"][0]["main"],
                    "weather_desc": data["weather"][0]["description"],

                    # 🌬 Wind
                    "wind_speed": data["wind"]["speed"],
                    "clouds": data["clouds"]["all"],

                    # ⏰ Time
                    "timestamp": data["dt"],
                    "datetime_24h": dt_obj.strftime("%Y-%m-%d %H:%M:%S"),
                    "datetime_12h": dt_obj.strftime("%Y-%m-%d %I:%M:%S %p"),
                    "date": dt_obj.strftime("%Y-%m-%d"),
                    "hour": dt_obj.hour,

                    # 🌗 Time category
                    "time_period": (
                        "Morning" if 5 <= dt_obj.hour < 12 else
                        "Afternoon" if 12 <= dt_obj.hour < 17 else
                        "Evening" if 17 <= dt_obj.hour < 21 else
                        "Night"
                    )
                }

                records.append(record)

        except Exception as e:
            print(f"⚠️ Error reading file {file}: {e}")
            continue

    # =========================
    # CREATE DATAFRAME
    # =========================
    df = pd.DataFrame(records)

    # 🔥 ลบ duplicate
    df = df.drop_duplicates(subset=["city", "timestamp"])

    # 🔥 sort เวลา (สำคัญมาก)
    df = df.sort_values(by=["city", "timestamp"])

    # 🔥 reset index
    df = df.reset_index(drop=True)

    # =========================
    # SAVE
    # =========================
    os.makedirs(PROCESSED_PATH, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(PROCESSED_PATH, f"weather_clean_{timestamp}.csv")

    df.to_csv(output_path, index=False)

    print(f"✅ Transformed data saved to {output_path}")
    print(f"📊 Total records: {len(df)}")


# =========================
# RUN
# =========================
if __name__ == "__main__":
    transform_weather()