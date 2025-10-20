from django.contrib import admin
from .models import *

admin.site.register([Product, DailySale, Store, Forecast, Replenishment])

# Register your models here.
