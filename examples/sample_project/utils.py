import os
import sys
import time
import datetime
import random
import string
import math
import re
import json
from typing import List, Dict, Any, Optional, Tuple, Union

class Logger:
    """Simple logging utility class"""
    
    LEVELS = {
        'DEBUG': 10,
        'INFO': 20,
        'WARNING': 30,
        'ERROR': 40,
        'CRITICAL': 50
    }
    
    def __init__(self, log_level='INFO', log_file=None):
        self.log_level = self.LEVELS.get(log_level, 20)
        self.log_file = log_file
        
    def _log(self, level, message):
        if self.LEVELS.get(level, 0) >= self.log_level:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_message = f"[{timestamp}] [{level}] {message}"
            print(log_message)
            
            if self.log_file:
                try:
                    with open(self.log_file, 'a') as f:
                        f.write(log_message + '\n')
                except Exception as e:
                    print(f"Failed to write to log file: {e}")
    
    def debug(self, message):
        self._log('DEBUG', message)
        
    def info(self, message):
        self._log('INFO', message)
        
    def warning(self, message):
        self._log('WARNING', message)
        
    def error(self, message):
        self._log('ERROR', message)
        
    def critical(self, message):
        self._log('CRITICAL', message)

def generate_random_string(length=10):
    """Generate a random string of specified length"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def format_file_size(size_bytes):
    """Format file size from bytes to human-readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} bytes"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes/1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes/(1024*1024):.2f} MB"
    else:
        return f"{size_bytes/(1024*1024*1024):.2f} GB"

def get_file_extension(filename):
    """Get the extension of a file"""
    return os.path.splitext(filename)[1]

def is_valid_python_file(filename):
    """Check if a file is a valid Python file"""
    if not filename.endswith('.py'):
        return False
    
    try:
        with open(filename, 'r') as f:
            content = f.read()
        compile(content, filename, 'exec')
        return True
    except:
        return False

def load_json_file(filename):
    """Load data from a JSON file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return None

def save_json_file(filename, data):
    """Save data to a JSON file"""
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving JSON file: {e}")
        return False

def get_timestamp():
    """Get current timestamp"""
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def measure_execution_time(func):
    """Decorator to measure execution time of a function"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Function {func.__name__} took {end_time - start_time:.4f} seconds to execute")
        return result
    return wrapper

def validate_email(email):
    """Validate an email address format"""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

def find_files_by_extension(directory, extension):
    """Find all files with a specific extension in a directory"""
    result = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(extension):
                result.append(os.path.join(root, file))
    return result

def remove_duplicates(input_list):
    """Remove duplicates from a list while preserving order"""
    seen = set()
    result = []
    for item in input_list:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result

class ConfigManager:
    """Simple configuration manager class"""
    
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config = self.load_config()
        
    def load_config(self):
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            return load_json_file(self.config_file)
        return {}
        
    def save_config(self):
        """Save configuration to file"""
        return save_json_file(self.config_file, self.config)
        
    def get(self, key, default=None):
        """Get a configuration value"""
        return self.config.get(key, default)
        
    def set(self, key, value):
        """Set a configuration value"""
        self.config[key] = value
        self.save_config()
        
    def delete(self, key):
        """Delete a configuration value"""
        if key in self.config:
            del self.config[key]
            self.save_config()
            return True
        return False

# Simple test function to demonstrate module usage
def test():
    logger = Logger(log_level='DEBUG')
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    
    print(f"Random string: {generate_random_string(15)}")
    print(f"Formatted size: {format_file_size(1024*1024*3.5)}")
    print(f"Current timestamp: {get_timestamp()}")
    
    print(f"Is valid email: test@example.com = {validate_email('test@example.com')}")
    print(f"Is valid email: invalid-email = {validate_email('invalid-email')}")
    
    # Test the measure_execution_time decorator
    @measure_execution_time
    def slow_function():
        time.sleep(1)
        return "Function completed"
    
    slow_function()

if __name__ == "__main__":
    test()