from django.urls import path
from users.views import SignUpView, GetTokenView

app_name = 'users'


urlpatterns = [
    path('v1/auth/signup/', SignUpView.as_view(), name='signup'),
    path('v1/auth/token/', GetTokenView.as_view(), name='token'),
]
