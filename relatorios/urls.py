from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('adicionar/', views.adicionar_relatorio, name='adicionar_relatorio'),
    path('lista/', views.lista_relatorios, name='lista_relatorios'),
    path('excluir/<int:pk>/', views.excluir_relatorio, name='excluir_relatorio'),
] 