from django.urls import path

from .views import HomeView, ItemDetailView, add_to_cart, remove_from_cart, OrderSummaryView, remove_single_item, \
    CheckoutView, PaymentView, AddCoupon, RequestRefund

app_name = 'core'
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('add_to_cart/<slug>/', add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<slug>/', remove_from_cart, name='remove_from_cart'),
    path('order_summary/', OrderSummaryView.as_view(), name='order_summary'),
    path('remove_single_item_from_cart/<slug>/', remove_single_item, name='remove_single_item_from_cart'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path("payment/<payment_option>/", PaymentView.as_view(), name="payment"),
    path('coupons/', AddCoupon.as_view(), name='coupons'),
    path("request-refund", RequestRefund.as_view(), name="request-refund"),

    # path('<int:pk>/', item_detail, name='item_detail'),
]