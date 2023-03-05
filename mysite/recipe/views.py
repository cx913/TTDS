from django.views.generic import TemplateView, ListView
from django.db.models import Q # new
from .models import Recipes


class HomePageView(TemplateView):
    template_name = 'recipe/home.html'

class SearchResultsView(ListView):
    model = Recipes
    template_name = 'recipe/search_results.html'

    def get_queryset(self):  # new
        query = self.request.GET.get("q")
        mydata = Recipes.objects.filter(
            title=query
        )
        return mydata