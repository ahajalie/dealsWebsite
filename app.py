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
	# 'db': 'dealsWebsite'
	'db' : 'website'
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
			else:
				salt = os.urandom(8)
				password = str(request.form['password0']) + salt;
				password = str(hashlib.sha1(password).hexdigest())
				cur.execute('''INSERT INTO User(email, salt, pass) VALUES (%s, %s, %s) ''',
						(email, salt, password,))
				db.commit()
				cur.close()
				db.close()
				session['user'] = email
				session['logged_in'] = True
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
				if (len(users) == 0):
					flash("There was a problem logging in. Either the email address or password is incorrect")
					return render_template("index.html")
				else:
					user = users[0]
					session['user'] = loginemail
					session['id'] = user['id']
					session['logged_in'] = True
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
	db = MySQLdb.connect(**codesDB)
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
	query = 'SELECT * from Product ' + whereClause + ' ORDER BY startDate DESC LIMIT 200 OFFSET %s'
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
	return render_template("deals.html", products=products, pageNumber=pageNumber, searchValue=searchTerms, 
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

@app.route('/product', methods=['GET'])
def product():	
	productID = request.args.get('id')
	if(productID != None):
		db = MySQLdb.connect(**codesDB)
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

@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	session['user'] = None
	return redirect('/')

# comment this out using a WSGI like gunicorn
# if you dont, gunicorn will ignore it anyway
if __name__ == '__main__':
    # listen on external IPs
    app.run(host='localhost', port=3000, debug=True)
    # app.run(host='0.0.0.0')
    # app.run(host='eecs485-10.eecs.umich.edu', port=5914, debug=True)
