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
    date_str = now.strftime(f"{weekday_vi}, %d/%m/%Y – %H:%M")
    return f"Hôm nay là {date_str}"


def get_weather(location="Hanoi"):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude=21.0285&longitude=105.8542&current_weather=true"
        response = requests.get(url)
        data = response.json()
        temp = data["current_weather"]["temperature"]
        wind = data["current_weather"]["windspeed"]
        return f"Thời tiết hiện tại ở {location}: {temp}°C, gió {wind} km/h."
    except Exception as e:
        return f"Không lấy được thời tiết do lỗi: {str(e)}"
