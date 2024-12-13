from flask import Flask, render_template, request, session, flash, redirect, url_for,send_file,jsonify,send_from_directory,make_response
import mysql.connector
import os 
from PIL import Image
from werkzeug.utils import secure_filename
import base64  # To decode BLOB data into a format usable by HTM
import io
from io import BytesIO
app = Flask(__name__)


#app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB limit

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Define the function to establish a database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",  # Your MySQL server address
        user="root",       # Your MySQL username
        password="Piuli12@.#",  # Your MySQL password
        database="cardb"  # The name of the database you're using
    )

def db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Piuli12@.#",
        database="cardb"
    )
    return connection




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
@app.route("/merge")
def merge():
    return render_template("merge.html")

@app.route("/photo")
def photo():
    return render_template("photo.html")

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
    image = request.files.getlist("image")

    image_paths = []
    for image in image:
        if image and image.filename:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_paths.append(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    try:
        cursor.execute(
            "INSERT INTO product_details_new (id, user_id, title, descriptions, tags, image) VALUES (%s, %s, %s, %s, %s, %s)",
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

cursor = db.cursor()

# Signup form handling




# Signup form handling
@app.route("/signupform", methods=["POST"])
def signupform():
    try:
        # Get form data
        id = request.form["id"]
        password = request.form["password"]
        username = request.form["username"]
        email = request.form["email"]

        # Connect to the database and execute query
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO signup (id, password, username, email) VALUES (%s, %s, %s, %s)",
            (id, password, username, email)
        )
        db.commit()
        cursor.close()
        db.close()

        return "Signup successful!"
    except Exception as e:
        return f"An error occurred: {e}"

# Product Detail route
#@app.route("/productdetail", methods=["GET", "POST"])
#@app.route("/productdetail/<int:car_id>", methods=["GET"])
#def productdetail(car_id=None):
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






# Folder to store uploaded images (not used for BLOB storage but needed for saving image temporarily if needed)
UPLOAD_FOLDER = 'static/assets'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#photo upload
# Route to handle image upload@app.route('/upload', methods=['POST'])
@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Validate MIME type
    if file.content_type not in ['image/jpeg', 'image/jpg']:
        return jsonify({'error': 'Invalid file format. Only JPEG is supported.'}), 400

    if file:
        try:
            name = secure_filename(file.filename)
            image_binary = file.read()

            # Connect to the database and store the image
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO image (name, image_path) VALUES (%s, %s)",
                (name, image_binary)
            )
            conn.commit()
            cursor.close()
            conn.close()

            return jsonify({'message': 'Image uploaded successfully!'}), 200
    
        except Exception as e:
            print("Error while uploading image:", str(e))  # Log the error for debugging
            return jsonify({'error': f'Error while uploading image: {str(e)}'}), 500

    return jsonify({'error': 'Unexpected error occurred!'}), 500


