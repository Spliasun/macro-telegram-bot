import json
import time
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from telegram import Bot

# --- 1. Змінні середовища (Railway або локально) ---
TELEGRAM_TOKEN = "Т7504279275:AAHHKkDpxDIhHaIwm3UpMq3jc2SHXgk6_co"
CHAT_ID = "189221460"
SHEET_ID = "1-SgyGPiebBPzyjChZvsRj_s9s6pUb-FijBekR1yXvM4"

# Вміст JSON ключа сервісного акаунта Google (в один рядок)
GOOGLE_KEY_JSON = """{ "type": "service_account", "project_id": "macro-sync", "private_key_id": "ec5b4b56551342c99e0337d25af0726d81244198", "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCh3ZhakWk1quRh\nNj+cBb/OcA1TmTkIYdiibLeBKO9VVvrJ4B4GfCNAf++vROJio+g6caOT6TNe4tkD\ngRTrP6jj2cXDNBeqz3fIX4cdw+5eOpESzUhu9HLOlz9uf1T8U5mwuBnWWHQs7xwx\nJ2ISko+7bukb38RkuCqJ8PZLzNvW1ys4VFX0JNag5hDd6kebBySLiajPtKjYDDFg\nlngStGhWriFQDuGM39jSuk4OnMmSrq4Ci2+fVH01i8fWNwxbb8Lt9nN7BqwwusCl\nEMQRu9+IZ34UIHHd4BHfxKonTvRzvVNJW3h214D0Jk4ilgA6Fzw9+GyG7OaP9rXI\nukp10mZXAgMBAAECggEAIHz7sWHyPgVY5XIf/k7hGqw+4IKmgdoxwxgTFOeEchqN\nJ6vGGwMbiDylfQZUcfv4BpL8hBmQaAEcEan86uLSITl6ih2QioYtwpf55K2I0Hzs\n1VtCqJKD4JdW8fS4uBSHioLJHM6QMtyjSfJfqt6j3rj6LNAS+SxFzX4B0WEC1vHy\nz4xrDiuEBHu+OrNmirmPvXnY3hsRIqqp4QPd7qPz2vjoNGI3OXMvxMBQ6vJveuL5\nmMwe50JllYCU0JJZ6VrmuFzD1Fo1yCrvUCvT2MuLCjdO+a2FFf1c3NPanIAs9QtT\nW4RpYU5x5FPewMqNuQRdmeriSHAIs71vNZqfJu8jYQKBgQDjkCMFsZzSjKi5ADyU\nz/NgI+/co5Tel4GO1RWyn5hrLt2cikiIBO7rhPJ4CKpIOQM5wXNRI2RHPufqRgj/\nzTqtjBTlB+Jyikculi3k5RB00C4Ldepb6dKeTr7cjI5V3MlwGXK16dh/F8tznL6p\n7fj/BfnlKipmxkHUJenRpj1TqQKBgQC2F8Mv5yqsdlTgyk1CuuINhZR1VbwVL2FT\nk0rr72T1+cDPPz83Ayo802dF8VSVkJT8X890ZoFNH/lB7K2rfGdLHHOYANKFqRWU\nkRAtq85BsuyM8zXqSmpEdx/kj/6EuH/PR+P+a65Vm/Dr8ptihxXlwIdNVzAB/dKP\nwnZjX2Yp/wKBgQDdoeNKR1s6gX5OeFmIgiRCLZ4OoU97n8myJ/yy9NdJBOMX9GKB\n/3QG9HwGxkG6h7SJiszaaILhFPZg6IcZRHPy1O0Ax7YX4m9Dg0b9mM93Rc6ioNx5\nWnkkcANZ4Jc8LwYN5OshG7kcxzsCxdW4wSpyjwp81J1pbYxtp+NbqfIuyQKBgFPR\ndlhbiUofogxjMtMvoRRmU6L7FvuNdrh4yXj3FjsffsAnNdsFyvB6w0PvxWafSeUt\n2RmUgZpVyG+vGXYhao6phxAF+OHrpfJgH9lWBzg4uyhaX4v8OxRO3VBhc9/16Wcp\niWo4eOQRRwHlB99/nPXH/L/+DSwtgToJYmN1q1pTAoGACcMtaSFqO5NUBFkv70sh\nBy6+xLgCbxqODwmZWECSaEjKqzJatXAY/8uims/h+L+IG6bgIrpLZIhvTMmMASZi\nyjbvAB4lIVJKlhV+VJAo9ulRCehH2BMBiNxHCZBzaK5ILDKJ7SoQMqB4LrSo75mc\nTi5+/rvBegr18YbngOxkUFI=\n-----END PRIVATE KEY-----\n", "client_email": "sheet-sync-bot@macro-sync.iam.gserviceaccount.com", "client_id": "110585103452012977975", "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://oauth2.googleapis.com/token", "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs", "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/sheet-sync-bot%40macro-sync.iam.gserviceaccount.com", "universe_domain": "googleapis.com" }"""

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
