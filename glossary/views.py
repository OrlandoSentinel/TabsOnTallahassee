from django.shortcuts import render
from django.http import HttpResponse

from glossary.models import Term


def index(request):
    return HttpResponse("Hello, world. You're at the glossary index.")

def glossary(request):
    glossary_terms = Term.objects.all()

    all_terms = []
    for term in glossary_terms:
        word = {}
        word[term.term] = term.definition
        all_terms.append(word)
    # import ipdb; ipdb.set_trace();

    context = {'all_terms': all_terms}

    return render(request, 'glossary/glossary.html', context)
