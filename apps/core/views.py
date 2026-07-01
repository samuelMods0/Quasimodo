from django.shortcuts import render

# Create your views here.
def styleguide(request):
    return render(request, "core/styleguide.html")
