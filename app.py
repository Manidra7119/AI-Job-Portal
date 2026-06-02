from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "jobportal_secret_key"

db = mysql.connector.connect(
    host="localhost",
    user="jobuser",
    password="job123",
    database="ai_job_portal"
)

cursor = db.cursor()

print("Database Connected Successfully!")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        sql = "SELECT * FROM users WHERE email=%s AND password=%s"
        values = (email, password)

        cursor.execute(sql, values)
        user = cursor.fetchone()

        if user:
            session["user"] = email
            return redirect("/dashboard")
        else:
            return "Invalid Email or Password"

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    return render_template("dashboard.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        fullname = request.form["fullname"]
        email = request.form["email"]
        password = request.form["password"]

        sql = "INSERT INTO users (fullname, email, password) VALUES (%s, %s, %s)"
        values = (fullname, email, password)

        cursor.execute(sql, values)
        db.commit()

        return "Registration Successful!"

    return render_template("register.html")


@app.route("/add-job", methods=["GET", "POST"])
def add_job():
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        job_title = request.form["job_title"]
        company_name = request.form["company_name"]
        location = request.form["location"]
        salary = request.form["salary"]

        sql = "INSERT INTO jobs (job_title, company_name, location, salary) VALUES (%s, %s, %s, %s)"
        values = (job_title, company_name, location, salary)

        cursor.execute(sql, values)
        db.commit()

        return redirect("/jobs")

    return render_template("add_job.html")


@app.route("/jobs")
def jobs():
    if "user" not in session:
        return redirect("/login")

    search = request.args.get("search")

    if search:
        sql = """
        SELECT * FROM jobs
        WHERE job_title LIKE %s
        OR company_name LIKE %s
        OR location LIKE %s
        """
        value = "%" + search + "%"
        cursor.execute(sql, (value, value, value))
    else:
        cursor.execute("SELECT * FROM jobs")

    jobs = cursor.fetchall()
    return render_template("jobs.html", jobs=jobs)


@app.route("/edit-job/<int:id>", methods=["GET", "POST"])
def edit_job(id):
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        job_title = request.form["job_title"]
        company_name = request.form["company_name"]
        location = request.form["location"]
        salary = request.form["salary"]

        sql = """
        UPDATE jobs
        SET job_title=%s,
            company_name=%s,
            location=%s,
            salary=%s
        WHERE id=%s
        """
        values = (job_title, company_name, location, salary, id)

        cursor.execute(sql, values)
        db.commit()

        return redirect("/jobs")

    cursor.execute("SELECT * FROM jobs WHERE id=%s", (id,))
    job = cursor.fetchone()

    return render_template("edit_job.html", job=job)


@app.route("/delete-job/<int:id>")
def delete_job(id):
    if "user" not in session:
        return redirect("/login")

    sql = "DELETE FROM jobs WHERE id=%s"
    values = (id,)

    cursor.execute(sql, values)
    db.commit()

    return redirect("/jobs")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True, port=5001)