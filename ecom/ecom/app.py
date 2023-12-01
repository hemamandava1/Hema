from flask import Flask, render_template, request, redirect, url_for, flash, session
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = 'your_very_secure_secret_key'

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client['grocery_store']
users = db.users
products = db.products
orders = db.orders


# Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'saitulasi1729@gmail.com'
app.config['MAIL_PASSWORD'] = 'mmsj bstu dzfa sgay'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

@app.route('/')
def index():
    # Check if user is logged in by looking for 'username' in session
    if 'username' in session:
        # Redirect to the products page if user is already logged in
        return redirect(url_for('show_products'))
    else:
        # If not logged in, redirect to the login page instead of rendering 'index.html'
        return redirect(url_for('login'))


@app.route('/add_to_wishlist/<product_id>', methods=['POST'])
def add_to_wishlist(product_id):
    if 'username' not in session:
        flash('Please log in to use the wishlist feature.', 'info')
        return redirect(url_for('login'))
    
    user = users.find_one({'username': session['username']})
    if user:
        product_id_obj = ObjectId(product_id)
        if product_id_obj not in user.get('wishlist', []):
            users.update_one({'_id': user['_id']}, {'$push': {'wishlist': product_id_obj}})
            flash('Item added to your wishlist.', 'success')
        else:
            flash('Item is already in your wishlist.', 'info')
    else:
        flash('User not found.', 'error')
    
    return redirect(request.referrer or url_for('show_products'))


@app.route('/remove_from_wishlist/<product_id>', methods=['POST'])
def remove_from_wishlist(product_id):
    if 'username' not in session:
        flash('Please log in to modify your wishlist.')
        return redirect(url_for('login'))

    # Find the user and their wishlist
    user = users.find_one({'username': session['username']})
    if user and 'wishlist' in user:
        # Remove the product from the wishlist
        new_wishlist = [item for item in user['wishlist'] if item != ObjectId(product_id)]
        users.update_one({'_id': user['_id']}, {'$set': {'wishlist': new_wishlist}})
        flash('Item removed from wishlist.', 'success')
    else:
        flash('Item not found in wishlist.', 'error')

    return redirect(url_for('wishlist'))

@app.route('/wishlist')
def wishlist():
    if 'username' not in session:
        flash('Please log in to view your wishlist.')
        return redirect(url_for('login'))
    
    user = users.find_one({'username': session['username']})
    if 'wishlist' not in user:
        # Initialize an empty wishlist if it does not exist
        users.update_one({'_id': user['_id']}, {'$set': {'wishlist': []}})
        user['wishlist'] = []
    
    wishlist_items = products.find({'_id': {'$in': user['wishlist']}})
    return render_template('wishlist.html', wishlist=wishlist_items)


@app.route('/products')
def show_products():
    if 'username' in session:
        product_list = products.find()
        return render_template('products.html', products=product_list, username=session['username'])
    else:
        return redirect(url_for('login'))  # Redirect to login if not authenticated


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        existing_user = users.find_one({'username': username})
        if existing_user is None:
            hashed_pass = generate_password_hash(password)
            users.insert_one({'username': username, 'email': email, 'password': hashed_pass})
            flash('Registration successful! Please log in.')
            return redirect(url_for('login'))
        else:
            flash('Username already exists.')
    return render_template('register.html')

import random

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Query the MongoDB database for the user
        user = users.find_one({'username': username})

        # Check if user exists and the password is correct
        if user and check_password_hash(user['password'], password):
            # Generate a random 6-digit code
            code = str(random.randint(100000, 999999))
            session['mfa_code'] = code
            session['username'] = user['username']  # Or appropriate identifier

            # Send email with the code
            msg = Message("Your Authentication Code", sender='your_email@example.com', recipients=[user['email']])
            msg.body = f"Your authentication code is: {code}"
            mail.send(msg)

            # Redirect to two-factor authentication page
            return redirect(url_for('two_factor_auth'))
        else:
            # Use flash to show invalid login message
            flash('Invalid username or password', 'error')

    # If it's a GET request or if login failed, render 'login.html'
    return render_template('login.html')


@app.route('/profile')
def profile():
    if 'username' not in session:
        flash('You must be logged in to view your profile.')
        return redirect(url_for('login'))
    user = users.find_one({'username': session['username']})
    return render_template('profile.html', username=user['username'], email=user.get('email', ''))

@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    if 'username' not in session:
        flash('You must be logged in to update your profile.')
        return redirect(url_for('login'))
    user = users.find_one({'username': session['username']})
    if request.method == 'POST':
        new_email = request.form.get('email')
        users.update_one({'username': session['username']}, {'$set': {'email': new_email}})
        flash('Profile updated successfully!')
        return redirect(url_for('profile'))
    return render_template('update_profile.html', email=user.get('email', ''))

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if 'username' not in session or not session.get('is_admin', False):
        flash('You must be an admin to add products')
        return redirect(url_for('index'))
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        image_url = request.form.get('image_url')
        products.insert_one({'name': name, 'description': description, 'price': price, 'image_url': image_url})
        flash('Product added successfully!')
    return render_template('add_product.html')

