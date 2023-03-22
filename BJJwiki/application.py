import cs50
import csv
import sys
import math


from cs50 import SQL
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
# from flask_mail import Mail, Message
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from itsdangerous import URLSafeTimedSerializer
from email.mime.text import MIMEText

# Configure application
app = Flask(__name__)

# Configure session
app.config['DEBUG'] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = mkdtemp()
#cofigure mail
# app.config['MAIL_SERVER'] = 'smtp.gmail.com'
# app.config['MAIL_PORT'] = 465
# app.config['MAIL_USE_SSL'] = True
# app.config['MAIL_USERNAME'] = 'gfleming223@gmail.com'
# app.config['MAIL_PASSWORD'] = 'jumble13'
# app.config['MAIL_DEFAULT_SENDER'] = 'gfleming223@gmail.com'


Session(app)
#configure email server
# mail=Mail(app)
s=URLSafeTimedSerializer('SHakeyB0neS97')

# Reload templates when they are changed
app.config["TEMPLATES_AUTO_RELOAD"] = True

#configure for sqlite
db = SQL("sqlite:///moveset.db")

# Ensure responses aren't cached
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

@app.route("/home", methods=["GET", "POST"])
def home():

    session["technique_list"] = db.execute("SELECT name, MAX(score), id, position, category from technique_list GROUP BY name ORDER BY name ASC")
    session["guard_list"] = db.execute("SELECT name, MAX(score), id from guard_list GROUP BY name ORDER BY name ASC")
    session["guard"] = [None]
    session["technique"] = [None]
    session["current_route"] = request.path
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User entered route by submitting a field
    if request.method == "POST":

        #Ensure that the desired username field was filled
        if not request.form.get("username"):
            return render_template("redirect.html", message="Desired username field must be filled", status = "error", redirect_path = "/register")

        # ensure that the desired password field was filled
        if not request.form.get("password"):
            return render_template("redirect.html", message="Desired password field must be filled", status = "error", redirect_path = "/register")

        #ensure that the confirm password field was filled
        if not request.form.get("confirmation"):
            return render_template("redirect.html", message="Confirm password field must be filled", status = "error", redirect_path = "/register")

        # ensure that the email field was filled
        if not request.form.get("email"):
            return render_template("redirect.html", message="email field must be filled", status = "error", redirect_path = "/register")

        #ensure that the password fields match
        if request.form.get("password") != request.form.get("confirmation"):
            return render_template("redirect.html", message="Passwords must match!", status = "error", redirect_path = "/register")

        #ensure that the password field is at least 6 characters long
        if len(request.form.get("password")) < 6:
            return render_template("redirect.html", message="Passwords must be at least 6 characters!", status = "error", redirect_path = "/register")

        #get user name
        username = request.form.get("username")
        email = request.form.get("email")

        #check if the username is available
        unique_ID_check = db.execute("SELECT * FROM user_list WHERE username = :username", username = username)

        #check if hashed email has been used
        unique_email_check = db.execute("SELECT * FROM user_list WHERE email = :email", email = email)
        if unique_email_check:
            return render_template("redirect.html", message="email already registered!!!", status = "error", redirect_path = "/register")

        if not unique_ID_check:
            hashed_password = generate_password_hash(request.form.get("password"))
            db.execute("INSERT INTO user_list (username, password, email) VALUES(:username,:password,:email)", username = request.form.get("username"),password = hashed_password, email=email)

            # Remember which user has logged in
            rows = db.execute("SELECT * FROM user_list WHERE username = :username", username=request.form.get("username"))
            session["user_id"] = rows[0]["id"]
            session["username"] = rows[0]["username"]
            session["user"] = rows[0]
            session["known_techniques"] = db.execute("SELECT * FROM known_techniques WHERE user_id=:user_id", user_id=session.get("user_id"))
            #generate token and email the user a unique email confirmation code
            # token = s.dumps(email)
            # msg = Message("Email Confirmation", sender = "gfleming223@gmail.com", recipients=[email])
            # link = url_for('email_confirmation', token=token, _external=True)
            # msg.body = "Your confirmation link is {}".format(link)
            # mail.send(msg)

            return render_template("redirect.html", message="Successfully registered, redirecting in 3 seconds...", status = "success", redirect_path = session.get("current_route"))
        else:
            return render_template("redirect.html", message="Username already registered!!!", status = "error", redirect_path = "/register")

    return render_template("register.html")

