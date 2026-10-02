"""
stego_core.py
=============
Core engine for the "Secure Steganography System Using Cryptographic Encryption".

Pipeline (Chapter 3, Algorithms 1 and 2)
----------------------------------------
Embedding :  Plain message -> AES-256-GCM encryption -> binary -> LSB embedding -> Stego-image
Extraction:  Stego-image   -> LSB extraction -> ciphertext -> AES-256-GCM decryption -> Plain message

Design decisions
----------------
* Encryption  : AES-256 in GCM mode (authenticated encryption) from the `cryptography`
                library. The 256-bit key is derived from the user's password with
                PBKDF2-HMAC-SHA256 (600,000 iterations) and a random 16-byte salt.
* Embedding   : LSB substitution on the R, G, B bytes of the cover image (1-4 bits/byte).
* Header      : A small fixed header (payload length, bit-depth, KDF salt) is stored in the
                LSBs of the first 168 bytes of the image, so the extractor knows where the
                hidden message ends (Chapter 3, section 3.17).
* Scattering  : The ciphertext bits are NOT written sequentially. Their positions come from a
                key-dependent pseudo-random permutation (Feistel network), which removes the
                "predictable embedding pattern" weakness noted in Chapter 1, section 1.8.
* Integrity   : GCM's authentication tag detects a wrong password OR a modified stego-image.
* Output      : Always a lossless PNG (JPEG compression would destroy the LSBs).

Payload layout (what is hidden in the image)
--------------------------------------------
    HEADER  (21 bytes, 1 bit per byte, sequential) : length(4) | depth(1) | salt(16)
    BODY    (scattered, `depth` bits per byte)     : nonce(12) | ciphertext | GCM tag(16)
"""

from __future__ import annotations

import hashlib
import io
import math
import struct
from dataclasses import dataclass

import numpy as np
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from PIL import Image

# --------------------------------------------------------------------------- constants
KDF_ITERATIONS = 600_000
SALT_LEN = 16
NONCE_LEN = 12
TAG_LEN = 16
OVERHEAD_BYTES = NONCE_LEN + TAG_LEN          # bytes added by encryption
HEADER_BYTES = 4 + 1 + SALT_LEN               # length + depth + salt
HEADER_BITS = HEADER_BYTES * 8                # 168 carrier bytes, 1 LSB each
MIN_DEPTH, MAX_DEPTH = 1, 4
MAX_PIXELS = 25_000_000
SUPPORTED_FORMATS = ("PNG", "JPEG", "BMP")


# --------------------------------------------------------------------------- exceptions
class StegoError(Exception):
    """Base class for all errors raised by this module."""


class CapacityError(StegoError):
    """The message does not fit into the selected cover image."""


class ExtractionError(StegoError):
    """No hidden data found, wrong key, or the stego-image was altered."""


# --------------------------------------------------------------------------- image helpers
def load_image(data: bytes | io.BytesIO | str) -> Image.Image:
    """Load an uploaded image, validate its format/size and return an RGB image."""
    try:
        if isinstance(data, (bytes, bytearray)):
            data = io.BytesIO(data)
        img = Image.open(data)
        fmt = (img.format or "").upper()
        img.load()
    except Exception as exc:  # noqa: BLE001
        raise StegoError("The selected file is not a valid image.") from exc
    if fmt not in SUPPORTED_FORMATS:
        raise StegoError(f"Unsupported image format '{fmt}'. Use PNG, JPG or BMP.")
    if img.width * img.height > MAX_PIXELS:
        raise StegoError("Image is too large (maximum 25 megapixels).")
    return img.convert("RGB")


def image_to_png_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="PNG", compress_level=6)
    return buf.getvalue()


# --------------------------------------------------------------------------- capacity (Chapter 3, 3.18)
def raw_capacity_bits(width: int, height: int, depth: int = 1, channels: int = 3) -> int:
    """Capacity = Width x Height x Channels x Bits  (Chapter 3, section 3.18)."""
    return width * height * channels * depth


