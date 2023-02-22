from django.urls import path

from .views import HomePageView, SearchResultsView

app_name = 'recipe'
urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("search/", SearchResultsView.as_view(), name="search_results")   
]