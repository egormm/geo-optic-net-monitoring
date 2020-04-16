from django.urls import path, include

from geoserver import views

app_name = 'geoserver'

urlpatterns = [
    path('map/', views.Map.as_view(), name='map'),
    path('boxes/', views.BoxList.as_view(), name='box-list'),
    path('wires/', views.WireList.as_view(), name='wire-list'),
    path('boxes/<int:pk>', views.BoxDetail.as_view(), name='box-detail'),
    path('wires/<int:pk>', views.WireDetail.as_view(), name='wire-detail'),
    path('clients/', views.ClientList.as_view(), name='client-info'),
    path('boxes/<int:pk>/', include('scheme.urls')),
]
