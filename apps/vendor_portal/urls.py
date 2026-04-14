from django.urls import path
from . import views

app_name = 'vendor_portal'

urlpatterns = [
    path('',               views.dashboard,     name='dashboard'),
    path('apply/',         views.apply_stall,   name='apply'),
    path('my-stall/',      views.my_stall,      name='my_stall'),
    path('images/',        views.upload_images, name='upload_images'),
    path('qr-code/',       views.qr_code,       name='qr_code'),
    path('subscription/',  views.subscription,  name='subscription'),
    path('violations/',    views.violations,    name='violations'),
]
