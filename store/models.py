from django.db import models
from category.models import Category
from django.utils.text import slugify
from django.urls import reverse
from django.db.models import Avg, Count
from accounts.models import Account
# Create your models here.

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=200,unique=True)
    product_slug = models.SlugField(max_length=255,unique=True)
    product_description = models.TextField(max_length=500,blank=True)
    product_price = models.PositiveIntegerField()
    product_image = models.ImageField(upload_to='photos/products')
    product_stock = models.PositiveIntegerField()
    is_available = models.BooleanField(default=True)
    product_category = models.ForeignKey(Category,on_delete=models.CASCADE)
    product_created_date = models.DateTimeField(auto_now_add=True)
    product_modified_date = models.DateTimeField(auto_now=True)


    def get_url(self):
        return reverse('product_detail',args=[self.product_category.cat_slug,self.product_slug])

    def __str__(self):
        return self.product_name

    def averageReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg

    def countReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(count=Count('id'))
        count = 0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count

    def save(self, *args, **kwargs):
        if not self.product_slug:
            self.product_slug = slugify(self.product_name)
        super(Product, self).save(*args, **kwargs)


class VariationsManagerr(models.Manager):
    def colors(self):
        return super(VariationsManagerr,self).filter(variation_category='color',is_active=True)

    def sizes(self):
        return super(VariationsManagerr,self).filter(variation_category='size',is_active=True)

variation_category_choices = (
    ('color','color'),
    ('size','size'),
)

class Variations(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=100,choices=variation_category_choices)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)

    objects = VariationsManagerr()

    def __str__(self):
        return self.variation_value



class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject


class ProductGallery(models.Model):
    product = models.ForeignKey(Product, default=None, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='store/products', max_length=255)

    def __str__(self):
        return self.product.product_name

    class Meta:
        verbose_name = 'productgallery'
        verbose_name_plural = 'product gallery'