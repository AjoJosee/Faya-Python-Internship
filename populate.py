import os
import django
from django.core.files import File

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from catalog.models import Product, ProductView, PrintArea

def run():
    print("Creating sample dataset...")
    
    # Check if we already have it
    if Product.objects.filter(name="Classic White T-Shirt").exists():
        print("Dataset already exists!")
        return

    # Create Product
    product = Product.objects.create(
        name="Classic White T-Shirt",
        description="A high-quality blank white t-shirt for your custom designs."
    )
    
    # Path to the generated image
    image_path = r"C:\Users\ASUS\.gemini\antigravity\brain\0d1ea70f-cd0a-4325-8d7a-4ca3e56fbc0c\white_tshirt_front_1776758818640.png"
    
    if os.path.exists(image_path):
        with open(image_path, 'rb') as f:
            # Create Product View
            view = ProductView(product=product, view_type='front')
            view.base_image.save('white_tshirt_front.png', File(f), save=True)
            
            # Create Print Area (assuming 1024x1024 image, center chest area)
            # Adjust these coordinates if needed. 
            PrintArea.objects.create(
                product_view=view,
                x=300,
                y=250,
                width=424,
                height=500
            )
            print("Successfully created product, view, and print area!")
    else:
        print("Could not find the generated image.")

if __name__ == '__main__':
    run()
