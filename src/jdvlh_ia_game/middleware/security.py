import json
import re
from fastapi import Request
from slowapi import Limiter
from slowapi.middleware import LimiterMiddleware
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)


class SecurityMiddleware(LimiterMiddleware):
    def __init__(self, app):
        super().__init__(
            app, limiter, default_limits=["10/minute"], storage_uri="memory://"
        )

    async def dispatch(self, request: Request, call_next):
        if request.method == "GET":
            return await call_next(request)

        # Sanitize input body (note: body is consumed, for MVP handle in endpoint)
        try:
            body = await request.body()
            if body:
                data = json.loads(body)
                if "choice" in data:
                    data["choice"] = re.sub(
                        r'[<>;{}()\\"]', "", data["choice"].strip()
                    )[:100]
        except Exception:
            pass

        response = await call_next(request)
        return response


security_middleware = SecurityMiddleware
