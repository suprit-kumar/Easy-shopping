from django.shortcuts import render
from django.shortcuts import get_object_or_404
from . import models
from category import models as cat_model
from carts.models import CartItem
from carts.views import _cart_id
import traceback
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q


def store(request, slug=None):
    specific_category = None
    products = None
    if slug:
        specific_category = get_object_or_404(cat_model.Category, cat_slug=slug)

        products = models.Product.objects.values('product_name', 'product_price', 'product_image', 'product_id',
                                                 'product_stock',
                                                 'product_slug', 'product_category__cat_slug', ).filter(
            is_available=True, product_category=specific_category).order_by('-product_modified_date')
        display_count = 2
    else:
        products = models.Product.objects.values('product_name', 'product_price', 'product_image', 'product_id',
                                                 'product_stock',
                                                 'product_slug', 'product_category__cat_slug', ).filter(
            is_available=True).order_by('-product_modified_date')
        display_count = 6
    paginator = Paginator(products, display_count)
    page = request.GET.get("page")
    paged_products = paginator.get_page(page)
    product_count = products.count()

    context = {
        'products': paged_products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)


def product_detail(request, slug, product_slug):
    try:
        single_product = models.Product.objects.get(product_category__cat_slug=slug, product_slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
        product_variations = models.Variations.objects.values('variation_category', 'variation_value').filter(
            product__product_category__cat_slug=slug,
            product__product_slug=product_slug,is_active=True)
        print(product_variations)
    except Exception as e:
        raise e
    context = {'single_product': single_product, 'in_cart': in_cart, 'product_variations': product_variations}

    return render(request, 'store/product_detail.html', context)


def search(request):
    keyword = request.GET.get("keyword")
    if keyword:
        products = models.Product.objects.values('product_name', 'product_price', 'product_image', 'product_id',
                                                 'product_stock',
                                                 'product_slug', 'product_category__cat_slug', ).filter(
            Q(product_name__icontains=keyword) | Q(product_description__icontains=keyword) | Q(
                product_slug__icontains=keyword), is_available=True).order_by('-product_modified_date')
        product_count = products.count()
        context = {
            'products': products,
            'product_count': product_count,
        }
    return render(request, 'store/store.html', context)
