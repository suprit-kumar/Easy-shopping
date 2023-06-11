from django.db import models
from django.utils.text import slugify
from django.urls import reverse
# Create your models here.


class Category(models.Model):
    cat_id = models.AutoField(primary_key=True)
    cat_name = models.CharField(max_length=50,unique=True)
    cat_slug = models.SlugField(default="",unique=True)
    cat_description = models.TextField(max_length=500,blank=True)
    cat_image = models.ImageField(upload_to='photos/categories',blank=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural= 'categories'

    def get_url(self):
        return reverse('products_by_category',args=[self.cat_slug])

    def __str__(self):
        return self.cat_name

    def save(self, *args,**kwargs):
        if not self.cat_slug:
            self.cat_slug = slugify(self.cat_name)
        super(Category, self).save(*args, **kwargs)