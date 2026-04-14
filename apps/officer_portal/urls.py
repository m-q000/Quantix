from django.urls import path
from . import views

app_name = 'officer_portal'

urlpatterns = [
    path('',                                    views.dashboard,         name='dashboard'),
    path('scan/',                               views.scan,              name='scan'),
    path('verify/<uuid:token>/',                views.verify_stall,      name='verify_stall'),
    path('inspections/',                        views.inspections_list,  name='inspections'),
    path('inspections/<int:pk>/',               views.inspection_detail, name='inspection_detail'),
]
