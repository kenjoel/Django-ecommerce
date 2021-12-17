import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, DetailView

from .forms import CheckoutForm, CouponForm
from .models import Item, OrderItem, Order, BillingAddress

import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

# `source` is obtained with Stripe.js; see https://stripe.com/docs/payments/accept-a-payment-charges#web-create-token
stripe.Charge.create(
    amount=2000,
    currency="usd",
    source="tok_mastercard",
    description="My First Test Charge (created for API docs)",
)


class HomeView(ListView):
    model = Item
    paginate_by = 10
    template_name = 'home-page.html'


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("/")


class ItemDetailView(DetailView):
    model = Item
    template_name = 'product.html'


@login_required
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
            return redirect('core:order_summary')
        else:
            messages.info(request, "This item was added to your cart")
            order.items.add(order_item)
            return redirect('core:order_summary')
    else:
        order_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=order_date)
        order.items.add(order_item)
        messages.info(request, "New item was added to your cart")
        return redirect('core:order_summary')


@login_required
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
            return redirect('core:order_summary')
        else:
            messages.info(request, "This item was Not in your cart")
            return redirect('core:product', slug=slug)


@login_required
def remove_single_item(request, slug):
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
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
                messages.info(request, "One of these item was Removed from your cart")
                return redirect('core:order_summary')
            else:
                order.items.remove(order_item)
                order_item.delete()
                messages.info(request, "This item was Removed from your cart")
                return redirect('core:order_summary')


class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True
            }
            return render(self.request, 'checkout-page.html', context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("core:checkout")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zipcode = form.cleaned_data.get('zip')
                billing_address = BillingAddress(
                    user=self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    zip=zipcode
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()
                return redirect('core:payment')

        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("core:checkout")
            # if form.is_valid():
            #     order.update_address(
            #         street_address=street_address,
            #         apartment_address=apartment_address,
            #         country=country,
            #         zip=zip
            #     )
            #     return redirect('core:payment')
            # messages.info(self.request, "Please fill in the required fields")
            # return redirect('core:checkout')


class Payment(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        context = {
            'order': order
        }
        return render(self.request, 'payment-page.html', context)

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        amount = int(order.get_total() * 100)
        try:
            charge = stripe.Charge.create(
                amount=amount,
                currency="usd",
                source=token
            )
            order.ordered = True
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()
        except stripe.error.CardError as e:
            body = e.json_body
            err = body.get('error', {})
            messages.warning(self.request, f"{err.get('message')}")
            return redirect('core:checkout')
        except stripe.error.RateLimitError as e:
            messages.warning(self.request, "Rate limit error")
            return redirect('core:checkout')
        except stripe.error.InvalidRequestError as e:
            messages.warning(self.request, "Invalid parameters")
            return redirect('core:checkout')
        except stripe.error.AuthenticationError as e:
            messages.warning(self.request, "Not authenticated")
            return redirect('core:checkout')
        except stripe.error.APIConnectionError as e:
            messages.warning(self.request, "Network error")
            return redirect('core:checkout')
        except stripe.error.StripeError as e:
            messages.warning(self.request, "Something went wrong. You were not charged. Please try again")
            return redirect('core:checkout')
        except Exception as e:
            messages.warning(self.request, "A serious error occurred. We have been notified")
            return redirect('core:checkout')
        messages.success(self.request, "Payment successful")
        return redirect('core:checkout')
