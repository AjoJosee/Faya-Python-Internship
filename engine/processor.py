import cv2
import numpy as np

def perspective_warp(design: np.ndarray, rotation: float = 0) -> np.ndarray:
    h, w = design.shape[:2]
    rotation = max(-45, min(45, rotation))
    
    src_points = np.float32([[0, 0], [w, 0], [0, h], [w, h]])
    tilt_offset = int(h * 0.15 * (rotation / 45.0))
    dst_points = np.float32([[tilt_offset, 0], [w - tilt_offset, 0], [0, h], [w, h]])
    
    matrix = cv2.getPerspectiveTransform(src_points, dst_points)
    warped = cv2.warpPerspective(design, matrix, (w, h))
    return warped

def create_displacement_map(product_crop: np.ndarray) -> tuple:
    h, w = product_crop.shape[:2]
    if len(product_crop.shape) == 3 and product_crop.shape[2] == 4:
        gray = cv2.cvtColor(product_crop[:, :, :3], cv2.COLOR_BGR2GRAY)
    elif len(product_crop.shape) == 3:
        gray = cv2.cvtColor(product_crop, cv2.COLOR_BGR2GRAY)
    else:
        gray = product_crop
        
    gray_smooth = cv2.GaussianBlur(gray, (5, 5), 1.0)
    sobelx = cv2.Sobel(gray_smooth, cv2.CV_32F, 1, 0, ksize=3)
    sobely = cv2.Sobel(gray_smooth, cv2.CV_32F, 0, 1, ksize=3)
    magnitude = np.sqrt(sobelx**2 + sobely**2)
    
    magnitude = (magnitude / (magnitude.max() + 1e-5) * 50).astype(np.float32)
    magnitude = np.clip(magnitude, -5, 5)
    
    mapx = np.zeros((h, w), dtype=np.float32)
    mapy = np.zeros((h, w), dtype=np.float32)
    
    for i in range(h):
        for j in range(w):
            dx, dy = sobelx[i, j], sobely[i, j]
            norm = np.sqrt(dx**2 + dy**2) + 1e-5
            dx_norm, dy_norm = dx / norm, dy / norm
            disp = magnitude[i, j]
            mapx[i, j] = j + dx_norm * disp
            mapy[i, j] = i + dy_norm * disp
            
    mapx = np.clip(mapx, 0, w - 1).astype(np.float32)
    mapy = np.clip(mapy, 0, h - 1).astype(np.float32)
    return mapx, mapy

