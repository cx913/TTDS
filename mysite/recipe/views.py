from django.views.generic import TemplateView, ListView
from django.shortcuts import render
from django.views import View
from django.contrib.staticfiles.views import serve
from django.http import JsonResponse
from .models import Recipes, NutritionalInfo
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
    if request.method == "POST":
        query = request.POST['q']
        # low case
        query = query.lower()
        # nutrition info
        energy = request.POST['energy']
        fat = request.POST['fat']
        protein = request.POST['protein']
        salts = request.POST['salts']
        saturates = request.POST['saturates']
        sugars = request.POST['sugars']

        if ' ' not in query:
            bm25_list = dict(
                sorted(qp.term_query(query, term_frequency, doc_len, doc_num).items(), key=lambda kv: kv[1],
                       reverse=True))
            ir_list = bm25_list.keys()
        else:
            bm25_list = dict(
                sorted(qp.tree_query(query, term_frequency, doc_len, doc_num).items(), key=lambda kv: kv[1],
                       reverse=True))
            ir_list = bm25_list.keys()
        limit_count = 0
        limit = 50
        all_data = None
        for doc_id in ir_list:
            if limit_count == limit:
                break
            if limit_count == 0:
                data = Recipes.objects.filter(
                    id=doc_id
                )
                nutrition = NutritionalInfo.objects.filter(
                    id=data[0].title
                )
                if len(nutrition) == 0:
                    all_data = data
                    limit_count += 1
                    continue
                # get values
                values = nutrition.all()[0].nutr_values_per100g
                values = ''.join([c for c in values if c.isdigit() or c == ',' or c == '.'])
                values = values.split(',')
                for value in values:
                    if value == '':
                        value = '0'
                values = [float(value) for value in values]
                # test
                f1 = qp.nutrition_test(energy, values[0])
                f2 = qp.nutrition_test(fat, values[1])
                f3 = qp.nutrition_test(protein, values[2])
                f4 = qp.nutrition_test(salts, values[3])
                f5 = qp.nutrition_test(saturates, values[4])
                f6 = qp.nutrition_test(sugars, values[5])
                if f1 and f2 and f3 and f4 and f5 and f6:
                    all_data = data
                    limit_count += 1
            else:
                data = Recipes.objects.filter(
                    id=doc_id
                )
                nutrition = NutritionalInfo.objects.filter(
                    id=data[0].title
                )
                if len(nutrition) == 0:
                    all_data = all_data | data
                    limit_count += 1
                    continue
                # get values
                values = nutrition.all().nutr_values_per100g
                values = ''.join([c for c in values if c.isdigit() or c == ',' or c == '.'])
                values = values.split(',')
                for value in values:
                    if value == '':
                        value = '50'
                values = [float(value) for value in values]
                # test
                f1 = qp.nutrition_test(energy, values[0])
                f2 = qp.nutrition_test(fat, values[1])
                f3 = qp.nutrition_test(protein, values[2])
                f4 = qp.nutrition_test(salts, values[3])
                f5 = qp.nutrition_test(saturates, values[4])
                f6 = qp.nutrition_test(sugars, values[5])
                if f1 and f2 and f3 and f4 and f5 and f6:
                    all_data = all_data | data
                    limit_count += 1
        return render(request, 'recipe/search_results.html', {'q': query, 'res': all_data})
    else:
        query = request.POST.get('q')
        return render(request, 'recipe/search_results.html', {})


def show_recipe(request, recipe_id):
    recipe = Recipes.objects.get(id=recipe_id)
    # nutritionalInfo = NutritionalInfo.objects.get(title=recipe.title)
    recipe.instructions = recipe.instructions.replace('text', '').replace('"', '').replace('[', '').replace(']',
                                                                                                          '').replace(
        '{', '').replace('}', '').replace(':', '').split(',')
    recipe.ingredients = recipe.ingredients.replace('text', '').replace('"', '').replace('[', '').replace(']',
                                                                                                          '').replace(
        '{', '').replace('}', '').replace(':', '').split(',')
    # return render(request, 'recipe/show_recipe.html', {'recipe': recipe, 'nutritionalInfo': nutritionalInfo})
    return render(request, 'recipe/show_recipe.html', {'recipe': recipe})

# class HomePageView(TemplateView):
#     template_name = 'recipe/home.html'
