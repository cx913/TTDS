from django.urls import path
from . import views

urlpatterns = [
    path('',  views.home, name='home'),
    path('search_results', views.search_results, name='search-results'),
    path('static/<path:path>', views.serve_static),
]
