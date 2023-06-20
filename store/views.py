from django.shortcuts import render,redirect
from django.shortcuts import get_object_or_404
from . import models
from category import models as cat_model
from carts.models import CartItem
from carts.views import _cart_id
from orders.models import OrderProduct
import traceback
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .forms import ReviewForm
from django.contrib import messages

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
    except Exception as e:
        raise e

    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(user=request.user,
                                                       product__product_id=single_product.product_id).exists()
        except:
            orderproduct = None
    else:
        orderproduct = None

    product_variations = models.Variations.objects.values('variation_category', 'variation_value').filter(
        product__product_category__cat_slug=slug,
        product__product_slug=product_slug, is_active=True).distinct()

    # Get the reviews
    reviews = models.ReviewRating.objects.filter(product__product_id=single_product.product_id, status=True)

    # Get the product gallery
    product_gallery = models.ProductGallery.objects.filter(product__product_id=single_product.product_id)

    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'product_variations': product_variations,
        'orderproduct': orderproduct,
        'reviews': reviews,
        'product_gallery': product_gallery,
    }

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


def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = models.ReviewRating.objects.get(user__id=request.user.id, product__product_id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(url)
        except:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = models.ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)
