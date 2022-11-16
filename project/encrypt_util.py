import base64
import logging
import traceback
from django.conf import settings
from cryptography.fernet import Fernet

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