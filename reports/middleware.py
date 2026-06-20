from django.core.cache import cache
from django.http import HttpResponse
from django.conf import settings
import time

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Allow static files and media to pass through without rate limiting
        if request.path.startswith(settings.STATIC_URL) or request.path.startswith(settings.MEDIA_URL):
            return self.get_response(request)

        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')

        # Determine limits
        if request.user.is_authenticated:
            limit = getattr(settings, 'RATE_LIMIT_AUTHENTICATED', 100)
            user_key = f"rl_auth_{request.user.id}"
        else:
            limit = getattr(settings, 'RATE_LIMIT_ANONYMOUS', 30)
            user_key = f"rl_anon_{ip}"

        # Current timestamp
        now = time.time()
        
        # Retrieve logs from cache
        request_history = cache.get(user_key, [])
        
        # Filter request timestamps in the last 60 seconds
        request_history = [t for t in request_history if now - t < 60]
        
        if len(request_history) >= limit:
            response_html = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Rate Limit Exceeded - BorderWatch BD</title>
                <style>
                    body {{
                        background: #121212;
                        color: #ffffff;
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                    }}
                    .container {{
                        text-align: center;
                        padding: 30px;
                        border-radius: 10px;
                        background: #1e1e1e;
                        border: 1px solid #A81C1C;
                        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
                        max-width: 450px;
                    }}
                    h1 {{ color: #A81C1C; font-size: 24px; margin-top: 0; }}
                    p {{ color: #cccccc; font-size: 16px; line-height: 1.5; }}
                    .btn {{
                        display: inline-block;
                        margin-top: 20px;
                        padding: 10px 20px;
                        background: #0A3B1B;
                        color: #fff;
                        text-decoration: none;
                        border-radius: 5px;
                        transition: background 0.3s;
                    }}
                    .btn:hover {{ background: #0e5c2a; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Access Temporarily Restricted</h1>
                    <p>You have made too many requests in a short period of time. Please wait a minute and refresh the page to try again.</p>
                    <p style="font-size: 12px; color: #777;">IP Ref: {ip}</p>
                    <a href="" onclick="window.location.reload();" class="btn">Retry Now</a>
                </div>
            </body>
            </html>
            """
            return HttpResponse(response_html, status=429)

        # Update cache
        request_history.append(now)
        cache.set(user_key, request_history, 60)

        return self.get_response(request)