@app.route('/update_product/<product_id>', methods=['GET', 'POST'])
def update_product(product_id):
    if 'username' not in session or not session.get('is_admin', False):
        flash('You must be an admin to update products')
        return redirect(url_for('index'))
    product = products.find_one({'_id': ObjectId(product_id)})
    if request.method == 'POST':
        updates = {
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'price': request.form.get('price'),
            'image_url': request.form.get('image_url')
        }
        products.update_one({'_id': ObjectId(product_id)}, {'$set': updates})
        flash('Product updated successfully!')
        return redirect(url_for('show_products'))
    return render_template('update_product.html', product=product)

@app.route('/delete_product/<product_id>')
def delete_product(product_id):
    if 'username' not in session or not session.get('is_admin', False):
        flash('You must be an admin to delete products')
        return redirect(url_for('index'))
    products.delete_one({'_id': ObjectId(product_id)})
    flash('Product deleted successfully!')
    return redirect(url_for('show_products'))

@app.route('/add_to_cart/<product_id>', methods=['POST'])
def add_to_cart(product_id):
    # Initialize the cart in the session if it doesn't exist
    if 'cart' not in session:
        session['cart'] = []

    cart = session['cart']
    # Get the quantity from the form, defaulting to 1 if not found
    quantity = int(request.form.get('quantity', 1))

    # Check if the product is already in the cart
    product_in_cart = next((item for item in cart if item['product_id'] == product_id), None)

    if product_in_cart:
        # Increase quantity by the specified amount if product is already in the cart
        product_in_cart['quantity'] += quantity
    else:
        # Find the product in the database
        product = products.find_one({'_id': ObjectId(product_id)})
        if product:
            # Add new item to the cart with the specified quantity
            cart_item = {
                'product_id': str(product['_id']),
                'name': product['name'],
                'price': product['price'],
                'quantity': quantity  # Use the quantity from the form
            }
            cart.append(cart_item)
        else:
            # Flash message if product is not found
            flash('Product not found!', 'danger')
            return redirect(url_for('show_products'))

    # Save the updated cart in the session
    session['cart'] = cart
    session.modified = True

    # Flash message for successfully adding item to the cart
    flash(f'{quantity} item(s) added to cart!', 'success')
    return redirect(url_for('show_products'))


@app.route('/cart')
def view_cart():
    return render_template('cart.html', cart=session.get('cart', []))

@app.route('/update_cart', methods=['POST'])
def update_cart():
    cart = session.get('cart', [])
    for item in cart:
        item_quantity = request.form.get('quantity_' + item['product_id'])
        item['quantity'] = int(item_quantity) if item_quantity else item['quantity']
    session['cart'] = cart
    session.modified = True
    flash('Cart updated!')
    return redirect(url_for('view_cart'))

@app.route('/remove_from_cart/<product_id>')
def remove_from_cart(product_id):
    cart = session.get('cart', [])
    cart = [item for item in cart if item['product_id'] != product_id]
    session['cart'] = cart
    session.modified = True
    flash('Item removed from cart!')
    return redirect(url_for('view_cart'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('is_admin', None)
    flash('You have been logged out.')
    return redirect(url_for('index'))

@app.route('/create_order', methods=['POST'])
def create_order():
    if 'username' not in session:
        flash('You need to be logged in to place an order.')
        return redirect(url_for('login'))
    
    cart_items = session.get('cart', [])
    if cart_items:
        cc_name = request.form.get('cc_name')
        cc_number = request.form.get('cc_number')
        cc_expiry = request.form.get('cc_expiry')
        cc_cvv = request.form.get('cc_cvv')
        address = request.form.get('address')

        order = {
            'username': session['username'],
            'items': cart_items,
            'status': 'Processing',
            'cc_name': cc_name,
            'cc_number': cc_number,
            'cc_expiry': cc_expiry,
            'cc_cvv': cc_cvv,
            'address': address
        }
        orders.insert_one(order)
        session.pop('cart', None)
        flash('Your order has been placed.')
        return redirect(url_for('order_history'))
    else:
        flash('Your cart is empty.')
        return redirect(url_for('show_products'))

@app.route('/order_history')
def order_history():
    if 'username' not in session:
        flash('You need to be logged in to view your order history.')
        return redirect(url_for('login'))
    user_orders = orders.find({'username': session['username']})
    return render_template('order_history.html', orders=user_orders)

@app.route('/checkout')
def checkout():
    if 'username' not in session:
        flash('You must be logged in to checkout.')
        return redirect(url_for('login'))
    return render_template('checkout.html', cart=session.get('cart', []))


@app.route('/two_factor_auth', methods=['GET', 'POST'])
def two_factor_auth():
    if request.method == 'POST':
        user_code = request.form['code']
        # Compare the user entered code with the session code
        if user_code == session.get('mfa_code'):
            # Clear the MFA code from the session
            session.pop('mfa_code', None)
            # Redirect to the products page after successful MFA
            return redirect(url_for('show_products'))
        else:
            flash('Invalid authentication code', 'error')
            return redirect(url_for('login'))

    return render_template('two_factor_auth.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash('You must be logged in to access the dashboard.')
        return redirect(url_for('login'))
    
    # Get the username from the session
    username = session['username']

    # You can add more logic here to retrieve additional dashboard data if needed

    return render_template('dashboard.html', username=username)

if __name__ == '__main__':
    app.run(debug=True)
