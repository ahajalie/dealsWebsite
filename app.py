# from flask import Flask, render_template, session, app, request
from flask import *
from flask.ext.sqlalchemy import SQLAlchemy
import MySQLdb
import os
import hashlib
import mimetypes
import sys
reload(sys)
sys.setdefaultencoding("ISO-8859-1")

app = Flask(__name__, template_folder='views', static_folder="static")
app.secret_key = '\x03\xbf\x9e8\xc7\xb2y,on\xac\xbe\x16\xf3+h\x15fY\xd7mS\x0b\x02'
mimetypes.add_type('image/svg+xml', '.svg')

db = SQLAlchemy()

# dbconfig = {
# 	'user': 'root',
# 	# 'passwd': 'thebesteecsgroupever',
# 	'host': 'localhost',
# 	'db': 'dealsWebsite'
# 	# 'db' : 'website'
# }

# @app.before_request
# def make_session_permanent():
# 	session.permanent = True

codesDB = {
	'user': 'root',
	# 'passwd': 'thebesteecsgroupever',
	'host': 'localhost',
	'db': 'dealsWebsite'
	# 'db' : 'website'
}

dbconfig = {
	'user': 'hajalie7',
	'passwd': 'broncos24',
	'host': 'hajalie7.mysql.pythonanywhere-services.com',
	'db' : 'hajalie7$default'
}

@app.route('/', methods=['GET', 'POST'])
def index():
	# flash("hello")
	if 'logged_in' in session:
		return redirect('/deals')
	if request.method == 'POST':
		#handle login or registration
		if "sign_up" in request.form:
			db = MySQLdb.connect(**dbconfig)
			cur = db.cursor(MySQLdb.cursors.DictCursor);
			email = request.form['email'].lower()
			cur.execute('''SELECT * 
			FROM User 
			WHERE email=%s ''', (email,))
			users = cur.fetchall();
			if (len(users) > 0):
				flash("Error: Email already exists, please try again")
			elif (request.form['password0'] != request.form['password1']):
				flash("Error: Passwords do not match, please try again")
			elif (len(request.form['password0']) < 6):
				flash("Error: Password must be at least 6 characters long")
			else:
				salt = os.urandom(8)
				password = str(request.form['password0']) + salt;
				password = str(hashlib.sha1(password).hexdigest())
				cur.execute('''INSERT INTO User(email, salt, pass, isSeller) VALUES (%s, %s, %s, 0) ''',
						(email, salt, password,))
				db.commit()
				cur.execute('''SELECT * 
					FROM User 
					WHERE email=%s and pass=%s''', (email, password,))
				users = cur.fetchall()
				cur.close()
				db.close()
				if(len(users) == 0):
					return str("Unknown error has occurred")
				user = users[0]				
				session['user'] = email
				session['id'] = user['id']
				session['logged_in'] = True
				session['seller'] = 0
				session.permanent = True;
				return redirect('/deals')
		elif "log_in" in request.form:
				db = MySQLdb.connect(**dbconfig)
				cur = db.cursor(MySQLdb.cursors.DictCursor);
				loginemail = request.form['loginemail'].lower()
				cur.execute('''SELECT salt 
					FROM User 
					WHERE email=%s''', (loginemail,))
				users = cur.fetchall()
				salt = "";
				if(len(users) != 0):
					salt = users[0]['salt']
				password = str(request.form['loginpassword']) + salt;
				password = str(hashlib.sha1(password).hexdigest())
				cur.execute('''SELECT * 
					FROM User 
					WHERE email=%s and pass=%s''', (loginemail, password,))
				users = cur.fetchall();
				cur.close()
				db.close()
				if (len(users) == 0):
					flash("There was a problem logging in. Either the email address or password is incorrect")
					return render_template("index.html")
				else:
					user = users[0]
					session['user'] = loginemail
					session['id'] = user['id']
					session['logged_in'] = True
					session['seller'] = user['isSeller']
					session.permanent = True
					return redirect('/')
		return redirect('/')
	# flash('hello')
	return render_template("index.html");

# @app.route('/deals', methods=['GET'])
# def deals():
# 	return render_template("deals.html")

