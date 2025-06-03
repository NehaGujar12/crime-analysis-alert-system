#import of packages, Libraries and modules.
from flask import Flask,render_template, request, flash, url_for,jsonify
import pandas as pd
import numpy as np
from flask import json
from flask import Flask, render_template, request, url_for

import smtplib
from email.message import EmailMessage
import imghdr
import os
from flask import session
import joblib
#from sklearn import cross_validation,preprocessing
from sklearn.linear_model import LinearRegression
#from sklearn.externals import joblib
from sklearn.ensemble import RandomForestRegressor
from plotly.offline import init_notebook_mode, iplot
from sklearn.model_selection import train_test_split
from flask_mail import Mail, Message

import joblib
#from sklearn import cross_validation,preprocessing
from sklearn.linear_model import LinearRegression
#from sklearn.externals import joblib
from sklearn.ensemble import RandomForestRegressor
from plotly.offline import init_notebook_mode, iplot
from sklearn.model_selection import train_test_split
from flask_mail import Mail, Message
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


#Starting of flask app
app = Flask(__name__)


app.secret_key = '31206b7b80bb51fafd95fcea504e7edc'
app.config['UPLOAD_FOLDER'] = 'static'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)  # Added back
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)




@app.route("/")
def index():
	return render_template("index.html")

@app.route("/home")
def Home():
	return render_template("home.html")

@app.route('/pred.html')
def pred():
	return render_template("pred.html")

@app.route('/vis.html')
def viz():
	return render_template("vis.html")

@app.route('/womenViz.html')
def womenViz():	
	return render_template('womenViz.html')

@app.route('/childrenViz.html')
def childrenViz():	
	return render_template('childrenViz.html')

@app.route('/IPCViz.html')
def IPCViz():	
	return render_template('IPCViz.html')

@app.route('/highlights.html')
def highlights():
	return render_template("highlights.html")



# @app.route('/prediction', methods=['GET', 'POST'])
# def upload_page():
#     if request.method == 'POST':
#         if 'file' not in request.files:
#             return render_template("upload.html", msg='No File Selected!')

#         file = request.files['file']

#         if file.filename == '':
#             return render_template("upload.html", msg='No File!')

#         if file and allowed_file(file.filename):
#             file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
#             img_src = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            
            
#             return render_template("Imageupload.html", msg="Image Upload Sucessfully!", user_image=file.filename)

#         else:
#             return render_template('upload.html', msg="Invalid File Format!")
		

@app.route('/women.html',methods = ['POST'])
def women():

	year = request.form.get("Predict_Year")		#Year fetching From UI.
	C_type = request.form.get("C_Type")			#Crime type fetching from UI
	state = request.form.get("state")			#State name fetching from UI
	
	df = pd.read_csv("static/StateWiseCAWPred1990-2016.csv", header=None)

	data1 = df.loc[df[0]==state].values			#Selecting State and its attributes.
	for x in data1:
		if x[1] == C_type:
			test = x
			break


	l = len(df.columns)					
	trendChangingYear = 2	

	xTrain = np.array([1990,1991,1992,1993,1994,1995,1996,1997,1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016])
	yTrain = test[2:29]

	X = df.iloc[0,2:l].values
	y = test[2:]
	regressor = LinearRegression()		#regression algorithm cealled.
	regressor.fit(X.reshape(-1,1),y)	#Data set is fitted in regression and Reshaped it.
	accuracy = regressor.score(X.reshape(-1,1),y)	#Finding Accuracy of Predictions.
	print("accuracy")
	accuracy_max = 0.65

	#Trending year(Influence Year) finding algorithm.
	if(accuracy < 0.65):			#Used 65% accuracy as benchmark for trending year finding algorithm.
		for a in range(3,l-8):

			X = df.iloc[0,a:l].values
			y = test[a:]
			regressor = LinearRegression()
			regressor.fit(X.reshape(-1,1),y)
			accuracy = regressor.score(X.reshape(-1,1),y)
			if (accuracy > accuracy_max):
				accuracy_max = accuracy
				print("accuracy_max")
				trendChangingYear = a
	print("trendChangingYear")			#Printing Trend Changing Year on server terminal.
	print ("test[trendChangingYear]")
	print("xTrain[trendChangingYear-2]")
	year = int(year)
	y = test[2:]
	b = []

	#If accuracy is Lower than 65%, only visualization of the data is shown - no predictions
	if accuracy < 0.65:				
		for k in range(2001,2017):
			a = str(k)
			b = np.append(b,a)
		y = list(y)
		yearLable = list(b)
		msg = "Data is not Sutaible for prediction"

	#Else predictions are shown and Run time data and labels are added to the graph.
	else:

		for j in range(2017,year+1):
			prediction = regressor.predict(j)
			if(prediction < 0):
				prediction = 0
			y = np.append(y,prediction)
		y = np.append(y,0)

		for k in range(1990,year+1):
			a = str(k)
			b = np.append(b,a)
		y = list(y)
		yearLable = list(b)
		msg = ""
	if C_type == "ASSAULT ON WOMEN WITH INTENT TO OUTRAGE HER MODESTY":
		C_type = "ASSAULT ON WOMEN"
	#Finally the template is rendered
	return render_template('women.html',data = [accuracy,yTrain,xTrain,state,year,data1,X,y,test,l],msg = msg,state=state, year=year, C_type=C_type,pred_data = y,years = yearLable)

