#!/usr/bin/env python3
"""
Generate a self-signed SSL certificate for Jupyter Lab.

Creates:
  - jupyter.key (private key)
  - jupyter.pem (certificate)

Usage:
  python generate_jupyter_certificate.py --output-dir ./certs --days 365
"""
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtensionOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization


def generate_jupyter_certificate(output_dir: Path, days: int = 365):
    """
    Generate a self-signed certificate for Jupyter Lab.
    
    Args:
        output_dir: Directory to save the key and certificate
        days: Validity period in days (default: 365)
    """
    output_dir = Path(output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    
    key_path = output_dir / "jupyter.key"
    cert_path = output_dir / "jupyter.pem"
    
    print(f"Generating self-signed certificate for Jupyter Lab...")
    print(f"  Valid for {days} days")
    print(f"  Output directory: {output_dir}")
    
    # Generate private key
    print("  Generating RSA private key (2048-bit)...")
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    
    # Build certificate
    print("  Building certificate...")
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "State"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Locality"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Algorithmic Trading"),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Trading Bot"),
        x509.NameAttribute(NameOID.COMMON_NAME, "jupyter-lab"),
    ])
    
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow())
        .not_valid_after(datetime.utcnow() + timedelta(days=days))
        .add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.DNSName("127.0.0.1"),
                x509.DNSName("jupyter-lab"),
                x509.DNSName("*.local"),
            ]),
            critical=False,
        )
        .add_extension(
            x509.BasicConstraints(ca=False, path_length=None),
            critical=True,
        )
        .sign(private_key, hashes.SHA256())
    )
    
    # Save private key
    print(f"  Saving private key to {key_path}...")
    with open(key_path, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))
    key_path.chmod(0o600)
    
    # Save certificate
    print(f"  Saving certificate to {cert_path}...")
    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    
    print("✓ Certificate generation complete!")
    print(f"  Private Key: {key_path}")
    print(f"  Certificate: {cert_path}")
    print()
    print("Use these files with Jupyter Lab:")
    print(f"  jupyter lab --certfile={cert_path} --keyfile={key_path}")
    

def main():
    parser = argparse.ArgumentParser(
        description="Generate self-signed SSL certificate for Jupyter Lab"
    )
    parser.add_argument(
        "--output-dir",
        default="./certs",
        help="Directory to save certificate files (default: ./certs)"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=365,
        help="Certificate validity period in days (default: 365)"
    )
    
    args = parser.parse_args()
    generate_jupyter_certificate(args.output_dir, args.days)


if __name__ == "__main__":
    main()
