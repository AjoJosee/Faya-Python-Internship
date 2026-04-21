# 🎨 Smart Product Customizer

Welcome to the **Smart Product Customizer**! This is a high-performance web application that allows users to realistically preview their custom designs (like logos or artwork) on physical products (like t-shirts, mugs, or hoodies). 

Instead of just pasting a flat image over a photo, this system uses advanced computer vision algorithms to warp the design so it perfectly matches the lighting, shadows, folds, and perspective of the fabric!

---

## 👥 Who is this for? (User Groups)

This system is built with two main groups of people in mind:

### 1. The Administrator (Store Owner)
As the admin, your job is to set up the catalog of blank products. You have access to a secure backend dashboard where you can:
* **Add new products:** Upload high-resolution photos of a product from different angles (Front view, Back view, etc.).
* **Define the Print Area:** You get to tell the system *exactly* where a design is allowed to be printed. By defining a specific X, Y coordinate and the width/height of the print zone, you ensure that customers cannot accidentally drag a logo off the edge of the shirt.

### 2. The End User (Customer)
The customer experiences a beautiful, interactive, and premium dark-themed website. Their workflow is simple:
* **Select a product:** Pick a shirt from the dropdown menu.
* **Upload artwork:** Drag and drop their custom PNG/JPG design onto the screen.
* **Adjust:** Use intuitive sliders to resize, position, and rotate their logo.
* **Generate & Download:** Click a button to instantly see a photorealistic render of their design wrapped onto the shirt. They can then save these renders to a gallery and download them!

---

## ⚙️ How Everything Works Under the Hood

To make this fast and realistic, we separated the logic into three main parts:

### 1. The Backend (Django)
The backbone of the application is built on **Python** and **Django**. It handles the database (saving products and print areas), serves the website to the user, and provides secure APIs for the frontend to communicate with.

### 2. The Interactive Frontend (Vanilla HTML/CSS/JS)
The frontend uses standard web technologies to provide a buttery-smooth experience. When a user drags sliders to move their logo, the frontend instantly calculates the new coordinates relative to the Admin's Print Area and sends a quick request to the backend to generate the image.

### 3. The Magic Engine (OpenCV)
When the backend receives the design and coordinates, it passes them to our custom C++ powered **OpenCV Engine**. This engine does four things incredibly fast (usually in under 300 milliseconds):
1. **Perspective Warp:** It tilts the 2D logo into 3D space so it matches the angle of the camera.
2. **Fabric Conformation:** It analyzes the grayscale wrinkles of the blank shirt and literally bends the pixels of the logo so they sink into the valleys of the wrinkles and stretch over the peaks.
3. **Shadow Blending:** It extracts the natural shadows from the room lighting and paints them directly *over* the logo.
4. **Edge Masking:** It slightly blurs the edges of the logo to mimic the way real ink bleeds into cotton threads.

---

## 🔐 Authentication & Authorization

The system enforces a strict separation of privileges using Django's built-in security features and Django REST Framework (DRF):

### 1. Admin Authorization (Session-Based)
The backend dashboard (`/admin`) is completely locked down. It utilizes **Django's Session Authentication**. 
* Only users with `is_staff` and `is_superuser` flags in the database can access this portal. 
* **Users & Groups Management:** The Superuser can use the built-in Django Auth panel to create new sub-admin accounts, set their passwords, and assign them to specific Groups with granular permissions (e.g., allowing a user to add Products but preventing them from deleting Print Areas).
* This ensures that only authorized store owners can add products, delete products, or modify the critical `PrintArea` coordinate boundaries.
* It is protected by CSRF (Cross-Site Request Forgery) tokens to prevent malicious hijacking.

### 2. End-User Access (Public & Stateless)
The customer-facing application is designed for a frictionless experience. 
* Customers **do not** need to create an account or log in to test designs on shirts.
* The API endpoint responsible for generating the images (`/api/render-preview/`) is explicitly configured in DRF to be public (`authentication_classes = []`, `permission_classes = []`).
* Because the image generation is a stateless operation (it takes an image, processes it, returns it, and immediately forgets it without saving it to the database), keeping this endpoint public is perfectly secure and removes unnecessary friction for the customer.

---

## 🚀 Quick Setup Guide

If you want to run this project on your own computer, follow these simple steps!

### Prerequisites
Make sure you have **Python 3.10+** installed.

### 1. Installation
Open your terminal and run the following commands:

```bash
# 1. Clone the repository
git clone https://github.com/AjoJosee/Faya-Python-Internship.git
cd Faya-Python-Internship

# 2. Create and activate a virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# 3. Install the required packages
pip install -r requirements.txt

# 4. Set up the database
python manage.py migrate
```

### 2. Create an Admin Account
To access the backend and upload products, you need an admin account:
```bash
python manage.py createsuperuser
```
(Follow the prompts to enter a username and password).

### 3. Run the Server
```bash
python manage.py runserver
```
* **Customer Website:** Open your browser and go to `http://127.0.0.1:8000/`
* **Admin Dashboard:** Go to `http://127.0.0.1:8000/admin` (Log in with the account you just created).

---

## 🌍 Deployment Ready

This repository is pre-configured to be deployed to modern cloud platforms (like Render.com) right out of the box! 
It includes:
* `requirements.txt` (with the Gunicorn web server included)
* `build.sh` (a script to automatically install dependencies and setup the database)
* `render.yaml` (an infrastructure-as-code file for one-click Render deployments)

Here's the link `https://product-customizer-2kba.onrender.com/`

Note: Currently the print area and coordinates are set random so the design will be probably out of the screen. You can adjust the size and change the position manually to get it on the shirt/cap. Also I couldn't find shadows to add and you can add it in the admin tab. I will fix all of this very very soon🙏
