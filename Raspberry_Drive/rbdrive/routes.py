#sources: https://www.youtube.com/channel/UCCezIgC97PvUuR4_gbFUs5g
from flask import render_template, url_for, flash, redirect, request, Response
from rbdrive import app, db, bcrypt
from .rbd_storage import *
from rbdrive.forms import RegistrationForm, LoginForm
from rbdrive.models import *
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = '/home/miguel/Raspberry_Drive/rbdrive/static'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/",methods=['GET','POST'])
@app.route("/login", methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('account'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('login'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)



@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('Account'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)





@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/account", methods=['GET', 'POST'])
@login_required

def account():

    if request.method == "POST":

        if request.files:
                
            folder = Folder(current_user.username,None,rbddev_test_bucket)
            file = request.files["file"]
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], file.filename))

            file =File(file.filename,None,rbddev_test_bucket,current_user.username+"/"+file.filename, "/home/miguel/Raspberry_Drive/rbdrive/static/" + file.filename)

            flash('File Saved', 'success')
            print("Image saved", current_user.username)



            return redirect(request.url)
        return render_template('account.html', title='Account')
    else:
        #username = current_user.username
        #unit= Unit(current_user.username,None,rbddev_test_bucket)
        #unit.Download('/'+username)     
       
        #file = s3.Bucket(rbddev_test_bucket).Object('credentials.csv')
        summaries = rbddev_test_bucket.objects.filter( Prefix=str(current_user.username))

        #unit = Unit(current_user.username, None, rbddev_test_bucket)
        #for file in rbddev_test_bucket.objects.filter( Prefix=str(current_user.username)):
        #    print(file.key)
        #    unit.Download('/home/miguel/Raspberry_Drive/static')

        return render_template('account.html', title='Account',bucket = rbddev_test_bucket, files = summaries)

    
@app.route('/delete', methods=['POST'])
def delete():
    key = request.form['key']

   
    rbddev_test_bucket.Object(key).delete()

    flash('File deleted successfully')
    return redirect(url_for('files'))


@app.route('/download', methods=['POST'])
def download():
    key = request.form['key']

    file_obj = rbddev_test_bucket.Object(key).get()

    return Response(
        file_obj['Body'].read(),
        mimetype='text/plain',
        headers={"Content-Disposition": "attachment;filename={}".format(key)}
     )


#def download_file_with_client(key):
  
#    client.download_file(bucket_name, key, local_path)
 #   print('Downloaded frile with boto3 client')




#local_path = '<e.g. ./log.txt>'

#download_file_with_client(access_key, secret_key, bucket_name, key, local_path)


