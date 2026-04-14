from django.urls import path
from . import views

app_name = 'municipality_portal'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Stalls
    path('stalls/',                          views.stall_list,            name='stall_list'),
    path('stalls/<int:pk>/',                 views.stall_detail,          name='stall_detail'),
    path('stalls/<int:pk>/approve/',         views.stall_approve,         name='stall_approve'),
    path('stalls/<int:pk>/reject/',          views.stall_reject,          name='stall_reject'),
    path('stalls/<int:pk>/suspend/',         views.stall_suspend,         name='stall_suspend'),
    path('stalls/<int:stall_pk>/subscribe/', views.subscription_create,   name='subscription_create'),

    # Locations
    path('locations/',                       views.location_list,         name='location_list'),
    path('locations/new/',                   views.location_create,       name='location_create'),
    path('locations/<int:pk>/edit/',         views.location_edit,         name='location_edit'),

    # Vendors
    path('vendors/',                         views.vendor_list,           name='vendor_list'),
    path('vendors/<int:pk>/',                views.vendor_detail,         name='vendor_detail'),

    # Officers
    path('officers/',                        views.officer_list,          name='officer_list'),
    path('officers/new/',                    views.officer_create,        name='officer_create'),

    # Violations
    path('violations/',                      views.violation_list,        name='violation_list'),

    # Reports
    path('reports/',                         views.reports,               name='reports'),
]
