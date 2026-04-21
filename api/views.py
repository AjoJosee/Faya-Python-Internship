from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import HttpResponse
from catalog.models import Product, ProductView
from .serializers import ProductSerializer
from engine.processor import render_design_on_product, detect_perspective
import cv2
import numpy as np

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all().prefetch_related('views', 'views__print_area')
    serializer_class = ProductSerializer

class RenderPreviewView(APIView):
    authentication_classes = []
    permission_classes = []
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        product_view_id = request.data.get('product_view_id')
        design_file = request.FILES.get('design')
        
        try:
            x = int(float(request.data.get('x', 0)))
            y = int(float(request.data.get('y', 0)))
            width = int(float(request.data.get('width', 100)))
            height = int(float(request.data.get('height', 100)))
            rotation = float(request.data.get('rotation', 0.0))
            auto_perspective = request.data.get('auto_perspective', 'false').lower() == 'true'
        except (ValueError, TypeError):
            return Response({"error": "Invalid numerical parameters."}, status=status.HTTP_400_BAD_REQUEST)

        if not product_view_id or not design_file:
            return Response({"error": "product_view_id and design are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product_view = ProductView.objects.get(id=product_view_id)
        except ProductView.DoesNotExist:
            return Response({"error": "Product view not found."}, status=status.HTTP_404_NOT_FOUND)

        # Load product base image
        product_image_path = product_view.base_image.path
        product_img = cv2.imread(product_image_path, cv2.IMREAD_UNCHANGED)
        if product_img is None:
            return Response({"error": "Failed to load product image."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Load design image from memory
        design_bytes = design_file.read()
        nparr = np.frombuffer(design_bytes, np.uint8)
        design_img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
        if design_img is None:
            return Response({"error": "Failed to decode design image."}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure design has alpha channel
        if design_img.shape[2] == 3:
            design_img = cv2.cvtColor(design_img, cv2.COLOR_BGR2BGRA)

        # Auto perspective detection if requested
        if auto_perspective:
            # Get crop of print area to analyze
            try:
                pa = product_view.print_area
                crop = product_img[pa.y:pa.y+pa.height, pa.x:pa.x+pa.width]
                detected_angle = detect_perspective(crop)
                rotation = detected_angle
            except Exception:
                pass # fallback to provided rotation

        # Render
        try:
            result_img = render_design_on_product(
                product_img, design_img, x, y, width, height, rotation=rotation
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Encode response
        _, buffer = cv2.imencode('.png', result_img)
        return HttpResponse(buffer.tobytes(), content_type='image/png')
