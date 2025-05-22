# Spargen E-Commerce Website

Spargen is a full-featured e-commerce web application built with Flask. It allows users to browse, search, and purchase products online, while sellers can manage their products and view orders. The platform supports user authentication, shopping cart, order management, and a modern UI with dark mode.

## Features

- User registration and login (Seller & Consumer roles)
- Product listing with images, categories, and search functionality
- Shopping cart and checkout with multiple payment methods
- Seller dashboard for product management
- Consumer dashboard for order tracking and profile management
- Profile editing with photo upload
- Responsive design with dark mode support

## User Roles

### Admin
- Access the admin dashboard(for admin there is a unique email id:as6294389@gmail.com and password:admin123)
- View platform analytics (total sales, users, products, orders)
- View and manage all users (deactivate accounts)
- View and manage all products (remove products)
- View and update all orders (change order status)
- See top-selling products
- Full control over the platform

### Seller
- Register as a seller
- Add, edit, and remove products
- Upload product images and videos
- View all listed products

### Consumer
- Register as a consumer
- Browse and search products
- Add products to cart and checkout
- Track orders and manage profile

## Project Structure

```
app.py
models.py
requirements.txt
static/
    css/
    images/
    js/
    uploads/
templates/
    base.html
    index.html
    login.html
    register.html
    seller_dashboard.html
    consumer_dashboard.html
    product.html
    cart.html
    payment.html
    ...
instance/
    ecommerce.db
migrations/
    ...
```

## How to Run

1. **Clone the repository:**
   ```sh
   git clone https://github.com/Ashutosh6294389/E-Commerce-Website.git
   cd E-Commerce-Website
   ```

2. **Create a virtual environment and activate it:**
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```sh
   pip install flask flask_sqlalchemy flask_migrate
   ```

4. **Set up the database:**
   ```sh
   flask db upgrade
   ```

5. **Run the application:**
   ```sh
   python app.py
   ```

6. **Open your browser and go to when  you see this link in terminal:**
   ```
   http://127.0.0.1:5000/
   ```


## License

This project is for educational purposes.

---

**Developed by Ashutosh Singh**