@app.route("/email_confirmation/<token>")
def email_confirmation(token):
    """Confirm user's email"""
    try:
        email = s.loads(token, max_age=3600)
    except:
        return render_template("redirect.html", message="Your verificaiton link has expired!!!", status = "error", redirect_path = "/register")
    db.execute("UPDATE user_list SET verified=:verified WHERE email=:email", verified=1, email=email)

    return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("redirect.html", message="must provide username", status = "error", redirect_path = "/login")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("redirect.html", message="must provide password", status = "error", redirect_path = "/login")

        # Query database for username
        rows = db.execute("SELECT * FROM user_list WHERE username = :username", username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1:
            return render_template("redirect.html", message="Username not found, redirecting in 3 seconds...", status = "error", redirect_path = "/login")
        if not check_password_hash(rows[0]["password"], request.form.get("password")):
            return render_template("redirect.html", message="Password incorrect, redirecting in 3 seconds...", status = "error", redirect_path = "/login")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]
        session["user"] = rows[0]
        session["known_techniques"] = db.execute("SELECT * FROM known_techniques WHERE user_id=:user_id", user_id=session.get("user_id"))

        # Redirect user to previous page
        return render_template("redirect.html", message="Successfully signed in, redirecting in 3 seconds...", status = "success", redirect_path = session.get("current_route"))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # msg = Message('Hey There', recipients=['flemdog13@hotmail.com'])
        # print(msg)
        # mail.send(msg)
    return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()
    session["technique_list"] = db.execute("SELECT name, MAX(score), id from technique_list GROUP BY name ORDER BY name ASC")
    session["guard_list"] = db.execute("SELECT name, MAX(score), id from guard_list GROUP BY name ORDER BY name ASC")
    session["guard"] = [None]
    session["technique"] = [None]

    session["current_route"] = "/home"


    # Redirect user to home page
    return render_template("redirect.html", message="Logged out, redirecting in 3 seconds...", status = "success", redirect_path = "/home")

@app.route("/profile", methods=["GET", "POST"])
def profile():
    """Display user profile"""

    #identify the top contributions made by the user
    submissions_known = db.execute("SELECT *, MAX(weighted_score) FROM known_techniques Inner Join technique_list on known_techniques.technique_id=technique_list.id WHERE user_id=:user_id AND category=:submission GROUP BY technique_id", user_id = session.get("user_id"), submission = "Submission")
    top_contributions = db.execute("SELECT id, name, score, type FROM technique_list WHERE username=:username UNION ALL SELECT id, name, score, type FROM guard_list WHERE username=:username ORDER BY score DESC LIMIT 5", username=session.get("username"))

    techniques_known = db.execute("SELECT *, MAX(weighted_score) FROM known_techniques Inner Join technique_list on known_techniques.technique_id=technique_list.id WHERE user_id=:user_id GROUP BY technique_id", user_id = session.get("user_id"))
    positions_known = db.execute("SELECT *, MAX(weighted_score) FROM known_guards Inner Join guard_list on known_guards.guard_id=guard_list.id WHERE user_id=:user_id GROUP BY guard_id", user_id = session.get("user_id"))

    if request.method == "POST":
        if request.form.get("belt_submitted") and request.form.get("submission"):
            print("a submission was entered")
        if request.form.get("session_time"):
            print("a session time was entered")

    session["current_route"] = request.path

    return render_template("profile.html", submissions_known = submissions_known, top_contributions=top_contributions, techniques_known=techniques_known, positions_known=positions_known)