# Route to serve the latest uploaded image
@app.route('/latest_image', methods=['GET'])
def latest_image():
    try:
        # Fetch the latest image from the database
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT image_path, name FROM image ORDER BY id DESC LIMIT 1"
        cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result:
            # Send the binary image data as a response
            image_binary = result['image_path']
            return send_file(
                io.BytesIO(image_binary),
                mimetype="image/jpeg",  # Adjust MIME type based on your image format
                as_attachment=False,
                download_name=result['name']
            )
        else:
            return jsonify({'error': 'No images found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    



# Example: Fetch 5-6 car images from the database
@app.route('/advertisements', methods=['GET'])
def fetch_advertisement_images():
    # Connect to your database and fetch 5-6 images
    connection = db_connection()  # Replace with your DB connection logic
    cursor = connection.cursor()
    query = "SELECT image_id, name, image_path FROM image LIMIT 12"
    cursor.execute(query)
    rows = cursor.fetchall()

    # Prepare the response with images
    image = []
    for row in rows:
        image_id = row[0]
        name = row[1]
        image_data = row[2]
        image_url = f"/image/{image_id}"  # You may add logic to serve images directly
        image.append({"id": image_id, "name": name, "url": image_url})

    return jsonify(image)   

@app.route('/image/<int:image_id>', methods=['GET'])
def get_image(image_id):
    connection = db_connection()  # Replace with your DB connection logic
    cursor = connection.cursor()
    query = "SELECT image_path FROM image WHERE image_id = %s"
    cursor.execute(query, (image_id,))
    row = cursor.fetchone()
    if row:
        return send_file(io.BytesIO(row[0]), mimetype='image/jpeg')
    else:
        return "Image not found", 404





# Route to create a product and upload images
@app.route('/merge', methods=['GET', 'POST'])
def merge_page():
    if request.method == 'POST':
        try:
            db_connection = mysql.connector.connect(**db_config)
            cursor = db_connection.cursor()

            # Extract car details from the form
            car_id = request.form['id']
            user_id = request.form['user_id']
            title = request.form['title']
            descriptions = request.form['descriptions']
            tags = request.form['tags']
            image= request.files.getlist('image')

            # Insert car details into the product_details_new table
            cursor.execute("""
                INSERT INTO product_details_new (car_id, user_id, title, descriptions, tags)
                VALUES (%s, %s, %s, %s, %s)
            """, (car_id, user_id, title, descriptions, tags))
            db_connection.commit()

            # Insert images into the image table
            for image in image:
                if image.filename != '':
                    filename = secure_filename(image.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    image.save(filepath)

                    with open(filepath, 'rb') as file:
                        image_blob = file.read()

                    cursor.execute("""
                        INSERT INTO image (car_id, name, image_path)
                        VALUES (%s, %s, %s)
                    """, (car_id, filename, image_blob))
                    db_connection.commit()

            cursor.close()
            db_connection.close()
            return jsonify({'message': 'Car And Image uploaded successfully!'}), 200

        except Exception as e:
            return jsonify({'error': str(e)})

    # If GET request, render the merge.html page
    return render_template('merge.html')
 # Render the same page with the success/error message and car data
    

# Route to fetch car details along with their associated images
@app.route('/merge/cars')
def get_merged_cars():
    try:
        db_connection = mysql.connector.connect(**db_config)
        cursor = db_connection.cursor(dictionary=True)

        # Fetch merged car details and images
        query = """
            SELECT 
                p.car_id, p.title, p.descriptions, p.tags, 
                i.image_id, i.name
            FROM product_details_new p
            LEFT JOIN image i ON p.car_id = i.car_id
        """
        cursor.execute(query)
        cars = cursor.fetchall()

        cursor.close()
        db_connection.close()

        # Pass the merged data to the template
        return render_template('merge.html', cars=cars)

    except Exception as e:
        return jsonify({'error': str(e)})
    
# Route to fetch the latest uploaded image@app.route('/latest_uploaded_image', methods=['GET'])
# if multiple show is not working then enable this and set limit 1
@app.route('/last_uploaded_image', methods=['GET'])
def last_uploaded_image():
    try:
        # Fetch the latest image from the database
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT image_path, name FROM image ORDER BY image_id DESC LIMIT 1"
        cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result:
            # Send the binary image data as a response
            image_binary = result['image_path']
            return send_file(
                io.BytesIO(image_binary),
                mimetype="image/jpeg",  # Adjust MIME type based on your image format
                as_attachment=False,
                download_name=result['name']
            )
        else:
            return jsonify({'error': 'No images found'}), 404
    except Exception as e:
        print("Error in last_uploaded_image:", str(e))
        return jsonify({'error': str(e)}), 500





#multiple photo showing
#@app.route('/last_uploaded_image', methods=['GET'])
#def last_uploaded_image():
    try:
        # Fetch the latest 5 images from the database
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT image_path, name FROM image ORDER BY id DESC LIMIT 5"
        cursor.execute(query)
        results = cursor.fetchall()  # Fetch all 5 rows
        cursor.close()
        conn.close()

        if results:
            # Return the images as a JSON response
            images = [
                {
                    'name': result['name'],
                    'image_path': f"data:image/jpeg;base64,{base64.b64encode(result['image_path']).decode('utf-8')}"
                } for result in results
            ]
            return jsonify({'images': images}), 200
        else:
            return jsonify({'error': 'No images found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/productdetail')
def productdetail():
    connection = get_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT 
            product_details_new.car_id, 
            product_details_new.user_id, 
            product_details_new.title, 
            product_details_new.descriptions, 
            product_details_new.tags, 
            image.image_path
        FROM 
            product_details_new 
        LEFT JOIN 
            image ON product_details_new.car_id = image.car_id;
        """
        cursor.execute(query)
        cars = cursor.fetchall()

        for car in cars:
            if car['image_path']:
                image_filename = f"car_{car['car_id']}.jpg"
                image_path = os.path.join('static/assets', image_filename)

                # Write the BLOB data to the assets directory
                try:
                    with open(image_path, 'wb') as image_file:
                        image_file.write(car['image_path'])
                    car['image_path'] = f'assets/{image_filename}'  # Relative to static
                except Exception as e:
                    print(f"Error saving image for Car ID {car['car_id']}: {e}")
                    car['image_path'] = None  # Skip on error

        print("Fetched Cars Data:", cars)  # Debugging: Verify data
    except Exception as e:
        print(f"Error fetching data: {e}")
        cars = []
    finally:
        cursor.close()
        connection.close()

    return render_template('productdetail.html', cars=cars)




@app.route('/image/<car_id>')
def serve_image(car_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        # Get image filename from database
        query = "SELECT image_path FROM image WHERE car_id = %s"
        cursor.execute(query, (car_id,))
        result = cursor.fetchone()

        if result and result['image_path']:
            # Return the image from the static folder
            image_filename = result['image_path']
            return send_from_directory('static/images', image_filename)
        else:
            return "Image not found", 404

    except Exception as e:
        
        return f"Error fetching image: {e}", 500
    finally:
        connection.close()

#@app.route("/search", methods=["GET"])
#def search():
    query = request.args.get("query")
    if not query:
        return "Error: No search query provided", 400
    # Execute SQL query to search for cars
    cursor.execute(
        "SELECT * FROM product_details_new WHERE title LIKE %s OR descriptions LIKE %s OR user_id LIKE %s OR tags LIKE %s",
        (
            "%" + query + "%",
            "%" + query + "%",
            "%" + query + "%",
            "%" + query + "%",
        ),
    )
    result = cursor.fetchall()

    return render_template("searchcar.html", result=result)

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        search_query = request.form.get("search_query")
        
        if search_query:
            # Query to search the product_details_new table based on the search_query
            cursor.execute("SELECT * FROM product_details_new WHERE title LIKE %s OR descriptions LIKE %s OR tags LIKE %s", 
                           ('%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%'))
            cars = cursor.fetchall()  # Fetch the cars matching the search query
            
            return render_template("searchcar.html", cars=cars)  # Pass the cars data to the template
        else:
            return render_template("searchcar.html", cars=[])
    
    return render_template("searchcar.html", cars=[])

if __name__ == "__main__":
    app.run(debug=True)
