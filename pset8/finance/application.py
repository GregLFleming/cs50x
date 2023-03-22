import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd, win

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    sumtotal = 0
    user = db.execute("SELECT username, cash from users WHERE id = :id", id = session['user_id'])
    stock_list = db.execute("SELECT symbol, shares from portfolio WHERE username = :username", username = user[0]["username"])
    for stock_list in stock_list:
        stock_check = lookup(stock_list['symbol'])
        db.execute("UPDATE portfolio SET value = :value WHERE(username = :username AND symbol = :symbol)", value = usd(stock_check["price"]), username = user[0]["username"], symbol = stock_list['symbol'])
        db.execute("UPDATE portfolio SET total = :total WHERE(username = :username AND symbol = :symbol)", total = usd(stock_list["shares"] * stock_check["price"]), username = user[0]["username"], symbol = stock_list['symbol'])
        sumtotal = sumtotal + stock_check["price"] * stock_list["shares"]
    holdings = db.execute("SELECT * from portfolio WHERE username = :username", username = user[0]["username"])
    sumtotal = usd(sumtotal + user[0]["cash"])

    #convert values into usd
    user[0]["cash"] = usd(user[0]["cash"])

    return render_template("index.html", holdings = holdings, user = user[0]["cash"], sumtotal = sumtotal)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    status = None
    if request.method == "POST":
        desired_stock = request.form.get("symbol")
        stock_qty = request.form.get("shares")
        available_cash = db.execute("SELECT cash from users WHERE id = :id", id = session['user_id'])
        if stock_qty.isalpha() == True:
            return apology("Quantity must be positive", 400)
        if not stock_qty.isdigit():
            return apology("Quantity must be an integer", 400)
        stock_qty = int(float(stock_qty))
        #Check if the fields are all filled and the stock exists
        if not desired_stock:
            status = "Enter a stock"
            return apology("Enter a stock", 400)
        if not stock_qty:
            status = "Enter a quantity"
            return apology("Enter a quantity", 400)
            if not desired_stock:
                status = "Enter both a stock and a quantity"
                return apology("Enter both a stock and a quantity", 400)
        if desired_stock and stock_qty:
            stock = lookup(desired_stock)
            if stock:
                stock_value = stock['price']
                total_cost = stock_value * stock_qty
                stock_value = usd(stock_value)

                #check if funds are available
                if total_cost < available_cash[0]["cash"]:
                    status = "Stock purchased!!!"

                    #subtract stock cost from the user table "cash" value
                    db.execute("UPDATE users SET cash = :cash WHERE id = :id", id = session['user_id'], cash = available_cash[0]["cash"] - total_cost)
                    usernametemp = db.execute("SELECT username from users WHERE id = :id", id = session['user_id'])

                    #create an entry in the "history" table and the portfolio
                    db.execute("INSERT INTO history (username, symbol, qty, price) VALUES(:username, :symbol, :qty, :price)", username = usernametemp[0]["username"], symbol = desired_stock, qty = stock_qty, price = stock_value)
                    stock_check = db.execute("SELECT shares from portfolio WHERE (symbol = :symbol and username = :username)", symbol = desired_stock, username = usernametemp[0]["username"])
                    if stock_check:
                        db.execute("UPDATE portfolio SET shares = :shares WHERE(username = :username AND symbol = :symbol)", shares = stock_check[0]["shares"] + stock_qty, username = usernametemp[0]["username"], symbol = desired_stock)
                    else:
                        db.execute("INSERT INTO portfolio (username, symbol, name, shares) VALUES(:username, :symbol, :name, :shares)", username = usernametemp[0]["username"], symbol = desired_stock, name = stock['name'], shares = stock_qty)
                    return redirect("/")
                else:
                    status = "Insufficient funds!"
                    return apology("Insufficient funds", 400)
            else:
                status = "Invalid Stock Symbol"
                return apology("Invalid Stock Symbol", 400)
    return render_template("buy.html", status = status)

@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""
    username = request.form.get("username")
    unique_ID_check = db.execute("SELECT * FROM users WHERE username = :username", username = username)
    if not unique_ID_check:
        return jsonify(True)
    else:
        print("jsonify sent false")
        return jsonify(False)