@app.route('/deals', methods=['GET'])
def secretdeals():
	if ('logged_in' in session):
		print session['user']
	# else:
		# return redirect('/')
	db = MySQLdb.connect(**dbconfig)
	cur = db.cursor(MySQLdb.cursors.DictCursor);
	searchTerm = "%%"
	offset = (0)
	pageNumber = request.args.get('page')
	if (pageNumber != None):
		offset = int(request.args.get('page')) * 200
	else:
		pageNumber = 0
	searchTerms = request.args.get('s')
	whereClause = ""
	words = []
	if(searchTerms != None):
		words = searchTerms.split(' ')
		whereClause = 'WHERE productTitle LIKE %s'
		words[0] = '%' + words[0] + '%'
		for index, word in enumerate(words):
			if index == 0:
				continue
			words[index] = '%' + word + '%'
			whereClause += " and productTitle LIKE %s "
	else:
		searchTerms = ""
	if (request.args.get('q') != None):
		whereClause += request.args.get('q')
	# return whereClause
	sqlTuples = tuple(words)
	sqlTuples = sqlTuples + (offset,)
	# return str(sqlTuples)
	query = 'SELECT * from Product ' + whereClause + ' ORDER BY startDate DESC LIMIT 0 OFFSET %s'
	# return str(query)
	cur.execute(query, sqlTuples)
	products = cur.fetchall()
	cur.close()
	db.close()
	loadLeftButton = False
	loadRightButton = False
	if(offset > 0):
		loadLeftButton = True
	if(len(products) == 200):
		loadRightButton = True
	# return str(products[0])
	# print int(session['seller'])
	return render_template("deals.html", isSeller = int(session['seller']), products=products, pageNumber=pageNumber, searchValue=searchTerms, 
		prevPage=loadLeftButton, nextPage=loadRightButton);

def url_for_other_page(currentPage, offset):
    args = request.view_args.copy()
    page = int(currentPage) + int(offset)
    args['s'] = request.args.get('s')
    args['q'] = request.args.get('q')    
    args['page'] = page    
    print str(url_for(request.endpoint, **args))
    return url_for(request.endpoint, **args)

app.jinja_env.globals['url_for_other_page'] = url_for_other_page



@app.route('/sellerPortal', methods=['GET', 'POST']) 
def sellerPortal():
	if ('logged_in' not in session):
		return redirect('/')
	if session['seller'] != 1:
		return redirect('/')
	if request.method == 'POST':
		db = MySQLdb.connect(**dbconfig)
		cur = db.cursor(MySQLdb.cursors.DictCursor);

		title = request.form['title']
		normalPrice = request.form['normalPrice']
		promoPrice = request.form['promoPrice']
		productURL = request.form['productURL']
		imageURL = request.form['imageURL']
		description = request.form['description']
		codes = request.form['codes']
		sellerEmail = session['user']
		duration = int(request.form['duration'])
		# cur.execute('''SELECT id from User WHERE email=%s''', (sellerEmail,))
		# sellerIdQueryResults = cur.fetchall()
		sellerID = session['id']
		# if(len(sellerIdQueryResults) > 0):
		# 	sellerID = sellerIdQueryResults[0]['id']
		# else:
			# return str("An error has occurred. Sorry")
		tuples = (title, normalPrice, promoPrice, productURL, imageURL, description, codes, sellerEmail, sellerID, 0, duration)

		cur.execute('''INSERT INTO Product (productTitle, normalPrice, promoPrice, productURL, imageURL, description, codeInput, sellerEmail, sellerID, status, duration)
			VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''', tuples)
		db.commit()
		db.close()
		cur.close()
		return redirect('/sellerPortal')
	if request.method == 'GET':
		db = MySQLdb.connect(**dbconfig)
		cur = db.cursor(MySQLdb.cursors.DictCursor);
		sellerID = int(session['id'])
		cur.execute('''SELECT id as productID, productTitle, imageURL, normalPrice, promoPrice
				FROM Product WHERE sellerID=%s and status=0''', (sellerID,) )
		unapprovedProducts = cur.fetchall()
		print unapprovedProducts
		cur.execute('''SELECT id as productID, productTitle, imageURL, normalPrice, promoPrice
				FROM Product WHERE id=%s and status=1''', (sellerID,) )
		approvedProducts = cur.fetchall()
		return render_template("sellerPortal.html", unapprovedProducts=unapprovedProducts, approvedProducts=approvedProducts)

@app.route('/editItem', methods=['GET', 'POST'])
def editItem():
	if ('logged_in' not in session):
		return redirect('/')
	if session['seller'] != 1:
		return redirect('/')
	db = MySQLdb.connect(**dbconfig)
	cur = db.cursor(MySQLdb.cursors.DictCursor);
	if request.method == 'GET':
		sellerID = int(session['id'])
		productID = request.args.get('id')
		if productID == None:
			return str("An error has occurred")
		cur.execute('''SELECT id as productID, productTitle, imageURL, productURL, normalPrice, promoPrice, description, codeInput, duration
				FROM Product WHERE sellerID=%s and status=0 and id=%s''', (sellerID, productID,) )
		product = cur.fetchall()
		print product
		if(len(product) == 0):
			return str("An error has occurred. Sorry")
		product = product[0]
		return render_template("editItem.html", product=product)
	if request.method == 'POST':
		db = MySQLdb.connect(**dbconfig)
		cur = db.cursor(MySQLdb.cursors.DictCursor);

		title = request.form['title']
		normalPrice = request.form['normalPrice']
		promoPrice = request.form['promoPrice']
		productURL = request.form['productURL']
		imageURL = request.form['imageURL']
		description = request.form['description']
		codes = request.form['codes']
		sellerEmail = session['user']
		sellerID = session['id']
		productID = int(request.form['productID'])
		duration = request.form['duration']

		tuples = (title, normalPrice, promoPrice, productURL, imageURL, description, codes, sellerID, productID, duration)

		cur.execute('''UPDATE Product SET productTitle= %s, normalPrice=%s, promoPrice=%s, productURL=%s, imageURL=%s, description=%s, codeInput=%s, duration=%s 
			WHERE sellerID=%s and id=%s''', tuples)
		db.commit()
		db.close()
		cur.close()
		return redirect('/sellerPortal')



