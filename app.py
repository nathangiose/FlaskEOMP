import hmac
from flask import *
from flask_mail import Mail, Message
from smtplib import SMTPRecipientsRefused
from flask_cors import CORS
from flask_jwt import JWT
import sqlite3

import cloudinary
import cloudinary.uploader


class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


class Admin(object):
    def __init__(self, admin_id, admin_username, admin_password):
        self.admin_id = admin_id
        self.admin_username = admin_username
        self.admin_password = admin_password


class Database(object):
    def __init__(self):
        self.conn = sqlite3.connect('UTA_Enrollment')
        self.cursor = self.conn.cursor()

    def sending_to_database(self, query, values):
        self.cursor.execute(query, values)
        self.conn.commit()

    def single_select(self, query):
        self.cursor.execute(query)
        self.conn.commit()

    def fetch(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()


# fetching users from the database
def fetch_users():
    with sqlite3.connect('UTA_Enrollment') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user")
        users_data = cursor.fetchall()

        new_data = []

        for data in users_data:
            new_data.append(User(data[0], data[5], data[6]))

        return new_data


# creating table for users
def init_user_table():
    conn = sqlite3.connect('UTA_Enrollment')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS user (user_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "first_name TEXT NOT NULL,"
                 "last_name TEXT NOT NULL,"
                 "address TEXT NOT NULL,"
                 "email TEXT NOT NULL,"
                 "username TEXT NOT NULL,"
                 "password TEXT NOT NULL)")
    print("user table successfully")
    conn.close()


init_user_table()
users = fetch_users()


# creating table for the products
def init_products_table():
    with sqlite3.connect('UTA_Enrollment') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS cart (product_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "item_name TEXT NOT NULL,"
                     "description TEXT NOT NULL,"
                     "quantity TEXT NOT NULL,"
                     "price TEXT NOT NULL,"
                     "type TEXT NOT NULL,"
                     "picture TEXT NOT NULL)")
    print("UTA_Enrollment table created successfully")


init_products_table()

username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}


def fetch_admin():
    with sqlite3.connect('UTA_Enrollment') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admin")
        users_data = cursor.fetchall()

        new_data = []

        for data in users_data:
            new_data.append(Admin(data[0], data[1], data[2]))

        return new_data


# admin account table
def init_admin_table():
    with sqlite3.connect('UTA_Enrollment') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS admin(admin_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "admin_username TEXT NOT NULL,"
                     "admin_password TEXT NOT NULL)")
        print("admin table created successfully")


init_admin_table()
admin = fetch_admin()

adminname_table = {a.admin_username: a for a in admin}
adminid_table = {a.admin_id: a for a in admin}


def authenticate(username, password):
    user = username_table.get(username, None)
    if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)


app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'this-is-a-secret'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'nathanjohngiose@gmail.com'
app.config['MAIL_PASSWORD'] = 'xfctbtgohreltssz'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['CORS-HEADERS'] = ['Content-Type']
mail = Mail(app)
jwt = JWT(app, authenticate, identity)
CORS(app, resources={r"/*": {"origins": "*"}})


# route to register users
@app.route('/user-registration/', methods=['POST'])
def user_registration():
    response = {}
    db = Database()
    try:
        if request.method == "POST":
            first_name = request.json['first_name']
            surname = request.json['last_name']
            address = request.json['address']
            email = request.json['email']
            username = request.json['username']
            password = request.json['password']

            query = "INSERT INTO user (first_name,last_name,address,email,username,password) VALUES(?,?,?,?,?,?)"
            values = (first_name, surname, address, email, username, password)
            db.sending_to_database(query, values)

            message = Message('Thank You', sender='nathanjohngiose@gmail.com', recipients=[email])
            message.body = "Thank you for registering happy shopping"
            mail.send(message)
            response["message"] = 'Success'
            response["status_code"] = 201
            return response

    except SMTPRecipientsRefused:
        response['message'] = "Please enter a valid email address"
        response['status_code'] = 400
        return response


@app.route("/register-admin/", methods=['POST'])
def admin_registration():
    response = {}
    db = Database()
    if request.method == "POST":
        username = request.json['admin_username']
        password = request.json['admin_password']

        query = "INSERT INTO admin (admin_username,admin_password) VALUES(?,?)"
        values = (username, password)
        db.sending_to_database(query, values)
        response["message"] = 'Success'
        response["status_code"] = 201
        return response
    else:
        response['message'] = "failed"
        response['status_code'] = 400


@app.route("/user-login/", methods=["POST"])
def login_user():
    response = {}
    if request.method == "POST":
        username = request.json["username"]
        password = request.json["password"]
        conn = sqlite3.connect("UTA_Enrollment")
        c = conn.cursor()
        statement = (f"SELECT * FROM user WHERE username='{username}' and password ="
                     f"'{password}'")
        c.execute(statement)
        if not c.fetchone():
            response['message'] = "failed"
            response["status_code"] = 401
            return response
        else:
            response['message'] = "welcome user"
            response["status_code"] = 201
            return response
    else:
        return "wrong method"


