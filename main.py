from flask import Flask, jsonify, request
from http import HTTPStatus
import mysql.connector
from datetime import datetime, timedelta, timezone
import jwt
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'MARK'

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'mydb' 
}

ROLES = {
    'admin': ['create', 'read', 'update', 'delete'],
    'manager': ['create', 'read', 'update'],
    'user': ['read']
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def get_user_by_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

def generate_token(user_id, role):
    token = jwt.encode({
        'user_id': user_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }, app.config['SECRET_KEY'])
    return token

def generate_token(user_id, role):
    token = jwt.encode({
        'user_id': user_id,
        'role': role,
        'exp': datetime.now(timezone.utc) + timedelta(hours=24)
    }, app.config['SECRET_KEY'])
    return token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'success': False, 'error': 'Invalid token format'}), HTTPStatus.UNAUTHORIZED
        
        if not token:
            return jsonify({'success': False, 'error': 'Token is required'}), HTTPStatus.UNAUTHORIZED
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = get_user_by_id(data['user_id'])
            if not current_user:
                return jsonify({'success': False, 'error': 'Invalid token'}), HTTPStatus.UNAUTHORIZED
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'error': 'Token has expired'}), HTTPStatus.UNAUTHORIZED
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'error': 'Invalid token'}), HTTPStatus.UNAUTHORIZED
            
        return f(current_user, *args, **kwargs)
    return decorated

def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(current_user, *args, **kwargs):
            if current_user['role'] not in ROLES or required_role not in ROLES[current_user['role']]:
                return jsonify({'success': False, 'error': 'Insufficient permissions'}), HTTPStatus.FORBIDDEN
            return f(current_user, *args, **kwargs)
        return decorated_function
    return decorator

def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    pattern = r'^\+?1?\d{9,15}$'
    return re.match(pattern, phone) is not None

def validate_amount(amount):
    try:
        float_amount = float(amount)
        return float_amount > 0
    except (TypeError, ValueError):
        return False
    
@app.route('/api/auth/register', methods=['POST'])
def register():
    if not request.json:
        return jsonify({'success': False, 'error': 'Request must be JSON'}), HTTPStatus.BAD_REQUEST
    
    data = request.json
    required_fields = ['username', 'password', 'email', 'role']
    
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'error': f'{field} is required'}), HTTPStatus.BAD_REQUEST
    
    if not validate_email(data['email']):
        return jsonify({'success': False, 'error': 'Invalid email format'}), HTTPStatus.BAD_REQUEST
    
    if data['role'] not in ROLES:
        return jsonify({'success': False, 'error': 'Invalid role'}), HTTPStatus.BAD_REQUEST
    
    if len(data['password']) < 8:
        return jsonify({'success': False, 'error': 'Password must be at least 8 characters'}), HTTPStatus.BAD_REQUEST
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", 
                      (data['username'], data['email']))
        if cursor.fetchone():
            return jsonify({'success': False, 'error': 'Username or email already exists'}), HTTPStatus.BAD_REQUEST
        
        hashed_password = generate_password_hash(data['password'])
        cursor.execute("""
            INSERT INTO users (username, password, email, role)
            VALUES (%s, %s, %s, %s)
        """, (data['username'], hashed_password, data['email'], data['role']))
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully'
        }), HTTPStatus.CREATED
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        cursor.close()
        conn.close()

@app.route('/api/auth/login', methods=['POST'])
def login():
    if not request.json:
        return jsonify({'success': False, 'error': 'Request must be JSON'}), HTTPStatus.BAD_REQUEST
    
    data = request.json
    if not data.get('username') or not data.get('password'):
        return jsonify({'success': False, 'error': 'Username and password are required'}), HTTPStatus.BAD_REQUEST
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM users WHERE username = %s", (data['username'],))
        user = cursor.fetchone()
        
        if user and check_password_hash(user['password'], data['password']):
            token = generate_token(user['id'], user['role'])
            return jsonify({
                'success': True,
                'token': token,
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'role': user['role']
                }
            }), HTTPStatus.OK
        return jsonify({'success': False, 'error': 'Invalid credentials'}), HTTPStatus.UNAUTHORIZED
    finally:
        cursor.close()
        conn.close()

