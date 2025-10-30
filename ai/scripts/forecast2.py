import numpy as np
import pandas as pd
import json
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, timedelta
import os

# Fayl yo'llari
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # D:\projects\s6\
CSV_PATH = os.path.join(BASE_DIR, 'data', 'sales_expanded_1000.csv')  # D:\projects\s6\data\sales_expanded_1000.csv
MODELS_DIR = os.path.join(BASE_DIR, 'models')
FORECAST_DIR = os.path.join(BASE_DIR, 'data', 'forecasts')

def ensure_directories():
    os.makedirs(FORECAST_DIR, exist_ok=True)
    os.makedirs(MODELS_DIR, exist_ok=True)

def forecast_model():
    if not os.path.exists(CSV_PATH):
        print(f"❌ Fayl topilmadi: {CSV_PATH}")
        return

    ensure_directories()

    # Ma'lumotlarni yuklash
    try:
        df = pd.read_csv(CSV_PATH)
        # Sana formatini DD/MM/YYYY deb talqin qilish
        df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
        # Noto'g'ri sanalarni tekshirish va o'chirish
        if df['date'].isnull().any():
            print(f"⚠️ {df['date'].isnull().sum()} ta noto'g'ri sana topildi va o'chirildi")
            df = df.dropna(subset=['date'])
        df = df.groupby(['product_id', 'date'])['quantity'].sum().reset_index()
    except Exception as e:
        print(f"❌ Ma'lumotlarni o'qishda xato: {e}")
        return

    # O'qitish uchun ma'lumotlarni filtrlash (2022-01-01 dan 2024-12-31 gacha)
    train_start = datetime(2022, 1, 1)
    train_end = datetime(2024, 12, 31)
    train_data = df[(df['date'] >= train_start) & (df['date'] <= train_end)]

    if train_data.empty:
        print("⚠️ O'qitish uchun ma'lumotlar topilmadi (2022-01-01 dan 2024-12-31 gacha).")
        return

    # Bashorat boshlanish sanasi va davomiyligi
    forecast_start = datetime(2025, 1, 1)
    forecast_days = 90  # Yanvar, fevral, mart (90 kun)

    # Har bir oy uchun bashoratlar
    current_month = forecast_start
    while current_month <= datetime(2025, 3, 31):
        month_str = current_month.strftime('%Y-%m')
        month_end = min(current_month + timedelta(days=31), datetime(2025, 3, 31)).replace(day=1) - timedelta(days=1)

        forecast_results = {}
        for product_id in train_data['product_id'].unique():
            model_path = os.path.join(MODELS_DIR, f'trained_model_product_{product_id}.keras')

            if not os.path.exists(model_path):
                print(f"⚠️ Model topilmadi: {model_path}")
                continue

            try:
                model = load_model(model_path)
                print(f"✅ Mahsulot {product_id} uchun model yuklandi: {model_path}")
            except Exception as e:
                print(f"❌ Model yuklashda xatolik: {product_id} - {e}")
                continue

            # Trening ma'lumotlari (2022-01-01 dan 2024-12-31 gacha)
            product_data = train_data[train_data['product_id'] == product_id].sort_values('date')['quantity'].values
            if len(product_data) < 30:
                print(f"⚠️ Mahsulot {product_id} uchun yetarlicha ma'lumot yo'q (kamida 30 kun kerak, bor: {len(product_data)})")
                continue

            # Ma'lumotlarni normalizatsiya qilish
            scaler = MinMaxScaler()
            scaled_data = scaler.fit_transform(product_data.reshape(-1, 1))

            # Bashorat qilish
            X_input = scaled_data[-30:].reshape(1, 30, 1)
            predictions = []
            forecast_dates = [(forecast_start + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(forecast_days)]

            for _ in range(forecast_days):
                try:
                    pred = model.predict(X_input, verbose=0)[0][0]
                    predictions.append(pred)
                    X_input = np.append(X_input[:, 1:, :], [[[pred]]], axis=1)
                except Exception as e:
                    print(f"❌ Mahsulot {product_id} uchun bashorat qilishda xato: {e}")
                    break

            if len(predictions) != forecast_days:
                print(f"⚠️ Mahsulot {product_id} uchun bashoratlar to'liq emas")
                continue

            # Bashoratlarni orqaga normal holatga keltirish
            predictions = scaler.inverse_transform(np.array(predictions).reshape(-1, 1)).flatten()

            # Faqat joriy oy uchun bashoratlarni filtrlash
            month_forecast = [
                {"date": date, "predicted_quantity": round(float(pred), 2)}
                for date, pred in zip(forecast_dates, predictions)
                if date.startswith(month_str)
            ]

            if month_forecast:
                forecast_results[str(product_id)] = {
                    "product_id": int(product_id),
                    "forecast": month_forecast
                }

        # JSON faylga yozish
        if forecast_results:
            json_path = os.path.join(FORECAST_DIR, f'forecast_{month_str}.json')
            try:
                with open(json_path, 'w') as f:
                    json.dump(forecast_results, f, indent=4)
                print(f"✅ {month_str} bashorati saqlandi: {json_path}")
            except Exception as e:
                print(f"❌ {month_str} bashoratini saqlashda xato: {e}")

        # Keyingi oyga o'tish
        current_month = (current_month.replace(day=1) + timedelta(days=32)).replace(day=1)

if __name__ == "__main__":
    forecast_model()