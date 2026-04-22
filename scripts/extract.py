import requests
import json
import os
from datetime import datetime

# =========================
# PATH CONFIG
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "config.json")
RAW_PATH = os.path.join(BASE_DIR, "data", "raw")

# =========================
# LOAD CONFIG
# =========================
with open(CONFIG_PATH) as f:
    config = json.load(f)

API_KEY = os.getenv("API_KEY")
CITIES = config["cities"]
URL = config["api_url"]
UNITS = config["units"]

# =========================
# FUNCTION
# =========================
def extract_weather():

    if not API_KEY:
        raise Exception("❌ API_KEY not found")

    os.makedirs(RAW_PATH, exist_ok=True)

    for city in CITIES:

        url = f"{URL}?q={city}&appid={API_KEY}&units={UNITS}"

        # 🔐 ซ่อน API key
        safe_url = url.replace(API_KEY, "****")
        print(f"🌐 Requesting: {safe_url}")

        try:
            # 🔥 เพิ่ม timeout กัน API ค้าง
            response = requests.get(url, timeout=10)

            if response.status_code != 200:
                print(f"❌ Error {response.status_code} for {city}")
                continue

            data = response.json()

            # =========================
            # 🔥 เพิ่ม metadata (สาย Data Engineer)
            # =========================
            data["_ingest_time"] = datetime.now().isoformat()
            data["_source"] = "openweather_api"

            # =========================
            # SAVE FILE (แยกตามเมือง)
            # =========================
            city_name = city.split(",")[0].replace(" ", "_")

            # 🔥 ป้องกันไฟล์ชน (เพิ่ม microseconds)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

            file_path = os.path.join(RAW_PATH, f"{city_name}_{timestamp}.json")

            with open(file_path, "w") as f:
                json.dump(data, f, indent=4)

            print(f"✅ Saved: {city_name} | dt={data.get('dt')}")

        except Exception as e:
            print(f"💥 Exception for {city}: {e}")


# =========================
# RUN
# =========================
if __name__ == "__main__":
    extract_weather()