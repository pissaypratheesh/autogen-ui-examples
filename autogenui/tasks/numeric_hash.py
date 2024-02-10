import hashlib

def create_numeric_hash(string):
    # Create a hash object using the SHA-256 algorithm
    hash_object = hashlib.sha256(string.encode())

    # Get the hexadecimal representation of the hash
    hash_value = hash_object.hexdigest()

    # Convert the hexadecimal representation to an integer
    numeric_hash = int(hash_value, 16)

     # Calculate the remainder when dividing by 9223372036854775807
    numeric_hash = numeric_hash % 9223372036854775807

    return numeric_hash

# Example usage
# input_string = "Hello, world!"
# numeric_hash = create_numeric_hash(input_string)
# print(numeric_hash)