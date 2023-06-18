from django.db import models
from store.models import Product,Variations
from accounts.models import Account
# Create your models here.


class Cart(models.Model):
    cart_id=models.CharField(max_length=250,blank=True)
    cart_added_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.cart_id


class CartItem(models.Model):
    # id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variations,blank=True)
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE,null=True)
    quantity = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    def sub_total(self):
        return self.quantity * self.product.product_price

    def __unicode__(self):
        return self.product
