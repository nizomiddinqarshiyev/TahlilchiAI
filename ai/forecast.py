import numpy as np
import pandas as pd
from keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
from sqlalchemy import create_engine
from datetime import datetime, timedelta
import os
from config import *

# PostgreSQL ulanish
engine = create_engine(DB_URL)

# Model joylashgan papka
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, 'models')
os.makedirs(MODELS_DIR, exist_ok=True)


# def forecast_model(store_id=1, forecast_days=30):
#     print("📊 Sotuv ma’lumotlari o‘qilmoqda...")
#     query = f"""
#         SELECT product_id, sale_date, quantity
#         FROM stock_dailysale
#         WHERE store_id = {store_id}
#         ORDER BY sale_date;
#     """
#     try:
#         df = pd.read_sql(query, engine)
#     except Exception as e:
#         print(f"❌ Ma’lumotlarni o‘qishda xato: {e}")
#         return f"❌ Ma’lumotlarni o‘qishda xato: {e}"
#
#     if df.empty:
#         print("⚠️ Sotuv ma’lumotlari topilmadi.")
#         return "⚠️ Sotuv ma’lumotlari topilmadi."
#
#     df['sale_date'] = pd.to_datetime(df['sale_date'])
#     df = df.groupby(['product_id', 'sale_date'])['quantity'].sum().reset_index()
#
#     all_forecasts = []
#
#     for product_id in df['product_id'].unique():
#         model_path = os.path.join(MODELS_DIR, f"trained_model_store_{store_id}_product_{product_id}.keras")
#         if not os.path.exists(model_path):
#             print(f"⚠️ Model topilmadi: {model_path}")
#             continue
#
#         product_data = df[df['product_id'] == product_id].sort_values('sale_date')['quantity'].values
#         if len(product_data) < 30:
#             continue
#
#         scaler = MinMaxScaler()
#         scaled_data = scaler.fit_transform(product_data.reshape(-1, 1))
#         X_input = scaled_data[-30:].reshape(1, 30, 1)
#
#         model = load_model(model_path)
#         preds = []
#         for _ in range(forecast_days):
#             pred = model.predict(X_input, verbose=0)[0][0]
#             preds.append(pred)
#             X_input = np.append(X_input[:, 1:, :], [[[pred]]], axis=1)
#
#         preds = scaler.inverse_transform(np.array(preds).reshape(-1, 1)).flatten()
#         last_date = df['sale_date'].max()
#         forecast_dates = [(last_date + timedelta(days=i+1)).strftime('%Y-%m-%d') for i in range(forecast_days)]
#
#         temp_df = pd.DataFrame({
#             'store_id': store_id,
#             'product_id': product_id,
#             'forecast_date': forecast_dates,
#             'predicted_quantity': preds,
#             'forecast_period': 'daily'
#         })
#         all_forecasts.append(temp_df)
#
#     if not all_forecasts:
#         print("⚠️ Hech qanday bashorat yaratilmagan.")
#         return "⚠️ Hech qanday bashorat yaratilmagan."
#
#     result_df = pd.concat(all_forecasts)
#     try:
#         result_df.to_sql('forecasts', engine, if_exists='append', index=False)
#         print(f"✅ {len(result_df)} ta bashorat natijasi forecasts jadvaliga yozildi.")
#         print("🎯 Bashorat jarayoni yakunlandi!")
#         return f"✅ {len(result_df)} ta bashorat natijasi {store_id}-store uchun {forecast_days} kunlik bashorat yaratildi."
#     except Exception as e:
#         print(f"❌ Forecast yozishda xato: {e}")
#         return f"❌ Forecast yozishda xato: {e}"


import numpy as np
import pandas as pd
from keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
from datetime import timedelta
import os
from django.db import transaction
from stock.models import Store, Product, Forecast  # <-- Django modellaringdan import qilamiz
from config import *
from sqlalchemy import create_engine

# PostgreSQL ulanish (agar kerak bo‘lsa)
engine = create_engine(DB_URL)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, 'models')
os.makedirs(MODELS_DIR, exist_ok=True)


def forecast_model(store_id=1, forecast_days=30):
    """Har bir product uchun LSTM modeldan foydalanib forecast yaratadi
    va Forecast jadvaliga yozadi (ORM orqali)."""
    print("📊 Sotuv ma’lumotlari o‘qilmoqda...")

    query = f"""
        SELECT product_id, sale_date, quantity
        FROM stock_dailysale
        WHERE store_id = {store_id}
        ORDER BY sale_date;
    """
    try:
        df = pd.read_sql(query, engine)
    except Exception as e:
        msg = f"❌ Ma’lumotlarni o‘qishda xato: {e}"
        print(msg)
        return msg

    if df.empty:
        msg = "⚠️ Sotuv ma’lumotlari topilmadi."
        print(msg)
        return msg

    df['sale_date'] = pd.to_datetime(df['sale_date'])
    df = df.groupby(['product_id', 'sale_date'])['quantity'].sum().reset_index()

    all_forecasts = []

    for product_id in df['product_id'].unique():
        model_path = os.path.join(MODELS_DIR, f"model_store_{store_id}_product_{product_id}.keras")
        if not os.path.exists(model_path):
            print(f"⚠️ Model topilmadi: {model_path}")
            continue

        product_data = df[df['product_id'] == product_id].sort_values('sale_date')['quantity'].values
        if len(product_data) < 30:
            continue

        scaler = MinMaxScaler()
        scaled_data = scaler.fit_transform(product_data.reshape(-1, 1))
        X_input = scaled_data[-30:].reshape(1, 30, 1)

        model = load_model(model_path)
        preds = []
        for _ in range(forecast_days):
            pred = model.predict(X_input, verbose=0)[0][0]
            preds.append(pred)
            X_input = np.append(X_input[:, 1:, :], [[[pred]]], axis=1)

        preds = scaler.inverse_transform(np.array(preds).reshape(-1, 1)).flatten()
        last_date = df['sale_date'].max()

        forecast_dates = [
            (last_date + timedelta(days=i + 1)).date()
            for i in range(forecast_days)
        ]

        # ORM uchun obyektlar yaratamiz
        store = Store.objects.get(id=store_id)
        product = Product.objects.get(id=product_id)

        for date, quantity in zip(forecast_dates, preds):
            all_forecasts.append(
                Forecast(
                    store=store,
                    product=product,
                    forecast_date=date,
                    predicted_quantity=round(float(quantity), 2),
                    forecast_period='daily'
                )
            )

    if not all_forecasts:
        msg = "⚠️ Hech qanday bashorat yaratilmagan."
        print(msg)
        return msg

    # ORM orqali bulk create
    try:
        with transaction.atomic():
            Forecast.objects.bulk_create(all_forecasts)
        msg = f"✅ {len(all_forecasts)} ta bashorat {store_id}-store uchun yaratildi va bazaga yozildi."
        print(msg)
        return msg
    except Exception as e:
        msg = f"❌ Forecast yozishda xato: {e}"
        print(msg)
        return msg





# if __name__ == "__main__":
#     forecast_model()