def payload_capacity_bytes(width: int, height: int, depth: int = 1) -> int:
    """Bytes of payload (nonce + ciphertext + tag) that fit, after reserving the header."""
    n = width * height * 3
    return max(0, ((n - HEADER_BITS) * depth) // 8)


def max_message_bytes(width: int, height: int, depth: int = 1) -> int:
    """Largest plaintext (UTF-8 bytes) that can be hidden in an image of this size."""
    return max(0, payload_capacity_bytes(width, height, depth) - OVERHEAD_BYTES)


# --------------------------------------------------------------------------- cryptography
def derive_keys(password: str, salt: bytes) -> tuple[bytes, bytes]:
    """Derive (AES-256 key, position-seed) from the password with PBKDF2-HMAC-SHA256."""
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=64, salt=salt, iterations=KDF_ITERATIONS)
    okm = kdf.derive(password.encode("utf-8"))
    return okm[:32], okm[32:]


def encrypt(plaintext: bytes, aes_key: bytes, aad: bytes, nonce: bytes) -> bytes:
    """AES-256-GCM. Returns ciphertext || tag."""
    return AESGCM(aes_key).encrypt(nonce, plaintext, aad)


def decrypt(ciphertext_and_tag: bytes, aes_key: bytes, aad: bytes, nonce: bytes) -> bytes:
    return AESGCM(aes_key).decrypt(nonce, ciphertext_and_tag, aad)


# --------------------------------------------------------------------------- keyed scattering
_C1 = np.uint64(0x9E3779B97F4A7C15)
_C2 = np.uint64(0xBF58476D1CE4E5B9)


def _round_keys(seed: bytes, rounds: int = 8) -> list[np.uint64]:
    return [
        np.uint64(int.from_bytes(hashlib.sha256(seed + bytes([r])).digest()[:8], "big"))
        for r in range(rounds)
    ]


def _feistel(x: np.ndarray, half: int, mask: np.uint64, rks: list[np.uint64]) -> np.ndarray:
    with np.errstate(over="ignore"):
        left = x >> np.uint64(half)
        right = x & mask
        for rk in rks:
            t = (right ^ rk) * _C1
            t ^= t >> np.uint64(29)
            t = t * _C2
            t ^= t >> np.uint64(32)
            left, right = right, left ^ (t & mask)
        return (left << np.uint64(half)) | right


def keyed_permutation(indices: np.ndarray, n: int, seed: bytes) -> np.ndarray:
    """
    Key-dependent permutation of the integers [0, n).
    A balanced Feistel network over the next power-of-4 domain plus "cycle walking"
    gives a true bijection, so no carrier byte is ever used twice.
    Pure integer arithmetic -> identical results on every machine / NumPy version.
    """
    if n < 2:
        return indices.astype(np.int64)
    bits = (n - 1).bit_length()
    bits += bits % 2
    bits = max(bits, 2)
    half = bits // 2
    mask = np.uint64((1 << half) - 1)
    rks = _round_keys(seed)
    y = _feistel(indices.astype(np.uint64), half, mask, rks)
    limit = np.uint64(n)
    bad = y >= limit
    while bad.any():
        y[bad] = _feistel(y[bad], half, mask, rks)
        bad = y >= limit
    return y.astype(np.int64)


def _body_positions(count: int, total_bytes: int, seed: bytes) -> np.ndarray:
    """Carrier-byte indices (after the header region) used for `count` hidden groups."""
    body_size = total_bytes - HEADER_BITS
    return HEADER_BITS + keyed_permutation(np.arange(count, dtype=np.uint64), body_size, seed)


# --------------------------------------------------------------------------- embedding
@dataclass
class EmbedResult:
    stego: Image.Image
    message_bytes: int      # plaintext size
    payload_bytes: int      # nonce + ciphertext + tag actually hidden
    capacity_bytes: int     # max payload for this image / depth
    depth: int
    ciphertext_hex: str


