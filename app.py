import os
import pandas as pd
from flask import Flask, render_template, request, flash, redirect, url_for

from database import get_connection

app = Flask(__name__)
app.secret_key = "simple-secret-key"

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
REQUIRED_COLUMNS = ["name", "email", "age"]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/uploads", methods=["POST"])
def upload():
    if "excel_file" not in request.files:
        flash("No file was selected.")
        return redirect(url_for("index"))

    file = request.files["excel_file"]

    if file.filename == "":
        flash("No file was selected.")
        return redirect(url_for("index"))

    
    if not file.filename.endswith(".xlsx"):
        flash("Please upload a .xlsx Excel file.")
        return redirect(url_for("index"))

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    try:
        data = pd.read_excel(filepath)
    except Exception:
        flash("Could not read the Excel file. Make sure it is a valid .xlsx file.")
        return redirect(url_for("index"))

    for column in REQUIRED_COLUMNS:
        if column not in data.columns:
            flash("Missing required column: " + column)
            return redirect(url_for("index"))

    if len(data) == 0:
        flash("The Excel file is empty.")
        return redirect(url_for("index"))

    valid_rows = []          
    rejected_rows = []       
    seen_emails_in_file = [] 
    connection = get_connection()
    cursor = connection.cursor()

    for index_in_file, row in data.iterrows():
        excel_row_number = index_in_file + 2

        name = row["name"]
        email = row["email"]
        age = row["age"]
        if pd.isna(name) or str(name).strip() == "":
            rejected_rows.append((excel_row_number, "Name is required"))
            continue

        if pd.isna(email) or str(email).strip() == "":
            rejected_rows.append((excel_row_number, "Email is required"))
            continue

        if pd.isna(age):
            rejected_rows.append((excel_row_number, "Age is required"))
            continue
        name = str(name).strip()
        email = str(email).strip()

        try:
            age = int(age)
        except ValueError:
            rejected_rows.append((excel_row_number, "Age must be an integer"))
            continue

        if email in seen_emails_in_file:
            rejected_rows.append((excel_row_number, "Duplicate email in file"))
            continue

        cursor.execute("SELECT id FROM people WHERE email = %s", (email,))
        existing_person = cursor.fetchone()
        if existing_person is not None:
            rejected_rows.append((excel_row_number, "Email already exists in database"))
            continue

        seen_emails_in_file.append(email)
        valid_rows.append((name, email, age))

    for name, email, age in valid_rows:
        cursor.execute(
            "INSERT INTO people (name, email, age) VALUES (%s, %s, %s)",
            (name, email, age)
        )

    connection.commit()
    cursor.close()
    connection.close()

    os.remove(filepath)

    return render_template(
        "result.html",
        inserted_count=len(valid_rows),
        rejected_rows=rejected_rows
    )


if __name__ == "__main__":
    app.run(debug=True)
