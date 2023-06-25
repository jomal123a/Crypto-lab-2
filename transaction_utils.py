from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.serialization import load_pem_private_key
import json
import string
import hashlib
import random
from datetime import datetime
from data import (
    Blockchain,
    Block
)


def find_miner_pk(block: Block):
    pk = None
    for r in block['records']:
        if not isinstance(r['content'], str):
            if r['content']['tx'] == 'SERVER':
                k = r['content']['rx']
                k = bytes(k, 'utf-8')
                pk = deserialize_rsa_public(k)
    return pk


def get_hash(data):
    sha256_hash = hashlib.sha256()
    sha256_hash.update(data)
    digest = sha256_hash.digest()
    return digest


def pow_calc_attempt(block: Block, d, pk, sk):
    block['timestamp'] = datetime.now().timestamp()
    b = random.getrandbits(32)
    b_hex = format(b, f'08x')

    t = Transaction(None, pk, 1.0, 0, True)
    block['PoW'] = b_hex
    block.add_new_prize_record(t.to_dict(to_str=True))

    data = json.dumps(block).encode('utf-8')

    #h_data = get_hash(data)
    # now h_data is also digital signature of a miner
    h_data = sign(data, sk)
    token = get_hash(h_data + bytes.fromhex(b_hex))
    token_num = int.from_bytes(token, "big")

    if token_num < ((2**256) / d):
        return (True, h_data)
    return (False, None)


def pow_check(block: Block, d: int, pk_miner: rsa.RSAPublicKey, signature: bytes):
    data = json.dumps(block).encode('utf-8')

    # Check if the digital signature matches
    if not verify(signature, data, pk_miner):
        return False
    
    h_data = signature
    token = get_hash(h_data + bytes.fromhex(block["PoW"]))
    token_num = int.from_bytes(token, "big")

    if token_num < ((2**256) / d):
        return True
    return False


def verify(signature: bytes, data: bytes, pk: rsa.RSAPublicKey):
    try:
        pk.verify(
            signature,
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except InvalidSignature:
        return False


def sign(data: bytes, sk: rsa.RSAPrivateKey) -> bytes:
    signature = sk.sign(
        data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature


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
        key_size=512
    )
    public_key = private_key.public_key()
    return (private_key, public_key)


def save_key(pk: rsa.RSAPrivateKey, filename):
    pem = pk.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    with open(filename, 'wb') as pem_out:
        pem_out.write(pem)



def load_key(filename):
    with open(filename, 'rb') as pem_in:
        pemlines = pem_in.read()
    private_key = load_pem_private_key(pemlines, None)
    return private_key


class Transaction:
    def __init__(self, 
                 tx: rsa.RSAPublicKey = None, 
                 rx: rsa.RSAPublicKey = None, 
                 ammount: float = 0.0,
                 t_balance: float = 0.0,
                 from_server: bool = False,
                 signature: bytes = None):
        self.tx = tx
        self.rx = rx
        self.ammount = ammount
        self.t_balance = t_balance
        self.from_server = from_server
        self.signature = signature

    def calc_signature(self, sk: rsa.RSAPrivateKey):
        data = self.to_dict(to_str=True)
        del data['t_balance']
        del data['signature']
        data_json = json.dumps(data).encode('utf-8')
        signature = sign(data_json, sk)
        return signature

    def to_dict(self, to_str=False):
        if self.from_server:
            tx_bytes = b'SERVER'
        else:
            tx_bytes = serialize_rsa_public(self.tx)
        rx_bytes = serialize_rsa_public(self.rx)

        trans = {"tx": tx_bytes if not to_str else tx_bytes.decode('utf-8'), 
                 "rx": rx_bytes if not to_str else rx_bytes.decode('utf-8'), 
                 "ammount": self.ammount,
                 "t_balance": self.t_balance,
                 "signature": str(self.signature.hex()) if self.signature != None else ""}

        return trans
    
    def from_dict(self, trans_dict):
        if self.from_server:
            self.tx = None
            self.from_server = True
        else:
            self.tx = deserialize_rsa_public(trans_dict["tx"])
        self.rx = deserialize_rsa_public(trans_dict["tx"])
        self.ammount = trans_dict["ammount"]
        self.t_balance = trans_dict["t_balance"]
        self.signature = trans_dict["signature"]
        