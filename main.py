from flask import Flask, jsonify, request
from http import HTTPStatus
import mysql.connector
from datetime import datetime


app = Flask(__name__)

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'mydb' 
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def validate_account(data, required_fields=None):
    if required_fields is None:
        required_fields = ['account_name', 'current_balance', 'Customers_customer_id']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    return True, None

def validate_customer(data, required_fields=None):
    if required_fields is None:
        required_fields = ['customer_name', 'customer_phone', 'customer_email', 'customer_municipality', 
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