from flask import Flask, jsonify, request
from http import HTTPStatus
import mysql.connector

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
