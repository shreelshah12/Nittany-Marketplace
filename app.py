from flask import Flask, render_template, request
import sqlite3 as sql
import hashlib

app = Flask(__name__)

host = 'http://127.0.0.1:5000/'


@app.route('/listproduct', methods=['POST', 'GET'])
def listproducts():
    connection = sql.connect('identifier.sqlite')
    global usercurr
    #print(usercurr)
    cursor = connection.execute('SELECT Product_Listings.category, Product_Listings.title, Product_Listings.product_name, Product_Listings.product_description, Product_Listings.price, Product_Listings.quantity, Product_Listings.listing_id FROM Product_Listings WHERE seller_email = (?);',(usercurr,))
    r2 = cursor.fetchall()
    #print(r2)
    return render_template('listproduct.html', r2 = r2)

@app.route('/mainpage', methods=['POST', 'GET'])
def mainpage():
    return render_template('input.html')

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    return render_template('index.html')

@app.route('/createnewlisting', methods=['POST', 'GET'])
def newlisting():
    connection = sql.connect('identifier.sqlite')
    global usercurr
    cursor = connection.execute('SELECT email FROM Sellers WHERE email = (?);', (usercurr,))
    r1 = cursor.fetchall()
    if r1:
        if r1[0][0] == usercurr:
            #print(usercurr, "match found")
            cursor = connection.execute('SELECT category_name FROM Categories;')
            result = cursor.fetchall()
            return render_template('createnewlisting.html', result = result)
    return 'As a Buyer, You Do Not Have Access To List Products'

import random
counter = 2598
@app.route('/publish', methods=['POST', 'GET'])
def addproduct():
    connection = sql.connect('identifier.sqlite')
    cursor = connection.execute('INSERT INTO Product_Listings (seller_email, listing_id, category, title, product_name, product_description, price, quantity,enabled) VALUES (?,?,?,?,?,?,?,?,?);', (usercurr, random.randint(10000,20000), request.form['product_categorie'], request.form['product_title'], request.form['product_name'], request.form['product_description'], request.form['product_price'], request.form['available_quantity'], "TRUE"),)
    connection.commit()
    return listproducts()


@app.route('/unlist', methods=['POST', 'GET'])
def unlistproduct():
    connection = sql.connect('identifier.sqlite')
    cursor = connection.execute('SELECT enabled FROM Product_Listings WHERE listing_id = (?);', (request.form['list_id'],))
    result = cursor.fetchall()
    if request.method == "POST":
        if result[0][0] == "TRUE":

            connection.execute('UPDATE Product_Listings SET enabled="FALSE" WHERE listing_id =?;',(request.form['list_id'],))
            connection.commit()
        else:
            connection.execute('UPDATE Product_Listings SET enabled="TRUE" WHERE listing_id =?;',(request.form['list_id'],))
            connection.commit()

    return listproducts()

@app.route('/userinfo', methods=['POST', 'GET'])
def change():
    if (request.method == "POST"):
        update_pwd = request.form['save']
        connection = sql.connect('identifier.sqlite')
        hashed_update = hashlib.sha256(update_pwd.encode('utf-8')).hexdigest()
        cursor = connection.execute('UPDATE USERS SET password = (?) WHERE email = (?);', (hashed_update, usercurr))
        connection.commit()
        return render_template('userinfo.html', error= checkinfo(usercurr))

    r1 = checkinfo(usercurr)
    return render_template('userinfo.html', error = r1)


usercurr = ''
@app.route('/', methods=['POST', 'GET'])
def name():
    error = ""
    if request.method == 'POST':
        result = valid_name(request.form['email'], request.form['password'])
        global usercurr
        usercurr = request.form['email']
        #print(usercurr, "HI")
        if result == 'USER IS SUCCESSFULLY FOUND':
            return render_template('input.html')
        else:
            return render_template('index.html', error = 'USER NOT FOUND: Check Login Credentials')
    return render_template('index.html', error=error)




@app.route('/userinfo', methods=['POST', 'GET'])
def userinfo():
    result1 = checkinfo(usercurr)
    return render_template('userinfo.html', error = result1)


def valid_name(email, pwd):
    connection = sql.connect('identifier.sqlite')
    cursor = connection.execute('SELECT password FROM USERS WHERE email = (?);', (email,))
    # connection.commit()
    result = cursor.fetchone()
    if result is not None and result[0] == hashlib.sha256(pwd.encode('utf-8')).hexdigest():
        return 'USER IS SUCCESSFULLY FOUND'
    return "USER NOT FOUND: Check Login Credentials"


def checkinfo(email):
    connection = sql.connect('identifier.sqlite')
    cursor = connection.execute('SELECT USERS.email, BUYERS.first_name, BUYERS.last_name, BUYERS.gender, BUYERS.age, A1.street_num, A1.street_name, A1.zipcode, Z1.city, Z2.state_id, A2.street_num, A2.street_name, A2.zipcode, Z2.city, Z2.state_id, Credit_Cards.credit_card_num FROM USERS INNER JOIN BUYERS ON USERS.email = BUYERS.email INNER JOIN ADDRESS A1 ON Buyers.home_address_id = A1.address_id INNER JOIN ADDRESS A2 ON Buyers.billing_address_id = A2.address_id INNER JOIN Zipcode_Info Z1 on A1.zipcode = Z1.zipcode INNER JOIN Zipcode_Info Z2 on A2.zipcode = Z2.zipcode INNER JOIN Credit_Cards on BUYERS.email = Credit_Cards.owner_email WHERE BUYERS.email = (?);',(email,))
    result = cursor.fetchone()
    return result

@app.route('/products', methods=['POST', 'GET'])
def products():
    connection = sql.connect('identifier.sqlite')
    cursor = connection.execute('SELECT Product_Listings.category, Product_Listings.title, Product_Listings.product_name, Product_Listings.product_description, Product_Listings.price, Product_Listings.quantity, Product_Listings.seller_email FROM Product_Listings WHERE enabled="TRUE"')
    result = cursor.fetchall()
    return render_template('products.html', result = result)

@app.route('/sub1', methods=['POST', 'GET'])
def sub1():
    connection = sql.connect('identifier.sqlite')
    if request.method == 'POST':
        #print(request.form['cat1'])
        cursor = connection.execute('SELECT category_name FROM Categories WHERE parent_category = ?;',(request.form['cat1'],))
        result = cursor.fetchall()
        #print(result)
        return render_template('sub1.html', result=result)
    return render_template('sub1.html')


@app.route('/sub2', methods=['POST', 'GET'])
def sub2():
    connection = sql.connect('identifier.sqlite')
    if request.method == "POST":
        # print(request.form['cat2'])
        cursor = connection.execute('SELECT category_name FROM Categories WHERE parent_category = ?;',(request.form['cat2'],))
        result = cursor.fetchall()
        # print(result)
        return render_template('sub3.html', result = result)

    return render_template('sub3.html')

@app.route('/finalproduct', methods=['POST', 'GET'])
def finalproduct():
    connection = sql.connect('identifier.sqlite')
    cursor = connection.execute('SELECT Product_Listings.category, Product_Listings.title, Product_Listings.product_name, Product_Listings.product_description, Product_Listings.price, Product_Listings.quantity, Product_Listings.seller_email FROM Product_Listings WHERE category = (?) AND enabled="TRUE";', (request.form['cat3'],))
    result = cursor.fetchall()
    return render_template('finalproduct.html', result = result)





if __name__ == "__main__":
    app.run()