def embed(cover: Image.Image, message: str, password: str, depth: int = 1) -> EmbedResult:
    """Encrypt `message` with `password` and hide it in `cover` (Algorithm 1)."""
    import os

    # ---- 1-4: accept and validate input
    if not message or not message.strip():
        raise StegoError("Please enter a secret message.")
    if not password:
        raise StegoError("Please enter an encryption key (password).")
    if not MIN_DEPTH <= depth <= MAX_DEPTH:
        raise StegoError(f"Bit depth must be between {MIN_DEPTH} and {MAX_DEPTH}.")

    plaintext = message.encode("utf-8")
    cover = cover.convert("RGB")
    w, h = cover.size
    capacity = payload_capacity_bytes(w, h, depth)
    needed = len(plaintext) + OVERHEAD_BYTES
    if needed > capacity:
        raise CapacityError(
            f"Message too large: needs {needed:,} bytes but this image holds only "
            f"{capacity:,} bytes at {depth} bit(s) per channel. "
            f"Use a larger image, a shorter message, or a higher bit depth."
        )

    # ---- 5: encrypt
    salt, nonce = os.urandom(SALT_LEN), os.urandom(NONCE_LEN)
    aes_key, pos_seed = derive_keys(password, salt)
    aad = salt + bytes([depth])
    ct_and_tag = encrypt(plaintext, aes_key, aad, nonce)
    payload = nonce + ct_and_tag

    # ---- 6: binary representation
    carrier = np.asarray(cover, dtype=np.uint8).reshape(-1).copy()
    total = carrier.size

    header = struct.pack(">IB", len(payload), depth) + salt
    header_bits = np.unpackbits(np.frombuffer(header, dtype=np.uint8))
    carrier[:HEADER_BITS] = (carrier[:HEADER_BITS] & 0xFE) | header_bits

    bits = np.unpackbits(np.frombuffer(payload, dtype=np.uint8))
    pad = (-len(bits)) % depth
    if pad:
        bits = np.concatenate([bits, np.zeros(pad, dtype=np.uint8)])
    groups = bits.reshape(-1, depth).astype(np.uint16)
    weights = (1 << np.arange(depth - 1, -1, -1)).astype(np.uint16)
    values = (groups * weights).sum(axis=1).astype(np.uint8)

    # ---- 10: modify least significant bits at key-dependent positions
    pos = _body_positions(len(values), total, pos_seed)
    clear_mask = np.uint8(0xFF ^ ((1 << depth) - 1))
    carrier[pos] = (carrier[pos] & clear_mask) | values

    stego = Image.fromarray(carrier.reshape(h, w, 3), "RGB")
    return EmbedResult(
        stego=stego,
        message_bytes=len(plaintext),
        payload_bytes=len(payload),
        capacity_bytes=capacity,
        depth=depth,
        ciphertext_hex=payload.hex(),
    )


# --------------------------------------------------------------------------- extraction
@dataclass
class ExtractResult:
    message: str
    payload_bytes: int
    depth: int
    ciphertext_hex: str


