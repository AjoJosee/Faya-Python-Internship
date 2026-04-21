document.addEventListener("DOMContentLoaded", function() {
    // Check if we are on the PrintArea page by looking for the product_view select field
    const productViewSelect = document.getElementById("id_product_view");
    if (!productViewSelect) return;

    // Create a container for the image and drawing box
    const container = document.createElement("div");
    container.id = "visual-selector-container";
    container.style.position = "relative";
    container.style.marginTop = "20px";
    container.style.marginBottom = "20px";
    container.style.display = "inline-block";
    container.style.border = "2px dashed #666";
    container.style.padding = "10px";
    container.style.backgroundColor = "#1e1e1e"; // For dark mode compatibility
    container.style.maxWidth = "600px";
    
    const title = document.createElement("h3");
    title.textContent = "Visual Print Area Selector (Click & Drag to draw)";
    title.style.marginTop = "0";
    title.style.marginBottom = "10px";
    container.appendChild(title);

    const imgContainer = document.createElement("div");
    imgContainer.style.position = "relative";
    container.appendChild(imgContainer);

    const img = document.createElement("img");
    img.id = "visual-selector-img";
    img.style.display = "none";
    img.style.maxWidth = "100%";
    img.style.height = "auto";
    img.style.userSelect = "none";
    img.style.cursor = "crosshair";
    
    const overlay = document.createElement("div");
    overlay.id = "visual-selector-box";
    overlay.style.position = "absolute";
    overlay.style.border = "2px solid #00ff00";
    overlay.style.backgroundColor = "rgba(0, 255, 0, 0.2)";
    overlay.style.display = "none";
    overlay.style.pointerEvents = "none";

    imgContainer.appendChild(img);
    imgContainer.appendChild(overlay);

    // Find the form container to insert the visual tool into
    const fieldset = document.querySelector("fieldset.module.aligned");
    if (fieldset) {
        fieldset.insertBefore(container, fieldset.firstChild);
    }

    const xInput = document.getElementById("id_x");
    const yInput = document.getElementById("id_y");
    const wInput = document.getElementById("id_width");
    const hInput = document.getElementById("id_height");

    // Fetch image URL logic using the existing products API
    async function updateImage() {
        const viewId = productViewSelect.value;
        if (!viewId) {
            img.style.display = "none";
            overlay.style.display = "none";
            return;
        }

        try {
            const response = await fetch("/api/products/");
            const products = await response.json();
            let imageUrl = null;
            for (let p of products) {
                for (let v of p.views) {
                    if (v.id == viewId) {
                        imageUrl = v.base_image;
                        break;
                    }
                }
            }
            if (imageUrl) {
                img.src = imageUrl;
                img.style.display = "block";
                img.onload = () => {
                    updateOverlayFromInputs();
                };
            } else {
                img.style.display = "none";
                overlay.style.display = "none";
            }
        } catch (e) {
            console.error("Failed to load product views for visual selector:", e);
        }
    }

    productViewSelect.addEventListener("change", updateImage);
    updateImage(); // initial load

    // Drawing logic
    let isDrawing = false;
    let startX, startY;

    img.addEventListener("mousedown", (e) => {
        isDrawing = true;
        const rect = img.getBoundingClientRect();
        startX = e.clientX - rect.left;
        startY = e.clientY - rect.top;
        
        overlay.style.display = "block";
        overlay.style.left = startX + "px";
        overlay.style.top = startY + "px";
        overlay.style.width = "0px";
        overlay.style.height = "0px";
    });

    img.addEventListener("mousemove", (e) => {
        if (!isDrawing) return;
        const rect = img.getBoundingClientRect();
        const currentX = e.clientX - rect.left;
        const currentY = e.clientY - rect.top;
        
        const x = Math.min(startX, currentX);
        const y = Math.min(startY, currentY);
        const w = Math.abs(currentX - startX);
        const h = Math.abs(currentY - startY);
        
        overlay.style.left = x + "px";
        overlay.style.top = y + "px";
        overlay.style.width = w + "px";
        overlay.style.height = h + "px";
    });

    img.addEventListener("mouseup", (e) => {
        if (!isDrawing) return;
        isDrawing = false;
        
        const rect = img.getBoundingClientRect();
        const scaleX = img.naturalWidth / rect.width;
        const scaleY = img.naturalHeight / rect.height;
        
        const currentX = e.clientX - rect.left;
        const currentY = e.clientY - rect.top;
        
        const x = Math.min(startX, currentX);
        const y = Math.min(startY, currentY);
        const w = Math.abs(currentX - startX);
        const h = Math.abs(currentY - startY);

        // Only update if they actually dragged a meaningful rectangle
        if (w > 5 && h > 5) {
            xInput.value = Math.round(x * scaleX);
            yInput.value = Math.round(y * scaleY);
            wInput.value = Math.round(w * scaleX);
            hInput.value = Math.round(h * scaleY);
        }
    });
    
    // Stop drawing if mouse leaves the image
    img.addEventListener("mouseleave", () => {
        if (isDrawing) {
            isDrawing = false;
            updateOverlayFromInputs(); // Reset to input values
        }
    });

    img.addEventListener("dragstart", (e) => e.preventDefault());

    // Sync from inputs back to visual overlay
    function updateOverlayFromInputs() {
        if (!img.naturalWidth) return;
        const x = parseInt(xInput.value) || 0;
        const y = parseInt(yInput.value) || 0;
        const w = parseInt(wInput.value) || 0;
        const h = parseInt(hInput.value) || 0;

        if (w > 0 && h > 0) {
            const rect = img.getBoundingClientRect();
            const scaleX = rect.width / img.naturalWidth;
            const scaleY = rect.height / img.naturalHeight;

            overlay.style.display = "block";
            overlay.style.left = (x * scaleX) + "px";
            overlay.style.top = (y * scaleY) + "px";
            overlay.style.width = (w * scaleX) + "px";
            overlay.style.height = (h * scaleY) + "px";
        } else {
            overlay.style.display = "none";
        }
    }

    xInput.addEventListener("input", updateOverlayFromInputs);
    yInput.addEventListener("input", updateOverlayFromInputs);
    wInput.addEventListener("input", updateOverlayFromInputs);
    hInput.addEventListener("input", updateOverlayFromInputs);
});
