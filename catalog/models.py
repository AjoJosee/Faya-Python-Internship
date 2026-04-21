from django.db import models
import json

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)

    def __str__(self):
        return self.name

class ProductView(models.Model):
    VIEW_TYPES = [
        ('front', 'Front'),
        ('back', 'Back'),
        ('side', 'Side'),
    ]
    product = models.ForeignKey(Product, related_name='views', on_delete=models.CASCADE)
    view_type = models.CharField(max_length=10, choices=VIEW_TYPES, default='front')
    base_image = models.ImageField(upload_to='products/base_images/')
    
    # Pre-calculated displacement and shadow map data path (stored as files)
    displacement_map_x = models.FileField(upload_to='products/maps/', blank=True, null=True)
    displacement_map_y = models.FileField(upload_to='products/maps/', blank=True, null=True)
    shadow_map = models.ImageField(upload_to='products/maps/', blank=True, null=True)

    def __str__(self):
        return f"{self.product.name} - {self.view_type}"

class PrintArea(models.Model):
    product_view = models.OneToOneField(ProductView, related_name='print_area', on_delete=models.CASCADE)
    x = models.IntegerField(help_text="X coordinate of top-left corner")
    y = models.IntegerField(help_text="Y coordinate of top-left corner")
    width = models.IntegerField(help_text="Maximum width of the print area")
    height = models.IntegerField(help_text="Maximum height of the print area")

    def __str__(self):
        return f"Print Area for {self.product_view}"
