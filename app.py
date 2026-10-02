"""
app.py  -  Secure Steganography System Using Cryptographic Encryption
Run with:  streamlit run app.py
"""

from __future__ import annotations

import time
from datetime import datetime

import pandas as pd
import streamlit as st

import stego_core as sc
from about_page import INSTITUTION, MATRIC, STUDENT, TITLE, render_about

st.set_page_config(page_title="SecureStego", page_icon="🔐", layout="wide")

# ----------------------------------------------------------------------------- styling
st.markdown(
    """
    <style>
    .hero{background:linear-gradient(135deg,#1e3a8a 0%,#4f46e5 60%,#7c3aed 100%);
          padding:1.6rem 1.8rem;border-radius:16px;color:#fff;margin-bottom:1.2rem}
    .hero-kicker{font-size:.75rem;letter-spacing:.15em;opacity:.8;font-weight:600}
    .hero-title{font-size:1.5rem;font-weight:700;line-height:1.3;margin:.35rem 0 .6rem}
    .hero-meta{font-size:.95rem;opacity:.92}
    .pipe{display:flex;flex-wrap:wrap;gap:.4rem;align-items:center;margin:.4rem 0 1rem}
    .pipe span{background:rgba(79,70,229,.12);border:1px solid rgba(79,70,229,.35);
               padding:.3rem .7rem;border-radius:999px;font-size:.85rem}
    .pipe i{opacity:.5;font-style:normal}
    .mono{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:.78rem;word-break:break-all}
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------- session state
if "log" not in st.session_state:
    st.session_state.log = []          # activity table (Chapter 3, section 3.20)
if "last_embed" not in st.session_state:
    st.session_state.last_embed = None


def log_activity(operation: str, file_name: str, status: str) -> None:
    st.session_state.log.append({
        "Activity_ID": len(st.session_state.log) + 1,
        "Operation": operation,
        "File_Name": file_name,
        "Date_Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Status": status,
    })


def pipeline(steps: list[str]) -> None:
    html = "<i>→</i>".join(f"<span>{s}</span>" for s in steps)
    st.markdown(f'<div class="pipe">{html}</div>', unsafe_allow_html=True)


# ----------------------------------------------------------------------------- sidebar
with st.sidebar:
    st.markdown("## 🔐 SecureStego")
    st.caption("Secure steganography using cryptographic encryption")
    page = st.radio(
        "Menu",
        ["🏠 Home", "🔏 Encrypt & Hide", "🔓 Extract & Decrypt", "📊 Image Quality", "🧪 System Tests", "ℹ️ About"],
        label_visibility="collapsed",
    )
    st.divider()
    st.caption(f"**{STUDENT}**  \n{MATRIC}  \n{INSTITUTION}")


# ============================================================================= HOME
def page_home() -> None:
    st.markdown(
        f"""<div class="hero"><div class="hero-kicker">FINAL YEAR PROJECT</div>
        <div class="hero-title">{TITLE}</div>
        <div class="hero-meta">Hide encrypted messages inside images — two layers of protection.</div></div>""",
        unsafe_allow_html=True,
    )
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Encryption", "AES-256-GCM")
    c2.metric("Key derivation", "PBKDF2-SHA256")
    c3.metric("Embedding", "LSB, 1–4 bits")
    c4.metric("Output", "Lossless PNG")

    st.subheader("Sending")
    pipeline(["Plain message", "AES-256 encryption", "Encrypted message", "LSB embedding", "Stego-image"])
    st.subheader("Receiving")
    pipeline(["Stego-image", "LSB extraction", "Encrypted message", "Decryption", "Original message"])

    st.info("🔐 **Encryption** protects the *content* of your message.  "
            "🖼️ **Steganography** hides the *existence* of your message.")

    st.subheader("Session activity")
    if st.session_state.log:
        st.dataframe(pd.DataFrame(st.session_state.log), width="stretch", hide_index=True)
    else:
        st.caption("No operations yet — use **Encrypt & Hide** to get started.")


# ============================================================================= HIDE
def page_hide() -> None:
    st.header("🔏 Encrypt & Hide Message")
    pipeline(["Message", "Key", "Encrypt", "Cover image", "Embed", "Stego-image"])

    left, right = st.columns(2, gap="large")

    with left:
        st.subheader("1 · Secret message")
        message = st.text_area("Type the message to protect", height=150, key="hide_msg",
                               placeholder="e.g. Meet me at 5 PM at the library.")
        up_txt = st.file_uploader("…or load a .txt file", type=["txt"], key="hide_txt")
        if up_txt is not None:
            try:
                message = up_txt.getvalue().decode("utf-8")
                st.caption(f"Using text from **{up_txt.name}** ({len(message):,} characters).")
            except UnicodeDecodeError:
                st.error("That text file is not valid UTF-8.")
                message = ""

        st.subheader("2 · Encryption key")
        pw = st.text_input("Password / key", type="password", key="hide_pw")
        pw2 = st.text_input("Confirm password", type="password", key="hide_pw2")
        score, label = sc.password_strength(pw)
        if pw:
            st.progress(score / 4, text=f"Strength: {label}")
        st.caption("⚠️ The key is never stored or embedded. If you lose it, the message cannot be recovered.")

    with right:
        st.subheader("3 · Cover image")
        up_img = st.file_uploader("Choose a cover image (PNG, JPG or BMP)", type=["png", "jpg", "jpeg", "bmp"],
                                  key="hide_img")
        depth = st.select_slider("LSB depth (bits per colour channel)", options=[1, 2, 3, 4], value=1,
                                 help="1 = best image quality, lowest capacity. 4 = highest capacity, more visible change.")
        cover = None
        if up_img is not None:
            try:
                cover = sc.load_image(up_img.getvalue())
                st.image(cover, caption=f"{up_img.name} — {cover.width}×{cover.height}px", width="stretch")
                cap = sc.max_message_bytes(cover.width, cover.height, depth)
                used = len(message.encode("utf-8")) if message else 0
                st.progress(min(1.0, used / cap) if cap else 1.0,
                            text=f"Capacity: {used:,} / {cap:,} bytes ({(used / cap * 100) if cap else 100:.1f}%)")
                st.caption(f"Raw capacity = {cover.width} × {cover.height} × 3 × {depth} = "
                           f"{sc.raw_capacity_bits(cover.width, cover.height, depth):,} bits")
            except sc.StegoError as exc:
                st.error(str(exc))

    st.divider()
    if st.button("🔐 Encrypt & Hide", type="primary", width="stretch"):
        name = up_img.name if up_img else "—"
        if cover is None:
            st.error("Please select a valid cover image.")
        elif pw != pw2:
            st.error("The two passwords do not match.")
        else:
            try:
                t0 = time.perf_counter()
                with st.spinner("Encrypting and embedding…"):
                    res = sc.embed(cover, message, pw, depth)
                    png = sc.image_to_png_bytes(res.stego)
                    metrics = sc.quality_metrics(cover, res.stego)
                st.session_state.last_embed = {
                    "res": res, "png": png, "metrics": metrics, "cover": cover,
                    "name": f"stego_{name.rsplit('.', 1)[0]}.png", "secs": time.perf_counter() - t0,
                }
                log_activity("Embed", name, "Success")
            except sc.StegoError as exc:
                log_activity("Embed", name, "Failure")
                st.error(str(exc))

    out = st.session_state.last_embed
    if out:
        res, m = out["res"], out["metrics"]
        st.success("✅ Message encrypted successfully.  ✅ Message embedded successfully.  "
                   "✅ Stego-image ready to save.")
        a, b = st.columns(2, gap="large")
        with a:
            st.image(out["cover"], caption="Original cover image", width="stretch")
        with b:
            st.image(res.stego, caption="Stego-image (contains the hidden message)", width="stretch")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("PSNR", "∞ dB" if m["psnr"] == float("inf") else f"{m['psnr']:.2f} dB")
        c2.metric("MSE", f"{m['mse']:.5f}")
        c3.metric("Payload hidden", f"{res.payload_bytes:,} B")
        c4.metric("Time", f"{out['secs']:.2f} s")
        st.caption("PSNR above ~40 dB is generally imperceptible to the human eye (Chapter 2, section 2.13).")

        st.download_button("⬇️ Save stego-image (PNG)", out["png"], file_name=out["name"],
                           mime="image/png", type="primary", width="stretch")
        st.warning("Send the image as a **file/document** — apps that re-compress photos "
                   "(WhatsApp photo mode, social media, JPG conversion) destroy the hidden data. "
                   "Share the key through a *different* channel.")
        with st.expander("What is actually hidden inside the image? (ciphertext)"):
            st.code(res.ciphertext_hex, language=None)
            st.caption("nonce (12 B) ‖ AES-GCM ciphertext ‖ authentication tag (16 B). "
                       "Without the key this is indistinguishable from random bytes.")


# ============================================================================= EXTRACT
def page_extract() -> None:
    st.header("🔓 Extract & Decrypt Message")
    pipeline(["Stego-image", "Key", "Extract", "Decrypt", "Original message"])

    left, right = st.columns(2, gap="large")
    with left:
        up = st.file_uploader("Select the stego-image (must be the PNG file produced by this system)",
                              type=["png", "bmp"], key="ext_img")
        pw = st.text_input("Decryption key", type="password", key="ext_pw")
    stego = None
    with right:
        if up is not None:
            try:
                stego = sc.load_image(up.getvalue())
                st.image(stego, caption=f"{up.name} — {stego.width}×{stego.height}px", width="stretch")
            except sc.StegoError as exc:
                st.error(str(exc))

    if st.button("🔓 Extract & Decrypt", type="primary", width="stretch"):
        if stego is None:
            st.error("Please select a valid stego-image.")
            return
        try:
            t0 = time.perf_counter()
            with st.spinner("Extracting and decrypting…"):
                res = sc.extract(stego, pw)
            log_activity("Extract", up.name, "Success")
            st.success("✅ Message extracted and decrypted successfully.")
            st.text_area("Recovered message", res.message, height=180)
            c1, c2, c3 = st.columns(3)
            c1.metric("Characters", f"{len(res.message):,}")
            c2.metric("Payload read", f"{res.payload_bytes:,} B")
            c3.metric("Time", f"{time.perf_counter() - t0:.2f} s")
            st.download_button("⬇️ Save message (.txt)", res.message.encode("utf-8"),
                               file_name="recovered_message.txt", mime="text/plain")
            with st.expander("Extracted ciphertext (before decryption)"):
                st.code(res.ciphertext_hex, language=None)
        except sc.StegoError as exc:
            log_activity("Extract", up.name if up else "—", "Failure")
            st.error(str(exc))


# ============================================================================= QUALITY
def page_quality() -> None:
    st.header("📊 Image Quality Analysis")
    st.write("Compare an original image with its stego-image using **MSE** and **PSNR** (Chapter 2, section 2.13).")

    out = st.session_state.last_embed
    src = st.radio("Images to compare",
                   ["Use the most recent embedding", "Upload two images"],
                   horizontal=True, index=0 if out else 1)
    orig = stego = None
    if src.startswith("Use"):
        if out:
            orig, stego = out["cover"], out["res"].stego
        else:
            st.info("No embedding in this session yet. Use **Encrypt & Hide** first, or upload two images.")
    else:
        c1, c2 = st.columns(2)
        u1 = c1.file_uploader("Original image", type=["png", "jpg", "jpeg", "bmp"], key="q1")
        u2 = c2.file_uploader("Stego-image", type=["png", "bmp"], key="q2")
        try:
            if u1 and u2:
                orig, stego = sc.load_image(u1.getvalue()), sc.load_image(u2.getvalue())
        except sc.StegoError as exc:
            st.error(str(exc))

    if orig is not None and stego is not None:
        try:
            m = sc.quality_metrics(orig, stego)
        except sc.StegoError as exc:
            st.error(str(exc))
            return
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("PSNR", "∞ dB" if m["psnr"] == float("inf") else f"{m['psnr']:.2f} dB")
        c2.metric("MSE", f"{m['mse']:.6f}")
        c3.metric("Bytes changed", f"{m['changed_pct']:.2f}%")
        c4.metric("Max pixel change", m["max_diff"])

        a, b, c = st.columns(3)
        a.image(orig, caption="Original", width="stretch")
        b.image(stego, caption="Stego-image", width="stretch")
        c.image(sc.difference_image(orig, stego), caption="Difference (amplified)", width="stretch")
        d, e = st.columns(2)
        d.image(sc.lsb_plane(orig), caption="LSB plane — original", width="stretch")
        e.image(sc.lsb_plane(stego), caption="LSB plane — stego-image", width="stretch")
        st.caption("The amplified difference and LSB planes make the otherwise invisible changes visible. "
                   "Key-dependent scattering spreads the changes randomly across the image instead of "
                   "leaving a predictable pattern.")


# ============================================================================= TESTS
def page_tests() -> None:
    st.header("🧪 System Tests")
    st.write("Automated test cases for functionality, security, message recovery and image quality "
             "(Chapter 4, sections 4.10 – 4.11). Each run uses a generated test image.")
    if st.button("▶️ Run all test cases", type="primary"):
        import selftest
        with st.spinner("Running tests… (key derivation is deliberately slow, ~30 s)"):
            rows = selftest.run_all()
        df = pd.DataFrame(rows)
        passed = int((df["Status"] == "PASS").sum())
        (st.success if passed == len(df) else st.error)(f"{passed} / {len(df)} test cases passed")
        st.dataframe(df, width="stretch", hide_index=True)
        st.download_button("⬇️ Download results (CSV)", df.to_csv(index=False).encode(),
                           file_name="test_results.csv", mime="text/csv")


# ============================================================================= ROUTER
{
    "🏠 Home": page_home,
    "🔏 Encrypt & Hide": page_hide,
    "🔓 Extract & Decrypt": page_extract,
    "📊 Image Quality": page_quality,
    "🧪 System Tests": page_tests,
    "ℹ️ About": render_about,
}[page]()
