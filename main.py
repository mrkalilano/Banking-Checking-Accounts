from flask import Flask, jsonify, request
from http import HTTPStatus
import mysql.connector
from datetime import datetime, timedelta
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
def get_customers():
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
def get_customer(customer_id):
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
def create_customer():
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
def update_customer(customer_id):
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
def delete_customer(customer_id):
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
def get_accounts():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM mydb.accounts;")
    accounts = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({'success': True, 'data': accounts, 'total': len(accounts)}), HTTPStatus.OK

@app.route('/api/accounts/<int:account_id>', methods=['GET'])
def get_account(account_id):
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
def create_account():
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
def update_account(account_id):
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
def delete_account(account_id):
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
def get_merchants():
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
def get_merchant(merchant_id):
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
def create_merchant():
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
def update_merchant(merchant_id):
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
def delete_merchant(merchant_id):
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
def get_transactions():
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
def get_transaction(transaction_id):
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
def create_transaction():
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
def update_transaction(transaction_id):
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
def delete_transaction(transaction_id):
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