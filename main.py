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