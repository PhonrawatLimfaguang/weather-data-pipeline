import sqlite3

conn = sqlite3.connect("data/weather.db")
cursor = conn.cursor()

query = """
SELECT t.hour, AVG(f.temperature)
FROM fact_weather f
JOIN dim_time t ON f.time_id = t.time_id
GROUP BY t.hour
"""

cursor.execute(query)

rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()