def validate_account(data, required_fields=None):
    if required_fields is None:
        required_fields = ['account_name', 'current_balance', 'Customers_customer_id']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    return True, None

def validate_customer(data, required_fields=None):
    if required_fields is None:
        required_fields = ['customer_name', 'customer_phone', 'customer_email', 'customer_street', 'customer_municipality', 
                         'customer_city', 'customer_province']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    
def validate_merchant(data, required_fields=None):
    if required_fields is None:
        required_fields = ['merchant_name', 'merchant_email']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    return True, None

def validate_transaction(data, required_fields=None):
    if required_fields is None:
        required_fields = ['transaction_type_description', 'amount', 'date_of_transaction', 
                         'balance', 'Accounts_account_id', 'Merchants_merchant_id']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    return True, None

@app.route('/api/customers', methods=['GET'])
@token_required
@role_required('read')
def get_customers(current_user):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM customers")
        customers = cursor.fetchall()
        return jsonify({'success': True, 'data': customers}), HTTPStatus.OK
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        cursor.close()
        conn.close()

@app.route('/api/customers/<int:customer_id>', methods=['GET'])
@token_required
@role_required('read')
def get_customer(current_user, customer_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM customers WHERE customer_id = %s", (customer_id,))
        customer = cursor.fetchone()
        if customer:
            return jsonify({'success': True, 'data': customer}), HTTPStatus.OK
        return jsonify({'success': False, 'error': 'Customer not found'}), HTTPStatus.NOT_FOUND
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        cursor.close()
        conn.close()
        
@app.route('/api/customers', methods=['POST'])
@token_required
@role_required('create')
def create_customer(current_user):
    if not request.json:
        return jsonify({'success': False, 'error': 'Request must be JSON'}), HTTPStatus.BAD_REQUEST

    data = request.json
    required_fields = ['customer_name', 'customer_phone', 'customer_email', 'customer_street','customer_municipality', 'customer_city', 'customer_province', 'customer_zipcode']
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'error': f'{field} is required'}), HTTPStatus.BAD_REQUEST

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO customers (customer_name, customer_phone, customer_email, customer_street, customer_municipality, customer_city, customer_province, customer_zipcode)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (data['customer_name'], data['customer_phone'], data['customer_email'], data['customer_street'], data['customer_municipality'],data['customer_city'],data['customer_province'], data['customer_zipcode']))
    conn.commit()
    new_customer_id = cursor.lastrowid
    cursor.close()
    conn.close()

    return jsonify({'success': True, 'data': {'customer_id': new_customer_id, **data}}), HTTPStatus.CREATED

