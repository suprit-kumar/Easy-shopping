from django.shortcuts import render
from store.models import Product


# Create your views here.
def home(request):
    products = Product.objects.values('product_name', 'product_price', 'product_image', 'product_description',
                                      'product_slug', 'product_stock', 'product_category__cat_name').filter(
        is_available=True).order_by('-product_modified_date')
    context = {
        'products': products
    }
    return render(request, 'home.html', context)