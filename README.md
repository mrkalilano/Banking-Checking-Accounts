# Banking Checking Accounts

The Banking Checking Accounts System is designed to manage and track customer checking accounts and their associated transactions. This streamlined system focuses on essential banking operations while maintaining accurate financial records and customer relationships.

## Installation
```bash
pip install -r requirements.txt
```

## Configuration
To configure the database:
1. Download the raw file of my mydb.sql in your device.
2. Import ```mydb``` MySQL database to your server or local machine.
2. Update the database configuration in the Flask app with your database connection details.

Environment variables needed:
- ```MYSQL_HOST```: The host for the MySQL database (e.g., localhost or IP address of the database server)
- ```MYSQL_USER```: MySQL username (e.g., root)
- ```MYSQL_PASSWORD```: MySQL password
- ```MYSQL_DB```: Name of the database (e.g., mydb)
- ```SECRET_KEY```: MARK

## API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| /	| GET	| Home/Index |
| /customers	| GET	| List all customers |
| /customers/<customer_id>	| GET	| List a specific customer using customer ID |
| /customers	| POST	| Add a new customer |
| /customers/<customer_id>	| PUT	| Update a customer's details |
| /customers/<customer_id>	| DELETE	| Delete a customer |
| /accounts	| GET	| List all accounts |
| /accounts/<account_id>	| GET	| List a specific account using account ID |
| /accounts	| POST	| Add a new account |
| /accounts/<account_id>	| PUT	| Update a account's details |
| /accounts/<vehicle_id>	| DELETE	| Delete an account |
| /merchants	| GET	| List all location |
| /merchants/<merchant_id>	| GET	| List a specific merchant using merchant ID |
| /merchants	| POST	| Add a new merchant |
| /merchants/<merchant_id>	| PUT	| Update a merchant's details |
| /merchants/<merchant_id>	| DELETE	| Delete a merchant |
| /transactions	| GET	| List all transactions |
| /transactions/<transaction_id>	| GET	| List a specific transaction using transaction ID |
| /transactions	| POST	| Add a new transaction |
| /transactions/<transaction_id>	| PUT	| Update a transaction's details |
| /transactions/<transaction_id>	| DELETE	| Delete a transaction |

## Testing
```bash
pip install pytest
pytest testing_main.py
```

## Git Commit Guidelines

Use conventional commits:
```bash
feat: add user authentication
fix: resolve database connection issue
docs: update API documentation
test: add user registration tests

