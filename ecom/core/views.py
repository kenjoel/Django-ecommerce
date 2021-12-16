from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import ListView, DetailView

from .models import Item, OrderItem, Order


class HomeView(ListView):
    model = Item
    paginate_by = 10
    template_name = 'home-page.html'


class ItemDetailView(DetailView):
    model = Item
    template_name = 'product.html'


def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    print(order_item, created)
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, f"You purchased {order_item.quantity} more of this item")
        else:
            messages.info(request, "This item was added to your cart")
            order.items.add(order_item)
    else:
        order_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=order_date)
        order.items.add(order_item)
    return redirect('core:product', slug=slug)


def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "This item was Removed from your cart")
            return redirect('core:product', slug=slug)
        else:
            messages.info(request, "This item was Not in your cart")
            return redirect('core:product', slug=slug)
