from django.conf.urls.static import static
from django.contrib import admin

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.urls import path, re_path, include

from core import settings

from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# project/urls.py
from django.conf.urls import handler404, handler500
# from django.shortcuts import render
#
# def custom_page_not_found(request, exception):
#     return render(request, '404.html', status=404)

# def custom_page_error(request, exception):
#     return render(request, '500.html', status=500)

# handler404 = custom_page_not_found
# handler500 = custom_page_error



schema_view = get_schema_view(
   openapi.Info(
      title="Tahlilchi API",
      default_version='v1',
      description="API hujjatlari",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="qarshiyevnizomiddin75@gmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)



urlpatterns = [
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('tahlilchi-admin/', admin.site.urls),
    path('api/stock/', include('stock.urls')),
    path('api/', include('users.urls')),

    # JWT token olish va yangilash
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
