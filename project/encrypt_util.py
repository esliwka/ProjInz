import base64
import pickle
import hashlib
import logging
import traceback
from django.conf import settings
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

def encrypt_data(data_):
    try:        
        data_ = str(data_)
        cipher_ = Fernet(settings.ENCRYPT_KEY)
        encrypt_ = cipher_.encrypt(data_.encode('ascii'))
        encrypt_ = base64.urlsafe_b64encode(encrypt_).decode("ascii") 
        return encrypt_

    except Exception as e:
        logging.getLogger("error_logger").error(traceback.format_exc())
        return None


def decrypt_data(data_):
    try:
        data_ = base64.urlsafe_b64decode(data_)
        cipher_ = Fernet(settings.ENCRYPT_KEY)
        decod_ = cipher_.decrypt(data_).decode("ascii")     
        return decod_

    except Exception as e:
        logging.getLogger("error_logger").error(traceback.format_exc())
        return None

def hash_data(data_):
    H = hashes.Hash(hashes.SHA3_224(), backend=default_backend())
    H.update(pickle.dumps(data_))
    return H.finalize()

def sec_hash(data_, hash_type=""):
    if hash_type == 'sha3_2':
        return hashlib.sha3_256(data_.encode()).hexdigest()
    elif hash_type == 'sha3_3':
        return hashlib.sha3_384(data_.encode()).hexdigest()
    elif hash_type == 'sha3_5':
        return hashlib.sha3_512(data_.encode()).hexdigest()
    else:
        return hashlib.sha3_224(str(data_).encode()).hexdigest()
    