from django.contrib import admin
from .models import *
import admin_thumbnails

@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1


# Register your models here.
class ProductAdmin(admin.ModelAdmin):
  prepopulated_fields = {"product_slug": ("product_name",)}
  list_display = ('product_name','product_price','product_stock','product_category','product_modified_date','is_available')


class VariationAdmin(admin.ModelAdmin):
  list_display = ('product', 'variation_category', 'variation_value', 'is_active', 'created_date',)
  list_editable = ('is_active',)
  list_filter = ('product', 'variation_category', 'variation_value', 'is_active',)

admin.site.register(Product,ProductAdmin)
admin.site.register(Variations,VariationAdmin)
admin.site.register(ReviewRating)
admin.site.register(ProductGallery)