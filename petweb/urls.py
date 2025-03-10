from django.urls import path
from petweb import views

app_name = 'petweb'

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
]