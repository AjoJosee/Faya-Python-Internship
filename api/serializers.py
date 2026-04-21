from rest_framework import serializers
from catalog.models import Product, ProductView

class ProductViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductView
        fields = ['id', 'view_type', 'base_image']

class ProductSerializer(serializers.ModelSerializer):
    views = ProductViewSerializer(many=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'thumbnail', 'views']
