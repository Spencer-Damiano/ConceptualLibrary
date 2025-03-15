# src/tests/test_api.py

import pytest
from app import create_app
from flask import json
from flask_pymongo import PyMongo
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Set up logging
log_dir = Path(__file__).parent / 'log'
log_dir.mkdir(exist_ok=True)

# Create test results logger
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
test_logger = logging.getLogger('test_results')
test_logger.setLevel(logging.INFO)
handler = logging.FileHandler(log_dir / f'test_results_{timestamp}.log')
handler.setFormatter(logging.Formatter('%(message)s'))
test_logger.addHandler(handler)

def log_test_result(testname, result, details=None):
    """Log test results to file"""
    status = "PASSED" if result else "FAILED"
    test_logger.info(f"{testname:<70} [{status:>10}]")
    if details:
        test_logger.info(f"\nDetails:\n{details}\n")

@pytest.fixture(scope='session')
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'MONGO_URI': 'mongodb://localhost:27017/test_db',
        'JWT_SECRET_KEY': 'test-key'
    })
    
    # Create a new PyMongo instance specifically for testing
    mongo = PyMongo()
    
    # Initialize extensions with app context
    with app.app_context():
        mongo.init_app(app)
        app.mongo = mongo  # Attach mongo to app instance
    
    yield app

@pytest.fixture(scope='session')
def client(app):
    return app.test_client()

@pytest.fixture(scope='function')
def test_db(app):
    with app.app_context():
        db = app.mongo.db
        # Clear collections before each test
        for collection in db.list_collection_names():
            db[collection].delete_many({})
        yield db
        # Clean up after test
        for collection in db.list_collection_names():
            db[collection].delete_many({})

@pytest.fixture
def test_user():
    return {
        'email': 'test@example.com',
        'password': 'test123',
        'name': 'Test User',
        'username': 'testuser'
    }

@pytest.fixture
def auth_headers(client, test_user, test_db):
    # Register user
    register_response = client.post(
        '/api/auth/register',
        json=test_user,
        content_type='application/json'
    )
    
    # Login to get token
    login_response = client.post(
        '/api/auth/login',
        json={
            'email': test_user['email'],
            'password': test_user['password']
        },
        content_type='application/json'
    )
    
    token = login_response.json['access_token']
    return {'Authorization': f'Bearer {token}'}

def test_register(client, test_user, test_db):
    """Test user registration"""
    try:
        response = client.post(
            '/api/auth/register',
            json=test_user,
            content_type='application/json'
        )
        assert response.status_code == 201
        assert response.json['message'] == 'User registered successfully'
        log_test_result("test_register", True)
    except AssertionError as e:
        log_test_result("test_register", False, str(e))
        raise

def test_register_duplicate_email(client, test_user, test_db):
    """Test registering with an existing email"""
    try:
        # First registration
        first_response = client.post('/api/auth/register', json=test_user)
        
        # Attempt duplicate registration
        second_response = client.post(
            '/api/auth/register',
            json=test_user,
            content_type='application/json'
        )
        assert second_response.status_code == 409
        assert second_response.json['message'] == 'Email already registered'
        log_test_result("test_register_duplicate_email", True)
    except AssertionError as e:
        log_test_result("test_register_duplicate_email", False, str(e))
        raise

def test_login(client, test_user, test_db):
    """Test user login"""
    try:
        # Register user first
        client.post('/api/auth/register', json=test_user)
        
        # Attempt login
        login_response = client.post(
            '/api/auth/login',
            json={
                'email': test_user['email'],
                'password': test_user['password']
            },
            content_type='application/json'
        )
        assert login_response.status_code == 200
        assert 'access_token' in login_response.json
        log_test_result("test_login", True)
    except AssertionError as e:
        log_test_result("test_login", False, str(e))
        raise

def test_login_invalid_credentials(client, test_user, test_db):
    """Test login with invalid credentials"""
    try:
        # Register user first
        client.post('/api/auth/register', json=test_user)
        
        # Attempt login with wrong password 
        login_response = client.post(
            '/api/auth/login',
            json={
                'email': test_user['email'],
                'password': 'wrongpassword'
            },
            content_type='application/json'
        )
        assert login_response.status_code == 401
        assert login_response.json['message'] == 'Invalid credentials'
        log_test_result("test_login_invalid_credentials", True)
    except AssertionError as e:
        log_test_result("test_login_invalid_credentials", False, str(e))
        raise

def test_protected_endpoint(client, auth_headers, test_db):
    """Test accessing a protected endpoint"""
    try:
        response = client.get(
            '/api/users/me',
            headers=auth_headers
        )
        assert response.status_code == 200
        assert 'email' in response.json
        log_test_result("test_protected_endpoint", True)
    except AssertionError as e:
        error_details = f"""
Status code was {response.status_code}, expected 200
Response: {response.data.decode() if response.data else 'No response data'}
Headers: {auth_headers}
"""
        log_test_result("test_protected_endpoint", False, error_details)
        raise