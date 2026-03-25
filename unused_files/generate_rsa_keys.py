#!/usr/bin/env python3
"""
Generate RSA private + public key pair and save as PEM files.

Usage examples:
  python generate_rsa_keys.py --private private.pem --public public.pem
  python generate_rsa_keys.py --private private.pem --public public.pem --passphrase mypass
"""
import argparse
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import BestAvailableEncryption, NoEncryption


def generate_rsa_keypair(key_size: int = 4096):
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=key_size)
    public_key = private_key.public_key()
    return private_key, public_key


def save_private_key(private_key, path: Path, passphrase: str | None = None):
    if passphrase:
        encryption = BestAvailableEncryption(passphrase.encode())
    else:
        encryption = NoEncryption()

    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption,
    )
    path.write_bytes(pem)


def save_public_key(public_key, path: Path):
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    path.write_bytes(pem)


def main():
    parser = argparse.ArgumentParser(description="Generate RSA key pair and save as PEM files")
    parser.add_argument("--private", required=True, help="Path to write private key (PEM)")
    parser.add_argument("--public", required=True, help="Path to write public key (PEM)")
    parser.add_argument("--passphrase", help="Optional passphrase to encrypt the private key")
    parser.add_argument("--bits", type=int, default=4096, help="RSA key size in bits (default: 4096)")

    args = parser.parse_args()

    priv_path = Path(args.private).expanduser().resolve()
    pub_path = Path(args.public).expanduser().resolve()

    priv_path.parent.mkdir(parents=True, exist_ok=True)
    pub_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Generating {args.bits}-bit RSA key pair...")
    private_key, public_key = generate_rsa_keypair(key_size=args.bits)

    print(f"Saving private key to {priv_path}")
    save_private_key(private_key, priv_path, args.passphrase)

    print(f"Saving public key to {pub_path}")
    save_public_key(public_key, pub_path)

    print("Done.")


if __name__ == "__main__":
    main