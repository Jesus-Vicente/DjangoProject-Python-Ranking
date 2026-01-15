from django.contrib import admin
from django.urls import path

from safaranking.views import *

urlpatterns = [
    path('', mostrar_inicio, name='inicio'),

    path('inicio/', mostrar_inicio, name='inicio'),
]
