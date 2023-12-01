from pymongo import MongoClient

# Establish a connection to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['grocery_store']

# Create or get the 'products' collection
products = db.products

# Sample products data
sample_products = [
    {"name": "Apples", "description": "Fresh apples from the farm", "price": 1.20, "image_url": "/static/images/apples.jpg"},
    {"name": "Bananas", "description": "Chiquita bananas (Bundle of 5)", "price": 0.99, "image_url": "/static/images/bananas.jpg"},
    {"name": "Carrots", "description": "Organic carrots (Pack of 3)", "price": 1.50, "image_url": "/static/images/carrots.jpg"},
    {"name": "Tomatoes", "description": "Juicy red tomatoes (1lb)", "price": 2.00, "image_url": "/static/images/tomatoes.jpg"},
    {"name": "Lettuce", "description": "Green lettuce", "price": 0.99, "image_url": "/static/images/lettuce.jpg"},
    {"name": "Chicken Breast", "description": "Boneless chicken breast (1lb)", "price": 3.99, "image_url": "/static/images/chicken_breast.jpg"},
    {"name": "Ground Beef", "description": "Ground beef (1lb)", "price": 5.49, "image_url": "/static/images/ground_beef.jpg"},
    {"name": "Oranges", "description": "Sweet and juicy oranges (Pack of 4)", "price": 3.99, "image_url": "/static/images/oranges.jpg"},
    {"name": "Grapes", "description": "Seedless grapes (1lb)", "price": 2.99, "image_url": "/static/images/grapes.jpg"},
    {"name": "Blueberries", "description": "Fresh blueberries (1 pint)", "price": 3.99, "image_url": "/static/images/blueberries.jpg"},
    {"name": "Strawberries", "description": "Organic strawberries (1lb)", "price": 4.99, "image_url": "/static/images/strawberries.jpg"},
    {"name": "Milk", "description": "Whole milk (1 gallon)", "price": 2.49, "image_url": "/static/images/milk.jpg"},
    {"name": "Eggs", "description": "Free-range eggs (1 dozen)", "price": 2.99, "image_url": "/static/images/eggs.jpg"},
    {"name": "Bread", "description": "Whole wheat bread", "price": 2.99, "image_url": "/static/images/bread.jpg"},
    {"name": "Butter", "description": "Unsalted butter (8oz)", "price": 1.99, "image_url": "/static/images/butter.jpg"},
    {"name": "Cheese", "description": "Cheddar cheese (8oz)", "price": 3.99, "image_url": "/static/images/cheese.jpg"},
    {"name": "Yogurt", "description": "Greek yogurt (5.3oz)", "price": 0.99, "image_url": "/static/images/yogurt.jpg"},
    {"name": "Spinach", "description": "Fresh spinach leaves (5oz)", "price": 2.99, "image_url": "/static/images/spinach.jpg"},
    {"name": "Potatoes", "description": "Russet potatoes (5lb bag)", "price": 3.49, "image_url": "/static/images/potatoes.jpg"},
    {"name": "Onions", "description": "Yellow onions (1lb)", "price": 1.29, "image_url": "/static/images/onions.jpg"}
]

# Insert products into the collection
products.delete_many({})  # Clear out existing products
products.insert_many(sample_products)

print("Products inserted into the database!")
