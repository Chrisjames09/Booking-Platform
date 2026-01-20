from flask import Flask, render_template, request, redirect, url_for, session
from forms import ptForm, ftForm, loginForm, ptUpdate
import shelve
from pt import PT
from ft import FT
from werkzeug.security import generate_password_hash, check_password_hash
import logging

app = Flask(__name__)
app.secret_key = 'test123'

def print_pt_database():
    db = shelve.open('pt.db', 'r')
    pt_dict = db.get('pt', {})
    db.close()

    print(pt_dict)

# Call this function to print the PT database when the application starts
print_pt_database()

@app.route('/', methods=['GET', 'POST'])
def login():
    form = loginForm(request.form)
    if request.method == 'POST':
        if form.validate():
            email = form.email.data
            password = form.password.data

            print(f"email: {email}password: {password}") #DEBUG

            db = shelve.open('pt.db', 'r')
            pt_dict = db.get('pt', {})
            db.close()
            print(f"Number of PT records in database: {len(pt_dict)}") #DEBUG

            for pt in pt_dict.values():
                print(f"Stored email: {pt.get_email()} - Stored password hash: {pt.get_password()}")  # DEBUG check
                if pt.get_email() == email and check_password_hash(pt.get_password(), password):
                    print(f"Email{pt.get_email()}") #DEBUG check email validity
                    print(f"Password{pt.check_password(password)}") #DEBUG check hashed password

                    if pt.type != 'user':
                        print("Account not user")  # DEBUG
                        session.clear()  # Clear the session data
                        return render_template('login.html', form=form, error="Account deactivated, please contact admin!")

                    session['user_id'] = pt.get_id()
                    session['user_name'] = pt.firstname + pt.lastname
                    session['account_type'] = pt.type
                    session['email'] = pt.get_email()
                    print(f"Login successful for: {pt.get_email()}")  # DEBUG
                    return redirect(url_for('profile', pt_id=pt.get_id()))
                else: #DEBUG
                    print("Password does not match")  # DEBUG



            return render_template('login.html', form=form, error="Invalid Email or Password")

    return render_template('login.html', form=form)


def superadmin():
    db = shelve.open('admin.db', 'c')
    admin_dict = db.get('admin', {})

    if 'super' not in [ft.get_type() for ft in admin_dict.values()]:
        hashed_password = generate_password_hash('1q2w3e4r')

        superadmin = FT(
            email='superadmin@mail.com',
            password=hashed_password,
            type='super',
        )
        admin_dict[superadmin.get_id()] = superadmin
        db['admin'] = admin_dict
        print(f"Superuser {superadmin.get_email()} created with ID {superadmin.get_id()}")

    db.close()

superadmin()

@app.route('/adm_login', methods=['GET', 'POST'])
def adm_login():
    form = loginForm(request.form)
    if request.method == 'POST':
        if form.validate():
            email = form.email.data
            password = form.password.data

            db = shelve.open('admin.db', 'r')
            admin_dict = db.get('admin', {})
            db.close()

            for ft in admin_dict.values():
                if ft.get_email() == email and check_password_hash(ft.get_password(), password):

                    if ft.get_type() not in ['admin', 'super']:
                        print("Account is not admin or super")  # DEBUG
                        session.clear()  # Clear session data
                        return redirect(url_for('adm_login'))

                    session['user_id'] = ft.get_id()
                    session['account_type'] = ft.type
                    session['email'] = ft.get_email()

                    if ft.get_type() == 'admin' or ft.get_type() == 'super':
                        session['account_type'] = ft.get_type()
                        return redirect(url_for('admin_dashboard'))

            return render_template('adm_login.html', form=form, error="Invalid Email or Password")

    return render_template('adm_login.html', form=form)



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    ptSignup = ptForm(request.form)
    if request.method == "POST" and ptSignup.validate():

        if request.method == "POST" and ptSignup.validate():
            pt_dict = {}
            db = shelve.open('pt.db', 'c')
            try:
                pt_dict = db.get('pt', {})
            except:
                print("Error in retrieving staff from pt.db.")

            for pt in pt_dict.values():
                if pt.get_email() == ptSignup.email.data:
                    db.close()
                    error_message = "Email is already registered. Please use a different email."
                    return render_template('signup.html', form=ptSignup, error=error_message)

            hashed_password = generate_password_hash(ptSignup.password.data)
            ptStaff = PT(
                ptSignup.firstname.data,
                ptSignup.lastname.data,
                ptSignup.gender.data,
                ptSignup.phone.data,
                ptSignup.address.data,
                ptSignup.bank.data,
                ptSignup.email.data,
                hashed_password,
                type='user'
            )

            pt_dict[ptStaff.get_id()] = ptStaff
            db['pt'] = pt_dict
            print(f"{ptStaff.get_email()} saved with user id {ptStaff.get_id()}")
