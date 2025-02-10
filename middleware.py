from django.http import HttpResponse
from django.views.debug import technical_500_response

class ShowAdminErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
        except Exception as e:
            if request.user.is_staff:
                return technical_500_response(request, type(e), e, e.__traceback__)
            raise
        return response
