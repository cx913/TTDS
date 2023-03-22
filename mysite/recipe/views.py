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
from itertools import chain

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
        filter_check = request.POST.get('filter', False)

        bm25_list = dict(
            sorted(qp.tree_query(query, term_frequency, doc_len, doc_num).items(), key=lambda kv: kv[1],
                    reverse=True))
        ir_list = bm25_list.keys()

        limit_count = 0
        limit = 50
        # for filter
        search_limit_count = 0
        search_limit = 5000
        all_data = None
        #check box
        if filter_check == 'filter':
            for doc_id in ir_list:
                # check if reach the limit
                nutrition = NutritionalInfo.objects.filter(
                     id=doc_id
                 )
                search_limit_count += 1
                if search_limit_count == search_limit:
                    break
                if len(nutrition) == 0:
                    continue
                # get values
                values = nutrition[0].nutr_values_per100g
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
                # filter
                if not(f1 and f2 and f3 and f4 and f5 and f6):
                    continue
                if limit_count == limit:
                    break
                # first retrive
                if limit_count == 0:
                    data = Recipes.objects.filter(
                        id=doc_id
                    )
                    all_data = data
                    limit_count += 1
                else:
                    data = Recipes.objects.filter(
                        id=doc_id
                    )
                    all_data = all_data | data
                    limit_count += 1
            return render(request, 'recipe/search_results.html', {'q': query, 'res': all_data})
        else:
            for doc_id in ir_list:
                # check if reach the limit
                if limit_count == limit:
                    break
                # first retrive
                if limit_count == 0:

                    data = Recipes.objects.filter(
                        id=doc_id
                    )
                    all_data = data
                    limit_count += 1
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
    recipe.image = qp.url_process(recipe.image)
    # nutritionalInfo = NutritionalInfo.objects.get(title=recipe.title)
    instructions_list = recipe.instructions.replace('text', '').replace('"', '').replace('[', '').replace(']',
                                                                                                          '').replace(
        '{', '').replace('}', '').replace(':', '').split(',')
    recipe_ingredients = []
    temp_instruction = ''
    for instruction in instructions_list:
        # temp_instruction = temp_instruction + ' ' + instruction

        if temp_instruction.endswith('.') or temp_instruction.endswith('!'):
            if instruction.startswith('('):
                temp_instruction = temp_instruction + ' ' + instruction
                recipe_ingredients.append(temp_instruction)
                temp_instruction = ''
                continue
            recipe_ingredients.append(temp_instruction)
            temp_instruction = ''
        temp_instruction = temp_instruction + ' ' + instruction
    if temp_instruction.endswith('.') or temp_instruction.endswith('!'):
        recipe_ingredients.append(temp_instruction)
    recipe.instructions = recipe_ingredients
    recipe.ingredients = recipe.ingredients.replace('text', '').replace('"', '').replace('[', '').replace(']',
                                                                                                          '').replace(
        '{', '').replace('}', '').replace(':', '').split(',')
    # return render(request, 'recipe/show_recipe.html', {'recipe': recipe, 'nutritionalInfo': nutritionalInfo})
    return render(request, 'recipe/show_recipe.html', {'recipe': recipe})

