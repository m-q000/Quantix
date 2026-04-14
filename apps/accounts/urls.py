from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/',               views.login_view,      name='login'),
    path('logout/',              views.logout_view,     name='logout'),
    path('register/',            views.register_vendor, name='register_vendor'),
    path('profile/',             views.profile,         name='profile'),
    path('demo/<str:role>/',     views.demo_login,      name='demo_login'),
]
