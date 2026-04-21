# 🎨 Smart Product Customizer

Welcome to the **Smart Product Customizer**! This is a high-performance, production-ready web application that allows users to realistically preview their custom designs (like logos or artwork) on physical products (like t-shirts, mugs, or hoodies). 

Instead of just pasting a flat image over a photo, this system uses advanced computer vision algorithms to warp the design so it perfectly matches the lighting, shadows, folds, and perspective of the fabric!

---

## ✨ Key Features

### 🛠️ For Administrators (Store Owners)
*   **Centralized Catalog:** Manage your products through a secure, built-in Django admin dashboard.
*   **Precision Print Areas:** Define exact coordinates where designs are allowed. This prevents users from placing logos in unrealistic spots (e.g., off the edge of a sleeve).
*   **Shadow & Texture Control:** Upload product photos and let the system automatically extract texture and shadow data for photorealistic results.

### 👕 For Customers
*   **Interactive Designer:** Drag, drop, rotate, and resize your artwork in real-time.
*   **Auto-Perspective Mapping:** The system automatically detects the product's angle and tilts your design to match.
*   **High-Fidelity Renders:** Generate 4K-ready previews that look like real photography, not digital overlays.
*   **Integrated Render Gallery:** Save multiple design iterations and download them instantly in a high-quality format.

---

## ⚙️ The Technology Stack

### 🔹 Core Engine (Python + OpenCV)
The "Magic" happens in our custom-built rendering engine:
1.  **Perspective Warp:** Dynamically adjusts the design's geometry to match the camera's point of view.
2.  **Fabric Conformation:** Uses displacement mapping to bend the design's pixels into the wrinkles and folds of the fabric.
3.  **Shadow Blending:** Extracts natural environmental lighting and re-applies it over the user's design for deep integration.
4.  **Edge Softening:** Mimics the way ink bleeds into fabric fibers, avoiding the "sticker" look of traditional overlays.

### 🔹 Backend (Django & REST Framework)
*   **Robust API:** Handles image processing requests efficiently.
*   **Secure Storage:** Manages product metadata and high-resolution assets.
*   **Production Configured:** Pre-set for deployment with Gunicorn and WhiteNoise for static file serving.

### 🔹 Frontend (Modern Vanilla JS)
*   **Dark-Mode Aesthetic:** A premium, sleek interface designed for modern brands.
*   **Zero-Friction UX:** No login required for customers to start designing.
*   **Responsive Layout:** Fully functional on desktops, tablets, and mobile devices.

---

## 🔐 Security & Permissions

*   **Admin Access:** Secured by Django's robust authentication system. Only authorized staff can modify the product catalog.
*   **Public API:** The rendering endpoint is public and stateless, ensuring high performance and a frictionless user experience without compromising server security.
*   **CSRF Protection:** Integrated protection for all administrative actions.

---

## 🚀 Quick Setup Guide

### Prerequisites
*   **Python 3.10+**
*   **pip** (Python package manager)

### 1. Installation
```bash
# Clone the repository
git clone https://github.com/AjoJosee/Faya-Python-Internship.git
cd Faya-Python-Internship

# Create and activate a virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate
```

### 2. Initial Setup
```bash
# Create an admin user to access the dashboard
python manage.py createsuperuser

# Start the development server
python manage.py runserver
```

### 3. Accessing the App
*   **Customer Designer:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
*   **Admin Dashboard:** [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)

---

## 🌍 Deployment

This project is optimized for **Render.com** and includes all necessary configuration files:
*   `render.yaml`: One-click infrastructure setup.
*   `build.sh`: Automatic build and migration script.
*   `gunicorn`: Production-grade WSGI server.

**Live Demo:** [https://product-customizer-2kba.onrender.com/](https://product-customizer-2kba.onrender.com/)

---

*Developed as part of the Faya Python Internship Program.*
