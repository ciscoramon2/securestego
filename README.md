# SecureStego — Secure Steganography System Using Cryptographic Encryption

Fadele Oluwatomiwa Samuel · 23D/7HCS/548 · Kwara State University

## Setup and run (local)

Requires Python 3.10 or newer.

1. Open a terminal in the project folder (the one containing `app.py`).

2. Create a virtual environment:

       python -m venv venv

3. Activate it:

   - Windows (Command Prompt): `venv\Scripts\activate`
   - Windows (PowerShell): `venv\Scripts\Activate.ps1`
   - macOS / Linux: `source venv/bin/activate`

   Your prompt should now start with `(venv)`.

   If PowerShell blocks the script, run this once and try again:

       Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

4. Install the dependencies:

       pip install -r requirements.txt

5. Start the app:

       streamlit run app.py

   It opens at http://localhost:8501

6. Optional: run the 18 automated tests from the terminal:

       python selftest.py

7. When finished, leave the virtual environment with `deactivate`.

On later runs, skip steps 2 and 4: activate the environment and run `streamlit run app.py`.

## Deploy on Streamlit Community Cloud

1. Push the project to GitHub with `app.py` and `requirements.txt` at the repo root. Do not commit the `venv` folder; add `venv/` to a `.gitignore` file.
2. Go to https://share.streamlit.io, sign in with GitHub and click Create app.
3. Select the repo and branch, set the main file to `app.py`, and click Deploy.

The platform installs everything in `requirements.txt` itself.

## Files
| File | Purpose |
|---|---|
| app.py | Streamlit UI (Home, Encrypt & Hide, Extract & Decrypt, Image Quality, System Tests, About) |
| stego_core.py | AES-256-GCM + PBKDF2, keyed LSB embedding/extraction, MSE/PSNR |
| about_page.py | About page built from Chapters 1-3 |
| selftest.py | 18 automated test cases (`python selftest.py`) |

## Notes
* Share the stego-image as the PNG produced by the app. JPEG conversion or social-media re-compression destroys the hidden bits.
* The key is never stored; losing it means the message cannot be recovered.
