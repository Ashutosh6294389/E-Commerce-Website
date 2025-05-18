from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from models import Product, User, db, Order, OrderItem
import os
from werkzeug.utils import secure_filename
from flask_migrate import Migrate
from datetime import timedelta


UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure database
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(days=7)  # Session lasts for 7 days
db.init_app(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/product/<int:product_id>')
def product(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product.html', product=product)

@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        # Handle product creation
        name = request.form['name']
        price = request.form['price']
        description = request.form['description']
        new_product = Product(name=name, price=price, description=description)
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for('admin'))
    products = Product.query.all()
    return render_template('admin.html', products=products)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session.permanent = True  # Make the session permanent
            session['user_id'] = user.id
            session['role'] = user.role
            session['username'] = user.username
            if user.role == 'seller':
                return redirect(url_for('seller_dashboard'))
            elif user.role == 'consumer':
                return redirect(url_for('consumer_dashboard'))
        else:
            flash("Invalid email or password. Please try again.")
    return render_template('login.html')

@app.route('/seller_dashboard')
def seller_dashboard():
    if 'user_id' in session and session.get('role') == 'seller':
        user = User.query.get(session['user_id'])  # Fetch the logged-in seller's details
        products = Product.query.all()  # Fetch all products (or filter by seller if needed)
        return render_template('seller_dashboard.html', user=user, products=products)
    return redirect(url_for('login'))

# ...existing code...
@app.route('/consumer_dashboard')
def consumer_dashboard():
    if 'user_id' in session and session.get('role') == 'consumer':
        user = User.query.get(session['user_id'])
        cart_items = session.get('cart', [])
        orders = Order.query.filter_by(user_id=user.id).order_by(Order.date.desc()).all()
        return render_template('consumer_dashboard.html', user=user, orders=orders, cart_items=cart_items)
    return redirect(url_for('login'))
# ...existing code...

@app.route('/register_choice')
def register_choice():
    return render_template('register_choice.html')


@app.route('/register/<role>', methods=['GET', 'POST'])
def register(role):
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        # Check if the email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered. Please log in.")
            return redirect(url_for('login'))
        # Create a new user
        if role in ['seller', 'consumer']:
            new_user = User(email=email, username=username, password=password, role=role)
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful! Please log in.")
            return redirect(url_for('login'))
    return render_template('register.html', role=role)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        user.email = request.form['email']
        user.username = request.form['username']
        # Handle password change
        if request.form['password']:
            user.password = request.form['password']
        # Handle photo upload
        if 'photo' in request.files:
            file = request.files['photo']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                user.photo = f'uploads/{filename}'
        db.session.commit()
        flash("Profile updated successfully!")
        if session.get('role') == 'seller':
            return redirect(url_for('seller_dashboard'))
        elif session.get('role') == 'consumer':
            return redirect(url_for('consumer_dashboard'))
    return render_template('edit_profile.html', user=user)

@app.route('/add_product', methods=['POST'])
def add_product():
    if 'user_id' not in session or session.get('role') != 'seller':
        return redirect(url_for('login'))

    name = request.form['name']
    price = request.form['price']
    description = request.form['description']
    category = request.form['category']

    # Handle image uploads
    image_files = request.files.getlist('images')
    image_paths = []
    for file in image_files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_paths.append(f'uploads/{filename}')

    # Handle video upload
    video_file = request.files.get('video')
    video_path = None
    if video_file and allowed_file(video_file.filename):
        filename = secure_filename(video_file.filename)
        video_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        video_path = f'uploads/{filename}'

    # Create a new product
    new_product = Product(
        name=name,
        price=price,
        description=description,
        images=','.join(image_paths),
        video=video_path,
        category=category
    )
    db.session.add(new_product)
    db.session.commit()
    flash("Product added successfully!")
    return redirect(url_for('seller_dashboard'))

@app.route('/remove_product/<int:product_id>', methods=['POST'])
def remove_product(product_id):
    if 'user_id' not in session or session.get('role') != 'seller':
        return redirect(url_for('login'))
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash("Product removed successfully!")
    return redirect(url_for('seller_dashboard'))

@app.route('/logout')
def logout():
    # Clear the session to log the user out
    session.clear()
    flash("You have been logged out successfully.")
    return redirect(url_for('login'))

@app.route('/search')
def search():
    query = request.args.get('query', '').strip()
    if query:
        # Search for products matching the query
        products = Product.query.filter(Product.name.ilike(f'%{query}%')).all()
        return render_template('search_results.html', products=products, query=query)
    flash("Please enter a search term.")
    return redirect(url_for('index'))

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'user_id' not in session:
        flash("Please log in to add items to your cart.")
        return redirect(url_for('login'))

    # Fetch the product
    product = Product.query.get_or_404(product_id)

    # Get the quantity from the form
    quantity = int(request.form.get('quantity', 1))  # Default to 1 if not provided

    # Initialize the cart in the session if not already present
    if 'cart' not in session:
        session['cart'] = []

    # Check if the product is already in the cart
    for item in session['cart']:
        if item['id'] == product.id:
            # If the product is already in the cart, update the quantity
            item['quantity'] += quantity
            session.modified = True
            flash(f"Updated quantity for {product.name} in your cart.")
            return redirect(url_for('cart'))

    # Ensure the image path is valid
    image_path = product.images.split(',')[0] if product.images else 'images/default-product.jpg'

    # Add the product to the cart
    session['cart'].append({
        'id': product.id,
        'name': product.name,
        'price': float(product.price),
        'quantity': quantity,  # Use the specified quantity
        'image': image_path  # First image or default
    })
    session.modified = True  # Mark session as modified to save changes

    flash(f"{product.name} has been added to your cart.")
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    if 'cart' in session:
        session['cart'] = [item for item in session['cart'] if item['id'] != product_id]
        session.modified = True
        flash("Item removed from your cart.")
    return redirect(url_for('cart'))

@app.route('/checkout')
def checkout():
    if 'cart' not in session or not session['cart']:
        flash("Your cart is empty.")
        return redirect(url_for('index'))
    # Implement payment logic here
    flash("Checkout successful!")
    session.pop('cart', None)  # Clear the cart after checkout
    return redirect(url_for('index'))

@app.route('/update_cart/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    if 'cart' in session:
        for item in session['cart']:
            if item['id'] == product_id:
                # Update the quantity
                item['quantity'] = int(request.form['quantity'])
                session.modified = True
                flash(f"Updated quantity for {item['name']} in your cart.")
                break
    return redirect(url_for('cart'))


@app.route('/payment', methods=['GET', 'POST'])
def payment():
    if 'user_id' not in session or 'cart' not in session or not session['cart']:
        flash("Your cart is empty.")
        return redirect(url_for('cart'))
    cart_items = session['cart']
    cart_total = sum(item['price'] * item['quantity'] for item in cart_items)
    if request.method == 'POST':
        address = request.form['address']
        payment_method = request.form['payment_method']
        total = cart_total
        # Create order
        order = Order(
            user_id=session['user_id'],
            address=address,
            payment_method=payment_method,
            status='Pending',
            total=total
        )
        db.session.add(order)
        db.session.commit()
        # Add order items
        for item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item['id'],
                name=item['name'],
                price=item['price'],
                quantity=item['quantity'],
                image=item['image']
            )
            db.session.add(order_item)
        db.session.commit()
        session.pop('cart', None)
        flash("Order placed successfully!")
        return redirect(url_for('consumer_dashboard'))
    return render_template('payment.html', cart_items=cart_items, cart_total=cart_total)


@app.route('/buy_now/<int:product_id>', methods=['GET', 'POST'])
def buy_now(product_id):
    if 'user_id' not in session:
        flash("Please log in to buy products.")
        return redirect(url_for('login'))

    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        quantity = int(request.form.get('quantity', 1))
        address = request.form['address']
        payment_method = request.form['payment_method']
        total = product.price * quantity

        # Create order
        order = Order(
            user_id=session['user_id'],
            address=address,
            payment_method=payment_method,
            status='Pending',
            total=total
        )
        db.session.add(order)
        db.session.commit()

        # Add order item
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            name=product.name,
            price=product.price,
            quantity=quantity,
            image=product.images.split(',')[0] if product.images else 'images/default-product.jpg'
        )
        db.session.add(order_item)
        db.session.commit()

        flash("Order placed successfully!")
        return redirect(url_for('consumer_dashboard'))

    # GET request: get quantity from query params
    quantity = int(request.args.get('quantity', 1))
    return render_template('payment.html', product=product, quantity=quantity, buy_now=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)