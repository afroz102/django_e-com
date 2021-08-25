from core.models import Item
from django.shortcuts import render

from django.views.generic import ListView, DetailView

# def home(request):
#     context = {
#         "items": Item.objects.all()
#     }
#     return render(request, 'core/home-page.html', context)


class HomeView(ListView):
    model = Item
    template_name = 'core/home-page.html'


class ItemDetailView(DetailView):
    model = Item
    template_name = 'core/item_details.html'