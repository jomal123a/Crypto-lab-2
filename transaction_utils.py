from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
import json
import string

def serialize_rsa_public(pk: rsa.RSAPublicKey) -> bytes:
    pk_bytes = pk.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.PKCS1
        )
    return pk_bytes


def serialize_rsa_private(sk: rsa.RSAPrivateKey) -> bytes:
    sk_bytes = sk.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
    return sk_bytes


def deserialize_rsa_private(sk: bytes) -> rsa.RSAPrivateKey:
    loaded_private = serialization.load_pem_private_key(
        sk,
        password=None
    )
    return loaded_private


def deserialize_rsa_public(pk: bytes) -> rsa.RSAPrivateKey:
    loaded_public = serialization.load_pem_public_key(
        pk
    )
    return loaded_public


def generate_rsa_key_pair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()
    return (private_key, public_key)


class Transaction:
    def __init__(self, 
                 tx: rsa.RSAPublicKey = None, 
                 rx: rsa.RSAPublicKey = None, 
                 ammount: float = 0.0,
                 t_balance: float = 0.0):
        self.tx = tx
        self.rx = rx
        self.ammount = ammount
        self.t_balance = t_balance

    def to_dict(self):
        tx_bytes = serialize_rsa_public(self.tx)
        rx_bytes = serialize_rsa_public(self.rx)

        trans = {"tx": tx_bytes, 
                 "rx": rx_bytes, 
                 "ammount": self.ammount,
                 "t_balance": self.t_balance}

        return trans
    
    def from_dict(self, trans_dict):
        self.tx = deserialize_rsa_public(trans_dict["tx"])
        self.rx = deserialize_rsa_public(trans_dict["tx"])
        self.ammount = trans_dict["ammount"]
        self.t_balance = trans_dict["t_balance"]
        