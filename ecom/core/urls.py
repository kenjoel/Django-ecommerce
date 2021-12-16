from django.urls import path

from .views import checkout, products, HomeView, ItemDetailView

app_name = 'core'
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('/checkout', products, name='checkout'),

    # path('<int:pk>/', item_detail, name='item_detail'),
]