def extract(stego: Image.Image, password: str) -> ExtractResult:
    """Extract and decrypt the hidden message (Algorithm 2)."""
    if not password:
        raise StegoError("Please enter the decryption key (password).")

    stego = stego.convert("RGB")
    carrier = np.asarray(stego, dtype=np.uint8).reshape(-1)
    total = carrier.size
    no_data = ExtractionError(
        "No hidden message could be found in this image (it may not be a stego-image, "
        "or it was re-compressed / edited after embedding)."
    )
    if total <= HEADER_BITS + 8:
        raise no_data

    # ---- read header
    header = np.packbits(carrier[:HEADER_BITS] & 1).tobytes()
    length, depth = struct.unpack(">IB", header[:5])
    salt = header[5:5 + SALT_LEN]
    if not MIN_DEPTH <= depth <= MAX_DEPTH:
        raise no_data
    if length < OVERHEAD_BYTES + 1 or length > ((total - HEADER_BITS) * depth) // 8:
        raise no_data

    # ---- read scattered body
    aes_key, pos_seed = derive_keys(password, salt)
    n_groups = math.ceil(length * 8 / depth)
    pos = _body_positions(n_groups, total, pos_seed)
    values = carrier[pos] & ((1 << depth) - 1)
    shifts = np.arange(depth - 1, -1, -1, dtype=np.uint8)
    bits = ((values[:, None] >> shifts) & 1).reshape(-1)[: length * 8].astype(np.uint8)
    payload = np.packbits(bits).tobytes()

    # ---- decrypt (authentication tag verifies key AND integrity)
    nonce, ct_and_tag = payload[:NONCE_LEN], payload[NONCE_LEN:]
    try:
        plaintext = decrypt(ct_and_tag, aes_key, salt + bytes([depth]), nonce)
    except InvalidTag as exc:
        raise ExtractionError(
            "Decryption failed: the key is incorrect, or the stego-image has been modified."
        ) from exc
    try:
        message = plaintext.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ExtractionError("Decrypted data is not valid text.") from exc

    return ExtractResult(message=message, payload_bytes=length, depth=depth,
                         ciphertext_hex=payload.hex())


# --------------------------------------------------------------------------- image quality (Chapter 2, 2.13)
def quality_metrics(original: Image.Image, stego: Image.Image) -> dict:
    """MSE and PSNR between two images of equal size (8-bit, MAX_I = 255)."""
    a = np.asarray(original.convert("RGB"), dtype=np.float64)
    b = np.asarray(stego.convert("RGB"), dtype=np.float64)
    if a.shape != b.shape:
        raise StegoError("Images must have the same dimensions to be compared.")
    diff = a - b
    mse = float(np.mean(diff ** 2))
    psnr = float("inf") if mse == 0 else 10 * math.log10(255.0 ** 2 / mse)
    return {
        "mse": mse,
        "psnr": psnr,
        "changed_pct": float(np.mean(a != b) * 100),
        "max_diff": int(np.max(np.abs(diff))),
    }


def difference_image(original: Image.Image, stego: Image.Image) -> Image.Image:
    """Amplified absolute difference (so invisible changes become visible)."""
    a = np.asarray(original.convert("RGB"), dtype=np.int16)
    b = np.asarray(stego.convert("RGB"), dtype=np.int16)
    d = np.abs(a - b)
    peak = d.max()
    if peak > 0:
        d = d * (255 // peak)
    return Image.fromarray(d.astype(np.uint8), "RGB")


def lsb_plane(img: Image.Image) -> Image.Image:
    """Visualise the least-significant-bit plane (white = 1, black = 0)."""
    arr = (np.asarray(img.convert("RGB"), dtype=np.uint8) & 1) * 255
    return Image.fromarray(arr.astype(np.uint8), "RGB")


# --------------------------------------------------------------------------- misc helpers
def password_strength(pw: str) -> tuple[int, str]:
    """Very small strength meter: returns (score 0-4, label)."""
    if not pw:
        return 0, "—"
    score = 0
    score += len(pw) >= 8
    score += len(pw) >= 12
    score += (any(c.islower() for c in pw) and any(c.isupper() for c in pw))
    score += any(c.isdigit() for c in pw) and any(not c.isalnum() for c in pw)
    return score, ["Very weak", "Weak", "Fair", "Good", "Strong"][score]


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def make_demo_cover(width: int = 320, height: int = 240, seed: int = 7) -> Image.Image:
    """Synthetic textured image used by the built-in self-tests / demo."""
    rng = np.random.default_rng(seed)
    x = np.linspace(0, 255, width)[None, :].repeat(height, axis=0)
    y = np.linspace(0, 255, height)[:, None].repeat(width, axis=1)
    noise = rng.integers(-12, 12, size=(height, width, 3))
    img = np.stack([x, y, (x + y) / 2], axis=-1) + noise
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB")
