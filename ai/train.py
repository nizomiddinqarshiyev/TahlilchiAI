import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense, Input
from sqlalchemy import create_engine
from datetime import datetime
import os

# import config

# PostgreSQL ulanish
# DB_URL = config.DB_URL
DB_URL = "postgresql://postgres:postgres@localhost:5432/tahlilchidb"
try:
    engine = create_engine(DB_URL)
except Exception as e:
    print(f"Bazaga ulanishda xatolik {e}")
# Model saqlanadigan joy
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, 'models')
os.makedirs(MODELS_DIR, exist_ok=True)


def build_model(time_step=30):
    """LSTM model yaratish"""
    model = Sequential([
        Input(shape=(time_step, 1)),
        LSTM(50, return_sequences=True),
        LSTM(25, return_sequences=False),
        Dense(25, activation="relu"),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model


# def train_model(store_id=1):
#     print("📊 Ma’lumotlar bazasidan o‘qilmoqda...")
#     query = f"""
#         SELECT product_id, sale_date, quantity
#         FROM stock_dailysale
#         WHERE store_id = {store_id}
#         ORDER BY sale_date;
#     """
#
#     try:
#         df = pd.read_sql(query, engine)
#     except Exception as e:
#         print(f"❌ Ma’lumotlarni o‘qishda xato: {e}")
#         return f"❌ Ma’lumotlarni o‘qishda xato: {e}"
#
#     if df.empty:
#         print("⚠️ Ma’lumotlar topilmadi.")
#         return "⚠️ Ma’lumotlar topilmadi."
#
#     df['sale_date'] = pd.to_datetime(df['sale_date'])
#     df = df.groupby(['product_id', 'sale_date'])['quantity'].sum().reset_index()
#
#     for product_id in df['product_id'].unique():
#         print(f"📦 Mahsulot {product_id} uchun model o‘qitilmoqda...")
#
#         product_data = df[df['product_id'] == product_id].sort_values('sale_date')['quantity'].values
#         if len(product_data) < 30:
#             print(f"⚠️ {product_id} - ma’lumot yetarli emas ({len(product_data)} ta)")
#             continue
#
#         scaler = MinMaxScaler()
#         scaled_data = scaler.fit_transform(product_data.reshape(-1, 1))
#
#         X_train, y_train = [], []
#         for i in range(len(scaled_data) - 30):
#             X_train.append(scaled_data[i:i + 30])
#             y_train.append(scaled_data[i + 30])
#
#         X_train, y_train = np.array(X_train), np.array(y_train)
#         if len(X_train) == 0:
#             continue
#
#         model = build_model(time_step=30)
#         try:
#             model.fit(X_train, y_train, epochs=20, batch_size=32, verbose=0)
#         except Exception as e:
#             print(f"❌ Modelni o‘qitishda xato: {e}")
#             continue
#
#         model_path = os.path.join(MODELS_DIR, f"model_store_{store_id}_product_{product_id}.keras")
#         try:
#             model.save(model_path)
#             print(f"✅ Model saqlandi: {model_path}")
#             return f"✅ Model saqlandi: model_store_{store_id}_product_{product_id}.keras"
#         except Exception as e:
#             print(f"❌ Modelni saqlashda xato: {e}")
#             return f"❌ Modelni saqlashda xato: {e}"
#
#     print("🎯 Barcha modellarning o‘qitilishi yakunlandi!")
#     return "🎯 Barcha modellarning o‘qitilishi yakunlandi!"


def train_model(store_id=1):
    print("📊 Ma’lumotlar bazasidan o‘qilmoqda...")
    query = f"""
        SELECT product_id, sale_date, quantity
        FROM stock_dailysale
        WHERE store_id = {store_id}
        ORDER BY sale_date;
    """

    try:
        df = pd.read_sql(query, engine)
    except Exception as e:
        print(f"❌ Ma’lumotlarni o‘qishda xato: {e}")
        return f"❌ Ma’lumotlarni o‘qishda xato: {e}"

    if df.empty:
        print("⚠️ Ma’lumotlar topilmadi.")
        return "⚠️ Ma’lumotlar topilmadi."

    df['sale_date'] = pd.to_datetime(df['sale_date'])
    df = df.groupby(['product_id', 'sale_date'])['quantity'].sum().reset_index()

    results = []  # <-- barcha mahsulotlar uchun natijalar

    for product_id in df['product_id'].unique():
        print(f"📦 Mahsulot {product_id} uchun model o‘qitilmoqda...")

        product_data = df[df['product_id'] == product_id].sort_values('sale_date')['quantity'].values
        if len(product_data) < 30:
            msg = f"⚠️ {product_id} - ma’lumot yetarli emas ({len(product_data)} ta)"
            print(msg)
            results.append(msg)
            continue

        scaler = MinMaxScaler()
        scaled_data = scaler.fit_transform(product_data.reshape(-1, 1))

        X_train, y_train = [], []
        for i in range(len(scaled_data) - 30):
            X_train.append(scaled_data[i:i + 30])
            y_train.append(scaled_data[i + 30])

        X_train, y_train = np.array(X_train), np.array(y_train)
        if len(X_train) == 0:
            continue

        model = build_model(time_step=30)
        try:
            model.fit(X_train, y_train, epochs=20, batch_size=32, verbose=0)
        except Exception as e:
            msg = f"❌ Modelni o‘qitishda xato: {product_id} — {e}"
            print(msg)
            results.append(msg)
            continue

        model_path = os.path.join(MODELS_DIR, f"model_store_{store_id}_product_{product_id}.keras")
        try:
            model.save(model_path)
            msg = f"✅ Model saqlandi: model_store_{store_id}_product_{product_id}.keras"
            print(msg)
            results.append(msg)
        except Exception as e:
            msg = f"❌ Modelni saqlashda xato: {product_id} — {e}"
            print(msg)
            results.append(msg)

    print("🎯 Barcha modellarning o‘qitilishi yakunlandi!")
    return results  # <-- endi barcha mahsulotlar bo‘yicha natijalar qaytadi



if __name__ == "__main__":
    train_model()
