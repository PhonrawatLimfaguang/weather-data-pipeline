-- =========================================
-- 🌦 Weather Data Warehouse Schema (Star Schema)
-- =========================================

-- =========================
-- 🌍 Location Dimension
-- =========================
CREATE TABLE dim_location (
    location_id INTEGER PRIMARY KEY AUTOINCREMENT,
    city TEXT NOT NULL,
    country TEXT NOT NULL,
    region TEXT
);

-- =========================
-- 📅 Time Dimension
-- =========================
CREATE TABLE dim_time (
    time_id INTEGER PRIMARY KEY AUTOINCREMENT,
    datetime TEXT NOT NULL,
    date TEXT NOT NULL,
    hour INTEGER NOT NULL
);

-- =========================
-- ☁️ Weather Dimension
-- =========================
CREATE TABLE dim_weather (
    weather_id INTEGER PRIMARY KEY AUTOINCREMENT,
    weather TEXT NOT NULL,
    weather_desc TEXT
);

-- =========================
-- ⭐ Fact Table
-- =========================
CREATE TABLE fact_weather (
    weather_fact_id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Foreign Keys
    location_id INTEGER,
    time_id INTEGER,
    weather_id INTEGER,

    -- Measures
    temperature REAL,
    humidity INTEGER,
    pressure INTEGER,
    wind_speed REAL,

    -- Relationships
    FOREIGN KEY (location_id) REFERENCES dim_location(location_id),
    FOREIGN KEY (time_id) REFERENCES dim_time(time_id),
    FOREIGN KEY (weather_id) REFERENCES dim_weather(weather_id)
);