@app.route("/profile/<position_link>")
def profile_visit(position_link):
    username_visit = position_link
    visit_id = db.execute("SELECT id FROM user_list WHERE username=:username", username=username_visit)[0]["id"]
    user_visit=db.execute("SELECT username, score FROM user_list WHERE username=:username", username=username_visit)[0]


    #identify the top contributions made by the user
    submissions_known = db.execute("SELECT *, MAX(weighted_score) FROM known_techniques Inner Join technique_list on known_techniques.technique_id=technique_list.id WHERE user_id=:visit_id AND category=:submission GROUP BY technique_id", visit_id=visit_id, submission = "Submission")
    top_contributions = db.execute("SELECT id, name, score, type FROM technique_list WHERE username=:username_visit UNION ALL SELECT id, name, score, type FROM guard_list WHERE username=:username_visit ORDER BY score DESC LIMIT 5", username_visit=username_visit)

    techniques_known = db.execute("SELECT *, MAX(weighted_score) FROM known_techniques Inner Join technique_list on known_techniques.technique_id=technique_list.id WHERE user_id=:visit_id GROUP BY technique_id", visit_id = visit_id)
    positions_known = db.execute("SELECT *, MAX(weighted_score) FROM known_guards Inner Join guard_list on known_guards.guard_id=guard_list.id WHERE user_id=:visit_id GROUP BY guard_id", visit_id = visit_id)

    session["current_route"] = request.path
    return render_template("profile_visit.html", user_visit=user_visit, submissions_known = submissions_known, top_contributions=top_contributions, techniques_known=techniques_known, positions_known=positions_known)

@app.route("/technique", methods=["GET", "POST"])
def technique():

    if request.method == "POST":
        technique_id = request.form.get("technique_variation")
        if technique_id == "-2":
            return redirect("/technique_variation_entry")
        if technique_id == "-3":
            return redirect("/login")
        else:
            session["technique"] = db.execute("SELECT * from technique_list WHERE id = :technique_id", technique_id = technique_id)
            return redirect("/technique")

    session["current_route"] = request.path
    session["technique"] = db.execute("SELECT * from technique_list WHERE id = :tid", tid = session["technique"][0]["id"])

    variations = db.execute("SELECT name, score, username, id from technique_list WHERE name = :name ORDER BY score DESC", name = session["technique"][0]["name"])
    score = db.execute("SELECT score from user_list where username=:username", username = session["technique"][0]["username"])

    technique=session["technique"][0]
    known_techniques=db.execute("SELECT * FROM known_techniques WHERE user_id=:user_id", user_id=session.get("user_id"))

    #check if the selected technique is known by the user
    technique_known = False
    if known_techniques:
        for known_techniques in known_techniques:
            if technique['id'] == known_techniques['technique_id']:
                print("technique known")
                technique_known = True

    return render_template("technique.html", technique_known=technique_known, variations=variations, score=score[0]["score"])

@app.route("/use_technique", methods=["GET", "POST"])
def use_technique():
    """Display user profile"""

    if request.method == "POST":

        if request.form.get("belt_used"):

            user_id=session.get("user_id")
            technique_id=session.get("technique")[0]["id"]
            weighted_score = int(request.form.get("belt_used"))

            #add karma to user who submitted technique
            username_target = session.get("technique")[0]["username"]
            current_user_score = db.execute("SELECT score from user_list where username=:username", username=username_target)
            updated_score = current_user_score[0]["score"] + weighted_score
            db.execute("UPDATE user_list SET score=:updated_score WHERE username=:username", updated_score=updated_score, username=username_target)

            #add karma to technique score
            current_technique_score=session.get("technique")[0]["score"]
            updated_technique_score = current_technique_score + weighted_score
            db.execute("UPDATE technique_list SET score=:updated_technique_score WHERE id=:technique_id", updated_technique_score=updated_technique_score, technique_id=technique_id)

            #refresh the user info and add an entry into the known techniques database
            session.get("user")["score"] = db.execute("SELECT score FROM user_list WHERE id=:user_id", user_id=session.get("user_id"))[0]["score"]
            db.execute("INSERT INTO known_techniques (user_id, technique_id, weighted_score) VALUES(:user_id, :technique_id, :weighted_score)", user_id=user_id, technique_id=technique_id, weighted_score=weighted_score)

    return redirect("/technique")

