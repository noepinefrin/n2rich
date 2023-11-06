from django.urls import path, include

from django.urls import path
from . import views

urlpatterns = [
    path('analysis_progress/', views.progress_view, name='analysis_progress'),
    path('', views.index, name='index'),
    path('analysis/', views.analysis, name='analysis')
]