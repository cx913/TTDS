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



def search_results(request):
    if request.method == "POST":
        query = request.POST['q']
        # low case
        query = query.lower()
        # nutrition info
        energy_min = int(request.POST['energy-min'])
        fat_min = int(request.POST['fat-min'])
        protein_min = int(request.POST['protein-min'])
        salts_min = int(request.POST['salt-min'])
        saturates_min = int(request.POST['saturate-min'])
        sugars_min = int(request.POST['sugar-min'])

        energy_max = int(request.POST['energy-max'])
        fat_max = int(request.POST['fat-max'])
        protein_max = int(request.POST['protein-max'])
        salts_max = int(request.POST['salt-max'])
        saturates_max = int(request.POST['saturate-max'])
        sugars_max = int(request.POST['sugar-max'])

        filter_data = {}


        if query.find('title:') == 0:
            recipe = Recipes.objects.filter(
                title__contains=query[6:]
            )
            # image url
            data = recipe[:200]
            for d in data:
                d.image = qp.url_process(d.image)
            return render(request, 'recipe/search_results_test.html', {'q': query, 'res': data})
        elif query.find('tag:') == 0:
            recipe = Recipes.objects.filter(
                tag__contains=query[4:]
            )
            # image url
            data = recipe[:200]
            for d in data:
                d.image = qp.url_process(d.image)
            return render(request, 'recipe/search_results_test.html', {'q': query, 'res': data})

        bm25_list = dict(
            sorted(qp.tree_query(query, term_frequency, doc_len, doc_num).items(), key=lambda kv: kv[1],
                    reverse=True))
        ir_list = bm25_list.keys()

        limit_count = 0
        limit = 200
        # for filter
        search_limit_count = 0
        search_limit = 5000
        all_data = []
        #check box
        mins = [energy_min, fat_min, protein_min, salts_min, saturates_min, sugars_min]
        maxs = [energy_max, fat_max, protein_max, salts_max, saturates_max, sugars_max]
        if qp.filter_check(mins, maxs):
            for doc_id in ir_list:
                # check if reach the limit
                search_limit_count += 1
                if search_limit_count == search_limit:
                    break
                recipe = Recipes.objects.get(
                    id=doc_id
                )
                if recipe.nutrition is None:
                    continue
                # get values
                values = recipe.nutrition
                values = ''.join([c for c in values if c.isdigit() or c == ',' or c == '.'])
                values = values.split(',')
                for value in values:
                    if value == '':
                       value = '0'
                values = [float(value) for value in values]
                # test
                f1 = qp.nutrition_test(energy_min, energy_max, values[0])
                f2 = qp.nutrition_test(fat_min, fat_max, values[1])
                f3 = qp.nutrition_test(protein_min, protein_max, values[2])
                f4 = qp.nutrition_test(salts_min, salts_max, values[3])
                f5 = qp.nutrition_test(saturates_min, saturates_max, values[4])
                f6 = qp.nutrition_test(sugars_min, sugars_max, values[5])
                # filter
                if not(f1 and f2 and f3 and f4 and f5 and f6):
                    continue
                if limit_count == limit:
                    break
                # first retrive
                data = Recipes.objects.get(
                    id=doc_id
                )
                # image url
                data.image = qp.url_process(data.image)
                data.tag = ",".join([x.capitalize() for x in data.tag.replace("'", '').split(',')])
                all_data.append(data)
                limit_count += 1
            return render(request, 'recipe/search_results_test.html', {'q': query, 'res': all_data})
        else:
            for doc_id in ir_list:
                # check if reach the limit
                if limit_count == limit:
                    break
                # first retrive
                data = Recipes.objects.get(
                    id=doc_id
                )
                # image url
                data.image = qp.url_process(data.image)
                data.tag = " , ".join([x.capitalize() for x in data.tag.replace("'", '').split(',')])
                all_data.append(data)
                limit_count += 1
        return render(request, 'recipe/search_results_test.html', {'q': query, 'res': all_data, 'filter': filter_data})
    else:
        query = request.POST.get('q')
        return render(request, 'recipe/search_results_test.html', {})


def show_recipe(request, recipe_id):
    recipe = Recipes.objects.get(id=recipe_id)
    recipe.image = qp.url_process(recipe.image)
    # nutritionalInfo = NutritionalInfo.objects.get(title=recipe.title)
    instructions_list = recipe.instructions.replace('text', '').replace('"', '').replace('[', '').replace(']',
                                                                                                          '').replace(
        '{', '').replace('}', '').replace(':', '').split(',')
    recipe_instructions = []
    temp_instruction = ''

    for instruction in instructions_list:
        # temp_instruction = temp_instruction + ' ' + instruction

        if temp_instruction.endswith('.') or temp_instruction.endswith('!') or temp_instruction.endswith(')'):
            if instruction.startswith('(') or instruction.startswith(')'):
                temp_instruction = temp_instruction + ' ' + instruction
                continue
            recipe_instructions.append(temp_instruction)
            temp_instruction = ''
        temp_instruction = temp_instruction + ' ' + instruction
    if temp_instruction.endswith('.') or temp_instruction.endswith('!') or temp_instruction.endswith(')'):
        recipe_instructions.append(temp_instruction)
    recipe.instructions = recipe_instructions
    
    ingredients_list = recipe.ingredients.replace('text', '').replace('"', '').replace('[', '').replace(']',
                                                                                                          '').replace(
        '{', '').replace('}', '').replace(':', '').split(',')
    recipe_ingredients = []
    temp_ingredient = ''
    temp_ingredient_idx = 0

    for idx, ingredient in enumerate(ingredients_list):
        if '(' in ingredient and ')' not in ingredient:
            temp_ingredient_idx = idx
            temp_ingredient = ingredient
            continue
        elif ')' in ingredient and '(' not in ingredient:
            if idx == (temp_ingredient_idx + 1) :
                temp_ingredient = temp_ingredient + ' ' + ingredient
            recipe_ingredients.append(temp_ingredient)
        else:
            recipe_ingredients.append(ingredient)
    recipe.ingredients = recipe_ingredients
    # return render(request, 'recipe/show_recipe.html', {'recipe': recipe, 'nutritionalInfo': nutritionalInfo})
    return render(request, 'recipe/show_recipe.html', {'recipe': recipe})