#DEBUG
            # print(pt_dict)
#DEBUG
            db.close()

        return redirect(url_for('login'))
    return render_template('signup.html', form=ptSignup)

@app.route('/adm_signup', methods=['GET', 'POST'])

def adm_signup():
    if 'account_type' not in session or session['account_type'] != 'super':
        return redirect(url_for('login'))
    ftSignup = ftForm(request.form)
    if request.method == "POST" and ftSignup.validate():

        if request.method == "POST" and ftSignup.validate():
            admin_dict = {}
            db = shelve.open('admin.db', 'c')
            try:
                admin_dict = db.get('admin', {})
            except:
                print("Error in retrieving staff from pt.db.")

            for ft in admin_dict.values():
                if ft.get_email() == ftSignup.email.data:
                    db.close()
                    error_message = "Email is already registered. Please use a different email."
                    return render_template('signup.html', form=ftSignup, error=error_message)

            hashed_password = generate_password_hash(ftSignup.password.data)

            ftStaff = FT(
                ftSignup.email.data,
                hashed_password,
                type='admin'
            )

            admin_dict[ftStaff.get_id()] = ftStaff
            db['admin'] = admin_dict
            print(f"{ftStaff.get_email()} saved with user id {ftStaff.get_id()}")
            db.close()

        return redirect(url_for('adm_login'))
    return render_template('adm_signup.html', form=ftSignup)

@app.route('/profile/<string:pt_id>')
def profile(pt_id):
    if 'user_id' not in session or session['user_id'] != pt_id:
        return redirect(url_for('login'))

    account_type = session.get('account_type') #DEBUG
    print(account_type) #DEBUG

    db = shelve.open('pt.db', 'r')
    pt_dict = db.get('pt', {})
    db.close()

    pt = pt_dict.get(pt_id)
    if pt:
        return render_template('profile.html', pt=pt)
    else:
        return redirect(url_for('login'))






