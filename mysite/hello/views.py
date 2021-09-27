from django.shortcuts import render

# Create your views here.
def index(request):
    context = {
        "title":"Hello Class!",
        "header": "CINS465 Hello World"
    }
    return render(request, "index.html", context = context)