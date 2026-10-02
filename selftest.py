"""
selftest.py
===========
Automated test cases for the Secure Steganography System (Chapter 4, sections 4.10 - 4.11).

Run from the command line:   python selftest.py
Or from the app:             sidebar -> "System Tests"
"""

from __future__ import annotations

import io
import time

import numpy as np
from PIL import Image

import stego_core as sc

MESSAGE = "Meet me at 5 PM at the library. Bring the documents."


def _png_roundtrip(img: Image.Image) -> Image.Image:
    return sc.load_image(sc.image_to_png_bytes(img))


def _expect_error(exc_type, fn) -> tuple[bool, str]:
    try:
        fn()
    except exc_type as exc:
        return True, f"{exc_type.__name__}: {str(exc)[:70]}"
    except Exception as exc:  # noqa: BLE001
        return False, f"Unexpected {type(exc).__name__}: {exc}"
    return False, "No error was raised"


def run_all() -> list[dict]:
    cover = sc.make_demo_cover(256, 256)
    w, h = cover.size
    results: list[dict] = []

    def record(tc, title, expected, fn):
        t0 = time.perf_counter()
        try:
            ok, actual = fn()
        except Exception as exc:  # noqa: BLE001
            ok, actual = False, f"Crashed: {type(exc).__name__}: {exc}"
        results.append({
            "Test": tc, "Description": title, "Expected result": expected,
            "Actual result": actual, "Status": "PASS" if ok else "FAIL",
            "Time (s)": round(time.perf_counter() - t0, 2),
        })

    # TC01 -------------------------------------------------------------
    def tc01():
        r = sc.embed(cover, MESSAGE, "Correct#Horse9")
        out = sc.extract(_png_roundtrip(r.stego), "Correct#Horse9")
        return out.message == MESSAGE, "Recovered message identical to original" if out.message == MESSAGE else "Mismatch"
    record("TC01", "Encrypt, embed, save as PNG, extract, decrypt (correct key)",
           "Original message recovered exactly", tc01)

    # TC02 -------------------------------------------------------------
    def tc02():
        msg = "Ẹ ku àbọ̀ 🔐 — 你好 — مرحبا"
        r = sc.embed(cover, msg, "pässwörd-ünïcode")
        out = sc.extract(r.stego, "pässwörd-ünïcode")
        return out.message == msg, "Unicode text recovered" if out.message == msg else "Mismatch"
    record("TC02", "Unicode / emoji message and non-ASCII password",
           "Message recovered exactly", tc02)

    # TC03 -------------------------------------------------------------
    def tc03():
        big = ("A long confidential report. " * 1000)[: sc.max_message_bytes(w, h, 1) // 2]
        r = sc.embed(cover, big, "k3y!")
        out = sc.extract(r.stego, "k3y!")
        return out.message == big, f"{len(big):,}-byte message recovered ({len(big) / sc.max_message_bytes(w, h, 1):.0%} of capacity)"
    record("TC03", "Large message (about 50% of image capacity)",
           "Message recovered exactly", tc03)

    # TC04 -------------------------------------------------------------
    def tc04():
        for d in range(1, 5):
            r = sc.embed(cover, MESSAGE, "pw-depth", depth=d)
            if sc.extract(r.stego, "pw-depth").message != MESSAGE:
                return False, f"Failed at depth {d}"
        return True, "Round trip succeeded for 1, 2, 3 and 4 bits per channel"
    record("TC04", "All supported LSB depths (1-4 bits per channel)",
           "Round trip succeeds at every depth", tc04)

    # shared stego for the negative tests
    base = sc.embed(cover, MESSAGE, "right-key")

    # TC05 -------------------------------------------------------------
    record("TC05", "Extraction with the WRONG key",
           "Rejected with an error; no message revealed",
           lambda: _expect_error(sc.ExtractionError, lambda: sc.extract(base.stego, "wrong-key")))

    # TC06 -------------------------------------------------------------
    record("TC06", "Extraction from an ordinary image (nothing hidden)",
           "Reports that no hidden message exists",
           lambda: _expect_error(sc.ExtractionError, lambda: sc.extract(cover, "right-key")))

    # TC07 -------------------------------------------------------------
    record("TC07", "Message larger than image capacity",
           "Rejected with a capacity error",
           lambda: _expect_error(sc.CapacityError,
                                 lambda: sc.embed(cover, "x" * (sc.max_message_bytes(w, h, 1) + 1), "k")))

    # TC08 -------------------------------------------------------------
    record("TC08", "Empty message",
           "Rejected with a validation error",
           lambda: _expect_error(sc.StegoError, lambda: sc.embed(cover, "   ", "k")))

    # TC09 -------------------------------------------------------------
    record("TC09", "Empty key / password",
           "Rejected with a validation error",
           lambda: _expect_error(sc.StegoError, lambda: sc.embed(cover, MESSAGE, "")))

    # TC10 -------------------------------------------------------------
    def tc10():
        arr = np.asarray(base.stego, dtype=np.uint8).reshape(-1).copy()
        arr[sc.HEADER_BITS:] ^= 1                       # flip every body LSB
        tampered = Image.fromarray(arr.reshape(h, w, 3), "RGB")
        return _expect_error(sc.ExtractionError, lambda: sc.extract(tampered, "right-key"))
    record("TC10", "Stego-image tampered with after embedding",
           "GCM authentication fails; tampering detected", tc10)

    # TC11 -------------------------------------------------------------
    def tc11():
        m = sc.quality_metrics(cover, base.stego)
        return m["psnr"] > 50 and m["max_diff"] <= 1, f"PSNR = {m['psnr']:.2f} dB, MSE = {m['mse']:.5f}, max pixel change = {m['max_diff']}"
    record("TC11", "Imperceptibility (1-bit LSB): PSNR / MSE",
           "PSNR above 50 dB, no pixel changes by more than 1", tc11)

    # TC12 -------------------------------------------------------------
    def tc12():
        m1 = sc.quality_metrics(cover, sc.embed(cover, MESSAGE, "pw", 1).stego)
        m4 = sc.quality_metrics(cover, sc.embed(cover, "x" * 3000, "pw", 4).stego)
        return m1["psnr"] > m4["psnr"], f"1-bit: {m1['psnr']:.1f} dB  vs  4-bit (large msg): {m4['psnr']:.1f} dB"
    record("TC12", "Capacity / quality trade-off (Chapter 2, 2.9)",
           "Lower depth gives higher PSNR", tc12)

    # TC13 -------------------------------------------------------------
    def tc13():
        a = sc.embed(cover, MESSAGE, "same-key")
        b = sc.embed(cover, MESSAGE, "same-key")
        differ = a.ciphertext_hex != b.ciphertext_hex
        return differ, "Ciphertexts differ (fresh random salt + nonce each time)" if differ else "Identical ciphertexts!"
    record("TC13", "Same message + same key encrypted twice",
           "Different ciphertext each time", tc13)

    # TC14 -------------------------------------------------------------
    def tc14():
        leaked = MESSAGE.encode().hex() in base.ciphertext_hex
        return (not leaked), "Plaintext not present in embedded data" if not leaked else "Plaintext visible!"
    record("TC14", "Plaintext never embedded directly (Chapter 3, 3.19.1)",
           "Only ciphertext is hidden in the image", tc14)

    # TC15 -------------------------------------------------------------
    def tc15():
        exp = w * h * 3 * 2
        got = sc.raw_capacity_bits(w, h, 2)
        return exp == got, f"{w}x{h}x3x2 = {got:,} bits"
    record("TC15", "Capacity formula: Width x Height x Channels x Bits",
           "Implementation matches the Chapter 3 formula", tc15)

    # TC16 -------------------------------------------------------------
    def tc16():
        n = 5000
        total = 40000
        p = sc.keyed_permutation(np.arange(n, dtype=np.uint64), total, b"seed" * 8)
        return len(np.unique(p)) == n and p.max() < total, f"{n:,} distinct positions inside [0, {total:,})"
    record("TC16", "Key-based pixel selection never reuses a carrier byte",
           "All selected positions are unique and in range", tc16)

    # TC17 -------------------------------------------------------------
    def tc17():
        buf = io.BytesIO()
        base.stego.save(buf, format="JPEG", quality=95)
        jpg = sc.load_image(buf.getvalue())
        return _expect_error(sc.ExtractionError, lambda: sc.extract(jpg, "right-key"))
    record("TC17", "Stego-image re-saved as JPEG (documented limitation, Ch.1 1.8)",
           "Hidden data is lost -> system reports failure safely", tc17)

    # TC18 -------------------------------------------------------------
    record("TC18", "Non-image file supplied as cover",
           "Rejected with an invalid-image error",
           lambda: _expect_error(sc.StegoError, lambda: sc.load_image(b"this is not an image")))

    return results


if __name__ == "__main__":
    rows = run_all()
    width = max(len(r["Description"]) for r in rows)
    for r in rows:
        print(f"{r['Test']}  {r['Status']:4}  {r['Description']:<{width}}  [{r['Time (s)']}s]  {r['Actual result']}")
    passed = sum(r["Status"] == "PASS" for r in rows)
    print(f"\n{passed}/{len(rows)} test cases passed")
    raise SystemExit(0 if passed == len(rows) else 1)
