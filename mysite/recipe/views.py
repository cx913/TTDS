from django.views.generic import TemplateView, ListView
from django.db.models import Q # new
from .models import Recipes
from pathlib import Path
import pickle
import math

BASE_DIR = Path(__file__).resolve().parent.parent
def bm25(term_freq, doc_len, doc_freq, num_docs, k1=1.2, b=0.75):
    """
    Calculates the BM25 score for a term in a document.

    Args:
        term_freq (int): The frequency of the term in the document.
        doc_len (int): The length of the document in words.
        doc_freq (int): The number of documents that contain the term.
        num_docs (int): The total number of documents in the corpus.
        k1 (float, optional): The k1 parameter. Default is 1.2.
        b (float, optional): The b parameter. Default is 0.75.

    Returns:
        float: The BM25 score for the term in the document.
    """
    idf = math.log((num_docs - doc_freq + 0.5) / (doc_freq + 0.5))
    tf_weight = ((k1 + 1) * term_freq) / (k1 * ((1 - b) + (b * (doc_len / num_docs))) + term_freq)
    return idf * tf_weight

class HomePageView(TemplateView):
    template_name = 'recipe/home.html'

class SearchResultsView(ListView):
    model = Recipes
    template_name = 'recipe/search_results.html'

    def get_queryset(self):  # new
        query = self.request.GET.get("q")
        ir = self.request.GET.get("ir_check")
        if ir:
            address = BASE_DIR / ('doc_index/' + query)
            try:
                with open(address, "rb") as f:
                    ID = pickle.load(f)
            except:
                print("ID not found")
                return []

            mydata = Recipes.objects.filter(
                id = ID.keys()
            )

        else:
            mydata = Recipes.objects.filter(
                title=query
            )
        return mydata

