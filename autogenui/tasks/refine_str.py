import re

def remove_whitespace_and_special_chars(string):
    # Remove whitespace
    string = re.sub(r'\s+', '', string)
    
    # Remove special characters
    string = re.sub(r'[^a-zA-Z0-9]', '', string)
    
    return string
