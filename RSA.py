# - Keygen (generate two primes p,q)
# - Encrypt/Decrypt integers with modular exponentiation
# Uses Miller-Rabin for primality testing.

import secrets
import math

# ---------------------------
# Miller-Rabin primality test
# ---------------------------
def is_probable_prime(n, k=10):
    """Return True if n is probably prime (Miller-Rabin with k rounds)."""
    if n < 2:
        return False
    # small primes quick check
    small_primes = [2,3,5,7,11,13,17,19,23,29]
    for p in small_primes:
        if n % p == 0:
            return n == p
    # write n-1 as d*2^s
    s = 0
    d = n - 1
    while d % 2 == 0:
        d //= 2
        s += 1
    def trial(a):
        x = pow(a, d, n)
        if x == 1 or x == n-1:
            return True
        for _ in range(s-1):
            x = (x * x) % n
            if x == n-1:
                return True
        return False
    for _ in range(k):
        a = secrets.randbelow(n - 3) + 2  # in [2, n-2]
        if not trial(a):
            return False
    return True

# ---------------------------
# Random prime generation
# ---------------------------
def generate_prime(bits):
    """Generate a prime number of exactly `bits` bits (probabilistic)."""
    assert bits >= 2
    while True:
        # high bit and low bit set to ensure bit length and oddness
        p = secrets.randbits(bits) | (1 << (bits - 1)) | 1
        if is_probable_prime(p):
            return p

# ---------------------------
# Extended GCD / modular inverse
# ---------------------------
def egcd(a, b):
    if b == 0:
        return (a, 1, 0)
    g, x1, y1 = egcd(b, a % b)
    return (g, y1, x1 - (a // b) * y1)

def modinv(a, m):
    g, x, _ = egcd(a, m)
    if g != 1:
        raise ValueError("modular inverse does not exist")
    return x % m

# ---------------------------
# Key generation
# ---------------------------
def generate_rsa_keypair(bits=1024, e=65537):
    """Generate an RSA keypair. bits is the total size of n (p and q roughly bits/2)."""
    half = bits // 2
    while True:
        p = generate_prime(half)
        q = generate_prime(bits - half)
        if p == q:
            continue
        n = p * q
        phi = (p - 1) * (q - 1)
        if math.gcd(e, phi) == 1:
            d = modinv(e, phi)
            return {"n": n, "e": e, "d": d, "p": p, "q": q}

# ---------------------------
# Basic RSA primitives
# ---------------------------
def rsa_encrypt_int(m, pub):
    """Encrypt integer m with public key pub={'n':n,'e':e}."""
    n, e = pub["n"], pub["e"]
    if not (0 <= m < n):
        raise ValueError("message integer out of range")
    return pow(m, e, n)

def rsa_decrypt_int(c, priv):
    """Decrypt integer c with private key priv={'n':n,'d':d}."""
    n, d = priv["n"], priv["d"]
    return pow(c, d, n)

# ---------------------------
# Byte-string helpers
# ---------------------------
def bytes_to_int(b):
    return int.from_bytes(b, byteorder="big")

def int_to_bytes(i, length=None):
    if length is None:
        # minimal length
        length = (i.bit_length() + 7) // 8 or 1
    return i.to_bytes(length, byteorder="big")

# Simple (insecure) padding for demo only: PKCS#1 v1.5-style (not full!)
def pkcs1_v15_pad(message_bytes, target_len):
    """
    Very small demo padding:
    - target_len: key size in bytes (i.e., ceil(n.bit_length()/8))
    - This pads as: 0x00 || 0x02 || PS || 0x00 || M, where PS are nonzero random bytes.
    Note: For production use, use a proper PKCS#1 v2.2 OAEP implementation.
    """
    mlen = len(message_bytes)
    if mlen > target_len - 11:
        raise ValueError("message too long for this key size")
    ps_len = target_len - mlen - 3
    # PS must be nonzero random bytes
    ps = bytearray()
    while len(ps) < ps_len:
        b = secrets.token_bytes(1)
        if b != b'\x00':
            ps += b
    return b'\x00\x02' + bytes(ps) + b'\x00' + message_bytes

def pkcs1_v15_unpad(padded):
    if len(padded) < 11 or padded[0:2] != b'\x00\x02':
        raise ValueError("bad padding")
    # find 0x00 separator
    sep_idx = padded.find(b'\x00', 2)
    if sep_idx < 0:
        raise ValueError("bad padding")
    return padded[sep_idx+1:]

# ---------------------------
# High-level helpers
# ---------------------------
def rsa_encrypt_bytes(message_bytes, pub):
    n = pub["n"]
    key_len = (n.bit_length() + 7) // 8
    padded = pkcs1_v15_pad(message_bytes, key_len)
    m = bytes_to_int(padded)
    c = rsa_encrypt_int(m, pub)
    return int_to_bytes(c, key_len)

def rsa_decrypt_bytes(cipher_bytes, priv):
    n = priv["n"]
    key_len = (n.bit_length() + 7) // 8
    c = bytes_to_int(cipher_bytes)
    m = rsa_decrypt_int(c, priv)
    padded = int_to_bytes(m, key_len)
    return pkcs1_v15_unpad(padded)

# ---------------------------
# Example usage
# ---------------------------
if __name__ == "__main__":
    # Generate small keypair for demo (use >=2048 bits in production)
    print("Generating RSA keypair (demo 1024-bit)...")
    keypair = generate_rsa_keypair(bits=1024)
    pub = {"n": keypair["n"], "e": keypair["e"]}
    priv = {"n": keypair["n"], "d": keypair["d"]}

    message = b"Hello RSA!"
    print("Plaintext:", message)

    cipher_bytes = rsa_encrypt_bytes(message, pub)
    print("Cipher (hex):", cipher_bytes.hex())

    decrypted = rsa_decrypt_bytes(cipher_bytes, priv)
    print("Decrypted:", decrypted)
    assert decrypted == message
    print("Success: decrypted matches original")
