# middleware.py
from django.utils.deprecation import MiddlewareMixin
from ipware import get_client_ip  # ixtiyoriy

from .models import RequestLog

class ClientIPMiddleware(MiddlewareMixin):
    def process_request(self, request):
        ip, _ = get_client_ip(request)
        RequestLog.objects.create(
            path=request.path,
            method=request.method,
            ip=ip
        )
        request.client_ip = ip