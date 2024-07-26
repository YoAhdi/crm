from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_migrate import Migrate
from wtforms import StringField, SubmitField, PasswordField, EmailField, IntegerField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.utils import secure_filename
from wtforms.validators import DataRequired, Email
import datetime
from datetime import timedelta
import mysql.connector

from sqlalchemy import create_engine, desc

import pandas as pd
import numpy as np

app = Flask(__name__)
app.config['SECRET_KEY'] = 'key'

# MySQL Database Connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://erpcrm:Erpcrmpass1!@aws-erp.cxugcosgcicf.us-east-2.rds.amazonaws.com:3306/erpcrmdb' 

engine = create_engine('mysql+pymysql://erpcrm:Erpcrmpass1!@aws-erp.cxugcosgcicf.us-east-2.rds.amazonaws.com:3306/erpcrmdb')

# Sets session timeout duration
app.permanent_session_lifetime = timedelta(minutes=30) 

# Initialize database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Accounts model
class Accounts(db.Model):
    __tablename__ = 'Accounts'
    AccountID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    CompanyName = db.Column(db.String(100), nullable=False)
    CompanyRevenue = db.Column(db.Integer, nullable=False)
    EmployeeHeadCount = db.Column(db.Integer, nullable=False)
    CompanyIndustry = db.Column(db.String(100))
    CompanySpecialties = db.Column(db.Text)
    CompanyType = db.Column(db.String(50))
    Country = db.Column(db.String(50), nullable=False)
    City = db.Column(db.String(50))
    Timezone = db.Column(db.String(50))
    
    # Test = db.Column(db.String(10))


# Test model
class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    date_added = db.Column(db.Date, default=datetime.datetime.now(datetime.timezone.utc))
    
    # Create a string
    def __repr__(self):
        return '<Name %r>' % self.name
    
    
