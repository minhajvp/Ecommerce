from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("verify-otp/", views.verify_otp, name="verify_otp"),
    # path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("add-to-cart-ajax/", views.add_to_cart_ajax, name="add_to_cart_ajax"),
    path("checkout/", views.checkout, name="checkout"),

    path("cart/buy_now/<int:product_id>/", views.buy_now, name="buy_now"),
    path("home/product_detail/<int:id>/", views.product_detail, name="product_detail"),
    path('update-quantity/', views.update_quantity, name='update_quantity'),
    # path('cart/', views.cart, name='cart'),
    
]