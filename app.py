from flask import Flask, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity
import mysql.connector
from mysql.connector import errorcode 
from werkzeug.security import generate_password_hash, check_password_hash
import os 
from dotenv import load_dotenv
import json 

load_dotenv()

app=Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'abcdefghijklmnopqrstuvwxyz123456') 

jwt=JWTManager(app)

db_config={
    'host':'127.0.0.1',
    'user':'root',
    'password':'1234',
    'database':'railway_management',
    'port':'3306'
}

# the following function will be called to connect to the DB
def connect_to_mysql():
    try:
        return mysql.connector.connect(**db_config)
    except mysql.connector.Error as e:
        if e.errno==errorcode.ER_ACCESS_DENIED_ERROR:
            print("Access Denied. Invalid Credentials")
        elif e.errno==errorcode.ER_BAD_DB_ERROR:
            print("Database not found!")
        else:
            print(e)
        return None
    
# user registration
@app.route('/register', methods= ['POST'])
def register():
    details=request.json
    first_name, last_name, email, phone, pwd, role = details['first_name'], details['last_name'], details['email'], details['phone'], details['pwd'], details['role']

    if role=='admin':
        auth_key=details['auth_key']
        if auth_key!=os.getenv('admin_auth_key'):
            return jsonify({'error':'Invalid admin key'}), 403

    encrypted_pwd=generate_password_hash(pwd)
    # print(len(encrypted_pwd))
    connection=connect_to_mysql()
    cursor=connection.cursor()

    try:
        q1="select * from users where phone=%s or email=%s"
        cursor.execute(q1,(phone, email))
        a=cursor.fetchall()

        if a:
            return jsonify({'error':'the email or phone already exists'}), 401
        else:
            q2="insert into users (first_name, last_name, phone, email, pwd, role) values (%s, %s, %s, %s, %s, %s)"
            cursor.execute(q2, (first_name, last_name, phone, email, encrypted_pwd, role))
        connection.commit()
        return jsonify({'message': 'User Registration Successful'}), 201
    except mysql.connector.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

# user login
@app.route('/login', methods= ['POST'])
def login():
    details=request.json 
    email,pwd=details['email'], details['pwd']

    connection=connect_to_mysql()
    cursor=connection.cursor(dictionary=True)

    try: 
        cursor.execute("select * from users where email=%s", (email,))
        user=cursor.fetchone()
        # print(1)
        if not user:
            return jsonify({'error':'Invalid Credentials'}), 401

        # print(2)
        if check_password_hash(user['pwd'], pwd):
            identity = json.dumps({'user_id': user['user_id'], 'role': user['role']})
            tkn = create_access_token(identity=identity)
            # tkn=create_access_token(identity={'user_id':user['user_id'], 'role':user['role']})
            return jsonify({'token': tkn}), 200
        else:
            return jsonify({'error':'Invalid Credentials'}), 401
        # print(3)
    except mysql.connector.Error as e:
        return jsonify({'error':str(e)}), 500
    finally:
        cursor.close()
        connection.close()

# adding a train (requires admin key)
@app.route('/trains', methods=['POST'])
@jwt_required()
def add_train(): 
    # print("Step0: Just started")
    user = json.loads(get_jwt_identity())
    # user=get_jwt_identity()
    # print("Step1:", user)
    if user['role']!='admin':
        return jsonify({'error':'Account not authorized'}), 403
    
    details= request.json
    # print("Step2:", details)
    train_name, source_stop, dest_stop, new_seats = details['train_name'], details['source_stop'], details['dest_stop'], details['new_seats']
    # print("Step3:", train_name, source_stop, dest_stop, new_seats)
    new_seats_int=int(new_seats)
    if new_seats_int<=0:
        return jsonify({'error':'Seats to add must be greater than 0'}),400
    connection=connect_to_mysql()
    cursor=connection.cursor()
    # print(1)

    try:
        q1="select train_id, seat_avl from trains where train_name=%s and source_stop=%s and dest_stop=%s"
        cursor.execute(q1, (train_name, source_stop, dest_stop))
        train = cursor.fetchone()
        q2="update trains set seat_avl=%s where train_id=%s"
        q3="insert into trains (train_name, source_stop, dest_stop, seat_avl) values (%s, %s, %s, %s)"
        # print(2)
        if train:
            added_seats=new_seats_int+train[1]
            cursor.execute(q2, (added_seats, train[0]))
            connection.commit()
        else:
            cursor.execute(q3, (train_name, source_stop, dest_stop, new_seats_int))
            connection.commit()
        # print(3)
        return jsonify({'message': 'Train Added Sucessfully'}), 201
        
    except mysql.connector.Error as e:
        return jsonify({'error':str(e)}), 500
    finally: 
        cursor.close()
        connection.close()
    
