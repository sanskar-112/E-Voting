import hashlib
import random
import string

def hash_data(data):
    """
    Hashes the input data using SHA-512.
    Returns the hexadecimal digest.
    """
    return hashlib.sha512(data.encode()).hexdigest()

def generate_otp(length=6):
    """
    Generates a numeric OTP of specified length.
    """
    digits = string.digits
    return ''.join(random.choice(digits) for i in range(length))

def verify_hash(plain_data, hashed_data):
    """
    Verifies if the plain data matches the hashed data.
    """
    return hash_data(plain_data) == hashed_data
