from django.views.generic import TemplateView, ListView
from django.shortcuts import render
from django.views import View
from django.contrib.staticfiles.views import serve
from django.http import JsonResponse
from .models import Recipes
import pickle
import math
from . import query_process as qp
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

term_frequency_address = BASE_DIR / 'doc_index' / 'term_frequency'
doc_len_address = BASE_DIR / 'doc_index' / 'doc_len'
num_docs = BASE_DIR / 'doc_index' / 'num_docs'

with open(term_frequency_address, "rb") as f:
    term_frequency = pickle.load(f)
with open(doc_len_address, "rb") as f:
    doc_len = pickle.load(f)
with open(num_docs, "rb") as f:
    doc_num = pickle.load(f)

def home(request):
    return render(request, 'recipe/home.html')


def serve_static(request, path):
    return serve(request, path, insecure=True)

def search_results(request):
    ctx = {}
    if request.method == "POST":
        query = request.POST['q']
        if ' ' not in query:
            ir_list = set(sorted(qp.term_query(query, term_frequency, doc_len, doc_num), reverse=True))
        else:
            ir_list = set(sorted(qp.tree_query(query, term_frequency, doc_len, doc_num), reverse=True))
        limit_count = 0
        limit = 50
        all_data = None
        for doc_id in ir_list:
            if limit_count == limit:
                break
            if limit_count == 0:
                all_data = Recipes.objects.filter(
                    id=doc_id
                )
            else:
                data = Recipes.objects.filter(
                    id=doc_id
                )
                all_data = all_data | data
            limit_count += 1

        return render(request, 'recipe/search_results.html', {'q': query, 'res': all_data})
    else:
        query = request.POST.get('q')
        return render(request, 'recipe/search_results.html', {})

def show_recipe(request, recipe_id):
    recipe = Recipes.objects.get(id=recipe_id)
    return render(request, 'recipe/show_recipe.html', {'recipe': recipe})




# class HomePageView(TemplateView):
#     template_name = 'recipe/home.html'


class SearchResultsView(ListView):
    model = Recipes
    template_name = 'recipe/search_results.html'

    def get_queryset(self):  # new
        query = self.request.GET.get("q")

        if ' ' not in query:
            ir_list = set(sorted(qp.term_query(query, term_frequency, doc_len, doc_num), reverse=True))
        else:
            ir_list = set(sorted(qp.tree_query(query, term_frequency, doc_len, doc_num), reverse=True))
        limit_count = 0
        limit = 50
        all_data = None
        for doc_id in ir_list:
            if limit_count == limit:
                break
            if limit_count == 0:
                all_data = Recipes.objects.filter(
                    id=doc_id
                )
            else:
                data = Recipes.objects.filter(
                    id=doc_id
                )
                all_data = all_data | data
            limit_count += 1
        return all_data




