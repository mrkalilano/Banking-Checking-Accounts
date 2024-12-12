import pytest
from main import app, get_db_connection
from datetime import datetime, timedelta, timezone
import jwt
from werkzeug.security import generate_password_hash
from unittest.mock import patch, MagicMock
from http import HTTPStatus

@pytest.fixture
def client():
    app.config['TESTING'] = True
    return app.test_client()

@pytest.fixture
def mock_db():
    with patch('main.get_db_connection') as mock:
        connection = MagicMock()
        cursor = MagicMock()
        connection.cursor.return_value = cursor
        mock.return_value = connection
        yield mock

@pytest.fixture
def auth_token():
    test_user = {
        'id': 1,
        'role': 'admin'
    }
    token = jwt.encode({
        'user_id': test_user['id'],
        'role': test_user['role'],
        'exp': datetime.now(timezone.utc) + timedelta(hours=24)  # Updated
    }, app.config['SECRET_KEY'])
    return token

# Authentication Tests
def test_register_success(client, mock_db):
    mock_db.return_value.cursor.return_value.fetchone.return_value = None
    data = {
        'username': 'testuser',
        'password': 'password123',
        'email': 'test@example.com',
        'role': 'user'
    }
    response = client.post('/api/auth/register', 
                          json=data,
                          content_type='application/json')
    assert response.status_code == HTTPStatus.CREATED
    assert response.json['success'] == True

def test_register_invalid_email(client):
    data = {
        'username': 'testuser',
        'password': 'password123',
        'email': 'invalid-email',
        'role': 'user'
    }
    response = client.post('/api/auth/register', 
                          json=data,
                          content_type='application/json')
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert 'Invalid email format' in response.json['error']

def test_login_success(client, mock_db):
    hashed_password = generate_password_hash('password123')
    mock_db.return_value.cursor.return_value.fetchone.return_value = {
        'id': 1,
        'username': 'testuser',
        'password': hashed_password,
        'email': 'test@example.com',
        'role': 'admin'
    }
    data = {
        'username': 'testuser',
        'password': 'password123'
    }
    response = client.post('/api/auth/login',
                          json=data,
                          content_type='application/json')
    assert response.status_code == HTTPStatus.OK
    assert 'token' in response.json

# Customer Tests
def test_get_customers(client, mock_db, auth_token):
    mock_customers = [
        {'customer_id': 1, 'customer_name': 'John Doe'},
        {'customer_id': 2, 'customer_name': 'Jane Smith'}
    ]
    mock_db.return_value.cursor.return_value.fetchall.return_value = mock_customers
    mock_db.return_value.cursor.return_value.fetchone.return_value = {'role': 'admin'}

    headers = {'Authorization': f'Bearer {auth_token}'}
    response = client.get('/api/customers', headers=headers)
    
    assert response.status_code == HTTPStatus.OK
    assert len(response.json['data']) == 2

def test_create_customer_success(client, mock_db, auth_token):
    mock_db.return_value.cursor.return_value.lastrowid = 1
    mock_db.return_value.cursor.return_value.fetchone.return_value = {'role': 'admin'}
    
    data = {
        'customer_name': 'John Doe',
        'customer_phone': '1234567890',
        'customer_email': 'john@example.com',
        'customer_street': '123 Main St',
        'customer_municipality': 'Springfield',
        'customer_city': 'Springfield',
        'customer_province': 'IL',
        'customer_zipcode': '62701'
    }
    
    headers = {'Authorization': f'Bearer {auth_token}'}
    response = client.post('/api/customers',
                          json=data,
                          headers=headers,
                          content_type='application/json')
    
    assert response.status_code == HTTPStatus.CREATED
    assert response.json['success'] == True

# Account Tests
def test_get_accounts(client, mock_db, auth_token):
    mock_accounts = [
        {'account_id': 1, 'account_name': 'Savings'},
        {'account_id': 2, 'account_name': 'Checking'}
    ]
    mock_db.return_value.cursor.return_value.fetchall.return_value = mock_accounts
    mock_db.return_value.cursor.return_value.fetchone.return_value = {'role': 'admin'}

    headers = {'Authorization': f'Bearer {auth_token}'}
    response = client.get('/api/accounts', headers=headers)
    
    assert response.status_code == HTTPStatus.OK
    assert len(response.json['data']) == 2

