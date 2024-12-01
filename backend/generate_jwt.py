import secrets

# Generate a random 32 byte hex string
# copy this value to the SECRET_KEY in the .env file
print(secrets.token_hex(32))