@app.route('/update_profile/<string:pt_id>', methods=['GET', 'POST'])
def update_profile(pt_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    current_user_id = session['user_id']
    account_type = session.get('account_type')

    if (account_type not in ['admin', 'super']) and (current_user_id != pt_id):
        return redirect(url_for('login'))

    db = shelve.open('pt.db', 'c')
    pt_dict = db.get('pt', {})
    pt = pt_dict.get(pt_id)

    if not pt:
        db.close()
        return redirect(url_for('login'))

    updateForm = ptUpdate(request.form)
    if request.method == 'POST' and updateForm.validate():
        pt.firstname = request.form['firstname']
        pt.lastname = request.form['lastname']
        pt.phone = request.form['phone']
        pt.address = request.form['address']
        pt.bank = request.form['bank']

        pt_dict[pt_id] = pt
        db['pt'] = pt_dict  # Save updated details
        db.close()

        if account_type == 'user':
            return redirect(url_for('profile', pt_id=pt_id))
        if account_type == 'admin' or account_type == 'super':
            return redirect(url_for('admin_dashboard'))

    updateForm.firstname.data = pt.firstname
    updateForm.lastname.data = pt.lastname
    updateForm.phone.data = pt.phone
    updateForm.address.data = pt.address
    updateForm.bank.data = pt.bank

    db.close()
    return render_template('update_profile.html', pt=pt, form=updateForm)

##
@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if 'account_type' not in session or session['account_type'] not in ['admin', 'super']:
        return redirect(url_for('adm_login'))

    db = shelve.open('pt.db', 'r')
    pt_dict = db.get('pt', {})
    db.close()

    pt_list = list(pt_dict.values())  # Convert the dict values to a list

    db = shelve.open('admin.db', 'r')
    admin_dict = db.get('admin', {})

    admin_list = list(admin_dict.values())

    return render_template('admin_dashboard.html', pt_list=pt_list, admin_list=admin_list)
##
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/deactivate_user/<string:id>', methods=['POST'])
def deactivate_user(id):
    if 'account_type' not in session or (session['account_type'] not in ['admin', 'super']):
        return redirect(url_for('login'))

    db = shelve.open('pt.db', 'c')
    pt_dict = db.get('pt', {})

    if id in pt_dict:
        pt = pt_dict[id]
        pt.type = 'inactivePT'
        db['pt'] = pt_dict  # Save changes
    db.close()

    return redirect(url_for('admin_dashboard'))

@app.route('/reactivate_user/<string:id>', methods=['POST'])
def reactivate_user(id):
    if 'account_type' not in session or (session['account_type'] not in ['admin', 'super']):
        return redirect(url_for('login'))

    db = shelve.open('pt.db', 'c')
    pt_dict = db.get('pt', {})

    if id in pt_dict:
        pt = pt_dict[id]
        pt.type = 'user'
        db['pt'] = pt_dict  # Save changes
    db.close()

    return redirect(url_for('admin_dashboard'))

@app.route('/deactivate_admin/<string:id>', methods=['POST'])
def deactivate_admin(id):
    if 'account_type' not in session or (session['account_type'] not in ['super']):
        return redirect(url_for('login'))

    db = shelve.open('admin.db', 'c')
    admin_dict = db.get('admin', {})

    if id in admin_dict:
        admin = admin_dict[id]
        admin.type = 'inactiveFT'
        db['admin'] = admin_dict  # Save changes
    db.close()

    return redirect(url_for('admin_dashboard'))

@app.route('/reactivate_admin/<string:id>', methods=['POST'])
def reactivate_admin(id):
    if 'account_type' not in session or (session['account_type'] not in ['super']):
        return redirect(url_for('login'))

    db = shelve.open('admin.db', 'c')
    admin_dict = db.get('admin', {})

    if id in admin_dict:
        admin = admin_dict[id]
        admin.type = 'admin'
        db['admin'] = admin_dict  # Save changes
    db.close()

    return redirect(url_for('admin_dashboard'))

# @app.route('/home/<string:id>')
# def pt_home(pt_id):
#     if 'user_id' not in session or session['user_id'] != pt_id:
#         return redirect(url_for('login'))
#
#     db = shelve.open('pt.db', 'r')
#     pt_dict = db.get('pt', {})
#     db.close()
#
#     pt = pt_dict.get(pt_id)
#
#     if pt:
#         return render_template('home.html', pt=pt)  # Return the template here
#     else:
#         return redirect(url_for('login'))


#########################
#MINGYI#
#########################
from flask import flash
import uuid

DB_FILE = "faq_db"

# Function to initialize test FAQ data (outside of routes)
def initialize_test_faq():
    with shelve.open(DB_FILE, writeback=True) as db:
        if "faqs" not in db:
            db["faqs"] = {}
        # Check if there are no FAQs in the database and add a test one
        if not db["faqs"]:
            faq_id = str(uuid.uuid4())  # Generate a unique ID for the FAQ
            db["faqs"][faq_id] = {
                "question": "What is Flask?",
                "answer": "Flask is a web framework.",
                "user_id": "Admin"
            }
            print("Test FAQ added!")  # Confirmation in the console

# Call the function to add test FAQ when the app starts
initialize_test_faq()

# Route to display the FAQ list
@app.route('/faq')
def faq():
####
    if 'user_id' not in session:
        return redirect(url_for('login'))

    account_type = session.get('account_type')

    if account_type not in ['user', 'admin']:
        return redirect(url_for('login'))
####
    with shelve.open(DB_FILE) as db:
        faqs = db.get("faqs", {})
    return render_template("faq.html", faqs=faqs)


# Route to create a new FAQ
@app.route("/createfaq", methods=["GET", "POST"])
def createfaq():
####
    if request.method == "POST":
        question = request.form["question"]
        answer = request.form["answer"]
        faq_id = str(uuid.uuid4())  # Generate a unique ID for the FAQ
####
        with shelve.open(DB_FILE, writeback=True) as db:
            if "faqs" not in db:
                db["faqs"] = {}
                ####
            db["faqs"][faq_id] = {"question": question, "answer": answer}
                ####
        flash("FAQ added successfully!", "success")
        return redirect(url_for("faq"))
    return render_template("createfaq.html")

# Route to edit an existing FAQ
@app.route("/editfaq/<faq_id>", methods=["GET", "POST"])
def editfaq(faq_id):
####
    if 'user_id' not in session:
        return redirect(url_for('login'))

    account_type = session.get('account_type')

    if account_type not in ['admin']:
        return redirect(url_for('login'))

####
    with shelve.open(DB_FILE) as db:
        faq = db["faqs"].get(faq_id)

    if not faq:
        flash("FAQ not found.", "danger")
        return redirect(url_for("faq"))

    if request.method == "POST":
        question = request.form["question"]
        answer = request.form["answer"]

        with shelve.open(DB_FILE, writeback=True) as db:
            db["faqs"][faq_id].update({"question": question, "answer": answer})

        flash("FAQ updated successfully!", "success")
        return redirect(url_for("faq"))

    return render_template("editfaq.html", faq=faq, faq_id=faq_id)

# Route to delete an FAQ
@app.route("/deletefaq/<faq_id>")
def deletefaq(faq_id):
    ####
    if 'user_id' not in session:
        return redirect(url_for('login'))

    account_type = session.get('account_type')

    if account_type not in ['admin']:
        return redirect(url_for('login'))

    ####

    with shelve.open(DB_FILE, writeback=True) as db:
        if faq_id in db["faqs"]:
            del db["faqs"][faq_id]
            flash("FAQ deleted successfully!", "success")
        else:
            flash("FAQ not found.", "danger")
    return redirect(url_for("faq"))



@app.route('/faqcontactus', methods=['GET', 'POST'])
def faq_contact_us():
    ####
    if 'user_id' not in session:
        return redirect(url_for('login'))

    account_type = session.get('account_type')

    if account_type not in ['user']:
        return redirect(url_for('login'))

    ####
    if request.method == 'POST':
        name = session.get('user_name')
        email = session.get('email')
        message = request.form['message']

        # Save to a separate database
        with shelve.open('contacts.db', writeback=True) as db:
            # Use an auto-incrementing ID
            contact_id = str(len(db) + 1)
            db[contact_id] = {
                'id': contact_id,
                'name': name,
                'email': email,
                'message': message
            }

        flash('Thank you for your message!', 'success')
        return redirect('/faqcontactus')

    return render_template('faqcontactus.html')


@app.route('/manage_contacts', methods=['GET', 'POST'])
def manage_contacts():
    ####
    if 'user_id' not in session:
        return redirect(url_for('login'))

    account_type = session.get('account_type')

    if account_type not in ['admin']:
        return redirect(url_for('login'))

    ####
    contacts = []
    with shelve.open('contacts.db') as db:
        for key in db:
            contact = db[key]
            contact['id'] = key  # Add the key as an 'id' field for display
            contacts.append(contact)

    return render_template('manage_contacts.html', contacts=contacts)

@app.route('/delete_contact/<contact_id>', methods=['POST'])
def delete_contact(contact_id):
    ####
    if 'user_id' not in session:
        return redirect(url_for('login'))

    account_type = session.get('account_type')

    if account_type not in ['admin']:
        return redirect(url_for('login'))

    ####
    with shelve.open('contacts.db', writeback=True) as db:
        if contact_id in db:
            del db[contact_id]
            flash('Contact deleted successfully.', 'success')
        else:
            flash('Contact not found.', 'danger')

    return redirect('/manage_contacts')

@app.route('/mark_as_done/<contact_id>', methods=['POST'])
def mark_as_done(contact_id):
    ####
    if 'user_id' not in session:
        return redirect(url_for('login'))

    account_type = session.get('account_type')

    if account_type not in ['admin']:
        return redirect(url_for('login'))

    ####
    with shelve.open('contacts.db', writeback=True) as db:
        if contact_id in db:
            contact = db[contact_id]
            contact['status'] = 'Done'  # Update the contact's status to "Done"
            db[contact_id] = contact  # Save the updated contact
            flash('Contact marked as done.', 'success')
        else:
            flash('Contact not found.', 'danger')

    return redirect('/manage_contacts')
#########################
#MINGYI END#
#########################

#########################
#KEBIN START# AYUBOO
#########################
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from Forms_Postings import CreatePostingForm
import shelve, Posting

import os
from werkzeug.utils import secure_filename
from datetime import datetime

# -- Ayub Part --

UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

ALLOWED_MC_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'docx', 'txt'}

