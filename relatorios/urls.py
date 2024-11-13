from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('adicionar/', views.adicionar_relatorio, name='adicionar_relatorio'),
] 