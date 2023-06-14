from django.shortcuts import render
from django.shortcuts import get_object_or_404
from . import models
from category import models as cat_model
from carts.models import CartItem
from carts.views import _cart_id
import traceback

def store(request, slug=None):
    specific_category = None
    products = None
    if slug:
        specific_category = get_object_or_404(cat_model.Category, cat_slug=slug)

        products = models.Product.objects.values('product_name', 'product_price', 'product_image','product_id',
                                                 'product_slug','product_category__cat_slug',).filter(
            is_available=True, product_category=specific_category).order_by('-product_modified_date')
    else:
        products = models.Product.objects.values('product_name', 'product_price', 'product_image','product_id',
                                                 'product_slug','product_category__cat_slug',).filter(
            is_available=True).order_by('-product_modified_date')
    context = {
        'products': products,
    }
    return render(request, 'store/store.html', context)


def product_detail(request, slug, product_slug):
    try:
        single_product = models.Product.objects.get(product_category__cat_slug=slug, product_slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request),product=single_product).exists()
    except Exception as e:
        raise e
    context = {'single_product':single_product,'in_cart':in_cart}

    return render(request, 'store/product_detail.html',context)
