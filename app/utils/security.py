# security.py
import re
import bleach
from html_sanitizer import Sanitizer
from sqlalchemy import text

# SQL Injection Prevention
def sanitize_sql_param(param):
    """
    Sanitize SQL parameters to prevent SQL injection
    This is a basic example - SQLAlchemy's parameterized queries are better
    """
    if param is None:
        return None
    
    # Convert to string if it's not already
    if not isinstance(param, str):
        param = str(param)
    
    # Remove potentially dangerous SQL characters
    dangerous_chars = ["'", "\"", ";", "--", "/*", "*/", "xp_", "exec", "insert", "select", 
                      "update", "delete", "drop", "truncate", "union", "alter"]
    
    # Replace dangerous characters with empty string
    for char in dangerous_chars:
        param = param.replace(char, "")
    
    return param

def is_valid_id(id_value):
    """Validate if the ID is a valid integer"""
    if isinstance(id_value, int):
        return True
    if isinstance(id_value, str) and id_value.isdigit():
        return True
    return False

# XSS Prevention
def sanitize_html(html_content):
    """Sanitize HTML content to prevent XSS"""
    # Configure allowed tags and attributes
    allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                    'ul', 'ol', 'li', 'span', 'div', 'blockquote', 'pre', 'code']
    allowed_attrs = {
        '*': ['class', 'style'],
        'a': ['href', 'title', 'target'],
        'img': ['src', 'alt', 'title', 'width', 'height'],
    }
    
    # Use bleach to sanitize HTML
    cleaned_html = bleach.clean(
        html_content,
        tags=allowed_tags,
        attributes=allowed_attrs,
        strip=True
    )
    
    return cleaned_html

# Additional HTML sanitizer for more complex content
sanitizer = Sanitizer()

def deep_sanitize_html(html_content):
    """More thorough HTML sanitization"""
    return sanitizer.sanitize(html_content)

# Input validation for different data types
def validate_string(value, max_length=255):
    """Validate string input"""
    if not isinstance(value, str):
        return False
    if len(value) > max_length:
        return False
    return True

def validate_email(email):
    """Validate email format"""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

def validate_date(date_str):
    """Validate date format (YYYY-MM-DD)"""
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    return bool(re.match(pattern, date_str))
