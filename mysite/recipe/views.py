from django.views.generic import TemplateView, ListView
from django.db.models import Q # new
from .models import Recipe


class HomePageView(TemplateView):
    template_name = 'recipe/home.html'

class SearchResultsView(ListView):
    model = Recipe
    template_name = 'recipe/search_results.html'

    def get_queryset(self):  # new
        query = self.request.GET.get("q")
        object_list = Recipe.objects.filter(
            Q(name__icontains=query)
        )
        return object_list