@app.route('/api/customers/<int:customer_id>', methods=['PUT'])
@token_required
@role_required('update')
def update_customer(current_user, customer_id):
    if not request.json:
        return jsonify({'success': False, 'error': 'Request must be JSON'}), HTTPStatus.BAD_REQUEST

    data = request.json
    required_fields = ['customer_name', 'customer_phone', 'customer_email', 'customer_street', 'customer_municipality', 'customer_city', 'customer_province', 'customer_zipcode']
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'error': f'{field} is required'}), HTTPStatus.BAD_REQUEST

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE customers SET customer_name = %s, customer_phone = %s, customer_email = %s, customer_street = %s, customer_municipality = %s, customer_city = %s, customer_province = %s, customer_zipcode = %s
        WHERE customer_id = %s
    """, (data['customer_name'], data['customer_phone'], data['customer_email'], data['customer_street'], data['customer_municipality'], data['customer_city'], data['customer_province'], data['customer_zipcode'], customer_id))
    conn.commit()
    if cursor.rowcount == 0:
        return jsonify({'success': False, 'error': 'Customer not found'}), HTTPStatus.NOT_FOUND
    cursor.close()
    conn.close()

    return jsonify({'success': True, 'message': 'Customer updated successfully'}), HTTPStatus.OK

@app.route('/api/customers/<int:customer_id>', methods=['DELETE'])
@token_required
@role_required('delete')
def delete_customer(current_user, customer_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM customers WHERE customer_id = %s", (customer_id,))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({'success': False, 'error': 'Customer not found'}), HTTPStatus.NOT_FOUND

        return jsonify({'success': True, 'message': 'Customer deleted successfully'}), HTTPStatus.OK

    except Exception as e:
        return jsonify({'success': False, 'error': f'An error occurred: {str(e)}'}), HTTPStatus.INTERNAL_SERVER_ERROR

    finally:
        cursor.close()
        conn.close()

        
@app.route('/api/accounts', methods=['GET'])
@token_required
@role_required('read')
def get_accounts(current_user):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM mydb.accounts;")
    accounts = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({'success': True, 'data': accounts, 'total': len(accounts)}), HTTPStatus.OK

@app.route('/api/accounts/<int:account_id>', methods=['GET'])
@token_required
@role_required('read')
def get_account(current_user, account_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM mydb.accounts WHERE account_id = %s", (account_id,))
    account = cursor.fetchone()
    cursor.close()
    conn.close()
    if account:
        return jsonify({'success': True, 'data': account}), HTTPStatus.OK
    return jsonify({'success': False, 'error': 'Account not found'}), HTTPStatus.NOT_FOUND

@app.route('/api/accounts', methods=['POST'])
@token_required
@role_required('create')
def create_account(current_user):
    if not request.json:
        return jsonify({'success': False, 'error': 'Request must be JSON'}), HTTPStatus.BAD_REQUEST

    data = request.json
    required_fields = ['account_name', 'current_balance', 'Customers_customer_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'error': f'{field} is required'}), HTTPStatus.BAD_REQUEST

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) FROM customers WHERE customer_id = %s
    """, (data['Customers_customer_id'],))
    customer_exists = cursor.fetchone()[0]

    if not customer_exists:
        return jsonify({'success': False, 'error': 'Customer not found'}), HTTPStatus.BAD_REQUEST

    cursor.execute("""
        INSERT INTO accounts (account_name, current_balance, Customers_customer_id)
        VALUES (%s, %s, %s)
    """, (data['account_name'], data['current_balance'], data['Customers_customer_id']))
    conn.commit()
    new_account_id = cursor.lastrowid
    cursor.close()
    conn.close()

    return jsonify({'success': True, 'data': {'account_id': new_account_id, **data}}), HTTPStatus.CREATED

