from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os
import base64

def encode_aes_256(key: bytes, plaintext: str) -> bytes:
    """Encrypts the plaintext using AES-256 encryption."""
    plaintext_bytes = plaintext.encode('utf-8')
    iv = os.urandom(12)  # GCM standard IV size is 12 bytes
    encryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv),
    ).encryptor()

    ciphertext = encryptor.update(plaintext_bytes) + encryptor.finalize()

    encodedb64_ciphertext = base64.b64encode(iv + encryptor.tag + ciphertext)
    return encodedb64_ciphertext

def decode_aes_256(key: bytes, encoded_ciphertext: str) -> str:
    """Decrypts the ciphertext using AES-256 decryption."""
    ciphertext_bytes = base64.b64decode(encoded_ciphertext)
    iv = ciphertext_bytes[:12]
    tag = ciphertext_bytes[12:28]
    ciphertext = ciphertext_bytes[28:]

    decryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv, tag),
    ).decryptor()

    plaintext_bytes = decryptor.update(ciphertext) + decryptor.finalize()
    return plaintext_bytes.decode('utf-8')