#get seat availability
@app.route('/trains/availability', methods=['GET'])
@jwt_required()
def get_seat_availability():
    details= request.json
    source_stop=details['source_stop']
    dest_stop=details['dest_stop']

    connection=connect_to_mysql()
    cursor=connection.cursor()

    try:
        q="select train_id, source_stop,dest_stop, seat_avl from trains where source_stop=%s and dest_stop=%s"
        cursor.execute(q,(source_stop, dest_stop))
        data=cursor.fetchall()
        return jsonify({'trains':data}), 200
    except mysql.connector.Error as e:
        return jsonify({'error':str(e)}), 500
    finally:
        cursor.close()
        connection.close()
    
# booking a seat (requires login)
@app.route('/bookings', methods=['POST'])
@jwt_required()
def book_seat():
    user = json.loads(get_jwt_identity())
    # user=get_jwt_identity()
    if user['role']!='customer':
        # print(user['role'])
        return jsonify({'error':'only for existing customers'}), 403

    train_id=request.json['train_id']
    tickets=request.json['tickets']
    connection=connect_to_mysql()
    cursor=connection.cursor(dictionary=True)

    try:
        connection.start_transaction()

        q='select train_id,seat_avl from trains where train_id=%s for update'
        cursor.execute(q,(train_id,))
        train=cursor.fetchone()

        if not train:
            connection.rollback()
            return jsonify({'error': 'trains not found'}), 404

        if train['seat_avl']<=0 or train['seat_avl']-tickets<0:
            connection.rollback()
            return jsonify({'error': 'not enough seats available'}), 400

        q2='update trains set seat_avl=seat_avl-%s where train_id=%s'
        q3='insert into bookings (user_id, train_id, seats_booked) values (%s, %s, %s)'
        cursor.execute(q2,(tickets,train_id))
        cursor.execute(q3,(user['user_id'], train_id, tickets))
        connection.commit()
        return jsonify({'message':'seat booked successfully'}), 201
    except mysql.connector.Error as e:
        connection.rollback()
        return jsonify({'error':str(e)}), 500
    finally:
        cursor.close()
        connection.close()

#checking a booking status (requires login and authorization, so that everyone cant access everyone's data, but only their own bookings)
@app.route('/bookings/<int:book_id>', methods=['GET'])
@jwt_required()
def get_booking_details(book_id):
    user = json.loads(get_jwt_identity())
    # user=get_jwt_identity() 

    connection=connect_to_mysql()
    cursor=connection.cursor(dictionary=True)

    try:
        query = """select u.user_id as user_id, t.train_id as train_id, b.id as booking_id, u.first_name as first_name, u.last_name as last_name, u.email as user_email, u.phone as phone, t.train_name as train_name, t.source_stop, t.dest_stop, b.book_time
                    from bookings b join users u on b.user_id = u.user_id join trains t on b.train_id = t.train_id where b.id = %s
        """
        cursor.execute(query, (book_id,))
        booking = cursor.fetchone()

        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        if user['role'] == 'admin' or user['user_id']==booking['user_id']:
            print(user['user_id'], booking['user_id'])
            return jsonify({'booking': booking}), 200
        return jsonify({'error': 'You are not authorized to view this booking'}), 403

        # return jsonify({'booking': booking}), 200
    except mysql.connector.Error as e:
        return jsonify({'error':str(e)}), 500
    finally:
        cursor.close()
        connection.close()

if __name__=="__main__":
    app.run(debug=True)

