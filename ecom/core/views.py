from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Item, OrderItem, Order


# Create your views here.


class HomeView(ListView):
    model = Item
    template_name = 'home-page.html'


class ItemDetailView(DetailView):
    model = Item
    template_name = 'product.html'


def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item = OrderItem.objects.create(item=item)
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
