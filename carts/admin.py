from django.contrib import admin
from .models import *
# Register your models here.


class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_id','cart_added_date')

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product','cart','quantity','is_active')

admin.site.register(Cart,CartAdmin)
admin.site.register(CartItem,CartItemAdmin)