def apply_wrinkle_displacement(design: np.ndarray, mapx: np.ndarray, mapy: np.ndarray) -> np.ndarray:
    if design.shape[2] == 4:
        bgr = design[:, :, :3]
        alpha = design[:, :, 3]
        remapped = cv2.remap(bgr, mapx, mapy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        remapped_alpha = cv2.remap(alpha, mapx, mapy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        result = np.dstack([remapped, remapped_alpha])
    else:
        result = cv2.remap(design, mapx, mapy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return result

def extract_shadow_map(product_crop: np.ndarray, strength: float = 0.08) -> np.ndarray:
    if len(product_crop.shape) == 3 and product_crop.shape[2] == 4:
        gray = cv2.cvtColor(product_crop[:, :, :3], cv2.COLOR_BGR2GRAY)
    elif len(product_crop.shape) == 3:
        gray = cv2.cvtColor(product_crop, cv2.COLOR_BGR2GRAY)
    else:
        gray = product_crop
        
    gray_inv = 255 - gray
    shadow = (gray_inv * strength) + (255 * (1 - strength))
    shadow = shadow.astype(np.uint8)
    shadow_map = np.stack([shadow, shadow, shadow], axis=2)
    return shadow_map

def apply_shadow_blend(design: np.ndarray, shadow_map: np.ndarray) -> np.ndarray:
    h, w = design.shape[:2]
    if design.shape[2] == 4:
        rgb = design[:, :, :3]
        alpha = design[:, :, 3:4]
    else:
        rgb = design
        alpha = np.ones((h, w, 1), dtype=np.uint8) * 255
        
    if shadow_map.shape != rgb.shape:
        shadow_map = cv2.resize(shadow_map, (w, h))
        
    blended = (rgb.astype(np.float32) * shadow_map.astype(np.float32) / 255).astype(np.uint8)
    
    if design.shape[2] == 4:
        result = np.dstack([blended, alpha])
    else:
        result = blended
    return result

def apply_edge_mask(design: np.ndarray, blur_radius: int = 5) -> np.ndarray:
    if design.shape[2] != 4:
        return design
    
    alpha = design[:, :, 3]
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    alpha_dilated = cv2.dilate(alpha, kernel, iterations=1)
    edge_mask = alpha_dilated - alpha
    
    blur_radius = max(1, min(blur_radius, 10))
    blurred_alpha = cv2.GaussianBlur(alpha, (blur_radius * 2 + 1, blur_radius * 2 + 1), 0)
    result_alpha = np.where(edge_mask > 0, blurred_alpha, alpha)
    
    result = design.copy()
    result[:, :, 3] = result_alpha.astype(np.uint8)
    return result

def detect_perspective(product_crop: np.ndarray) -> float:
    """Automatically detect perspective rotation using contour analysis."""
    if len(product_crop.shape) >= 3:
        gray = cv2.cvtColor(product_crop, cv2.COLOR_BGR2GRAY)
    else:
        gray = product_crop
        
    _, thresh = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        c = max(contours, key=cv2.contourArea)
        rect = cv2.minAreaRect(c)
        angle = rect[-1]
        if angle > 45:
            angle = 90 - angle
        return min(max(angle, -45), 45)
    return 0.0

def precalculate_product_maps(product_crop: np.ndarray):
    """Precalculates displacement and shadow maps for a print area."""
    mapx, mapy = create_displacement_map(product_crop)
    shadow_map = extract_shadow_map(product_crop)
    return mapx, mapy, shadow_map

def render_design_on_product(
    product_image: np.ndarray,
    design_image: np.ndarray,
    x: int, y: int, width: int, height: int,
    rotation: float = 0,
    mapx: np.ndarray = None,
    mapy: np.ndarray = None,
    shadow_map: np.ndarray = None
) -> np.ndarray:
    if product_image.shape[2] == 4:
        product_image = cv2.cvtColor(product_image, cv2.COLOR_BGRA2BGR)
        
    design_resized = cv2.resize(design_image, (width, height), interpolation=cv2.INTER_LANCZOS4)
    
    # 1. Perspective alignment
    design_warped = perspective_warp(design_resized, rotation)
    
    x1, y1 = max(0, x), max(0, y)
    x2, y2 = min(product_image.shape[1], x + width), min(product_image.shape[0], y + height)
    product_crop = product_image[y1:y2, x1:x2].copy()
    
    # 2. Fabric conformation (wrinkles)
    if mapx is not None and mapy is not None:
        if mapx.shape[:2] != design_warped.shape[:2]:
            mapx = cv2.resize(mapx, (x2-x1, y2-y1))
            mapy = cv2.resize(mapy, (x2-x1, y2-y1))
        design_warped = apply_wrinkle_displacement(design_warped, mapx, mapy)
    
    # 3. Realistic blending (shadows and edges)
    if shadow_map is None:
        shadow_map = extract_shadow_map(product_crop, strength=0.08)
    design_shadowed = apply_shadow_blend(design_warped, shadow_map)
    design_final = apply_edge_mask(design_shadowed)
    
    # Composite onto product
    composite = product_image.copy()
    if design_final.shape[2] == 4:
        design_bgr = design_final[:, :, :3]
        alpha = design_final[:, :, 3:4].astype(np.float32) / 255.0
    else:
        design_bgr = design_final
        alpha = np.ones((design_final.shape[0], design_final.shape[1], 1), dtype=np.float32)
        
    product_region = composite[y1:y2, x1:x2].astype(np.float32)
    design_region = design_bgr.astype(np.float32)
    
    blended = (1 - alpha) * product_region + alpha * design_region
    composite[y1:y2, x1:x2] = np.clip(blended, 0, 255).astype(np.uint8)
    
    return composite
