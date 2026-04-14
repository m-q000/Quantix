from django.urls import path
from . import views

app_name = 'public_portal'

urlpatterns = [
    path('',                              views.map_view,          name='map'),
    path('stall/<int:stall_id>/',         views.stall_detail,      name='stall_detail'),
    path('verify/<uuid:token>/',          views.verify_qr,         name='verify_qr'),
    path('report/<int:stall_id>/',        views.report_violation,  name='report_violation'),
]