# -- Ayub End --


# integrating both vid and mc allowed files
def allowed_file(filename, file_type):
    if file_type.lower() == 'video':
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS
    elif file_type.lower() == 'mc':
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_MC_EXTENSIONS
    return False

# route for ft job posting
@app.route('/posting', methods=['POST', 'GET'])
def posting():
    ####
    if 'user_id' not in session:
        return redirect(url_for('login'))

    account_type = session.get('account_type')

    if account_type not in ['admin']:
        return redirect(url_for('login'))

    ####
    posting_job = CreatePostingForm(request.form) # saving the form template into a variable
    if request.method == "POST" and posting_job.validate():
        posting_dict = {}
        db = shelve.open('bookings', 'c')

        # checking if db w key exist, if T then replace the mpty dict w the existing db, else continue
        try:
            posting_dict = db['Jobs']
        except:
            print("Error in retrieving bookings db | Does not exist")

        # getting the form inputs w .data and storing it into a variable with the format as an object
        posting_job = Posting.PostingForm(posting_job.company_name.data, posting_job.position.data, posting_job.quantity.data, posting_job.description.data, posting_job.pay_rate.data, posting_job.date.data, posting_job.start_time.data, posting_job.end_time.data)

        # giving the entire data from the form a key w the id generated from each class
        posting_dict[posting_job.get_posting_id()] = posting_job
        # storing the final dict into the db w the key 'Job' | int are not allowed to be stored as keys hence a dict to store the id seperately b4 into the db
        db['Jobs'] = posting_dict

        db.close()

        return redirect(url_for('booking'))
    return render_template('postings.html', form=posting_job)