@app.route('/api/accounts/<int:account_id>', methods=['PUT'])
@token_required
@role_required('update')
def update_account(current_user, account_id):
    if not request.json:
        return jsonify({'success': False, 'error': 'Request must be JSON'}), HTTPStatus.BAD_REQUEST

    data = request.json
    required_fields = ['account_name', 'current_balance', 'Customers_customer_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'error': f'{field} is required'}), HTTPStatus.BAD_REQUEST

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE accounts SET account_name = %s, current_balance = %s, Customers_customer_id = %s
        WHERE account_id = %s
    """, (data['account_name'], data['current_balance'], data['Customers_customer_id'], account_id))
    conn.commit()
    if cursor.rowcount == 0:
        return jsonify({'success': False, 'error': 'Customer not found'}), HTTPStatus.NOT_FOUND
    cursor.close()
    conn.close()

    return jsonify({'success': True, 'message': 'Accounts updated successfully'}), HTTPStatus.OK

@app.route('/api/accounts/<int:account_id>', methods=['DELETE'])
@token_required
@role_required('delete')
def delete_account(current_user, account_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM accounts WHERE account_id = %s", (account_id,))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({'success': False, 'error': 'Account not found'}), HTTPStatus.NOT_FOUND

        return jsonify({'success': True, 'message': 'Account deleted successfully'}), HTTPStatus.OK

    except Exception as e:
        return jsonify({'success': False, 'error': f'An error occurred: {str(e)}'}), HTTPStatus.INTERNAL_SERVER_ERROR

    finally:
        cursor.close()
        conn.close()
      

@app.route('/api/merchants', methods=['GET'])
@token_required
@role_required('read')
def get_merchants(current_user):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM merchants")
        merchants = cursor.fetchall()
        return jsonify({'success': True, 'data': merchants}), HTTPStatus.OK
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        cursor.close()
        conn.close()

@app.route('/api/merchants/<int:merchant_id>', methods=['GET'])
@token_required
@role_required('read')
def get_merchant(current_user, merchant_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM merchants WHERE merchant_id = %s", (merchant_id,))
        merchant = cursor.fetchone()
        if merchant:
            return jsonify({'success': True, 'data': merchant}), HTTPStatus.OK
        return jsonify({'success': False, 'error': 'Merchant not found'}), HTTPStatus.NOT_FOUND
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        cursor.close()
        conn.close()
        
@app.route('/api/merchants', methods=['POST'])
@token_required
@role_required('create')
def create_merchant(current_user):
    if not request.json:
        return jsonify({'success': False, 'error': 'Request must be JSON'}), HTTPStatus.BAD_REQUEST

    data = request.json
    required_fields = ['merchant_name', 'merchant_email']
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'error': f'{field} is required'}), HTTPStatus.BAD_REQUEST

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO merchants (merchant_name, merchant_email)
        VALUES (%s, %s)
    """, (data['merchant_name'], data['merchant_email']))
    conn.commit()
    new_merchant_id = cursor.lastrowid
    cursor.close()
    conn.close()

    return jsonify({'success': True, 'data': {'merchant_id': new_merchant_id, **data}}), HTTPStatus.CREATED

