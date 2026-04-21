from rest_framework import serializers
from catalog.models import Product, ProductView, PrintArea

class PrintAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrintArea
        fields = ['x', 'y', 'width', 'height']

class ProductViewSerializer(serializers.ModelSerializer):
    print_area = PrintAreaSerializer(read_only=True)
    class Meta:
        model = ProductView
        fields = ['id', 'view_type', 'base_image', 'print_area']

class ProductSerializer(serializers.ModelSerializer):
    views = ProductViewSerializer(many=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'thumbnail', 'views']
