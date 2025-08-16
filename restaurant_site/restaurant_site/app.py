# app.py
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Dummy login/signup navigation
@app.route('/')
def home():
    return render_template("home.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('menu'))
    return render_template("login.html")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        return redirect(url_for('login'))
    return render_template("signup.html")

# Dish list shown on /menu
@app.route('/menu')
def menu():
    dishes = [
        {"id": "1", "name": "Margherita Pizza", "price": 200, "image": "margherita.jpg"},
        {"id": "2", "name": "Veg Burger", "price": 120, "image": "burger.jpg"},
        {"id": "3", "name": "Cheese Sandwich", "price": 100, "image": "sandwich.jpg"},
        {"id": "4", "name": "Paneer Tikka", "price": 180, "image": "tikka.jpg"},
        {"id": "5", "name": "Gulab Jamun", "price": 80, "image": "gulab.jpg"},
    ]
    return render_template("menu.html", dishes=dishes)

# Handle order and display bill
@app.route('/order', methods=['POST'])
def order():
    selected_ids = request.form.getlist('dish')
    dish_map = {
        "1": ("Margherita Pizza", 200),
        "2": ("Veg Burger", 120),
        "3": ("Cheese Sandwich", 100),
        "4": ("Paneer Tikka", 180),
        "5": ("Gulab Jamun", 80),
    }

    ordered_items = [(dish_map[id][0], dish_map[id][1]) for id in selected_ids if id in dish_map]
    total = sum(price for _, price in ordered_items)

    return render_template("bill.html", orders=ordered_items, total=total)

if __name__ == '__main__':
    app.run(debug=True)