@app.route('/api/merchants/<int:merchant_id>', methods=['PUT'])
@token_required
@role_required('update')
def update_merchant(current_user, merchant_id):
    if not request.json:
        return jsonify({'success': False, 'error': 'Request must be JSON'}), HTTPStatus.BAD_REQUEST

    data = request.json
    required_fields = ['merchant_name', 'merchant_email']
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'error': f'{field} is required'}), HTTPStatus.BAD_REQUEST

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE merchants SET merchant_name = %s, merchant_email = %s
        WHERE merchant_id = %s
    """, (data['merchant_name'], data['merchant_email'], merchant_id))
    conn.commit()
    if cursor.rowcount == 0:
        return jsonify({'success': False, 'error': 'Merchant not found'}), HTTPStatus.NOT_FOUND
    cursor.close()
    conn.close()

    return jsonify({'success': True, 'message': 'Merchants updated successfully'}), HTTPStatus.OK

@app.route('/api/merchants/<int:merchant_id>', methods=['DELETE'])
@token_required
@role_required('delete')
def delete_merchant(current_user, merchant_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM merchants WHERE merchant_id = %s", (merchant_id,))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({'success': False, 'error': 'Merchant not found'}), HTTPStatus.NOT_FOUND

        return jsonify({'success': True, 'message': 'Merchant deleted successfully'}), HTTPStatus.OK

    except Exception as e:
        return jsonify({'success': False, 'error': f'An error occurred: {str(e)}'}), HTTPStatus.INTERNAL_SERVER_ERROR

    finally:
        cursor.close()
        conn.close()

        
@app.route('/api/transactions', methods=['GET'])
@token_required
@role_required('read')
def get_transactions(current_user):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM transactions")
        transactions = cursor.fetchall()
        return jsonify({'success': True, 'data': transactions}), HTTPStatus.OK
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        cursor.close()
        conn.close()

@app.route('/api/transactions/<int:transaction_id>', methods=['GET'])
@token_required
@role_required('read')
def get_transaction(current_user, transaction_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM transactions WHERE transaction_id = %s", (transaction_id,))
        transaction = cursor.fetchone()
        if transaction:
            return jsonify({'success': True, 'data': transaction}), HTTPStatus.OK
        return jsonify({'success': False, 'error': 'Transaction not found'}), HTTPStatus.NOT_FOUND
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR
    finally:
        cursor.close()
        conn.close()
        
@app.route('/api/transactions', methods=['POST'])
@token_required
@role_required('create')
def create_transaction(current_user):
    if not request.json:
        return jsonify({'success': False, 'error': 'Request must be JSON'}), HTTPStatus.BAD_REQUEST

    data = request.json
    required_fields = ['transaction_type_description', 'amount', 'date_of_transaction', 'balance', 'Accounts_account_id', 'Merchants_merchant_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'error': f'{field} is required'}), HTTPStatus.BAD_REQUEST

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) FROM accounts WHERE account_id = %s
    """, (data['Accounts_account_id'],))
    account_exists = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) FROM merchants WHERE merchant_id = %s
    """, (data['Merchants_merchant_id'],))
    merchant_exists = cursor.fetchone()[0]

    if not account_exists:
        return jsonify({'success': False, 'error': 'Account not found'}), HTTPStatus.BAD_REQUEST
    if not merchant_exists:
        return jsonify({'success': False, 'error': 'Merchant not found'}), HTTPStatus.BAD_REQUEST

    cursor.execute("""
        INSERT INTO transactions (transaction_type_description, amount, date_of_transaction, balance, Accounts_account_id, Merchants_merchant_id)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (data['transaction_type_description'], data['amount'], data['date_of_transaction'], data['balance'], data['Accounts_account_id'], data['Merchants_merchant_id']))
    conn.commit()
    new_transaction_id = cursor.lastrowid
    cursor.close()
    conn.close()

    return jsonify({'success': True, 'data': {'transaction_id': new_transaction_id, **data}}), HTTPStatus.CREATED

@app.route('/api/transactions/<int:transaction_id>', methods=['PUT'])
@token_required
@role_required('update')
def update_transaction(current_user, transaction_id):
    if not request.json:
        return jsonify({'success': False, 'error': 'Request must be JSON'}), HTTPStatus.BAD_REQUEST

    data = request.json
    required_fields = ['transaction_type_description', 'amount', 'date_of_transaction', 'balance', 'Accounts_account_id', 'Merchants_merchant_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'error': f'{field} is required'}), HTTPStatus.BAD_REQUEST

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE transactions SET transaction_type_description = %s, amount = %s, date_of_transaction = %s, Accounts_account_id = %s, Merchants_merchant_id = %s
        WHERE transaction_id = %s
    """, (data['transaction_type_description'], data['amount'], data['date_of_transaction'], data['Accounts_account_id'], data['Merchants_merchant_id'], transaction_id))
    conn.commit()
    if cursor.rowcount == 0:
        return jsonify({'success': False, 'error': 'Transaction not found'}), HTTPStatus.NOT_FOUND
    cursor.close()
    conn.close()

    return jsonify({'success': True, 'message': 'Transactions updated successfully'}), HTTPStatus.OK

@app.route('/api/transactions/<int:transaction_id>', methods=['DELETE'])
@token_required
@role_required('delete')
def delete_transaction(current_user, transaction_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM transactions WHERE transaction_id = %s", (transaction_id,))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({'success': False, 'error': 'Transaction not found'}), HTTPStatus.NOT_FOUND

        return jsonify({'success': True, 'message': 'Transaction deleted successfully'}), HTTPStatus.OK

    except Exception as e:
        return jsonify({'success': False, 'error': f'An error occurred: {str(e)}'}), HTTPStatus.INTERNAL_SERVER_ERROR

    finally:
        cursor.close()
        conn.close()
        
if __name__ == '__main__':
    app.run(debug=True)