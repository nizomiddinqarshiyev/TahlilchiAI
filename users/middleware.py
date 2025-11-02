import os
import datetime
from django.utils.deprecation import MiddlewareMixin
from ipware import get_client_ip


class ClientIPMiddleware(MiddlewareMixin):
    """
    Har bir HTTP so‘rov haqida log yozuvchi middleware.
    Loglar: IP, method, path va status_code — faylga yoziladi.
    """

    def process_request(self, request):
        # IP manzilni olish
        ip, _ = get_client_ip(request)
        request.client_ip = ip or "UNKNOWN"

    def process_response(self, request, response):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        today = datetime.date.today()
        # log fayli joylashuvi
        logs_dir = os.path.join(os.getcwd(), "logs")
        os.makedirs(logs_dir, exist_ok=True)
        log_file_path = os.path.join(logs_dir, f"req_log{today}.log")

        # yozuv formati
        ip = getattr(request, "client_ip", "UNKNOWN")
        method = getattr(request, "method", "N/A")
        path = getattr(request, "path", "N/A")
        status = getattr(response, "status_code", "???")

        log_line = f"[{timestamp}] {ip} - {method} {path} - Status: {status}\n"

        # faylga yozish
        with open(log_file_path, "a", encoding="utf-8") as f:
            f.write(log_line)

        return response

