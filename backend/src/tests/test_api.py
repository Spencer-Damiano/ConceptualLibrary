# src/tests/test_api.py

import pytest
from app import create_app
from flask import json
import logging
import os

# Configure logging
auth_logger = logging.getLogger('auth_tests')
auth_logger.setLevel(logging.DEBUG)

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    # Use a separate test database
    app.config['MONGO_URI'] = 'mongodb://localhost:27017/test_db'
    # Ensure we're using test config
    app.config['JWT_SECRET_KEY'] = 'test-key'
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def test_user():
    return {
        'email': 'test@example.com',
        'password': 'test123',
        'name': 'Test User',
        'username': 'testuser'
    }

@pytest.fixture
def auth_headers(client, test_user):
    """Create a user and get auth headers"""
    auth_logger.info("Setting up auth headers for test user")
    
    # Register user
    register_response = client.post(
        '/api/auth/register',
        json=test_user,  # Use json instead of manually converting to JSON
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