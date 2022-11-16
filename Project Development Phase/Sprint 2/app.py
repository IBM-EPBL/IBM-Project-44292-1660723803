from flask import (
    Flask,
    render_template,
    send_file,
    request,
    redirect,
    url_for,
    session,
    flash,
)
import ibm_db
import re
from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from io import BytesIO

app = Flask(__name__)
app.secret_key = "Zenik"

conn = ibm_db.connect(
    "DATABASE=bludb;"
    "HOSTNAME=2d46b6b4-cbf6-40eb-bbce-6251e6ba0300.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;"
    "PORT=32328;"
    "SECURITY=SSL;"
    "SSLServerCertificate=DigiCertGlobalRootCA.crt;"
    "UID=fpj20933;"
    "PWD=ELH6dqXE1OBE0MGC;",
    "",
    "",
)


@app.route("/", methods=["POST", "GET"])
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    msg = ""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        sql = "SELECT clients.*,budgets.MAXBUDGET FROM clients LEFT JOIN BUDGETS ON CLIENTs.ID=BUDGETS.ID WHERE username =? AND password =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, username)
        ibm_db.bind_param(stmt, 2, password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        # print(account)
        if account:
            session["Loggedin"] = True
            session["id"] = account["ID"]
            session["email"] = account["EMAIL"]
            session["username"] = account["USERNAME"]
            session["budget"] = account["MAXBUDGET"]
            print(session["Loggedin"])
            return redirect("/dashboard")
        else:
            msg = "Incorrect login credentials"
    flash(msg)
    return render_template("login.html", title="Login")


@app.route("/register", methods=["GET", "POST"])
def register():
    msg = ""
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        password1 = request.form["password1"]
        sql = "SELECT * FROM CLIENTS WHERE username =? or email=? "
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, username)
        ibm_db.bind_param(stmt, 2, email)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            msg = "Account already exists"
        elif password1 != password:
            msg = "re-entered password doesnt match"
        elif not re.match(r"[A-Za-z0-9]+", username):
            msg = "Username should be only alphabets and numbers"
        else:
            sql = "INSERT INTO clients(EMAIL,USERNAME,PASSWORD) VALUES (?,?,?)"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, email)
            ibm_db.bind_param(stmt, 2, username)
            ibm_db.bind_param(stmt, 3, password)
            ibm_db.execute(stmt)
            return redirect("/dashboard")
    flash(msg)
    return render_template("register.html", title="Register")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


def isLogged():
    return session["Loggedin"]


@app.route("/dashboard")
def dashboard():
    if isLogged:
        return render_template("dashboard.html", title="Dashboard")
    else:
        flash("Login to go to dashboard")
        return redirect("/login")


@app.route("/changePassword/", methods=["POST", "GET"])
def changePassword():
    msg = "Enter the new password"
    if request.method == "POST":
        pass1 = request.form["pass1"]
        pass2 = request.form["pass2"]
        if pass1 == pass2:
            sql = "UPDATE CLIENTS SET password=? where id=?"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, pass1)
            ibm_db.bind_param(stmt, 2, session["id"])
            if ibm_db.execute(stmt):
                msg = "Successfully Changed Password!!!!"

        else:
            msg = "Passwords not equal"
    flash(msg)
    return redirect(url_for("dashboard"))


@app.route("/changeBudget/", methods=["POST", "GET"])
def changeBudget():
    msg = "Enter the new budget"
    if request.method == "POST":
        budgetAmount = request.form["budgetAmount"]
        sql = "UPDATE BUDGETS SET maxBudget=? where id=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, budgetAmount)
        ibm_db.bind_param(stmt, 2, session["id"])
        if ibm_db.execute(stmt):
            session["budget"] = budgetAmount
            msg = "Successfully Changed Budget!!!!"
        else:
            msg = "Budget not changed"
    flash(msg)
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    app.debug = True
    app.run()