@app.route("/admin-login/", methods=["POST"])
def login():
    response = {}
    if request.method == "POST":
        username = request.json["admin_username"]
        password = request.json["admin_password"]
        conn = sqlite3.connect("UTA_Enrollment")
        c = conn.cursor()
        statement = (f"SELECT * FROM admin WHERE admin_username='{username}' and admin_password ="
                     f"'{password}'")
        c.execute(statement)
        if not c.fetchone():
            response['message'] = "failed"
            response["status_code"] = 401
            return response
        else:
            response['message'] = "welcome admin user"
            response["status_code"] = 201
            return response
    else:
        return "wrong method"


@app.route('/show-users/', methods=['GET'])
def show_users():
    response = {}
    with sqlite3.connect('UTA_Enrollment') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user")

        all_users = cursor.fetchall()

    response['status_code'] = 200
    response['data'] = all_users
    return response


@app.route('/show-user/<username>', methods=["GET"])
def view_user(username):
    response = {}
    with sqlite3.connect('UTA_Enrollment') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user WHERE username='" + str(username) + "'")
        response['status_code'] = 200
        response['data'] = cursor.fetchone()
        response['message'] = "user retrieved successfully"
    return jsonify(response)


# protected route that creates products
@app.route('/products-create/', methods=['POST'])
def products_create():
    response = {}
    database = Database()

    if request.method == "POST":
        item_name = request.json['item_name']
        description = request.json['description']
        quantity = request.json['quantity']
        price = request.json['price']
        type = request.json['type']

        query = "INSERT INTO cart (item_name, description, quantity, price, type, picture) Values(?,?,?,?,?,?)"
        values = (item_name, description, quantity, price, type, upload_file())

        database.sending_to_database(query, values)
        response['message'] = "item added successfully"
        response['status_code'] = 201
        return response


# route to show all the products
@app.route('/get-products/', methods=['GET'])
def get_products():
    response = {}
    database = Database()

    query = "SELECT * FROM cart"
    database.single_select(query)
    response['status_code'] = 201
    response['data'] = database.fetch()
    return response


# route to edit products
@app.route('/edit-product/<int:product_id>/', methods=['PUT'])
def edit_product(product_id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('UTA_Enrollment') as conn:
            cursor = conn.cursor()
            incoming_data = dict(request.json)
            put_data = {}

            if incoming_data.get("item_name") is not None:
                put_data["item_name"] = incoming_data.get("item_name")
                with sqlite3.connect('UTA_Enrollment') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE cart SET item_name =? WHERE product_id =?", (put_data['item_name'],
                                                                                        product_id))
                    conn.commit()
                    response['message'] = "Update was successful"
                    response["status_code"] = 201
            if incoming_data.get("description") is not None:
                put_data["description"] = incoming_data.get("description")
                with sqlite3.connect('UTA_Enrollment') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE cart SET description =? WHERE product_id =?",
                                   (put_data['description'], product_id))
                    conn.commit()
                    response['message'] = "Update was successful"
                    response["status_code"] = 201
            if incoming_data.get("quantity") is not None:
                put_data["quantity"] = incoming_data.get("quantity")
                with sqlite3.connect('UTA_Enrollment') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE cart SET quantity =? WHERE product_id =?",
                                   (put_data['quantity'], product_id))
                    conn.commit()
                    response['message'] = "Update was successful"
                    response["status_code"] = 201
            if incoming_data.get("price") is not None:
                put_data["price"] = incoming_data.get("price")
                with sqlite3.connect('UTA_Enrollment') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE cart SET price =? WHERE product_id =?",
                                   (put_data['price'], product_id))
                    conn.commit()
                    response['message'] = "Update was successful"
                    response["status_code"] = 201
            if incoming_data.get("type") is not None:
                put_data["type"] = incoming_data.get("type")
                with sqlite3.connect('UTA_Enrollment') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE cart SET type =? WHERE product_id =?",
                                   (put_data['type'], product_id))
                    conn.commit()
                    response['message'] = "Update was successful"
                    response["status_code"] = 201
                return response


@app.route("/delete-user/<int:user_id>")
def delete_user(user_id):
    response = {}
    database = Database()

    query = "DELETE FROM user WHERE user_id='" + str(user_id) + "'"
    database.single_select(query)
    response['status_code'] = 200
    response['message'] = "user deleted successfully."
    return response


# route that deletes a single product
@app.route("/delete-product/<int:product_id>")
def delete_post(product_id):
    response = {}
    database = Database()

    query = "DELETE FROM cart WHERE product_id=" + str(product_id)
    database.single_select(query)
    response['status_code'] = 200
    response['message'] = "product deleted successfully."
    return response


def upload_file():
    app.logger.info('in upload route')
    cloudinary.config(cloud_name='dn4ec3kh6', api_key='155764151157187',
                      api_secret='7OrN8Aaj08Tjuz_Hw_zVxvQJWBs')
    upload_result = None
    if request.method == 'POST' or request.method == 'PUT':
        product_image = request.json['picture']
        app.logger.info('%s file_to_upload', product_image)
        if product_image:
            upload_result = cloudinary.uploader.upload(product_image)
            app.logger.info(upload_result)
            return upload_result['url']


# route that gets a single product by its ID
@app.route('/get-product/<int:product_id>/', methods=["GET"])
def get_post(product_id):
    response = {}
    database = Database()

    query = "SELECT * FROM cart WHERE product_id=" + str(product_id)
    database.single_select(query)

    response["status_code"] = 200
    response["description"] = "product retrieved successfully"
    response['data'] = database.fetch()
    return response


if __name__ == '__main__':
    app.run()