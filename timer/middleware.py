import uuid
from datetime import timedelta
from django.utils import timezone

class PomodoroUserCookieMiddleware:
    COOKIE_NAME = 'pomodoro_user_id'
    # Set cookie expiry to 1 year
    COOKIE_MAX_AGE = int(timedelta(days=365).total_seconds())

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user_id = None
        set_cookie = False

        if self.COOKIE_NAME in request.COOKIES:
            try:
                user_id = uuid.UUID(request.COOKIES[self.COOKIE_NAME])
            except (ValueError, TypeError):
                # Invalid cookie value, generate a new one
                user_id = uuid.uuid4()
                set_cookie = True
        else:
            # Cookie doesn't exist, generate a new one
            user_id = uuid.uuid4()
            set_cookie = True

        # Attach the user_id and flag to the request
        request.pomodoro_user_id = user_id
        request.set_pomodoro_cookie = set_cookie

        response = self.get_response(request)

        # Set the cookie on the response if needed
        if getattr(request, 'set_pomodoro_cookie', False):
            response.set_cookie(
                self.COOKIE_NAME,
                str(request.pomodoro_user_id),
                max_age=self.COOKIE_MAX_AGE,
                httponly=True, # Make cookie inaccessible to JavaScript (recommended)
                samesite='Lax' # Good default for security
            )

        return response 