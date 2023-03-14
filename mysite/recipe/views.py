from django.views.generic import TemplateView, ListView
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


class HomePageView(TemplateView):
    template_name = 'recipe/home.html'


class SearchResultsView(ListView):
    model = Recipes
    template_name = 'recipe/search_results.html'

    def get_queryset(self):  # new
        query = self.request.GET.get("q")
        ir = self.request.GET.get("ir_check")
        # load frequency, doc lengths, doc number

        if ir:
            ir_list = qp.term_query(query, term_frequency, doc_len, doc_num)
            limit_count = 0
            limit = 20
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

        else:
            mydata = Recipes.objects.filter(
                title=query
            )
        return mydata