@app.route('/children.html',methods = ['POST'])
def children():

	year = request.form.get("Predict_Year")		#Year fetching From UI.
	C_type = request.form.get("C_Type")			#Crime type fetching from UI
	state = request.form.get("state")			#State name fetching from UI

	#reading CSV file.
	df = pd.read_csv("static/Statewise Cases Reported of Crimes Committed Against Children 1994-2016.csv", header=None)

	data1 = df.loc[df[0]==state].values			#Selecting State and its attributes.
	for x in data1:
		if x[1] == C_type:
			test = x
			break


	l = len(df.columns)

	trendChangingYear = 2
	accuracy_max = 0.65

	# Year array for Javascript for Labeling to the Graph  
	xTrain = np.array([1994,1995,1996,1997,1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016])
	yTrain = test[2:25]

	X = df.iloc[0,2:l].values
	y = test[2:]
	regressor = LinearRegression()		#regression Algorithm Called.
	regressor.fit(X.reshape(-1,1),y)	#Data set is fitted in regression and Reshaped it.
	accuracy = regressor.score(X.reshape(-1,1),y)	#Finding Accuracy of Prdictions.
	print("accuracy")
	accuracy_max = 0.65
	if(accuracy < 0.65):
		for a in range(3,l-4):

			X = df.iloc[0,a:l].values
			y = test[a:]
			regressor = LinearRegression()
			regressor.fit(X.reshape(-1,1),y)
			accuracy = regressor.score(X.reshape(-1,1),y)
			if (accuracy > accuracy_max):
				accuracy_max = accuracy
				print("accuracy_max")
				trendChangingYear = a
	print("trendChangingYear")			#Printing Trend Changing Year on server terminal.
	print("test[trendChangingYear]")
	print("xTrain[trendChangingYear-2]")
	yTrain = test[trendChangingYear:]
	xTrain = xTrain[trendChangingYear-2:]
	regressor.fit(xTrain.reshape(-1,1),yTrain)
	accuracy = regressor.score(xTrain.reshape(-1,1),yTrain)

	year = int(year)
	y = test[2:]
	b = []
	if accuracy < 0.65:
		for k in range(2001,2017):
			a = str(k)
			b = np.append(b,a)
		y = list(y)
		yearLable = list(b)
		year = 2016
		msg = "Data is not Suitable for prediction"
	else:

		for j in range(2017,year+1):
			prediction = regressor.predict(j)
			if(prediction < 0):
				prediction = 0
			y = np.append(y,prediction)
		y = np.append(y,0)

		for k in range(1994,year+1):
			a = str(k)
			b = np.append(b,a)
		y = list(y)
		yearLable = list(b)
		msg = ""

	return render_template('children.html',data = [accuracy,yTrain,xTrain,state,year,data1,X,y,test,l],state=state, year=year,msg=msg, C_type=C_type,pred_data = y,years = yearLable)