@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    user = db.execute("SELECT username from users WHERE id = :id", id = session['user_id'])
    transactions = db.execute("SELECT * from history WHERE username = :username", username = user[0]["username"])
    return render_template("history.html", transactions = transactions)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():

    """Get stock quote."""
    if request.method == "POST":
        stock_search = request.form.get("symbol")
        if stock_search:
            stock = lookup(stock_search)
            if stock:
                stock_value = stock['price']
                stock_value=usd(stock_value)
                stock_symbol = stock['symbol']
            else:
                stock_symbol = "Invalid Stock Symbol"
                return apology("Invalid Stock Symbol", 400)
        else:
            return apology("No Stock Symbol Selected", 400)

        return render_template("quoted.html", symbol = stock_symbol, price = stock_value)
    else:
        return render_template("quote.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User entered route by submitting a field
    if request.method == "POST":

        #Ensure that the desired username field was filled
        if not request.form.get("username"):
            return apology("Desired username field must be filled", 400)

        # ensure that the desired password field was filled
        if not request.form.get("password"):
            return apology("Desired password field must be filled", 400)

        #ensure that the confirm password field was filled
        if not request.form.get("confirmation"):
            return apology("Confirm password field must be filled", 400)

        #ensure that the password fields match
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("Passwords must match!", 400)

        #ensure that the password field is at least 6 characters long
        if len(request.form.get("password")) < 7:
            return apology("Passwords must be at least 6 characters!", 400)

        #Store hashed password
        username = request.form.get("username")
        name_available = check()

        unique_ID_check = db.execute("SELECT * FROM users WHERE username = :username", username = username)

        if not unique_ID_check:
            hashed_password = generate_password_hash(request.form.get("password"))
            db.execute("INSERT INTO users (username, hash) VALUES(:username,:hash)", username = request.form.get("username"),hash = hashed_password)
            session["user_id"] = request.form.get("register_username")
            return win("Successfully registered, redirect in 5 seconds...", 200)
        else:
            return apology("Username already registered!!!", 400)

    return render_template("register.html")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    status = None
    desired_stock = request.form.get("symbol")
    stock_qty = request.form.get("shares", type = int)

    user = db.execute("SELECT username from users WHERE id = :id", id = session['user_id'])
    available_cash = db.execute("SELECT cash from users WHERE id = :id", id = session['user_id'])
    holdings = db.execute("SELECT * from portfolio WHERE username = :username", username = user[0]["username"])
    stocks_available = db.execute("SELECT shares from portfolio WHERE (username = :username AND symbol = :symbol)", username = user[0]["username"], symbol = desired_stock)

    #Check if the fields are all filled and the stock exists
    if not desired_stock:
        status = "Select a stock"
    if not stock_qty:
        status = "Enter a quantity"
        if not desired_stock:
            status = "Enter both a stock and a quantity"

    if desired_stock and stock_qty:
        stock = lookup(desired_stock)
        if stock:
            stock_value = stock['price']
            total_cost = stock_value * stock_qty

            if stock_qty <= stocks_available[0]['shares']:
                #add stock value to user's cash
                db.execute("UPDATE users SET cash = :cash WHERE id = :id", id = session['user_id'], cash = available_cash[0]["cash"] + total_cost)
                usernametemp = db.execute("SELECT username from users WHERE id = :id", id = session['user_id'])

                #create an entry in the "history" table and the portfolio
                db.execute("INSERT INTO history (username, symbol, qty, price) VALUES(:username, :symbol, :qty, :price)", username = usernametemp[0]["username"], symbol = desired_stock, qty = -1*stock_qty, price = -1*stock_value)
                stock_check = db.execute("SELECT shares from portfolio WHERE (symbol = :symbol and username = :username)", symbol = desired_stock, username = usernametemp[0]["username"])

                if stock_check:
                    db.execute("UPDATE portfolio SET shares = :shares WHERE(username = :username AND symbol = :symbol)", shares = stock_check[0]["shares"] - stock_qty, username = usernametemp[0]["username"], symbol = desired_stock)
                    status = "Sale complete!"
                    stocks_available = db.execute("SELECT shares from portfolio WHERE (username = :username AND symbol = :symbol)", username = user[0]["username"], symbol = desired_stock)
                    if stocks_available[0]['shares'] < 1:
                        db.execute("DELETE FROM portfolio WHERE(username = :username AND symbol = :symbol)", username = user[0]["username"], symbol = desired_stock)
                    return redirect("/")
            else:
                status = "Not enough stocks in portfolio"
                return apology("Not enough stocks in portfolio", 400)
        else:
            status = "Invalid Stock Symbol"
    return render_template("sell.html", holdings = holdings, status = status)



def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