# Merchant Tests
def test_get_merchants(client, mock_db, auth_token):
    mock_merchants = [
        {'merchant_id': 1, 'merchant_name': 'Store A'},
        {'merchant_id': 2, 'merchant_name': 'Store B'}
    ]
    mock_db.return_value.cursor.return_value.fetchall.return_value = mock_merchants
    mock_db.return_value.cursor.return_value.fetchone.return_value = {'role': 'admin'}

    headers = {'Authorization': f'Bearer {auth_token}'}
    response = client.get('/api/merchants', headers=headers)
    
    assert response.status_code == HTTPStatus.OK
    assert len(response.json['data']) == 2

def test_create_merchant_success(client, mock_db, auth_token):
    mock_db.return_value.cursor.return_value.lastrowid = 1
    mock_db.return_value.cursor.return_value.fetchone.return_value = {'role': 'admin'}
    
    data = {
        'merchant_name': 'New Store',
        'merchant_email': 'store@example.com'
    }
    
    headers = {'Authorization': f'Bearer {auth_token}'}
    response = client.post('/api/merchants',
                          json=data,
                          headers=headers,
                          content_type='application/json')
    
    assert response.status_code == HTTPStatus.CREATED
    assert response.json['success'] == True

# Transaction Tests
def test_get_transactions(client, mock_db, auth_token):
    mock_transactions = [
        {'transaction_id': 1, 'amount': 100.00},
        {'transaction_id': 2, 'amount': 200.00}
    ]
    mock_db.return_value.cursor.return_value.fetchall.return_value = mock_transactions
    mock_db.return_value.cursor.return_value.fetchone.return_value = {'role': 'admin'}

    headers = {'Authorization': f'Bearer {auth_token}'}
    response = client.get('/api/transactions', headers=headers)
    
    assert response.status_code == HTTPStatus.OK
    assert len(response.json['data']) == 2

def test_create_transaction_success(client, mock_db, auth_token):
    mock_db.return_value.cursor.return_value.lastrowid = 1
    mock_db.return_value.cursor.return_value.fetchone.return_value = {'role': 'admin'}
    
    data = {
        'transaction_type_description': 'Purchase',
        'amount': 100.00,
        'date_of_transaction': '2024-12-12',
        'balance': 900.00,
        'Accounts_account_id': 1,
        'Merchants_merchant_id': 1
    }
    
    headers = {'Authorization': f'Bearer {auth_token}'}
    response = client.post('/api/transactions',
                          json=data,
                          headers=headers,
                          content_type='application/json')
    
    assert response.status_code == HTTPStatus.CREATED
    assert response.json['success'] == True

# Edge Cases and Error Handling Tests
def test_invalid_token(client):
    headers = {'Authorization': 'Bearer invalid_token'}
    response = client.get('/api/customers', headers=headers)
    assert response.status_code == HTTPStatus.UNAUTHORIZED

def test_expired_token(client):
    expired_token = jwt.encode({
        'user_id': 1,
        'role': 'admin',
        'exp': datetime.now(timezone.utc) - timedelta(hours=1)  # Updated
    }, app.config['SECRET_KEY'])
    
    headers = {'Authorization': f'Bearer {expired_token}'}
    response = client.get('/api/customers', headers=headers)
    assert response.status_code == HTTPStatus.UNAUTHORIZED

def test_missing_required_fields(client, auth_token):
    headers = {'Authorization': f'Bearer {auth_token}'}
    data = {'incomplete': 'data'}
    
    response = client.post('/api/customers',
                          json=data,
                          headers=headers,
                          content_type='application/json')
    
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_invalid_role_access(client, auth_token):
    user_token = jwt.encode({
        'user_id': 2,
        'role': 'user',
        'exp': datetime.now(timezone.utc) + timedelta(hours=24)  # Updated
    }, app.config['SECRET_KEY'])
    
    headers = {'Authorization': f'Bearer {user_token}'}
    data = {'some': 'data'}
    
    response = client.post('/api/customers',
                          json=data,
                          headers=headers,
                          content_type='application/json')
    
    assert response.status_code == HTTPStatus.FORBIDDEN