@app.route('/ipc.html',methods = ['POST'])
def ipc():

	year = request.form.get("Predict_Year")		#Year fetching From UI.
	C_type = request.form.get("C_Type")			#Crime type fetching from UI
	state = request.form.get("state")			#State name fetching from UI

	#reading CSV file.
	df = pd.read_csv("static/StateIPCPred2001_16.csv", header=None)

	data1 = df.loc[df[0]==state].values			#Selecting State and its attributes.
	for x in data1:
		if x[1] == C_type:
			test = x
			break


	l = len(df.columns)
	trendChangingYear = 2
	accuracy_max = 0.65

	# Year array for Javascript for Labeling to Graph  
	xTrain = np.array([2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016])
	yTrain = test[2:18]

	X = df.iloc[0,2:l].values
	y = test[2:]
	regressor = LinearRegression()		#regression Algorithm Called.
	regressor.fit(X.reshape(-1,1),y)	#Data set is fitted in regression and Reshaped it.
	accuracy = regressor.score(X.reshape(-1,1),y)	#Finding Accuracy of Prdictions.

	print("accuracy")
	accuracy_max = 0.65

	#Trending year(Influence Year) finding algorithm.
	if(accuracy < 0.65):			#Used 65% accuracy as benchmark for trending year finding algorithm.
		for a in range(3,l-4):

			X = df.iloc[0,a:l].values
			y = test[a:]
			regressor = LinearRegression()
			regressor.fit(X.reshape(-1,1),y)
			accuracy = regressor.score(X.reshape(-1,1),y)
			if (accuracy > accuracy_max):
				accuracy_max = accuracy
				print("accuracy_max")
				trendChangingYear = a
	print("trendChangingYear")				#Printing Trend Changing Year on server terminal.
	print("test[trendChangingYear]")
	print("xTrain[trendChangingYear-2]")
	year = int(year)
	y = test[2:]
	b = []

	#If accuracy is Lower than 65%, only Visualization of the data is shown - no predictions.
	if accuracy < 0.65:
		for k in range(2001,2017):
			a = str(k)
			b = np.append(b,a)
		y = list(y)
		yearLable = list(b)
		year = 2016
		msg = "Data is not Suitable for prediction"

	#Else predictions are shown and Run time data and labels are added to the graph.
	else:

		for j in range(2017,year+1):
			prediction = regressor.predict(j)
			if(prediction < 0):
				prediction = 0
			y = np.append(y,prediction)
		y = np.append(y,0)

		for k in range(2001,year+1):
			a = str(k)
			b = np.append(b,a)
		y = list(y)
		yearLable = list(b)
		msg = ""
	
	#Finally the template is rendered.
	return render_template('ipc.html',data = [accuracy,yTrain,xTrain,state,year,data1,X,y,test,l],msg = msg, state=state, year=year, C_type=C_type,pred_data = y,years = yearLable)


