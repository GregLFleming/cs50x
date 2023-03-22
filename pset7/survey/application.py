import cs50
import csv

from flask import Flask, jsonify, redirect, render_template, request

# Configure application
app = Flask(__name__)

# Reload templates when they are changed
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.after_request
def after_request(response):
    """Disable caching"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET"])
def get_index():
    return redirect("/form")

@app.route("/form", methods=["GET"])
def get_form():
    return render_template("form.html")


@app.route("/form", methods=["POST"])
def post_form():

    # import registrant info
    firstname = request.form.get("firstname")
    lastname = request.form.get("lastname")
    academy = request.form.get("academy")
    age = request.form.get("age")
    belt = request.form.get("belt")
    weight = request.form.get("weight")
    gender = request.form.get("gender")

    # check that forms are complete
    if not firstname:
        return render_template("error.html", message="First Name Required!")
    if not lastname:
        return render_template("error.html", message="Last Name Required!")
    if not academy:
        return render_template("error.html", message="Academy Required")
    if not age:
        return render_template("error.html", message="Age Required!")
    if not belt:
        return render_template("error.html", message="Belt Required!")
    if not weight:
        return render_template("error.html", message="Weight Required!")
    if not gender:
        return render_template("error.html", message="Gender Selection Required!")

    file = open("survey.csv","a")
    writer = csv.writer(file)
    writer.writerow((firstname, lastname, gender, age, belt, weight, academy))
    file.close()
    return redirect("/sheet")


@app.route("/sheet", methods=["GET"])
def get_sheet():
    file = open("survey.csv","r")
    reader = csv.reader(file)
    competitors = list(reader)
    file.close()
    return render_template("competitor_list.html", competitors = competitors)
