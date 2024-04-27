import psycopg2
from flask import Flask, render_template, request, redirect, session, g, flash

app = Flask(__name__, static_folder="static")
app.secret_key = "my-secret-key"


def connect_db():
    """establishing connection with database"""
    conn = psycopg2.connect(
        database="test_database",
        user="test_user",
        password="test@123",
        host="127.0.0.1",
        port="5432",
    )
    cur = conn.cursor()
    return conn, cur


@app.before_request
def before_request():
    # Initialize the g object with is_authenticated and user information
    g.is_authenticated = False
    g.user = None
    if session.get("user_id") is not None:
        conn, cur = connect_db()
        cur.execute(
            "SELECT id, email FROM microcam.user_details WHERE id = %s",
            (session["user_id"],),
        )
        user = cur.fetchone()
        cur.close()
        conn.close()
        if user is not None:
            g.is_authenticated = True
            g.user = {"id": user[0], "email": user[1]}


@app.route("/")
def home():
    return render_template("html/index.html")


@app.route("/alert")
def alert():
    return render_template("html/alert.html")


@app.route("/about")
def about():
    return render_template("html/about.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        message = request.form["message"]

        # Insert the contact form data into the database
        conn, cur = connect_db()
        cur.execute(
            "INSERT INTO microcam.contact_us (name, email, message) VALUES (%s, %s, %s)",
            (name, email, message),
        )
        conn.commit()
        cur.close()
        conn.close()
        flash("Thank you for contacting us!","success")
        flash("We have received your request and will get back to you as soon as possible.","success")
        return redirect("/alert")

    return render_template("html/contact.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # Check if the user is already logged in
    if g.get("is_authenticated"):
        return redirect("/profile")

    if request.method == "POST":
        # Extract the login information from the form
        email = request.form["email"]
        password = request.form["password"]

        # Check if the user exists in the database and the password is correct
        conn, cur = connect_db()
        cur.execute(
            "SELECT id, email, password FROM microcam.user_details WHERE email = %s",
            (email,),
        )
        user = cur.fetchone()
        cur.close()
        conn.close()
        if user and (user[2] == password):
            # Set the user's information in the session
            session.clear()
            session["user_id"] = user[0]
            session["user_email"] = user[1]
            # Redirect to the dashboard page
            return redirect("/dashboard")

        # Display an error message if the login information is incorrect
        flash("Incorrect email or password", "error")

    return render_template("html/login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        phone = request.form["phone"]
        address = request.form["address"]
        city = request.form["city"]
        country = request.form["country"]

        # Check if the email is already in use
        conn, cur = connect_db()
        cur.execute(
            "SELECT email FROM microcam.user_details WHERE email = %s", (email,)
        )
        user = cur.fetchone()
        if user:
            flash("Email already in use. Please choose a different one.", "error")
            return redirect("/alert")

        # Insert the new user into the database
        cur.execute(
            "INSERT INTO microcam.user_details (name, email, password, phone, address, city, country) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id;",
            (name, email, password, phone, address, city, country),
        )
        user_id=cur.fetchone()
        conn.commit()

        # Store the user's information in the session and redirect to their profile page
        session.clear()
        session["user_id"] = user_id[0]
        session["user_email"] = email
        cur.close()
        conn.close()
        return redirect("/profile")

    return render_template("html/signup.html")


@app.route("/profile", methods=["GET", "POST"])
def profile():
    # Check if the user is logged in
    if not g.get("is_authenticated"):
        return redirect("/login")

    # Retrieve the user's information from the database
    conn, cur = connect_db()
    cur.execute(
        "SELECT * FROM microcam.user_details WHERE id = %s", (g.user["id"],)
    )
    user_details = cur.fetchone()
    cur.close()
    conn.close()

    if request.method == "POST":
        # Check if the user clicked the logout button
        if request.form.get("action") == "logout":
            session.clear()
            return redirect("/login")

        # Check if the user clicked the change password button
        elif request.form.get("action") == "change_password":
            old_password = request.form["old_password"]
            new_password = request.form["new_password"]
            confirm_password = request.form["confirm_password"]

            # Check if the credentials are correct
            if user_details[3] == old_password and new_password == confirm_password:
                # Update the user's password in the database
                conn, cur = connect_db()
                cur.execute(
                    "UPDATE microcam.user_details SET password = %s WHERE id = %s",
                    (new_password, g.user["id"]),
                )
                conn.commit()
                cur.close()
                conn.close()
                flash("Password changed successfully", "success")
            else:
                flash("Incorrect credentials", "error")

        # Check if the user clicked the update profile button
        elif request.form.get("action") == "update_profile":
            name = request.form["name"]
            phone = request.form["phone"]
            address = request.form["address"]
            city = request.form["city"]
            country = request.form["country"]

            # Update the user's information in the database
            conn, cur = connect_db()
            cur.execute(
                "UPDATE microcam.user_details SET name = %s, phone = %s, address = %s, city = %s, country = %s, updated_at = now() WHERE id = %s",
                (name, phone, address, city, country, g.user["id"]),
            )
            conn.commit()
            cur.close()
            conn.close()
            flash("Profile updated successfully", "success")
            return redirect("/profile")

    return render_template("html/profile.html", user_details=user_details)


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    # Initialize the image variable
    image = None
    details = None
    #image = None
    #image = None

    # Check if the user is logged in
    if not g.get("is_authenticated"):
        return redirect("/login")

    # If an image ID is specified, retrieve the image details from the database
    image_id = request.args.get("image_id")
    if image_id:
        conn, cur = connect_db()
        cur.execute(
            "SELECT * FROM microcam.images WHERE id = %s AND user_id = %s",
            (image_id, g.user["id"]),
        )
        image = cur.fetchone()
        cur.close()
        conn.close()
        if image:
            # If the user is sharing the image with another user, insert the share into the shares table
            if request.method == "POST" and request.form.get("action") == "share_image":
                share_email = request.form.get("share_email")
                conn, cur = connect_db()
                cur.execute(
                    "SELECT id FROM microcam.user_details WHERE email = %s",
                    (share_email,),
                )
                share_user = cur.fetchone()
                if share_user:
                    cur.execute(
                        "INSERT INTO microcam.image_shares (image_id, user_id) VALUES (%s, %s)",
                        (image_id, share_user[0]),
                    )
                    conn.commit()
                    flash("Image shared successfully", "success")
                else:
                    flash("User not found", "error")
                cur.close()
                conn.close()

            # If the user is entering the image details, insert the details into the images table
            elif request.method == "POST" and request.form.get("action") == "enter_details":
                name = request.form.get("name")
                description = request.form.get("description")
                date = request.form.get("date")
                conn, cur = connect_db()
                cur.execute(
                    "UPDATE microcam.images SET name = %s, description = %s, date = %s WHERE id = %s",
                    (name, description, date, image_id),
                )
                conn.commit()
                cur.close()
                conn.close()
                flash("Image details saved successfully", "success")

            # If the user is editing the image details, update the details in the images table
            elif request.method == "POST" and request.form.get("action") == "edit_details":
                name = request.form.get("name")
                description = request.form.get("description")
                date = request.form.get("date")
                conn, cur = connect_db()
                cur.execute(
                    "UPDATE microcam.images SET name = %s, description = %s, date = %s WHERE id = %s",
                    (name, description, date, image_id),
                )
                conn.commit()
                cur.close()
                conn.close()
                flash("Image details updated successfully", "success")

            # Retrieve the image details from the database
            conn, cur = connect_db()
            cur.execute(
                "SELECT name, description, date FROM microcam.images WHERE id = %s",
                (image_id,),
            )
            details = cur.fetchone()
            cur.close()
            conn.close()

    # If no image ID is specified, display the capture image and save image sections
    else:
        # If the user is capturing an image, save the image data to the images table
        if request.method == "POST" and request.form.get("action") == "save_image":
            image_data = request.form.get("image")
            name = request.form.get("name")
            description = request.form.get("description")
            date = request.form.get("date")
            conn, cur = connect_db()
            cur.execute(
                "INSERT INTO microcam.images (user_id, filename, name, description, date) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                (g.user["id"], "", name, description, date),
            )
            image_id = cur.fetchone()[0]
            cur.execute(
                "UPDATE microcam.images SET filename = %s WHERE id = %s",
                ("image_" + str(image_id) + ".png", image_id),
            )
            conn.commit()
            cur.close()
            conn.close()
            with open("static/uploads/image_" + str(image_id) + ".png", "wb") as f:
                f.write(base64.b64decode(image_data.split(",")[1]))
            flash("Image saved successfully", "success")

        # Retrieve the user's images from the database
        conn, cur = connect_db()
        cur.execute(
            "SELECT id, filename FROM microcam.images WHERE user_id = %s",
            (g.user["id"],),
        )
        images = cur.fetchall()
        cur.close()
        conn.close()

        # Retrieve the images shared with the user from the database
        conn, cur = connect_db()
        cur.execute(
            "SELECT * FROM microcam.image_shares JOIN microcam.images ON microcam.image_shares.image_id = microcam.images.id WHERE microcam.image_shares.user_id = %s",
            (g.user["id"],),
        )
        shared_images = cur.fetchall()
        cur.close()
        conn.close()

    return render_template(
        "html/dashboard.html",
        image=image,
        details=details,
        images=images,
        shared_images=shared_images,
    )

#@app.route("/dashboard")
#def dashboard():
    # Check if the user is logged in
#    if not g.get("is_authenticated"):
#        return redirect("/login")
#    
#    return render_template("html/dashboard.html")


if __name__ == "__main__":
    app.run(debug=True)   #for development and debugging mode
    #app.run(debug=False)  #for production mode
