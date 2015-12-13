from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from glossary.models import Term


def glossary(request):
    glossary_terms = Term.objects.all()
    all_terms = [{term.term: term.definition} for term in glossary_terms]
    context = {'all_terms': all_terms}

    return render(request, 'glossary/glossary.html', context)


def glossary_json(request):
    glossary_terms = Term.objects.all()
    all_terms = {term.term: term.definition for term in glossary_terms}
    return JsonResponse(all_terms)