# route for pt job booking
@app.route('/booking')
def booking():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    account_type = session.get('account_type')

    if account_type not in ['user', 'admin']:
        return redirect(url_for('login'))


    # Opening the db and taking the value of the data stored with the key 'Jobs'
    booking_dict = {}
    db = shelve.open('bookings', 'c')
    booking_dict = db.get('Jobs', {})
    db.close()

    # Creating lists to store booked and available jobs
    booked_jobs = []
    available_jobs = []

    print("11")
    print(session)

    # Separate booked jobs from available jobs
    for key in booking_dict:
        job = booking_dict.get(key)
        if account_type == "user":
            if session['user_name'] in job.get_booked_by():
                booked_jobs.append(job)
            else:
                available_jobs.append(job)
        elif account_type == "admin":
            if session['user_id'] in job.get_booked_by():
                booked_jobs.append(job)
            else:
                available_jobs.append(job)

    # Calculate counts
    booked_count = len(booked_jobs)
    available_count = len(available_jobs)
    print("B", booked_count)
    print("A", available_count)

    # creating a list to store the id (amt of data / form output) in the db to the list so that we can run for loop in the html
    booking_list = []
    for key in booking_dict:
        job = booking_dict.get(key)
        booking_list.append(job)

    for i in booking_list:
        print(i)

    return render_template('booking.html', booked_jobs=booked_jobs, available_jobs=available_jobs, booked_count=booked_count, available_count=available_count, jobs=booking_list)

# To update / edit info of job
@app.route('/update_posting/<int:id>', methods=['POST', 'GET']) # route to file with id in the url to target the respective job
def update_posting(id):
    ####
    if 'user_id' not in session:
        return redirect(url_for('login'))

    account_type = session.get('account_type')

    if account_type not in ['admin']:
        return redirect(url_for('login'))

    ####
    update_form = CreatePostingForm(request.form)
    # if post method is requested and form exists, edit the existing data in db
    if request.method == 'POST' and update_form.validate():
        db = shelve.open('bookings', 'w')
        job_dict = db['Jobs']

        # rewriting the data in the db by replacing it in the dict since we brought it out in line 61.
        jobs = job_dict.get(id)
        jobs.set_co_name(update_form.company_name.data)
        jobs.set_position(update_form.position.data)
        jobs.set_quantity(update_form.quantity.data)
        jobs.set_description(update_form.description.data)
        jobs.set_pay_rate(update_form.pay_rate.data)
        jobs.set_date(update_form.date.data)
        jobs.set_start_time(update_form.start_time.data)
        # print(update_form.start_time.data)
        jobs.set_end_time(update_form.end_time.data)

        # replacing the old db dict w the new dict
        db['Jobs'] = job_dict
        db.close()

        # redirect back to the booking page aft post method
        return redirect(url_for('booking'))
    # else if no post methd, [when update button is selected].=
    else:
        # open db and extract the data in the dict
        db = shelve.open('bookings', 'r')
        job_dict = db['Jobs']
        db.close()

        # replacing each form input with the values in the db by .get_, .get_ works here as we stored the data into the db / dict in obj format. The empty input of the forms are access by .data
        jobs = job_dict.get(id)
        update_form.company_name.data = jobs.get_co_name()
        update_form.position.data = jobs.get_position()
        update_form.quantity.data = jobs.get_quantity()
        update_form.description.data = jobs.get_description()
        update_form.pay_rate.data = jobs.get_pay_rate()
        update_form.date.data = jobs.get_date()
        update_form.start_time.data = jobs.get_start_time()
        update_form.end_time.data = jobs.get_end_time()

        return render_template('update_posting.html', form=update_form)

