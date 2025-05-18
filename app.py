from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from forms import EntryForm, ContactForm, LoginForm, RegisterForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///firstapp.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


class People(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(100))
    lname = db.Column(db.String(100))
    email = db.Column(db.String(200))

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(10))
    email = db.Column(db.String(120))
    website = db.Column(db.String(200))
    message = db.Column(db.Text)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)


@app.route('/', methods=['GET', 'POST'])
def index():
    form = EntryForm()
    if form.validate_on_submit():
        new_person = People(fname=form.fname.data, lname=form.lname.data, email=form.email.data)
        db.session.add(new_person)
        db.session.commit()
        flash("Entry added successfully", "success")
        return redirect(url_for('index'))

    allpeople = People.query.all()
    return render_template('index.html', form=form, allpeople=allpeople)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        msg = ContactMessage(
            name=form.name.data,
            phone=form.phone.data,
            email=form.email.data,
            website=form.website.data,
            message=form.message.data
        )
        db.session.add(msg)
        db.session.commit()
        flash("Message submitted successfully", "success")
        return redirect(url_for('index'))
    return render_template('contact.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. You can now log in.", "success")
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            flash(f"Logged in as {form.email.data}", "info")
            return redirect(url_for('index'))   
        else:
            flash("Invalid email or password", "danger")
            return redirect(url_for('login'))
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out", "info")
    return redirect(url_for('index'))

@app.route('/delete/<int:sno>')
def delete(sno):
    person = People.query.get_or_404(sno)
    db.session.delete(person)
    db.session.commit()
    flash("Entry deleted", "warning")
    return redirect(url_for('index'))

@app.route('/update/<int:sno>', methods=['GET', 'POST'])
def update(sno):
    person = People.query.get_or_404(sno)
    form = EntryForm(obj=person)
    if form.validate_on_submit():
        person.fname = form.fname.data
        person.lname = form.lname.data
        person.email = form.email.data
        db.session.commit()
        flash("Entry updated", "info")
        return redirect(url_for('index'))
    return render_template('update.html', form=form)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
