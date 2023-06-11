from django.contrib import admin
from .models import *



# Register your models here.
class ProductAdmin(admin.ModelAdmin):
  prepopulated_fields = {"product_slug": ("product_name",)}
  list_display = ('product_name','product_price','product_stock','product_category','product_modified_date','is_available')



admin.site.register(Product,ProductAdmin)