from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from store.models import Product, Variations
from .models import *


# Create your views here.


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    product = Product.objects.get(product_id=product_id)  # Get the product
    product_variations = []
    if request.method == "POST":
        for item in request.POST:
            key = item
            value = request.POST.get(key)

            print("key: ", key, "value: ", value)
            try:
                variation = Variations.objects.get(product=product, variation_category__iexact=key,
                                                    variation_value__iexact=value)
                product_variations.append(variation)
            except:pass

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))  # Get the cart using the cart id present in the session
    except:
        cart = Cart.objects.create(cart_id=_cart_id(request))
    cart.save()

    is_cart_item_exist = CartItem.objects.filter(product=product,cart=cart).exists()

    if is_cart_item_exist:
        cart_item = CartItem.objects.filter(product=product,cart=cart)  # Get the cart using the cart id present in the session
        # Get existing variations -> database
        # current variations -> product_variations
        # item_id -> database
        existing_var_list = []
        id = []
        for item in cart_item:
            existing_variations = item.variations.all()
            existing_var_list.append(list(existing_variations))
            id.append(item.id)

        print(existing_var_list)

        if product_variations in existing_var_list:
            # increase the cart item quantity
            index = existing_var_list.index(product_variations)
            item_id = id[index]
            item = CartItem.objects.get(product=product,id=item_id)
            item.quantity += 1
            item.save()
        else:
            item = CartItem.objects.create(product=product,cart=cart,quantity=1)
            if product_variations:
                item.variations.clear()
                item.variations.add(*product_variations)
            item.save()
    else:
        cart_item = CartItem.objects.create(
            product=product,
            cart=cart,
            quantity=1
        )
        if product_variations:
            cart_item.variations.clear()
            cart_item.variations.add(*product_variations)
        cart_item.save()
    return redirect('cart')


def remove_cart(request, product_id,cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    try:
        product = get_object_or_404(Product, product_id=product_id)
        cart_item = CartItem.objects.get(product=product, cart=cart,id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:pass
    return redirect('cart')


def remove_cart_item(request, product_id,cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, product_id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart,id=cart_item_id)
    cart_item.delete()
    return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):
    try:
        tax = grand_total = 0
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
