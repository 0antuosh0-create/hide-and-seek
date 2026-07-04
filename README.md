# Hide and Seek

**English** | [فارسی](README.fa.md)

A modern Python desktop application for image steganography. Hide encrypted messages inside images using LSB encoding with optional AES-256 encryption.

## Features

- **LSB Steganography** — Hide messages in the least significant bits of RGB pixels
- **AES-256 Encryption** — Optional Fernet encryption with PBKDF2 key derivation
- **Unique Salt** — Each message gets a random salt for maximum security
- **Batch Processing** — Encode/decode multiple images at once
- **Drag & Drop** — Drag images directly onto the drop zone
- **Multi-Format** — Export as PNG, BMP, or TIFF (all lossless)
- **Dark Theme** — GitHub-inspired UI with smooth animations
- **Risk Meter** — Real-time detection risk analysis
- **Image Comparison** — Side-by-side view with PSNR calculation

## Installation

```bash
pip install customtkinter Pillow cryptography numpy
python steganohide.py
```

Dependencies are auto-installed on first run if missing.

## How It Works

Each pixel has R, G, B channels (0-255). LSB encoding replaces the least significant bit of each channel with one bit of your message. Changing bit 0 of a value like 182 (10110110) to 183 (10110111) is a difference of 1 — invisible to the human eye.

### Binary Protocol

```
MAGIC (32 bits) | FLAG (8 bits) | SALT (128 bits) | LENGTH (32 bits) | PAYLOAD (N bits)
```

- **MAGIC**: `"STEG"` header for detection
- **FLAG**: `0xFF` if encrypted, `0x00` if plain text
- **SALT**: Unique random salt for key derivation
- **LENGTH**: Payload size in bits
- **PAYLOAD**: The hidden message (optionally encrypted)

## Security Notes

- All processing is 100% local — nothing leaves your computer
- Encryption uses industry-standard AES-256 via Fernet
- PBKDF2 with 100,000 iterations for secure key derivation
- Each message gets a unique random salt
- Output is always lossless (PNG, BMP, TIFF)

### Limitations

- JPEG images lose hidden data (lossy compression destroys LSBs)
- Image editing, resizing, or cropping destroys hidden data
- Without a password, anyone can decode the message
- LSB steganography can be detected by statistical analysis

## License

MIT License - Made by Antoush, Long May The Sunshine — see [LICENSE](LICENSE) for details.
