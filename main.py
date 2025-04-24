import json
import time
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from telegram import Bot

# --- 1. Змінні середовища (Railway або локально) ---
TELEGRAM_TOKEN = "ТУТ_ТВІЙ_ТОКЕН"
CHAT_ID = "ТУТ_ТВІЙ_CHAT_ID"
SHEET_ID = "ТУТ_ТВОЄ_ID_ТАБЛИЦІ"

# Вміст JSON ключа сервісного акаунта Google (в один рядок)
GOOGLE_KEY_JSON = """ТУТ_ВСТАВ_ВСЕЙ_JSON_ЯК_ТЕКСТ"""

# --- 2. Telegram ініціалізація ---
bot = Bot(token=TELEGRAM_TOKEN)

# --- 3. Підключення до Google Sheets ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(GOOGLE_KEY_JSON), scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet("Calendar_USA")

# --- 4. Проста заглушка: тестова подія (імітація парсингу) ---
def get_test_event():
    return {
        "Дата": datetime.now().strftime("%Y-%m-%d"),
        "Час": "14:30",
        "Подія": "Non-Farm Payrolls",
        "Країна": "США",
        "Факт": "310K",
        "Прогноз": "240K",
        "Попереднє": "210K",
        "Важливість": "⭐⭐⭐"
    }

# --- 5. Запис події в таблицю ---
def write_to_sheet(event):
    row = [event[col] for col in ["Дата", "Час", "Подія", "Країна", "Факт", "Прогноз", "Попереднє", "Важливість"]]
    sheet.append_row(row)

# --- 6. Генерація Telegram-повідомлення ---
def generate_summary(event):
    return (
        f"📊 Macro Event — {event['Дата']}\n\n"
        f"Подія: {event['Подія']} ({event['Країна']})\n"
        f"Факт: {event['Факт']} | Прогноз: {event['Прогноз']} | Попереднє: {event['Попереднє']}\n"
        f"Важливість: {event['Важливість']}\n\n"
        f"▶️ Потенційна волатильність, слідкуй за ринком."
    )

# --- 7. Надсилання повідомлення в Telegram ---
def send_to_telegram(message):
    bot.send_message(chat_id=CHAT_ID, text=message)

# --- 8. Основна логіка ---
if __name__ == "__main__":
    event = get_test_event()
    write_to_sheet(event)
    summary = generate_summary(event)
    send_to_telegram(summary)
    print("✅ Подія оброблена та відправлена.")
