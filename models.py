import os
from django.db import models
from django.conf import settings


class TempProduct(models.Model):
    product_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=300)
    body = models.TextField(null=True, blank=True)
    meta_title = models.CharField(max_length=255, null=True, blank=True)
    meta_description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title
    
    class Meta:
        managed = False
        db_table = 'temp_products_table'


class TempImage(models.Model):
    product = models.ForeignKey(
        TempProduct,
        to_field='product_id',
        related_name='images',
        on_delete=models.CASCADE
    )
    sort_order = models.IntegerField()
    caption = models.CharField(max_length=250)
    title = models.CharField(max_length=255, null=True, blank=True)
    file = models.ImageField(upload_to="images_temp", max_length=255)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    file_size = models.IntegerField(null=True, blank=True)
    collection_id = models.IntegerField()
    file_hash = models.CharField(max_length=40, null=True, blank=True)
    zoom_scale = models.FloatField(default=1)
    remove_bg = models.BooleanField(default=False)
    remove_wm = models.BooleanField(default=False)
    
    def delete(self, *args, **kwargs):
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        super(TempImage, self).delete(*args, **kwargs)

    def __str__(self):
        return self.product.title
    
    class Meta:
        managed = False
        db_table = 'temp_images_table'