import hashlib

HASH_TYPES = ['md5', 'sha1', 'sha256', 'sha384', 'sha512']

def generate_checksum(file_path, hash_type='md5'):
    """Generate a checksum for a file using the specified hash type."""
    if not file_path:
        raise ValueError("File path cannot be empty.")
    
    hash_object = hashlib.new(hash_type)
    with open(file_path, 'rb') as f:
        while chunk := f.read(4096):
            hash_object.update(chunk)
    
    return hash_object.hexdigest()

def compare_checksum_with_string(file_path, expected_string, hash_type='md5', console=False):
    """Compare the generated checksum of a file with a given string using the specified hash type."""
    if not file_path:
        raise ValueError("File path cannot be empty.")
    
    calculated_checksum = generate_checksum(file_path, hash_type)
    
    result = bool(calculated_checksum.lower() == expected_string.lower())
    if console: 
        compare_result_log_to_console(result, calculated_checksum, expected_string)
    return(result)

def get_all_checksums(file_path):
    checksums = dict({})

    for hash_type in HASH_TYPES:
        checksums[hash_type.upper()] = generate_checksum(file_path, hash_type)
    
    return checksums

# output into string for console purpose
def print_key_value_pair(checksums):
    """Print a dictionary with checksum types as keys and their corresponding values."""
    for hash_type, checksum in checksums.items():
        print(f"{hash_type} Checksum: {checksum}")

def compare_result_log_to_console(result, calculated_checksum, expected_string):
    print(f"Checksum matches: {calculated_checksum}" if result else f"Checksum does not match. Expected: {expected_string}, Got: {calculated_checksum}")


"""console tester"""
if __name__ == "__main__":
    file_path = '6dbc45e956b50a3173c4eb2d075ab1f4.txt'  # Replace with your file path
    expected_string = '6dbc45e956b50a3173c4eb2d075ab1f4'  # Replace with the expected MD5 string

    compare_checksum_with_string(file_path, expected_string, console=True)

    print_key_value_pair(get_all_checksums(file_path))
    print("\n\n")
    for hash_name in get_hash_types():
        print(f"{hash_name}")