from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError, Optional
import bcrypt
from flask_mysqldb import MySQL
import re

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'database'
app.secret_key = 'your_secret_key_here'

mysql = MySQL(app)

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")

    def validate_email(self, field):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s", (field.data,))
        user = cursor.fetchone()
        cursor.close()
        if user:
            raise ValidationError('Email already taken.')

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class ContactForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    second_name = StringField("Second Name", validators=[DataRequired()])
    phone_number = StringField("Phone Number", validators=[DataRequired()])
    email = StringField("Email", validators=[Optional(), Email()])
    submit = SubmitField("Save")

    def __init__(self, *args, **kwargs):
        self.contact_id = kwargs.pop('contact_id', None)  
        super(ContactForm, self).__init__(*args, **kwargs)

    def validate_phone_number(self, field):
        if not re.match(r"^\+\d{1,3}\d{7,14}$", field.data):
            raise ValidationError("Phone number must include country code and be valid (e.g., +123456789).")

        cursor = mysql.connection.cursor()
        
        if self.contact_id: 
            cursor.execute("SELECT id FROM contacts WHERE phone_number=%s AND user_id=%s AND id != %s", 
                           (field.data, session['user_id'], self.contact_id))
        else:  
            cursor.execute("SELECT id FROM contacts WHERE phone_number=%s AND user_id=%s", 
                           (field.data, session['user_id']))
        
        contact = cursor.fetchone()
        cursor.close()

        if contact:
            raise ValidationError("Phone number already exists. Please use a different phone number.")


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, hashed_password))
        mysql.connection.commit()
        cursor.close()

        flash("Registration successful! Please login.")
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    session.pop('_flashes', None)

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, password FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            if bcrypt.checkpw(password.encode('utf-8'), user[1].encode('utf-8')):
                session['user_id'] = user[0]
                return redirect(url_for('contactlist'))
            else:
                flash("Wrong password. Please try again.", "error")
        else:
            flash("No account found with that email address.", "error")

    return render_template('login.html', form=form)




@app.route('/contactlist', methods=['GET', 'POST'])
def contactlist():
    if 'user_id' in session:
        cursor = mysql.connection.cursor()
        cursor.execute(
            "SELECT id, CONCAT(first_name, ' ', second_name) AS name FROM contacts WHERE user_id=%s",
            (session['user_id'],)
        )
        contacts = cursor.fetchall()
        cursor.close()

        return render_template('contactlist.html', contacts=contacts)
    
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("You have been logged out successfully.")
    return redirect(url_for('login'))

@app.route('/delete_contact/<int:contact_id>')
def delete_contact(contact_id):
    if 'user_id' in session:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM contacts WHERE id=%s AND user_id=%s", (contact_id, session['user_id']))
        mysql.connection.commit()
        cursor.close()
        flash("Contact deleted successfully!")
        return redirect(url_for('contactlist'))
    return redirect(url_for('login'))

@app.route('/add_contact', methods=['GET', 'POST'])
def add_contact():
    if 'user_id' in session:
        form = ContactForm()
        if form.validate_on_submit():
            first_name = form.first_name.data
            second_name = form.second_name.data
            phone_number = form.phone_number.data
            email = form.email.data
            user_id = session['user_id']

            cursor = mysql.connection.cursor()
            cursor.execute(
                "INSERT INTO contacts (first_name, second_name, phone_number, email, user_id) VALUES (%s, %s, %s, %s, %s)",
                (first_name, second_name, phone_number, email, user_id)
            )
            mysql.connection.commit()
            cursor.close()

            flash("Contact added successfully!")
            return redirect(url_for('contactlist'))

        return render_template('add_contact.html', form=form)
    
    return redirect(url_for('login'))

@app.route('/view_contact/<int:contact_id>', methods=['GET', 'POST'])
def view_contact(contact_id):
    if 'user_id' in session:
        cursor = mysql.connection.cursor()
        cursor.execute(
            "SELECT first_name, second_name, phone_number, email FROM contacts WHERE id=%s AND user_id=%s",
            (contact_id, session['user_id'])
        )
        contact = cursor.fetchone()
        cursor.close()

        if not contact:
            flash("Contact not found or you do not have permission to view this contact.")
            return redirect(url_for('contactlist'))

        form = ContactForm(contact_id=contact_id, first_name=contact[0], second_name=contact[1], phone_number=contact[2], email=contact[3])

        if form.validate_on_submit():
            first_name = form.first_name.data
            second_name = form.second_name.data
            phone_number = form.phone_number.data
            email = form.email.data

            cursor = mysql.connection.cursor()
            cursor.execute(
                "UPDATE contacts SET first_name=%s, second_name=%s, phone_number=%s, email=%s WHERE id=%s AND user_id=%s",
                (first_name, second_name, phone_number, email, contact_id, session['user_id'])
            )
            mysql.connection.commit()
            cursor.close()

            flash("Contact updated successfully!")
            return redirect(url_for('contactlist'))

        return render_template('view_contact.html', form=form, contact_id=contact_id)
    
    return redirect(url_for('login'))



@app.route('/edit_contact/<int:contact_id>', methods=['GET', 'POST'])
def edit_contact(contact_id):
    if 'user_id' in session:
        cursor = mysql.connection.cursor()
        cursor.execute(
            "SELECT first_name, second_name, phone_number, email FROM contacts WHERE id=%s AND user_id=%s",
            (contact_id, session['user_id'])
        )
        contact = cursor.fetchone()
        cursor.close()

        if not contact:
            flash("Contact not found or you do not have permission to edit this contact.")
            return redirect(url_for('contactlist'))

        form = ContactForm(
            first_name=contact[0], 
            second_name=contact[1], 
            phone_number=contact[2], 
            email=contact[3],
            original_phone_number=contact[2]  
        )

        if form.validate_on_submit():
            first_name = form.first_name.data
            second_name = form.second_name.data
            phone_number = form.phone_number.data
            email = form.email.data

            cursor = mysql.connection.cursor()
            cursor.execute(
                "UPDATE contacts SET first_name=%s, second_name=%s, phone_number=%s, email=%s WHERE id=%s AND user_id=%s",
                (first_name, second_name, phone_number, email, contact_id, session['user_id'])
            )
            mysql.connection.commit()
            cursor.close()

            flash("Contact updated successfully!")
            return redirect(url_for('contactlist'))

        return render_template('edit_contact.html', form=form, contact_id=contact_id)
    
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