# Test form class
class ImportForm(FlaskForm):
    name = StringField('UserID:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired()])
    email = EmailField('Email:', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')
    
    
# Account form
class AccountForm(FlaskForm):
    company_name = StringField('Company Name:*', validators=[DataRequired()])
    company_revenue = IntegerField('Revenue:*', validators=[DataRequired()])
    employee_head_count = IntegerField('Head Count:*', validators=[DataRequired()])
    company_specialties = StringField('Company Specialties:')
    company_type = StringField('Company Type:')
    country = StringField('Country:*', validators=[DataRequired()])
    city = StringField('City:')
    timezone = StringField('Timezone:')
    submit = SubmitField('Submit')
    
# Delete form
class DeleteForm(FlaskForm):
    submit = SubmitField('Delete')
    
# class FileForm(FlaskForm):
#     upload = FileField('File')  
#     submit = SubmitField('Submit')s
    
class UploadForm(FlaskForm):
    upload = FileField('File', validators=[FileRequired()])
    submit = SubmitField('Submit')


# Import account
@app.route('/account_import/', methods=['GET', 'POST'])
def account_import():
    form = UploadForm()
    if form.validate_on_submit():
        f = form.upload.data
        filename = f.filename  
        # Read the file data
        file_content = f.read()
        flash('Account import successful.')
        return render_template('account_import.html', form=form)
    else:
        return render_template('account_import.html', form=form)
    

# Accounts list    
@app.route('/accounts_list/')
def accounts_list():
    accounts = Accounts.query.order_by(desc(Accounts.AccountID))
    return render_template('accounts_list.html', accounts=accounts)


# Update record
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = AccountForm()
    delete_form = DeleteForm()
    account = Accounts.query.get_or_404(id)
    if form.validate_on_submit():

        account.CompanyName = request.form['company_name']
        account.CompanyRevenue = request.form['company_revenue']
        account.EmployeeHeadCount = request.form['employee_head_count']
        account.CompanySpecialties = request.form['company_specialties']
        account.CompanyType = request.form['company_type']
        account.Country = request.form['country']
        account.City = request.form['city']
        account.Timezone = request.form['timezone']
        
        try:
            db.session.commit()
            flash('User updated successfully.')
            return redirect(url_for('accounts_list'))
        except:
            flash('User update failed.')
            return render_template('update.html', form=form, delete_form=delete_form, account=account)
    
    if delete_form.validate_on_submit():
        try:
            db.session.delete(account)
            db.session.commit()
            flash('Account deleted successfully.')
            return redirect(url_for('accounts_list'))
        except:
            flash('Record delete failed.')
            return render_template('update.html', form=form, delete_form=delete_form, account=account)
    
    form.company_name.data = ''
    form.company_revenue.data = ''
    form.employee_head_count.data = ''
    form.company_specialties.data = ''
    form.company_type.data = ''
    form.country.data = ''
    form.city.data = ''
    form.timezone.data = ''    
    
    return render_template('update.html', form=form, delete_form=delete_form, account=account)        
            
            
# Delete account record
# @app.route('/account/<int:id>')
# def delete(id):
#     account = Accounts.query.get_or_404(id)
#     form = AccountForm()
    
#     try:
#         db.session.delete(account)
#         db.session.commit()
#         accounts = Accounts.query.order_by(desc(Accounts.AccountID))
#         flash('Account deleted successfully.')
#         return render_template('accounts_list', form=form, accounts=accounts)
    
#     except:
#         flash('Error deleting account.')
#         return render_template('new_account.html', form=form, accounts=accounts)
        
 

 
 



# Add account
@app.route('/new_account/', methods=['GET', 'POST'])
def new_account():
    company_name = None;
    company_revenue = None
    employee_head_count = None
    company_specialties = None
    company_type = None
    country = None
    city = None
    timezone = None
    submit = None

    
    ids = pd.read_sql("SELECT AccountID FROM Accounts", con=engine)
    next_id = ids.iloc[-1, 0] + 10
    
    form = AccountForm()
    if form.validate_on_submit():
        account = Accounts(AccountID=next_id, CompanyName=form.company_name.data, CompanyRevenue=form.company_revenue.data, 
                           EmployeeHeadCount=form.employee_head_count.data, CompanySpecialties=form.company_specialties.data,
                           CompanyType = form.company_type.data, Country=form.country.data, City=form.city.data, Timezone=form.timezone.data)
        db.session.add(account)
        db.session.commit()
        
        company_name = request.form['company_name']
        company_revenue = request.form['company_revenue']
        employee_head_count = request.form['employee_head_count']
        company_specialties = request.form['company_specialties']
        company_type = request.form['company_type']
        country = request.form['country']
        city = request.form['city']
        timezone = request.form['timezone']
        
        form.company_name.data = ''
        form.company_revenue.data = ''
        form.employee_head_count.data = ''
        form.company_specialties.data = ''
        form.company_type.data = ''
        form.country.data = ''
        form.city.data = ''
        form.timezone.data = ''
        
        flash('New account added successfully.')
           
    return render_template('new_account.html', form=form, company_name=company_name, company_revenue=company_revenue)





    
########################################################################################################################################################################################

# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# # Internal Server Error
# @app.errorhandler(500)
# def server_error(e):
#     return render_template('404.html'), 500
        

# Test form
@app.route('/test/', methods=['GET', 'POST'])
def test():
    name = None
    password = None
    email = None
    form = ImportForm()
    # Validate form
    if form.validate_on_submit():
        user = Test.query.filter_by(email=form.email.data).first()
        if user is None:     
            user = Test(name=form.name.data, email=form.email.data, password=form.password.data)
            db.session.add(user)
            db.session.commit()
            
        name = form.name.data
        password = form.password.data
        email = form.email.data
        form.name.data = ''
        form.email.data = ''
        form.password.data = ''
        flash('User added successfully.')
    users = Test.query.order_by(Test.date_added)
    return render_template('test.html', form=form, name=name, password=password, email=email, users=users)




@app.route('/')
def index():
    if 'user' in session:
        usr = session['user']
        return render_template('index.html', user=usr)
    else:
        return redirect(url_for('login'))


@app.route('/login/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST': 
        session.permanent = True
        user = request.form['nm']
        password = request.form['pass']
        session['user'] = user
        session['pass'] = password
        
        flash('Login successful.', 'info')
        return redirect(url_for('index'))
    else:
        if 'user' in session:
            return redirect(url_for('index'))
        return render_template('login.html')

@app.route('/logout/')
def logout():
    session.pop('user', None)
    
    session.pop('email', None) # Test
    flash('Successfully logged out.', "info")
    return redirect(url_for('login'))


@app.route('/user/')
def user():
    if 'user' in session:
        user = session['user']
        password = session['pass']
        return render_template('user.html', user=user, password=password)
    else:
        return redirect(url_for('login'))


@app.route('/base/')
def base():
    return render_template('base.html')




# TODO
@app.route('/accounts/')
def accounts():
        return render_template('accounts.html')


@app.route('/leads/')
def leads():
    return render_template('leads.html')

@app.route('/opportunities/')
def opportunities():
    return render_template('opportunities.html')

@app.route('/sales/')
def sales():
    return render_template('sales.html')

@app.route('/marketing/')
def marketing():
    return render_template('marketing.html')

@app.route('/service/')
def service():
    return render_template('service.html')

@app.route('/analytics/')
def analytics():
    return render_template('analytics.html')

@app.route('/help/')
def help():
    return render_template('help.html')

@app.route('/home')
def home():
    return render_template('home.html')

if __name__ == "__main__":
    app.run(debug=True)
    
