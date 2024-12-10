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