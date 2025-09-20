# data/realtime_data.py
from datetime import datetime
import requests

def get_current_datetime():
    weekdays_vi = {
        "Monday": "Thứ Hai",
        "Tuesday": "Thứ Ba",
        "Wednesday": "Thứ Tư",
        "Thursday": "Thứ Năm",
        "Friday": "Thứ Sáu",
        "Saturday": "Thứ Bảy",
        "Sunday": "Chủ Nhật"
    }

    now = datetime.now()
    weekday_en = now.strftime("%A")
    weekday_vi = weekdays_vi.get(weekday_en, weekday_en)
    date_str = now.strftime(f"{weekday_vi}, %d/%m/%Y - %H:%M")
    return date_str

WEATHER_CODES = {
    0: "trời quang đãng ☀️",
    1: "trời có mây nhẹ 🌤️",
    2: "trời nhiều mây ⛅",
    3: "trời u ám ☁️",
    45: "sương mù 🌫️",
    48: "sương mù đông đặc 🌫️",
    51: "mưa phùn nhẹ 🌦️",
    53: "mưa phùn vừa 🌦️",
    55: "mưa phùn nặng 🌧️",
    61: "mưa nhẹ 🌦️",
    63: "mưa vừa 🌧️",
    65: "mưa lớn ⛈️",
    71: "tuyết nhẹ ❄️",
    73: "tuyết vừa ❄️",
    75: "tuyết dày ❄️",
    80: "mưa rào nhẹ 🌦️",
    81: "mưa rào vừa 🌧️",
    82: "mưa rào nặng ⛈️",
    95: "giông bão ⛈️",
    96: "giông kèm mưa đá ⚡",
    99: "giông kèm mưa đá mạnh ⚡❄️"
}

def get_coords(location: str):
    url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json&limit=1"
    res = requests.get(url, headers={"User-Agent": "MINH/1.0"})
    res.raise_for_status()
    data = res.json()
    if not data:
        raise ValueError(f"Không tìm thấy địa điểm: {location}")
    return float(data[0]["lat"]), float(data[0]["lon"])

def get_weather(location="Hanoi"):
    try:
        lat, lon = get_coords(location)
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        weather = data["current_weather"]
        temp = weather["temperature"]
        wind = weather["windspeed"]
        code = weather["weathercode"]
        desc = WEATHER_CODES.get(code, "thời tiết không xác định")

        return f"Thời tiết hiện tại ở {location}: {desc}, {temp}°C, gió {wind} km/h."
    except Exception as e:
        return f"⚠️ Không lấy được thời tiết cho {location} do lỗi: {str(e)}"