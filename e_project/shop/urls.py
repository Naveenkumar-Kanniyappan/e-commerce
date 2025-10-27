from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'), 
    path('logout/', views.logout_view, name='logout'),
    path('reset_password/', views.reset_password, name='reset_password'),
    path('set_new_password/<str:uidb64>/<str:token>/', views.set_new_password, name='set_new_password'),
    path('collections/', views.collections, name='collections'),
    path('collections/<str:name>/', views.collectionsview, name='collectionsview'),
    path('collections/<str:cname>/<path:pname>/', views.productDetails, name='productDetails'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('buy_now/<int:product_id>/', views.buy_now, name='buy_now'),
    path('cart/', views.cart_view, name='cart'),
    path('update_cart/<int:product_id>/', views.update_cart, name='update_cart'),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment_success/', views.payment_success, name='payment_success'),

]
