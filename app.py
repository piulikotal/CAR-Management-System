from flask import Flask, render_template, request, session, flash, redirect, url_for
import mysql.connector
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Piuli12@.#",
    database="cardb"
)

cursor = db.cursor(dictionary=True)

# Index route
@app.route("/")
def index():
    return render_template("index.html")

# Signup route
@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/productlist")
def productlist():
    cursor.execute("SELECT * FROM product_details_new")
    cars = cursor.fetchall()
    return render_template("productlist.html", cars=cars)

@app.route("/createproduct")
def createproduct():
    return render_template("createproduct.html")

@app.route("/createproduct", methods=["POST"])
def createproduct_post():
    id = request.form.get("id")
    user_id = request.form.get("user_id")
    title = request.form.get("title")
    description = request.form.get("descriptions")
    tags = request.form.get("tags")
    images = request.files.getlist("images")

    image_paths = []
    for image in images:
        if image and image.filename:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_paths.append(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    try:
        cursor.execute(
            "INSERT INTO product_details_new (id, user_id, title, descriptions, tags, images) VALUES (%s, %s, %s, %s, %s, %s)",
            (id, user_id, title, description, tags, ','.join(image_paths))
        )
        db.commit()
        flash("Car added successfully!", "success")
        return redirect(url_for("productlist"))
    except Exception as e:
        db.rollback()
        flash(f"An error occurred: {e}", "danger")
        return redirect(url_for("createproduct"))

# Edit car details route (No image option)
@app.route("/edit_car/<int:car_id>", methods=["GET","POST"])
def edit_car(car_id):
    # Fetch the existing car details
    cursor.execute("SELECT * FROM product_details_new WHERE id = %s", (car_id,))
    car = cursor.fetchone()
    
    if not car:
        return "Car not found", 404

    if request.method == "POST":
        # Get the updated description and tags from the form
        title = request.form.get("title")
        description = request.form.get("descriptions")
        tags = request.form.get("tags")

        try:
            # Update only the title, description, and tags in the database
            cursor.execute(
                "UPDATE product_details_new SET title = %s, descriptions = %s, tags = %s WHERE id = %s",
                (title, description, tags, car_id)
            )
            db.commit()
            flash("Car details updated successfully!", "success")
            return redirect(url_for("productlist"))
        except Exception as e:
            db.rollback()
            flash(f"An error occurred: {e}", "danger")
            return redirect(url_for("edit_car", car_id=car_id))

    # Render the edit car page with the current car details
    return render_template("edit_car.html", car=car)

# Delete car route
@app.route("/delete_car/<int:car_id>", methods=["POST"])
def delete_car(car_id):
    cursor.execute("SELECT * FROM product_details_new WHERE id = %s", (car_id,))
    car = cursor.fetchone()

    if not car:
        return "Car not found", 404

    try:
        cursor.execute("DELETE FROM product_details_new WHERE id = %s", (car_id,))
        db.commit()
        flash("Car deleted successfully!", "success")
        return redirect(url_for("productlist"))
    except Exception as e:
        db.rollback()
        flash(f"An error occurred: {e}", "danger")
        return redirect(url_for("productlist"))

# Signup form handling
@app.route("/signupform", methods=["POST"])
def signup_form():
    id = request.form["id"]
    password = request.form["password"]
    username = request.form["username"]
    email = request.form["email"]

    cursor.execute(
        "INSERT INTO signup (id,password,username,email) VALUES (%s,%s, %s, %s)",
        (id, password, username, email)
    )
    db.commit()

    return "Signup successful!"

# Product Detail route
@app.route("/productdetail", methods=["GET", "POST"])
@app.route("/productdetail/<int:car_id>", methods=["GET"])
def productdetail(car_id=None):
    cursor = db.cursor(dictionary=True)

    if car_id:
        cursor.execute("SELECT * FROM product_details_new WHERE id = %s", (car_id,))
        car = cursor.fetchone()

        if not car:
            return "Car not found", 404

        return render_template("productdetail.html", car=car)

    cursor.execute("SELECT * FROM product_details_new")
    cars = cursor.fetchall()

    return render_template("productdetail.html", cars=cars)

if __name__ == "__main__":
    app.run(debug=True)
