import cs50
import csv
import sys
from cs50 import SQL

from flask import Flask, jsonify, redirect, render_template, request, g

# Configure application
app = Flask(__name__)

# Reload templates when they are changed
app.config["TEMPLATES_AUTO_RELOAD"] = True

#configure for sqlite
db = SQL("sqlite:///moveset.db")

technique_list = db.execute("SELECT technique_name from technique_list")
guard_list = db.execute("SELECT guard_name from guard_list")
guard_name = "Select a Position"
category = "Select a Category"
technique_name = "Select a Technique"

@app.after_request
def after_request(response):
    """Disable caching"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods=["GET"])
def get_index():
    return redirect("/home")

@app.route("/home", methods=["GET"])
def get_home():
    global guard_name
    global category
    global technique_name
    global technique_list

    guard_name = "Select a Position"
    category = "Select a Category"
    technique_name = "Select a Technique"
    technique_list = db.execute("SELECT technique_name from technique_list")

    return render_template("home.html", technique_list=technique_list, guard_list=guard_list, guard_name=guard_name, category = category, technique_name = technique_name)

@app.route("/home", methods=["POST"])
def post_home():

    global guard_name
    global category
    global technique_name
    global technique_list
    global guard_list

    guard_name = request.form.get("guard_name")
    category = request.form.get("category")
    technique_name = request.form.get("technique_name")
    guard_list = db.execute("SELECT guard_name from guard_list")
    technique_list = db.execute("SELECT technique_name from technique_list")

    if guard_name=="Add a new Position":
        return redirect("/guard_entry")

    if guard_name and guard_name!="Select a technique" and guard_name!="Add a new Position":
        #guard selected
        technique_list = db.execute("SELECT technique_name from technique_list WHERE technique_position = :guard_name", guard_name = guard_name)
        if category and category!="Select a Technique":
            #guard selected and category selected
            technique_list = db.execute("SELECT technique_name from technique_list WHERE technique_position=:guard_name and technique_category = :category", guard_name = guard_name, category = category)
        if not technique_name:
            #guard selected and technique not selected
            return redirect("/guard")


    if category and category!="Select a Technique":
        #category selected
        technique_list = db.execute("SELECT technique_name from technique_list WHERE technique_category = :category", category = category)
        if guard_name and guard_name!="Select a technique" and guard_name!="Add a new Position":
            #category and guard selected
            technique_list = db.execute("SELECT technique_name from technique_list WHERE technique_position=:guard_name and technique_category = :category", guard_name = guard_name, category = category)
            if technique_name == "Add a new Technique":
                return redirect("/technique_entry")

    if technique_name  and technique_name == "Add a new Technique":
        return render_template("error.html", message="Position and Category MUST be selected before a new technique may be entered!! Redirecting in 3 seconds...")


    if technique_name and technique_name !="Select a technique" and technique_name!="Add a new Technique":
        #Technique selected
        return redirect("/technique")

    return render_template("home.html", technique_list=technique_list, guard_list=guard_list, guard_name=guard_name, category = category, technique_name = technique_name)

@app.route("/technique_entry", methods=["GET"])
def get_technique_entry():
    global guard_name
    global category
    global technique_name

    return render_template("technique_entry.html", technique_list = technique_list, guard_list = guard_list, guard_name = guard_name, category = category, technique_name = technique_name)

@app.route("/technique_entry", methods=["POST"])
def post_technique_entry():
    global guard_name
    global category
    global technique_name

    # import new technique fields from new technique page
    technique_name = request.form.get("technique_name")
    attack_description = request.form.get("attack_description")
    attack_end_position = request.form.get("attack_end_position")
    attack_demonstration = request.form.get("attack_demonstration")
    defense_description = request.form.get("defense_description")
    defense_end_position = request.form.get("defense_end_position")
    defense_demonstration = request.form.get("defense_demonstration")
    technique_position = guard_name
    technique_category = category

    # check that forms were completed

    if not technique_name:
        return render_template("error.html", message="Technique Name Required!")
    if not attack_description:
        attack_description = "Entry not complete! Help by filling this field."
    if not attack_end_position:
        attack_end_position = "N/A"
    if not attack_demonstration:
        attack_demonstration = "URL not provided! Help by adding a youtube link"
    if not defense_description:
        defense_description = "Entry not complete! Help by filling this field."
    if not defense_end_position:
        defense_end_position = "N/A"
    if not defense_demonstration:
        defense_demonstration = "URL not provided! Help by adding a youtube link"

    #create a new entry in the technique database
    db.execute("INSERT INTO technique_list (technique_name, attack_description, attack_end_position, attack_demonstration, defense_description, defense_end_position, defense_demonstration, technique_position, technique_category) VALUES(:technique_name, :attack_description, :attack_end_position, :attack_demonstration, :defense_description, :defense_end_position, :defense_demonstration, :technique_position, :technique_category)", technique_name=technique_name, attack_description=attack_description, attack_end_position=attack_end_position, attack_demonstration=attack_demonstration, defense_description=defense_description, defense_end_position=defense_end_position, defense_demonstration=defense_demonstration, technique_position=technique_position, technique_category=technique_category)

    return redirect("/home")

@app.route("/guard_entry", methods=["GET"])
def get_guard_entry():

    return render_template("guard_entry.html", guard_list = guard_list, technique_list = technique_list)

@app.route("/guard_entry", methods=["POST"])
def post_guard_entry():

    # import new technique fields from new technique page
    guard_name = request.form.get("guard_name")
    top_description = request.form.get("top_description")
    top_demonstration = request.form.get("top_demonstration")
    bottom_description = request.form.get("bottom_description")
    bottom_demonstration = request.form.get("bottom_demonstration")

    # check that forms were completed

    if not guard_name:
        return render_template("error.html", message="Position Name Required!")
    if not top_description:
        top_description = "Entry not complete! Help by filling this field."
    if not top_demonstration:
        top_demonstration = "URL not provided! Help by adding a youtube link"
    if not bottom_description:
        bottom_description = "Entry not complete! Help by filling this field."
    if not bottom_demonstration:
        bottom_demonstration = "URL not provided! Help by adding a youtube link"

    #create a new entry in the guard database
    db.execute("INSERT INTO guard_list (guard_name, top_description, top_demonstration, bottom_description, bottom_demonstration) VALUES(:guard_name, :top_description, :top_demonstration, :bottom_description, :bottom_demonstration)", guard_name=guard_name, top_description=top_description, top_demonstration=top_demonstration, bottom_description=bottom_description, bottom_demonstration=bottom_demonstration)

    return redirect("/home")

@app.route("/technique", methods=["GET"])
def get_technique():
    global guard_name
    global category
    global technique_name

    technique = db.execute("SELECT * from technique_list WHERE technique_name = :technique_name", technique_name = technique_name)
    technique[0]["attack_demonstration"] = technique[0]["attack_demonstration"].replace("youtu.be","www.youtube.com/embed")
    technique[0]["defense_demonstration"] = technique[0]["defense_demonstration"].replace("youtu.be","www.youtube.com/embed")

    return render_template("technique.html", technique = technique[0], technique_list = technique_list, guard_list = guard_list, guard_name = guard_name, category = category, technique_name = technique_name)

@app.route("/technique", methods=["POST"])
def post_technique():



    return redirect("/home")

@app.route("/guard", methods=["GET"])
def get_guard():
    global guard_name
    global category
    global technique_name

    guard = db.execute("SELECT * from guard_list WHERE guard_name = :guard_name", guard_name = guard_name)
    guard[0]["top_demonstration"] = guard[0]["top_demonstration"].replace("youtu.be","www.youtube.com/embed")
    guard[0]["bottom_demonstration"] = guard[0]["bottom_demonstration"].replace("youtu.be","www.youtube.com/embed")

    return render_template("guard.html", guard = guard[0], technique_list = technique_list, guard_list = guard_list, guard_name = guard_name, category = category, technique_name = "Select a Technique")

@app.route("/guard", methods=["POST"])
def post_guard():
    return redirect("/home")

@app.route("/technique_edit", methods=["GET"])
def get_technique_edit():
    global guard_name
    global category
    global technique_name

    technique = db.execute("SELECT * from technique_list WHERE technique_name = :technique_name", technique_name = technique_name)

    return render_template("technique_edit.html", technique = technique[0], technique_list = technique_list, guard_list = guard_list, guard_name = guard_name, category = category, technique_name = technique_name)

@app.route("/technique_edit", methods=["POST"])
def post_technique_edit():
    global guard_name
    global category
    global technique_name

    # import new technique fields from new technique page

    attack_description = request.form.get("attack_description")
    attack_end_position = request.form.get("attack_end_position")
    attack_demonstration = request.form.get("attack_demonstration")
    defense_description = request.form.get("defense_description")
    defense_end_position = request.form.get("defense_end_position")
    defense_demonstration = request.form.get("defense_demonstration")

    # check that forms were completed

    if not attack_description:
        attack_description = "Entry not complete! Help by filling this field."
    if not attack_end_position:
        attack_end_position = "N/A"
    if not attack_demonstration:
        attack_demonstration = "URL not provided! Help by adding a youtube link"
    if not defense_description:
        defense_description = "Entry not complete! Help by filling this field."
    if not defense_end_position:
        defense_end_position = "N/A"
    if not defense_demonstration:
        defense_demonstration = "URL not provided! Help by adding a youtube link"

    #update entry in database
    db.execute("UPDATE technique_list SET attack_description = :attack_description, attack_end_position = :attack_end_position, attack_demonstration = :attack_demonstration, defense_description = :defense_description, defense_end_position = :defense_end_position, defense_demonstration = :defense_demonstration WHERE technique_name = :technique_name", technique_name = technique_name, attack_description = attack_description, attack_end_position = attack_end_position, attack_demonstration = attack_demonstration, defense_description = defense_description, defense_end_position = defense_end_position, defense_demonstration = defense_demonstration)

    return redirect("/home")

@app.route("/guard_edit", methods=["GET"])
def get_guard_edit():

    guard = db.execute("SELECT * from guard_list WHERE guard_name = :guard_name", guard_name = guard_name)

    return render_template("guard_edit.html", guard = guard[0], guard_list = guard_list, technique_list = technique_list)

@app.route("/guard_edit", methods=["POST"])
def post_guard_edit():

    # import new technique fields from new technique page
    top_description = request.form.get("top_description")
    top_demonstration = request.form.get("top_demonstration")
    bottom_description = request.form.get("bottom_description")
    bottom_demonstration = request.form.get("bottom_demonstration")

    # check that forms were completed

    if not top_description:
        top_description = "Entry not complete! Help by filling this field."
    if not top_demonstration:
        top_demonstration = "URL not provided! Help by adding a youtube link"
    if not bottom_description:
        bottom_description = "Entry not complete! Help by filling this field."
    if not bottom_demonstration:
        bottom_demonstration = "URL not provided! Help by adding a youtube link"

    #update entry in the guard database
    db.execute("UPDATE guard_list SET top_description = :top_description, top_demonstration = :top_demonstration, bottom_description = :bottom_description, bottom_demonstration = :bottom_demonstration WHERE guard_name = :guard_name", guard_name = guard_name, top_description = top_description, top_demonstration = top_demonstration, bottom_description = bottom_description, bottom_demonstration = bottom_demonstration)

    return redirect("/home")

@app.route("/guard/<position_link>")
def testroute(position_link):
    global guard_name
    global category
    global technique_name
    global technique_list

    guard_name = position_link
    technique_list = db.execute("SELECT technique_name from technique_list WHERE technique_position = :guard_name", guard_name = guard_name)

    return redirect("/guard")
