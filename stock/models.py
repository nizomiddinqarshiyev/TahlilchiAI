from django.db import models
from django.conf import settings

class Store(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='store_manager'
    )
    opened_date = models.DateField()

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    unit = models.CharField(max_length=20)
    shelf_life_days = models.IntegerField()
    store_id = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True, related_name='products')

    def __str__(self):
        return self.name


class DailySale(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='daily_sales')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='daily_sales')
    sale_date = models.DateField()
    quantity = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.store.name} - {self.product.name} ({self.sale_date})"


class StockData(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='stock_data')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_data')
    stock = models.IntegerField()
    days_to_cover = models.IntegerField()

    def __str__(self):
        return f"{self.store.name} - {self.product.name} stock: {self.stock}"


class Forecast(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='forecasts')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='forecasts')
    forecast_date = models.DateField()
    predicted_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    forecast_period = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.product.name} forecast ({self.forecast_date}) ({self.forecast_period})"


class Replenishment(models.Model):
    PERIOD_TYPE_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('shelf_life', 'Shelf Life'),
    ]

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='replenishments')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='replenishments')
    period_start = models.DateField()
    period_end = models.DateField()
    suggested_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    period_type = models.CharField(max_length=20, choices=PERIOD_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.store.name} - {self.product.name} ({self.period_type})"