# for the del job post btn to work
@app.route('/deleteJob/<int:id>', methods=['POST', 'GET'])
def delete_posting(id):
    ####
    if 'user_id' not in session:
        return redirect(url_for('login'))

    account_type = session.get('account_type')

    if account_type not in ['admin']:
        return redirect(url_for('login'))

    ####
    # deleting the posting by removing the data in db by the stored id. by using .pop and storing back into the db
    job_dict = {}
    db = shelve.open('bookings', 'w')
    job_dict = db['Jobs']

    job_dict.pop(id)

    db['Jobs'] = job_dict
    db.close()

    return redirect(url_for('booking'))

# TO BE EDITTED AFTER INTEGRATING - HOW MC SYSTEM WORK? | WHEN CANCEL GO TO MC PAGE INSTD > CANCEL BOOKING FROM MC PAGE
# Making booking btn multitask for booking and cancelling
@app.route('/bookJob/<int:id>', methods=['POST', 'GET'])
def booking_job(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    current_user_id = session['user_id']
    current_user_name = session['user_name']
    account_type = session.get('account_type')

    if account_type not in ['user']:
        return redirect(url_for('login'))

    db = shelve.open('bookings', 'w')
    job_dict = db['Jobs']
    job = job_dict.get(id)

    if job.get_quantity() > 0:
        job.set_quantity(job.get_quantity() - 1)  # Decrease available quantity
        job.set_booked_by(current_user_name)  # Add user to booked list
        db['Jobs'] = job_dict  # Save changes

        # Add the job to the user's booked jobs list
        booked_jobs = db.get(f'{current_user_id}_BookedJobs', [])
        booked_jobs.append({
            'id': job.get_posting_id(),
            'title': job.get_position(),
            'start': job.get_date().strftime('%Y-%m-%d') + ' ' + job.get_start_time().strftime('%H:%M'),
            'end': job.get_date().strftime('%Y-%m-%d') + ' ' + job.get_end_time().strftime('%H:%M'),
            'description': job.get_description()
        })
        db[f'{current_user_id}_BookedJobs'] = booked_jobs  # Save updated list
    else:
        print("No available slots")

    db.close()
    return redirect(url_for('booking'))

@app.route('/cancelJob/<int:id>', methods=['POST'])
def cancel_job(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Redirect to apply_leave page instead of canceling directly
    return redirect(url_for('apply_leave', job_id=id))

@app.route('/schedule')
def calendar():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    current_user_id = session['user_id']

    # Extracting the values of jobs that were booked by the current user
    booked_jobs = []

    db = shelve.open('bookings', 'r')
    if f'{current_user_id}_BookedJobs' in db:
        booked_jobs = db[f'{current_user_id}_BookedJobs']
    db.close()

    # Passing the list into render_template() as var events so that we can use it in the HTML file
    return render_template('schedule.html', events=booked_jobs)

# -- AYUB PART --

# function to check allowed file extensions

# Mutators & Accessors for Leave DB
def get_leave_requests():
    with shelve.open('leave_requests', 'c') as db:
        return db.get('LeaveRequests', [])

def save_leave_request(leave_request):
    with shelve.open('leave_requests', 'c') as db:
        lr_list = db.get('LeaveRequests', [])
        lr_list.append(leave_request)
        db['LeaveRequests'] = lr_list

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

@app.route('/applyLeave/<int:job_id>', methods=['GET', 'POST'])
def apply_leave(job_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    current_user_id = session['user_id']
    current_user_name = session['user_name']
    account_type = session.get('account_type')

    if account_type not in ['user']:
        return redirect(url_for('login'))

    job = None
    with shelve.open('bookings', 'r') as db:
        job_dict = db.get("Jobs", {})
        job = job_dict.get(job_id)

    if job is None:
        return redirect(url_for('booking'))  # Redirect if job not found

    if request.method == 'POST':
        user_name = session.get('user_name')
        date = request.form["job_date"]
        reason = request.form['reason']
        remarks = request.form['remarks']
        file = request.files['file_upload']

        if file and allowed_file(file.filename, 'mc'):
            filename = secure_filename(file.filename)  # Sanitize and Secure the filename
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)

            leave_request = {
                'user_name': user_name,
                'date': date,
                'reason': reason,
                'remarks': remarks,
                'file_path': f'uploads111/{filename}'  # Store the relative file path
            }
            save_leave_request(leave_request)

            # Cancel the booking after leave request is submitted
            with shelve.open('bookings', 'w') as db:
                job_dict = db.get("Jobs", {})
                job = job_dict.get(job_id)
                job.cancel_booking(current_user_name)  # Remove user from booked list
                db['Jobs'] = job_dict  # Save changes

                # Remove the job from the user's booked jobs list
                booked_jobs = db.get(f'{current_user_id}_BookedJobs', [])
                booked_jobs = [j for j in booked_jobs if j['id'] != job_id]  # Remove the job
                db[f'{current_user_id}_BookedJobs'] = booked_jobs  # Save updated list

            return redirect(url_for('booking'))

    return render_template('leave.html', job=job)


@app.route('/viewLeaveRequests')
def view_leave_requests():
    ####
    if 'user_id' not in session:
        return redirect(url_for('login'))

    account_type = session.get('account_type')

    if account_type not in ['admin']:
        return redirect(url_for('login'))

    ####
    lr_list = get_leave_requests() # Load leave req from db

    return render_template('admin_leave_requests.html', leave_req=lr_list)

@app.route('/deleteLeaveRequest/<int:request_id>', methods=['POST'])
def delete_leave_request(request_id):
    ####
    if 'user_id' not in session:
        return redirect(url_for('login'))

    account_type = session.get('account_type')

    if account_type not in ['admin']:
        return redirect(url_for('login'))

    ####
    with shelve.open('leave_requests', 'c') as db:
        leave_requests = db.get('LeaveRequests', [])

        if 0 <= request_id < len(leave_requests):
            deleted_request = leave_requests.pop(request_id)
            db['LeaveRequests'] = leave_requests  # Update the database

            # Optionally, delete the file associated with the request
            if 'file_path' in deleted_request and os.path.exists(deleted_request['file_path']):
                os.remove(deleted_request['file_path'])

    return redirect(url_for('view_leave_requests'))

@app.route('/edit_leave_remark/<int:request_id>', methods=['GET', 'POST'])
def edit_leave_remark(request_id):
    ####
    if 'user_id' not in session:
        return redirect(url_for('login'))

    account_type = session.get('account_type')

    if account_type not in ['admin']:
        return redirect(url_for('login'))

    ####
    with shelve.open('leave_requests') as db:
        lr_list = db.get('LeaveRequests', [])
        if request_id < len(lr_list):
            leave_request = lr_list[request_id]
        else:
            flash("Leave request not found!", "danger")
            return redirect(url_for('view_leave_requests'))

    if request.method == 'POST':
        # Update the remark
        leave_request['remarks'] = request.form['remark']
        # saving back to db
        with shelve.open('leave_requests', writeback=True) as db:
            db['LeaveRequests'] = lr_list
        flash("Remark updated successfully!", "success")

        return redirect(url_for('view_leave_requests'))

    # Pass the leave_request data to the template
    return render_template('edit_remark.html', leave_request=leave_request, request_id=request_id)

@app.route('/updateLeaveRemark/<int:request_id>', methods=['POST'])
def update_leave_remark(request_id):
    ####
    if 'user_id' not in session:
        return redirect(url_for('login'))

    account_type = session.get('account_type')

    if account_type not in ['admin']:
        return redirect(url_for('login'))

    ####
    new_remark = request.form['remark']

    with shelve.open('leave_requests', 'c') as db:
        leave_requests = db.get('LeaveRequests', [])

        if 0 <= request_id < len(leave_requests):
            leave_requests[request_id]['remarks'] = new_remark
            db['LeaveRequests'] = leave_requests  # Update the database

    return redirect(url_for('view_leave_requests'))

# -- AYUB END --

# # route for view more details on posted job
# @app.route('/booking_more/<int:id>')
# def view_job(id):
#     db = shelve.open('bookings', 'r')
#     posted_job = db.get('Jobs', {})


# Load count id for job posting
Posting.PostingForm.load_count_id()
#########################
#KEBIN END# AYUBOO
#########################


#########################
#QWIS START#
#########################
from flask import Flask, render_template, request, redirect, url_for
import os, shelve

from Video import Video

ALLOWED_VIDEO_EXTENSIONS = {'mp4'}

# Function to check allowed file extensions
@app.route('/Tutorial')
def tutorial():
    videos = []
    with shelve.open('video.db', 'c') as db:
        if 'Videos' in db:
            videos_dict = db['Videos']
            videos = list(videos_dict.values()) # Retrieve all video objects


    return render_template('tutorial.html', videos=videos)

@app.route('/Add_video', methods=['GET', 'POST'])
def upload_video():
    ####
    if 'user_id' not in session:
        return redirect(url_for('login'))

    account_type = session.get('account_type')

    if account_type not in ['admin']:
        return redirect(url_for('login'))

    ####

    if request.method == 'POST':
        if 'video' not in request.files:
            return "No video file found"

        video = request.files['video']
        title = request.form.get('title','').strip()
        description = request.form.get('description', '').strip()


        if video.filename == "":
            return 'No video file selected'

        if not allowed_file(video.filename, 'video'):
            return "Invalid file type. Please select a mp4 file."

        if video and allowed_file(video.filename, 'video'):
            sanitized_title = title.replace(" ","_").replace(".","_")
            file_extension = video.filename.rsplit('.', 1)[1].lower()
            filename = f"{sanitized_title}.{file_extension}"
            video_path = os.path.join('static/videos', filename)
            video.save(video_path)

            # Create a Video object and save it to shelve
            new_video = Video(title=title, file_path=filename, description=description)

            with shelve.open('video.db', 'c') as db:
                if 'Videos' not in db:
                    db['Videos'] = {}

                videos_dict = db['Videos']
                videos_dict[new_video.get_id()] = new_video  # Add new video
                db['Videos'] = videos_dict  # Save back to shelve



            return redirect(url_for('tutorial'))
    return render_template('add_videos.html')

@app.route('/delete_video/<int:id>', methods=['POST'])
def delete_video(id):
    ####
    if 'user_id' not in session:
        return redirect(url_for('login'))

    account_type = session.get('account_type')

    if account_type not in ['admin']:
        return redirect(url_for('login'))

    ####
    with shelve.open('video.db', 'w') as db:
        videos_dict = db.get('Videos', {})

        if id in videos_dict:
            # Get the video to delete
            video_to_delete = videos_dict.pop(id)

            # Remove the file from the filesystem
            video_path = os.path.join('static/videos', video_to_delete.file_path)
            if os.path.exists(video_path):
                os.remove(video_path)

            # Save updated dictionary back to shelve
            db['Videos'] = videos_dict

    return redirect(url_for('tutorial'))

@app.route('/edit_video/<int:id>', methods=['GET', 'POST'])
def edit_video(id):
    ####
    if 'user_id' not in session:
        return redirect(url_for('login'))

    account_type = session.get('account_type')

    if account_type not in ['admin']:
        return redirect(url_for('login'))

    ####
    with shelve.open('video.db', 'w') as db:
        videos_dict = db.get('Videos', {})
        video = videos_dict.get(id)

        if not video:
            return "Video not found", 404

        if request.method == 'POST':
            # Update video title and description
            video.title = request.form['title']
            video.description = request.form['description']

            # Save updated video back to shelve
            videos_dict[id] = video
            db['Videos'] = videos_dict

            return redirect(url_for('tutorial'))

    return render_template('edit_video.html', video=video)
#########################
#QWIS END#
#########################


if __name__ == '__main__':
    app.run(debug=True)