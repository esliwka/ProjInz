import hashlib
import secrets

def generate_salt():
    return secrets.token_hex(3)

def sec_hash(data_, hash_type=""):
    # data_ = generate_salt() + data_
    if hash_type == 'sha3_2':
        return hashlib.sha3_256(data_.encode()).hexdigest()
    elif hash_type == 'sha3_3':
        return hashlib.sha3_384(data_.encode()).hexdigest()
    elif hash_type == 'sha3_5':
        return hashlib.sha3_512(data_.encode()).hexdigest()
    else:
        return hashlib.sha3_224(str(data_).encode()).hexdigest()