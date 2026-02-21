from __future__ import annotations
import os
from dataclasses import dataclass
from typing import Optional

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization

@dataclass
class KeyPair:
    priv: Ed25519PrivateKey
    pub: Ed25519PublicKey

def load_or_create_keypair(path: str) -> KeyPair:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    if os.path.exists(path):
        data = open(path, "rb").read()
        priv = serialization.load_pem_private_key(data, password=None)
        assert isinstance(priv, Ed25519PrivateKey)
        return KeyPair(priv=priv, pub=priv.public_key())

    priv = Ed25519PrivateKey.generate()
    pem = priv.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    with open(path, "wb") as f:
        f.write(pem)
    return KeyPair(priv=priv, pub=priv.public_key())

def pubkey_fingerprint(pub: Ed25519PublicKey) -> str:
    raw = pub.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    # short fingerprint
    return raw.hex()[:16]

def sign(priv: Ed25519PrivateKey, msg: bytes) -> str:
    sig = priv.sign(msg)
    return sig.hex()

def verify(pub: Ed25519PublicKey, msg: bytes, sig_hex: str) -> bool:
    try:
        pub.verify(bytes.fromhex(sig_hex), msg)
        return True
    except Exception:
        return False
