from django.shortcuts import render,redirect
from django.http import HttpResponse
from store.models import Product
from .models import *
# Create your views here.

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request,product_id):
    product = Product.objects.get(product_id=product_id) # Get the product
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request)) # Get the cart using the cart id present in the session
    except:
        cart = Cart.objects.create(
            cart_id = _cart_id(request)
        )
    cart.save()
    try:
        cart_item = CartItem.objects.get(product=product,cart=cart)  # Get the cart using the cart id present in the session
        cart_item.quantity+=1
    except:
        cart_item = CartItem.objects.create(
            product=product,
            cart=cart,
            quantity=1
        )
    cart_item.save()
    return redirect('cart')

def cart(request):
    return render(request,'store/cart.html')