from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('add-to-cart/<uuid:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-success/<uuid:order_id>/', views.order_success, name='order_success'),
    path('product-feedback/<uuid:product_id>/', views.product_feedback, name='product_feedback'),
]
