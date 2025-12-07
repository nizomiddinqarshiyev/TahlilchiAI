from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum
from .models import Forecast, StockData, Replenishment

def calculate_replenishment(store, product):
    shelf_life = product.shelf_life_days

    # 1. Ombordagi mavjud qty olish
    stock_obj = StockData.objects.filter(store=store, product=product).first()
    stock = stock_obj.stock if stock_obj else 0

    # 2. Kelgusi shelf_life kun forecastlarini yig‘ish
    today = timezone.now().date()
    end_date = today + timedelta(days=shelf_life)

    total_forecast = Forecast.objects.filter(
        store=store,
        product=product,
        forecast_date__range=[today, end_date]
    ).aggregate(total=Sum('predicted_quantity'))['total'] or 0

    # 3. Buyurtma hisoblash
    suggested_qty = total_forecast - stock
    if suggested_qty < 0:
        suggested_qty = 0

    # 4. Replenishment yozuvi yaratish
    replen = Replenishment.objects.create(
        store=store,
        product=product,
        period_start=today,
        period_end=end_date,
        suggested_quantity=suggested_qty,
        period_type='shelf_life'
    )

    return {
        "product": product.name,
        "shelf_life_days": shelf_life,
        "stock": stock,
        "total_forecast": total_forecast,
        "suggested_order": float(suggested_qty),
        "period_start": today,
        "period_end": end_date
    }