@app.route("/technique_entry", methods=["GET", "POST"])
def technique_entry():

    if request.method == "POST":

        # import new technique fields from new technique page
        name = request.form.get("name")
        attack_description = request.form.get("attack_description")
        attack_end_position = request.form.get("attack_end_position")
        attack_demonstration = request.form.get("attack_demonstration")
        defense_description = request.form.get("defense_description")
        defense_end_position = request.form.get("defense_end_position")
        defense_demonstration = request.form.get("defense_demonstration")
        position = request.form.get("starting_position")
        category = request.form.get("category")

        # check that forms were completed
        if not name:
            return render_template("redirect.html", message="Technique Name Required!", redirect_path = "/technique_entry")
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
        if not position:
            return render_template("redirect.html", message="Start position required!!!", redirect_path = "/technique_entry")
        if not category:
            return render_template("redirect.html", message="Category required!!!", redirect_path = "/technique_entry")

        #parse youtube links
        if "youtu.be" in attack_demonstration:
            attack_demonstration = attack_demonstration.replace("youtu.be","www.youtube.com/embed")
        if "youtu.be" in defense_demonstration:
            defense_demonstration = defense_demonstration.replace("youtu.be","www.youtube.com/embed")
        if "www.youtube.com" in attack_demonstration:
            attack_demonstration = attack_demonstration.replace("/watch?v=","/embed/")
        if "www.youtube.com" in defense_demonstration:
            defense_demonstration = defense_demonstration.replace("/watch?v=","/embed/")

        #create a new entry in the technique database
        db.execute("INSERT INTO technique_list (name, attack_description, attack_end_position, attack_demonstration, defense_description, defense_end_position, defense_demonstration, position, category, username) VALUES(:name, :attack_description, :attack_end_position, :attack_demonstration, :defense_description, :defense_end_position, :defense_demonstration, :position, :category, :username)", name=name, attack_description=attack_description, attack_end_position=attack_end_position, attack_demonstration=attack_demonstration, defense_description=defense_description, defense_end_position=defense_end_position, defense_demonstration=defense_demonstration, position=position, category=category, username=session.get("username"))
        session["technique"] = db.execute("SELECT * FROM technique_list ORDER BY id DESC LIMIT 1")
        return render_template("redirect.html", message="Technique entered, redirecting in 3 seconds...", status = "success", redirect_path = "/technique")

    return render_template("technique_entry.html")

@app.route("/technique_variation_entry", methods=["GET", "POST"])
def technique_variation_entry():

    if request.method == "POST":
        # import new technique fields from new technique page
        name=session["technique"][0]["name"]
        attack_description = request.form.get("attack_description")
        attack_end_position = request.form.get("attack_end_position")
        attack_demonstration = request.form.get("attack_demonstration")
        defense_description = request.form.get("defense_description")
        defense_end_position = request.form.get("defense_end_position")
        defense_demonstration = request.form.get("defense_demonstration")
        print(session.get("technique"))
        position = session.get("technique")[0]["position"]
        category = session.get("technique")[0]["category"]

        # check that forms were completed

        if not name:
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
        if not position:
            return render_template("redirect.html", message="Start position required!!!", redirect_path = "/technique_variation_entry")
        if not category:
            return render_template("redirect.html", message="Category required!!!", redirect_path = "/technique_variation_entry")


        #parse youtube links
        if "youtu.be" in attack_demonstration:
            attack_demonstration = attack_demonstration.replace("youtu.be","www.youtube.com/embed")
        if "youtu.be" in defense_demonstration:
            defense_demonstration = defense_demonstration.replace("youtu.be","www.youtube.com/embed")
        if "www.youtube.com" in attack_demonstration:
            attack_demonstration = attack_demonstration.replace("/watch?v=","/embed/")
        if "www.youtube.com" in defense_demonstration:
            defense_demonstration = defense_demonstration.replace("/watch?v=","/embed/")

        #create a new entry in the technique database
        db.execute("INSERT INTO technique_list (name, attack_description, attack_end_position, attack_demonstration, defense_description, defense_end_position, defense_demonstration, position, category, username) VALUES(:name, :attack_description, :attack_end_position, :attack_demonstration, :defense_description, :defense_end_position, :defense_demonstration, :position, :category, :username)", name=name, attack_description=attack_description, attack_end_position=attack_end_position, attack_demonstration=attack_demonstration, defense_description=defense_description, defense_end_position=defense_end_position, defense_demonstration=defense_demonstration, position=position, category=category, username=session.get("username"))
        session["technique"] = db.execute("SELECT * FROM technique_list ORDER BY id DESC LIMIT 1")
        return render_template("redirect.html", message="Variation entered, redirecting in 3 seconds...", status = "success", redirect_path = "/technique")

    return render_template("technique_variation_entry.html", session=session)

