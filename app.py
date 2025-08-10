from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime, date
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# ------------------ Data Handling ------------------

def load_users():
    if os.path.exists('data/users.json'):
        with open('data/users.json') as f:
            return json.load(f)
    return {}

def save_users(users):
    # Ensure the 'data' directory exists
    os.makedirs('data', exist_ok=True)
    with open('data/users.json', 'w') as f:
        json.dump(users, f, indent=4)

def load_leaves():
    if os.path.exists('data/leaves.json'):
        with open('data/leaves.json') as f:
            return json.load(f)
    return []

def save_leaves(leaves):
    os.makedirs('data', exist_ok=True)
    with open('data/leaves.json', 'w') as f:
        json.dump(leaves, f, indent=4)

def add_leave(username, start_date, end_date, leave_type, reason):
    leaves = load_leaves()
    leaves.append({
        'username': username,
        'start_date': start_date,
        'end_date': end_date,
        'leave_type': leave_type,
        'reason': reason
    })
    save_leaves(leaves)


# ------------------ Routes ------------------

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    users = load_users()
    error = None
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        if username not in users:
            error = "Username not found."
        elif users[username]['password'] != password:
            error = "Incorrect password."
        else:
            session['user'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard', username=username))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('user', None)  # Correct key to pop is 'user'
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    users = load_users()
    error = None
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        confirm = request.form['confirm_password']
        email = request.form['email'].strip()

        if username in users:
            error = "Username already exists."
        elif password != confirm:
            error = "Passwords do not match."
        elif len(password) < 6 or not any(c.isdigit() for c in password):
            error = "Password must be at least 6 characters and include a number."
        else:
            users[username] = {'password': password, 'email': email, 'leave_quota': 20} # Default leave quota
            save_users(users)
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
    return render_template('signup.html', error=error)

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    users = load_users()
    message = None
    if request.method == 'POST':
        username = request.form['username'].strip()
        if username in users:
            # In a real app, you would send a reset link to their email
            # This is a simple hint for demonstration purposes
            message = f"Password hint for {username}: {users[username]['password'][:2]}***"
        else:
            message = "Username not found."
    return render_template('forgot_password.html', message=message)


@app.route('/dashboard/<username>')
def dashboard(username):
    # Check if the user is logged in and is the correct user
    if 'user' not in session or session['user'] != username:
        flash('Please log in to view this page.', 'danger')
        return redirect(url_for('login'))

    users = load_users()
    leaves = load_leaves()

    user_leaves = [l for l in leaves if l['username'] == username]
    
    # Calculate used leave days
    used_days = 0
    for leave in user_leaves:
        start_date = datetime.strptime(leave['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(leave['end_date'], '%Y-%m-%d')
        used_days += (end_date - start_date).days + 1

    remaining = users[username].get('leave_quota', 20) - used_days
    
    return render_template('dashboard.html', username=username, leaves=user_leaves, used=used_days, remaining=remaining)


@app.route('/apply_leave', methods=['GET', 'POST'])
def apply_leave():
    if 'user' not in session:
        flash('Please log in to apply for leave.', 'danger')
        return redirect(url_for('login'))
        
    error = None
    if request.method == 'POST':
        start = request.form['start_date']
        end = request.form['end_date']
        leave_type = request.form['leave_type']
        reason = request.form['reason'].strip()

        try:
            start_date = datetime.strptime(start, '%Y-%m-%d').date()
            end_date = datetime.strptime(end, '%Y-%m-%d').date()
            today = date.today()

            if start_date < today:
                error = "Start date cannot be in the past."
            elif end_date < start_date:
                error = "End date must be after start date."
            elif len(reason) < 10:
                error = "Reason must be at least 10 characters."
            else:
                add_leave(session['user'], start, end, leave_type, reason)
                flash('Leave request submitted successfully!', 'success')
                return redirect(url_for('dashboard', username=session['user']))
        except ValueError:
            error = "Invalid date format."
    return render_template('leave_form.html', error=error)


@app.route('/cancel_leave/<username>/<int:index>')
def cancel_leave(username, index):
    if 'user' not in session or session['user'] != username:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('login'))

    leaves = load_leaves()
    # Filter leaves to get only the current user's leaves
    user_leaves_indices = [i for i, l in enumerate(leaves) if l['username'] == username]

    if 0 <= index < len(user_leaves_indices):
        original_index = user_leaves_indices[index]
        del leaves[original_index]
        save_leaves(leaves)
        flash('Leave request cancelled.', 'success')
    else:
        flash('Leave request not found.', 'danger')

    return redirect(url_for('dashboard', username=username))

# ------------------ Run App ------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)