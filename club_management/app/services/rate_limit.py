from collections import deque
from math import ceil
from threading import Lock
from time import monotonic
from fastapi import HTTPException, Request
from app.core.config import settings


class LoginLimiter:
    def __init__(self):
        self.attempts = {}
        self.lock = Lock()

    def check(self, key):
        now = monotonic()
        window = settings.LOGIN_RATE_WINDOW_SECONDS
        with self.lock:
            for host, attempts in list(self.attempts.items()):
                while attempts and attempts[0] <= now - window:
                    attempts.popleft()
                if not attempts:
                    del self.attempts[host]
            attempts = self.attempts.setdefault(key, deque())
            if len(attempts) >= settings.LOGIN_RATE_LIMIT:
                raise HTTPException(429, 'Quá nhiều lần đăng nhập, vui lòng thử lại sau',
                                    headers={'Retry-After': str(max(1, ceil(attempts[0] + window - now)))})
            attempts.append(now)


login_limiter = LoginLimiter()


def limit_login(request: Request):

    login_limiter.check(request.client.host if request.client else 'unknown')