@app.route("/technique/<position_link>")
def technique_redirect(position_link):

    tid = position_link
    session["technique"] = db.execute("SELECT * from technique_list WHERE id = :tid", tid = tid)

    return redirect("/technique")

@app.route("/guard", methods=["GET", "POST"])
def guard():

    if request.method == "POST":
        guard_id = request.form.get("guard_variation")
        if guard_id == "-2":
            return redirect("/guard_variation_entry")
        if guard_id == "-3":
             return redirect("/login")
        else:
            session["guard"] = db.execute("SELECT * from guard_list WHERE id = :guard_id", guard_id = guard_id)
            return redirect("/guard")

        return redirect("/home")

    session["current_route"] = request.path
    session["guard"] = db.execute("SELECT * from guard_list WHERE id = :gid", gid = session["guard"][0]["id"])

    variations = db.execute("SELECT name, score, username, id from guard_list WHERE name = :name ORDER BY score DESC", name = session["guard"][0]["name"])
    score = db.execute("SELECT score from user_list where username=:username", username = session["guard"][0]["username"])

    guard=session["guard"][0]
    known_guards=db.execute("SELECT * FROM known_guards WHERE user_id=:user_id", user_id=session.get("user_id"))

    #check if the selected technique is known by the user
    guard_known = False
    if known_guards:
        for known_guards in known_guards:
            if guard['id'] == known_guards['guard_id']:
                print("Guard known")
                guard_known = True

    return render_template("guard.html", guard_known=guard_known, variations=variations, score=score[0]["score"])

@app.route("/use_guard", methods=["GET", "POST"])
def use_guard():
    """Display user profile"""

    if request.method == "POST":

        if request.form.get("belt_used"):
            user_id=session.get("user_id")
            guard_id=session.get("guard")[0]["id"]
            weighted_score = int(request.form.get("belt_used"))

            #add karma to user who submitted technique
            username_target = session.get("guard")[0]["username"]
            current_user_score = db.execute("SELECT score from user_list where username=:username", username=username_target)
            updated_score = current_user_score[0]["score"] + weighted_score
            db.execute("UPDATE user_list SET score=:updated_score WHERE username=:username", updated_score=updated_score, username=username_target)

            #add karma to guard score
            current_guard_score=session.get("guard")[0]["score"]
            updated_guard_score = current_guard_score + weighted_score
            db.execute("UPDATE guard_list SET score=:updated_guard_score WHERE id=:guard_id", updated_guard_score=updated_guard_score, guard_id=guard_id)

            #refresh the user info and add an entry into the known techniques database
            session.get("user")["score"] = db.execute("SELECT score FROM user_list WHERE id=:user_id", user_id=session.get("user_id"))[0]["score"]
            db.execute("INSERT INTO known_guards (user_id, guard_id, weighted_score) VALUES(:user_id, :guard_id, :weighted_score)", user_id=user_id, guard_id=guard_id, weighted_score=weighted_score)

    return redirect("/guard")