@app.route('/product', methods=['GET'])
def product():	
	productID = request.args.get('id')
	if(productID != None):
		db = MySQLdb.connect(**dbconfig)
		cur = db.cursor(MySQLdb.cursors.DictCursor);
		query = '''SELECT CODE FROM Code1 WHERE product_id=%s'''
		cur.execute(query, (productID,))
		codes = cur.fetchall()
		picURL = request.args.get('picurl')
		returnString = ""
		if(picURL != None):
			returnString = "<img src=\"" + picURL + "\"><br/>"
		for code in codes:
			returnString += code['CODE'] + "<br/>"
		cur.close()
		db.close()
		return str(returnString)
	else:
		return redirect('/')

@app.route('/products', methods=['GET'])
def myProducts():
	return redirect('/')	

@app.route('/myaccount', methods=['GET', 'POST'])
def myAccount():
	if 'logged_in' not in session:
		return redirect('/')
	if request.method == 'POST':
		db = MySQLdb.connect(**dbconfig)
		cur = db.cursor(MySQLdb.cursors.DictCursor);
		if "become_seller" in request.form:
			cur.execute('''UPDATE User SET isSeller=1 WHERE id=%s''', (session['id'],))
			db.commit()
			session['seller'] = 1
			flash("You are now a seller! View the seller portal above to list your products!", "success-occurred")
		# elif "update_email" in request.form:
		# 	cur.execute('''SELECT * FROM USER WHERE id=%s''', (session['id'],))
		# 	users = cur.fetchall()
		# 	if len(users) == 0:
		# 		return str("An unknown error occurred. Sorry")
		# 	user = users[0]
		# 	salt = users[0]['salt']
		# 	oldpassword = str(request.form['emailpassword']) + salt;
		# 	oldpassword = str(hashlib.sha1(oldpassword).hexdigest())
		# 	email = request.form['email'].lower()
		# 	cur.execute('''SELECT * FROM USER WHERE email=%s''', (email,))
		# 	users = cur.fetchall()
		# 	if oldpassword != user['pass']:
		# 		flash("Current password given is incorrect", "error-occurred")
		# 		db.close()
		# 		cur.close()
		# 		return redirect('/myaccount')			
		# 	#Telling User about email address, insecure, possibly fix
		# 	elif len(users) > 0:
		# 		flash("Error: An account with that email address already exists", "error-occurred")
		# 	else:
		# 		cur.execute('''UPDATE User SET email=%s WHERE id=%s''', 
		# 			(email, session['id'],))
		# 		db.commit()
		# 		flash("Email successfully changed!", "success-occurred")
		elif "update_password" in request.form:
			#first, check if passwords match
			password = str(request.form['password0'])
			password2 = str(request.form['password1'])
			if password != password2:
				flash("Passwords do not match", "error-occurred")
				db.close()
				cur.close()
				return redirect('/myaccount')			
			#yes, i am copy pasting. sorry
			cur.execute('''SELECT * FROM User WHERE id=%s''', (session['id'],))
			users = cur.fetchall()
			if len(users) == 0:
				return str("An unknown error occurred. Sorry")
			user = users[0]
			salt = users[0]['salt']
			oldpassword = str(request.form['emailpassword']) + salt;
			oldpassword = str(hashlib.sha1(oldpassword).hexdigest())
			password = password + salt
			password = str(hashlib.sha1(password).hexdigest())
			if oldpassword != user['pass']:
				flash("Current password given is incorrect", "error-occurred")
				db.close()
				cur.close()
				return redirect('/myaccount')
			else:
				cur.execute('''UPDATE User SET pass=%s WHERE id=%s''', (password, session['id'],))
				flash("Password successfully changed", "success-occurred")
		db.close()
		cur.close()
		return redirect('/myaccount')
	if 'seller' in session:
		isSeller = int(session['seller'])
	else:
		isSeller = 0
	return render_template("myaccount.html", isSeller=isSeller)

@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	session['user'] = None
	session['seller'] = None
	session['id'] = None
	return redirect('/')

# comment this out using a WSGI like gunicorn
# if you dont, gunicorn will ignore it anyway
if __name__ == '__main__':
    # listen on external IPs
    app.run(host='localhost', port=3000, debug=True)
    # app.run(host='0.0.0.0')
    # app.run(host='eecs485-10.eecs.umich.edu', port=5914, debug=True)
