from django.shortcuts import render


def index(request):
    user = request.user
    return render(
        request,
        'home/index.html',
        {'user': user}
    )


def about(request):
    return render(request, 'home/about.html')