import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense, Input
import os
from datetime import datetime

# Fayl yo'llari
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # D:\projects\s6\
CSV_PATH = os.path.join(BASE_DIR, 'data', 'sales_expanded_1000.csv')  # D:\projects\s6\data\sales_expanded_1000.csv
MODELS_DIR = os.path.join(BASE_DIR, 'models')

def ensure_directories():
    os.makedirs(MODELS_DIR, exist_ok=True)

def build_model(time_step=30):
    model = Sequential([
        Input(shape=(time_step, 1)),
        LSTM(50, return_sequences=True),
        LSTM(25, return_sequences=False),
        Dense(25, activation="relu"),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

def train_model():
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
    df = df[(df['date'] >= train_start) & (df['date'] <= train_end)]

    if df.empty:
        print("⚠️ O'qitish uchun ma'lumotlar topilmadi (2022-01-01 dan 2024-12-31 gacha).")
        return

    # Har bir mahsulot uchun modelni o‘qitish
    unique_products = df['product_id'].unique()
    for product_id in unique_products:
        print(f"📦 Mahsulot {product_id} uchun model o'qitilmoqda...")
        product_data = df[df['product_id'] == product_id].sort_values('date')['quantity'].values
        if len(product_data) < 30:  # Yetarli ma'lumot bo‘lishi kerak
            print(f"⚠️ Mahsulot {product_id} uchun yetarlicha ma'lumot yo'q (kamida 30 kun kerak, bor: {len(product_data)})")
            continue

        # Ma'lumotlarni normalizatsiya qilish
        scaler = MinMaxScaler()
        scaled_data = scaler.fit_transform(product_data.reshape(-1, 1))

        # Trening ma'lumotlarini tayyorlash
        X_train, y_train = [], []
        for i in range(len(scaled_data) - 30):
            X_train.append(scaled_data[i:i + 30])
            y_train.append(scaled_data[i + 30])

        X_train, y_train = np.array(X_train), np.array(y_train)
        if len(X_train) == 0:
            print(f"⚠️ Mahsulot {product_id} uchun trening ma'lumotlari yetarli emas")
            continue

        # Modelni yaratish va o‘qitish
        model = build_model(time_step=30)
        try:
            model.fit(X_train, y_train, epochs=20, batch_size=32, verbose=1)
        except Exception as e:
            print(f"❌ Mahsulot {product_id} uchun modelni o'qitishda xato: {e}")
            continue

        # Modelni saqlash
        model_path = os.path.join(MODELS_DIR, f'trained_model_product_{product_id}.keras')
        try:
            model.save(model_path)
            print(f"✅ Mahsulot {product_id} uchun model saqlandi: {model_path}")
        except Exception as e:
            print(f"❌ Mahsulot {product_id} uchun modelni saqlashda xato: {e}")

if __name__ == "__main__":
    train_model()