from django.contrib import admin
from .models import Product, ProductView

class ProductViewInline(admin.TabularInline):
    model = ProductView
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [ProductViewInline]

@admin.register(ProductView)
class ProductViewAdmin(admin.ModelAdmin):
    list_display = ('product', 'view_type')
