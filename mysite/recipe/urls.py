from django.urls import path
from . import views

urlpatterns = [
    path('',  views.home, name='home'),
    path('search_results', views.search_results, name='search-results'),
    path('show_recipe/<recipe_id>', views.show_recipe, name='show-recipe'),
    # path("search_ir/", SearchResultsView.as_view(), name="search_ir_results"),
    path('static/<path:path>', views.serve_static),
]
