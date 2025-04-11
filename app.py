from flask import Flask, render_template, request, redirect, session, jsonify
import os
from dotenv import load_dotenv
from database import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash
import re
import string

# Load environment variables from a .env file (if present)
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "fallback-key-in-dev")  # fallback only for dev

# Your routes go here...    
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/services")
def services():
    return render_template("services.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        message = request.form["message"]
        # Here you can store, email, or process the contact form
        return render_template("contact.html", success=True)
    return render_template("contact.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message", "").lower()
    
    # Clean message: remove punctuation
    user_msg_clean = user_msg.translate(str.maketrans('', '', string.punctuation))

    # Define keywords to look for
    keywords_map = {
        "open account": ["open account", "create account", "new account"],
        "loan": ["loan", "apply loan", "get a loan", "borrow money"],
        "contact": ["contact", "call", "email", "reach you"],
        "credit card": ["credit card", "apply card", "get card"],
        "branch": ["branch", "atm", "location"],
        "net banking": ["net banking", "online banking", "internet banking"],
        "forgot password": ["forgot password", "reset password", "recover password"],
        "account types": ["account types", "types of accounts", "different accounts"],
        "interest rate": ["interest rate", "interest", "rates"],
        "dashboard": ["dashboard", "my account", "my profile"],
        "services": ["services", "what you offer", "what services"],
        "investment options": ["investment", "mutual funds", "fd", "fixed deposit", "recurring deposit"],
        "safe banking": ["safe", "secure", "protection", "fraud"],
        "offers": ["offers", "discounts", "cashback", "promotions"],
        "faq": ["faq", "questions", "help", "support"],
        "register": ["register", "sign up", "create user"],
        "hello": ["hello", "hi", "hey"],
        "thanks": ["thank", "thanks", "appreciate"],
        "bye": ["bye", "goodbye", "see you"],
        "who are you": ["who are you", "what are you", "who am I talking to"],
        "what is trustbank": ["what is trustbank", "tell me about trustbank"],
        "how to login": ["how to login", "log in", "sign in"],
        "how to register": ["how to register", "sign up", "create account"],
    }

    chat_responses = {
        "hello": "Hello! How can I help you with your banking needs today?",
        "open account": "You can open a new account by visiting our Services page.",
        "loan": "We offer personal, car, education, and home loans. Visit our Services page to apply.",
        "contact": "You can contact us via the Contact page or call our 24x7 helpline: 1800-123-4567.",
        "credit card": "We offer Platinum, Gold, and Student credit cards. Would you like help choosing one?",
        "branch": "You can find branch and ATM locations using the locator on our Contact page.",
        "net banking": "You can access Net Banking after logging in. Don’t have access? Register online or contact support.",
        "forgot password": "You can reset your password from the Login page using the 'Forgot Password' option.",
        "account types": "We offer savings, current, salary, and joint accounts. Visit our Services page to explore more.",
        "interest rate": "Our savings interest rate is 3.5% p.a. For loan and deposit rates, visit the Services page.",
        "dashboard": "You can access your dashboard after login. It includes balance, transactions, and personalized features.",
        "services": "We offer Loans, Account Services, Credit Cards, Net Banking, and Investments. Check them out on the Services page.",
        "investment options": "We offer Fixed Deposits, Mutual Funds, and Recurring Deposits. Visit the Services page to know more.",
        "safe banking": "Always use strong passwords and never share OTPs. Enable two-factor authentication for added safety.",
        "offers": "We have seasonal offers on credit cards and loan interest rates. Visit our Services page for current promotions.",
        "faq": "You can check out our FAQs section or just ask me anything you'd like to know!",
        "register": "You can create a new user account by visiting the Register page from the navigation menu.",
        "thanks": "Happy to help! Feel free to ask anything else.",
        "bye": "Goodbye! Have a great day. If you need more help, I’m just a message away!",
        "who are you": "I’m your AI Helpdesk, here to assist you with banking queries and navigation.",
        "what is trustbank": "TrustBank is a modern digital bank offering secure, convenient, and customer-first banking services.",
        "how to login": "Click the Login link at the top right, enter your credentials, and access your dashboard securely.",
        "how to register": "Click the Register link in the navigation bar, fill in your details, and you're all set!",
    }

    # Check which keyword matches
    for intent, variations in keywords_map.items():
        for phrase in variations:
            if phrase in user_msg_clean:
                return jsonify({"reply": chat_responses[intent]})

    return jsonify({"reply": "I'm here to help! You can ask me about accounts, loans, cards, branches, or anything else!"})



# User Registration Route
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        # Hash the password before storing it
        hashed_password = generate_password_hash(password)
        
        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                         (username, hashed_password))
            conn.commit()
            return redirect("/login")
        except sqlite3.IntegrityError:
            return render_template("register.html", error="Username already exists!")
        finally:
            conn.close()

    return render_template("register.html")

# User Login Route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        
        if user and check_password_hash(user["password"], password):
            session["username"] = username
            return redirect("/dashboard")
        else:
            return render_template("login.html", error="Invalid credentials!")
    
    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect("/login")
    return render_template("dashboard.html", username=session["username"])

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
