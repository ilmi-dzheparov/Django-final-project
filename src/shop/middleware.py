import uuid
from django.utils.deprecation import MiddlewareMixin


class SessionTokenMiddleware(MiddlewareMixin):
    """
    Создание токена сессии для работы корзины, когда пользователь не авторзован и для слияния корзин при авторизации
    """

    def process_request(self, request):
        session_token = request.COOKIES.get('session_token')
        if not session_token:
            session_token = str(uuid.uuid4())
            request.session['session_token'] = session_token
        else:
            request.session['session_token'] = session_token

    def process_response(self, request, response):
        if 'session_token' in request.session:
            response.set_cookie('session_token', request.session['session_token'])
        return response