@app.route('/sll.html',methods = ['POST'])
def sll():

	year = request.form.get("Predict_Year")		#Year fetching From UI.
	C_type = request.form.get("C_Type")			#Crime type fetching from UI
	state = request.form.get("state")			#State name fetching from UI

	#reading CSV file.
	df = pd.read_csv("static/StateSLLPred2001_16.csv", header=None)

	data1 = df.loc[df[0]==state].values			#Selecting State and its attributes.
	for x in data1:
		if x[1] == C_type:
			test = x
			break


	l = len(df.columns)
	trendChangingYear = 2
	accuracy_max = 0.65

	# Year array for Javascript for Labeling to Graph  
	xTrain = np.array([2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016])
	yTrain = test[2:18]

	X = df.iloc[0,2:l].values
	y = test[2:]
	regressor = LinearRegression()		#regression Algorithm Called.
	regressor.fit(X.reshape(-1,1),y)	#Data set is fitted in regression and Reshaped it.
	accuracy = regressor.score(X.reshape(-1,1),y)	#Finding Accuracy of Prdictions.
	print("accuracy")
	accuracy_max = 0.65

	#Trending year(Influence Year) finding algorithm.
	if(accuracy < 0.65):			#Used 65% accuracy as benchmark for trending year finding algorithm.
		for a in range(3,l-4):

			X = df.iloc[0,a:l].values
			y = test[a:]
			regressor = LinearRegression()
			regressor.fit(X.reshape(-1,1),y)
			accuracy = regressor.score(X.reshape(-1,1),y)
			if (accuracy > accuracy_max):
				accuracy_max = accuracy
				print("accuracy_max")
				trendChangingYear = a
	print("trendChangingYear")				#Printing Trend Changing Year on server terminal.
	print("test[trendChangingYear]")
	print("xTrain[trendChangingYear-2]")
	year = int(year)
	y = test[2:]
	b = []

	#If accuracy is Lower than 65%, only Visualization of the data is shown - not predictions.
	if accuracy < 0.65:
		for k in range(2001,2017):
			a = str(k)
			b = np.append(b,a)
		y = list(y)
		yearLable = list(b)
		year = 2016
		msg = "Data is not Suitable for prediction"

	#Else predictions are shown and Run time data and labels are added to the graph.
	else:

		for j in range(2017,year+1):
			prediction = regressor.predict(j)
			if(prediction < 0):
				prediction = 0
			y = np.append(y,prediction)
		y = np.append(y,0)

		for k in range(2001,year+1):
			a = str(k)
			b = np.append(b,a)
		y = list(y)
		yearLable = list(b)
		msg = ""
	
	#Finally the template is rendered.
	return render_template('sll.html',data = [accuracy,yTrain,xTrain,state,year,data1,X,y,test,l],msg = msg, state=state, year=year, C_type=C_type,pred_data = y,years = yearLable)







# Allowed file extensions for image upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static/uploads')

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def send_email_with_attachment(to_email, subject, body, attachment_path=None):
    """Send an email with an optional image attachment."""
    sender_email = "pragati.code@gmail.com"
    sender_password = "grqheqzoutabdfzd"

    # Create EmailMessage object
    new_message = EmailMessage()
    new_message['Subject'] = subject
    new_message['From'] = sender_email
    new_message['To'] = to_email
    new_message.set_content(body)

    # Attach image if provided
    if attachment_path and os.path.exists(attachment_path):
        with open(attachment_path, 'rb') as f:
            image_data = f.read()
            image_type = imghdr.what(f.name)
            image_name = os.path.basename(attachment_path)
        new_message.add_attachment(image_data, maintype='image', subtype=image_type, filename=image_name)

    # Send the email
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(new_message)
            print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {str(e)}")

@app.route('/Imageupload.html', methods=['GET', 'POST'])
def Imageupload():
    file_url = None
    submitted_text = None

    if request.method == 'POST':
        # Handle text input
        submitted_text = request.form.get('entry', None)

        # Handle image upload
        file = request.files.get('upload', None)
        if file and allowed_file(file.filename):
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            file_url = url_for('static', filename=f'uploads/{filename}')

            # Email configuration
            email_subject = "Uploaded Image and Details"
            email_body = f"Hi,\n\nThe user has submitted the following text:\n{submitted_text}\n\nAttached is the uploaded image."
            recipient_email = "tanmayghadigaonkar2003@gmail.com"

            # Send email with attachment
            send_email_with_attachment(
                to_email=recipient_email,
                subject=email_subject,
                body=email_body,
                attachment_path=file_path
            )
        else:
            # If no file or invalid file format
            file_url = None

    return render_template('Imageupload.html', file_url=file_url, submitted_text=submitted_text)

#############################################################################################3


#routing Path for About page.
@app.route('/About.html')
def About():
	return render_template("/About.html")


from flask import Flask, render_template, request, redirect, url_for
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            return 'Username already exists!'
        if User.query.filter_by(email=email).first():
            return 'Email already exists!'

        new_user = User(full_name=full_name, email=email, username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))
    return render_template('Registration.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            session['logged_in'] = True
            return redirect(url_for("Home"))
        return 'Invalid credentials'
    return render_template('login.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000, debug=True)



