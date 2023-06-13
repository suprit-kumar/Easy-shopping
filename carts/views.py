from django.shortcuts import render, redirect,get_object_or_404
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from store.models import Product
from .models import *


# Create your views here.


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    product = Product.objects.get(product_id=product_id)  # Get the product
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))  # Get the cart using the cart id present in the session
    except:
        cart = Cart.objects.create(
            cart_id=_cart_id(request)
        )
    cart.save()
    try:
        cart_item = CartItem.objects.get(product=product,
                                         cart=cart)  # Get the cart using the cart id present in the session
        cart_item.quantity += 1
    except:
        cart_item = CartItem.objects.create(
            product=product,
            cart=cart,
            quantity=1
        )
    cart_item.save()
    return redirect('cart')


def remove_cart(request,product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product,product_id=product_id)
    cart_item = CartItem.objects.get(product=product,cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')


def remove_cart_item(request,product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, product_id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart')

def cart(request, total=0, quantity=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.product_price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total) / 100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass  # Just ignore

    context = {"total": total, "quantity": quantity, "tax": tax, "grand_total": grand_total, "cart_items": cart_items}
    return render(request, 'store/cart.html', context)
