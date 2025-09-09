from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = "your_secret_key"

# In-memory user data
users = {"12345": "password123"}  # Example user credentials
purchase_requests_list = []  # Renamed to avoid conflict with the route function

# Login Route
@app.route("/", methods=["GET", "POST"])
def login():
    if "user" in session:  # If user is already logged in, redirect to home
        return redirect(url_for("home"))
    if request.method == "POST":
        cpf = request.form.get("cpf")
        password = request.form.get("password")
        if cpf in users and users[cpf] == password:
            session["user"] = cpf
            return redirect(url_for("home"))  # Redirect to home page on successful login
        else:
            flash("Invalid CPF or password!")
    return render_template("login.html")

# Home Route
@app.route("/home")
def home():
    if "user" not in session:  # Ensure only logged-in users can access
        flash("Please log in to access the home page.")
        return redirect(url_for("login"))
    return render_template("home.html")

# Purchase Request Submission
@app.route("/purchase", methods=["GET", "POST"])
def purchase():
    if "user" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        request_data = {
            "id": len(purchase_requests_list) + 1,  # Reference the renamed list
            "requester": request.form.get("requesterName"),
            "email": request.form.get("email"),
            "department": request.form.get("department"),
            "item": request.form.get("item"),
            "quantity": request.form.get("quantity"),
            "price":request.form.get("price"),
            "status": "Pending"
        }
        purchase_requests_list.append(request_data)
        flash("Purchase request submitted successfully!")
        return redirect(url_for("view_purchase_requests"))  # Changed to the new route
    return render_template("purchase.html")

# View Purchase Requests
@app.route("/purchase_requests")
def view_purchase_requests():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("purchase_request.html", purchase_requests=purchase_requests_list)

# Update Request (Approve, Reject, Delete)
@app.route("/update_request/<int:request_id>", methods=["POST"])
def update_request(request_id):
    action = request.json.get('action')
    # Find the request by ID
    request_data = next((r for r in purchase_requests_list if r['id'] == request_id), None)

    if request_data:
        if action == 'approve':
            request_data['status'] = 'Approved'
        elif action == 'reject':
            request_data['status'] = 'Rejected'
        elif action == 'delete':
            purchase_requests_list.remove(request_data)
        return jsonify({"success": True})

    return jsonify({"success": False, "message": "Request not found"})
@app.route('/order_approved/<int:request_id>')
def order_approved(request_id):
    # Fetch the purchase request using the request_id
    # Pass necessary data (e.g., vendor info, payment status) to the template
    return render_template('order_approved.html', request_id=request_id)


# Logout Route
@app.route("/logout")
def logout():
    session.pop("user", None)  # Remove user from session
    flash("You have been logged out.")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