@app.route("/guard_entry", methods=["GET", "POST"])
def guard_entry():

    if request.method == "POST":
        # import new technique fields from new technique page
        name = request.form.get("name")
        top_description = request.form.get("top_description")
        top_demonstration = request.form.get("top_demonstration")
        bottom_description = request.form.get("bottom_description")
        bottom_demonstration = request.form.get("bottom_demonstration")

        # check that forms were completed
        if not name:
            return render_template("error.html", message="Position Name Required!")
        if not top_description:
            top_description = "Entry not complete! Help by filling this field."
        if not top_demonstration:
            top_demonstration = "URL not provided! Help by adding a youtube link"
        if not bottom_description:
            bottom_description = "Entry not complete! Help by filling this field."
        if not bottom_demonstration:
            bottom_demonstration = "URL not provided! Help by adding a youtube link"

        #parse youtube link
        if "youtu.be" in top_demonstration:
            top_demonstration = top_demonstration.replace("youtu.be","www.youtube.com/embed")
        if "youtu.be" in bottom_demonstration:
            bottom_demonstration = bottom_demonstration.replace("youtu.be","www.youtube.com/embed")
        if "www.youtube.com" in top_demonstration:
            top_demonstration = top_demonstration.replace("/watch?v=","/embed/")
        if "www.youtube.com" in bottom_demonstration:
            bottom_demonstration = bottom_demonstration.replace("/watch?v=","/embed/")

        #create a new entry in the guard database
        db.execute("INSERT INTO guard_list (name, top_description, top_demonstration, bottom_description, bottom_demonstration, username) VALUES(:name, :top_description, :top_demonstration, :bottom_description, :bottom_demonstration, :username)", name=name, top_description=top_description, top_demonstration=top_demonstration, bottom_description=bottom_description, bottom_demonstration=bottom_demonstration, username=session.get("username"))
        session["guard"] = db.execute("SELECT * FROM guard_list ORDER BY id DESC LIMIT 1")
        return render_template("redirect.html", message="Guard entered, redirecting in 3 seconds...", status = "success", redirect_path = "/guard")

    return render_template("guard_entry.html")

@app.route("/guard_variation_entry", methods=["GET", "POST"])
def guard_variation_entry():

    if request.method == "POST":
        # import new technique fields from new technique page
        name = session["guard"][0]["name"]
        top_description = request.form.get("top_description")
        top_demonstration = request.form.get("top_demonstration")
        bottom_description = request.form.get("bottom_description")
        bottom_demonstration = request.form.get("bottom_demonstration")

        # check that forms were completed

        if not name:
            return render_template("error.html", message="Position Name Required!")
        if not top_description:
            top_description = "Entry not complete! Help by filling this field."
        if not top_demonstration:
            top_demonstration = "URL not provided! Help by adding a youtube link"
        if not bottom_description:
            bottom_description = "Entry not complete! Help by filling this field."
        if not bottom_demonstration:
            bottom_demonstration = "URL not provided! Help by adding a youtube link"

        #parse youtube link
        if "youtu.be" in top_demonstration:
            top_demonstration = top_demonstration.replace("youtu.be","www.youtube.com/embed")
        if "youtu.be" in bottom_demonstration:
            bottom_demonstration = bottom_demonstration.replace("youtu.be","www.youtube.com/embed")
        if "www.youtube.com" in top_demonstration:
            top_demonstration = top_demonstration.replace("/watch?v=","/embed/")
        if "www.youtube.com" in bottom_demonstration:
            bottom_demonstration = bottom_demonstration.replace("/watch?v=","/embed/")

        #create a new entry in the guard database
        db.execute("INSERT INTO guard_list (name, top_description, top_demonstration, bottom_description, bottom_demonstration, username) VALUES(:name, :top_description, :top_demonstration, :bottom_description, :bottom_demonstration, :username)", name=name, top_description=top_description, top_demonstration=top_demonstration, bottom_description=bottom_description, bottom_demonstration=bottom_demonstration, username=session.get("username"))
        session["guard"] = db.execute("SELECT * FROM guard_list ORDER BY id DESC LIMIT 1")
        return render_template("redirect.html", message="Variation entered, redirecting in 3 seconds...", status = "success", redirect_path = "/guard")

    return render_template("guard_variation_entry.html")


@app.route("/guard/<position_link>")
def guard_redirect(position_link):

    name = position_link
    session["guard"] = db.execute("SELECT *, MAX(score) from guard_list WHERE name = :name GROUP BY name", name = name)

    return redirect("/guard")


create_message(Greg, flemdog13@hotmail.com, "This is a test message")

send_message(service, gfleming223@gmail.com, message)




def create_message(sender, to, subject, message_text):
  """Create a message for an email.

  Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.

  Returns:
    An object containing a base64url encoded email object.
  """
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(message.as_string())}

def send_message(service, user_id, message):
  """Send an email message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

  Returns:
    Sent Message.
  """
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        print 'Message Id: %s' % message['id']
        return message
    except errors.HttpError, error:
        print 'An error occurred: %s' % error