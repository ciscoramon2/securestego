"""
about_page.py
=============
The "About" page: project details taken from Chapters 1 - 3 of the project report.
"""

from __future__ import annotations

import streamlit as st

TITLE = "Design and Implementation of a Secure Steganography System Using Cryptographic Encryption"
STUDENT = "Fadele Oluwatomiwa Samuel"
MATRIC = "23D/7HCS/548"
INSTITUTION = "Kwara State University"


# ----------------------------------------------------------------------------- diagrams
ARCHITECTURE_DOT = """
digraph G {
  rankdir=TB; bgcolor="transparent";
  node [shape=box, style="rounded,filled", fillcolor="#e8eefc", color="#4f6bed", fontname="Helvetica", fontsize=11];
  edge [color="#6b7280"];
  USER [label="USER", fillcolor="#fff3cd", color="#d4a017"];
  UI [label="USER INTERFACE\\n(Streamlit)"];
  ENC [label="ENCRYPTION MODULE\\n(AES-256-GCM)"];
  IMG [label="IMAGE INPUT\\n(Cover image)"];
  EMB [label="STEGANOGRAPHY MODULE\\n(LSB embedding)"];
  STG [label="STEGO-IMAGE", fillcolor="#d1f2d9", color="#2e9e57"];
  EXT [label="EXTRACTION MODULE\\n(LSB extraction)"];
  DEC [label="DECRYPTION MODULE"];
  MSG [label="ORIGINAL MESSAGE", fillcolor="#d1f2d9", color="#2e9e57"];
  USER -> UI; UI -> ENC; UI -> IMG; ENC -> EMB; IMG -> EMB; EMB -> STG;
  STG -> EXT [label="  transmission / storage", fontsize=9];
  EXT -> DEC; DEC -> MSG;
}
"""

FLOWCHART_DOT = """
digraph F {
  rankdir=TB; bgcolor="transparent";
  node [shape=box, style="rounded,filled", fillcolor="#e8eefc", color="#4f6bed", fontname="Helvetica", fontsize=11];
  edge [color="#6b7280"];
  S [label="START", shape=oval, fillcolor="#d1f2d9", color="#2e9e57"];
  O [label="Open application"];
  D [label="Select operation", shape=diamond, fillcolor="#fff3cd", color="#d4a017"];
  A1 [label="Enter secret message"]; A2 [label="Enter key"]; A3 [label="Encrypt message"];
  A4 [label="Select cover image"]; A5 [label="Embed ciphertext"]; A6 [label="Generate stego-image"];
  B1 [label="Select stego-image"]; B2 [label="Enter key"]; B3 [label="Extract hidden data"];
  B4 [label="Decrypt data"]; B5 [label="Display original message"];
  E [label="END", shape=oval, fillcolor="#f8d7da", color="#c0392b"];
  S -> O -> D;
  D -> A1 [label=" Embed"]; A1 -> A2 -> A3 -> A4 -> A5 -> A6 -> E;
  D -> B1 [label=" Extract"]; B1 -> B2 -> B3 -> B4 -> B5 -> E;
}
"""

USECASE_DOT = """
digraph U {
  rankdir=LR; bgcolor="transparent";
  node [fontname="Helvetica", fontsize=11];
  USER [shape=box, style="filled", fillcolor="#fff3cd", color="#d4a017", label="USER\\n(Actor)"];
  node [shape=ellipse, style="filled", fillcolor="#e8eefc", color="#4f6bed"];
  USER -> "Enter secret message"; USER -> "Select cover image"; USER -> "Enter encryption key";
  "Enter secret message" -> "Encrypt message" -> "Embed message" -> "Save stego-image";
  USER -> "Open stego-image" -> "Extract hidden data" -> "Decrypt message" -> "View original message";
}
"""

DFD_DOT = """
digraph D {
  rankdir=TB; bgcolor="transparent";
  node [shape=box, style="rounded,filled", fillcolor="#e8eefc", color="#4f6bed", fontname="Helvetica", fontsize=11];
  edge [color="#6b7280", fontname="Helvetica", fontsize=9];
  U [label="USER", shape=oval, fillcolor="#fff3cd", color="#d4a017"];
  E [label="Encryption Module"]; S [label="Steganography Module"];
  ST [label="STORAGE", shape=cylinder, fillcolor="#eeeeee", color="#888888"];
  X [label="Extraction Module"]; DE [label="Decryption Module"];
  O [label="Original Message", shape=oval, fillcolor="#d1f2d9", color="#2e9e57"];
  U -> E [label="Secret message + key"]; E -> S [label="Ciphertext"]; S -> ST [label="Stego-image"];
  ST -> X [label="Stego-image"]; X -> DE [label="Ciphertext"]; DE -> O;
}
"""


# ----------------------------------------------------------------------------- page
def render_about() -> None:
    st.markdown(
        f"""
        <div class="hero">
          <div class="hero-kicker">PROJECT ABOUT PAGE</div>
          <div class="hero-title">{TITLE}</div>
          <div class="hero-meta"><b>{STUDENT}</b> &nbsp;·&nbsp; Matric No: <b>{MATRIC}</b> &nbsp;·&nbsp; {INSTITUTION}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tabs = st.tabs([
        "📘 Overview", "1️⃣ Introduction", "2️⃣ Literature Review", "3️⃣ Analysis & Design",
        "🧩 Chapter → Code Map",
    ])

    # =========================================================================== OVERVIEW
    with tabs[0]:
        c1, c2 = st.columns([3, 2], gap="large")
        with c1:
            st.subheader("Abstract")
            st.write(
                "The increasing need for secure communication and protection of sensitive information "
                "has made information security an important area of research. Conventional methods of "
                "securing information, such as cryptographic encryption, protect the content of a message "
                "but may reveal the existence of confidential communication. Steganography, on the other "
                "hand, conceals the existence of information within a digital medium but may not adequately "
                "protect the hidden information if it is successfully extracted. This project presents the "
                "design and implementation of a Secure Steganography System Using Cryptographic Encryption, "
                "which combines encryption and steganography to provide an additional layer of security for "
                "confidential information."
            )
            st.write(
                "The proposed system encrypts a secret message using a cryptographic algorithm before "
                "embedding the encrypted message into a digital image using the Least Significant Bit (LSB) "
                "steganography technique. The resulting stego-image appears similar to the original image, "
                "thereby reducing suspicion and concealing the existence of the secret communication. At the "
                "receiving end, the system extracts the encrypted message from the stego-image and decrypts "
                "it using the appropriate cryptographic key to recover the original message."
            )
            st.write(
                "The system is designed and implemented using appropriate programming tools and tested to "
                "evaluate its functionality, security, message recovery, and image quality. The results "
                "demonstrate that combining cryptographic encryption with steganography provides stronger "
                "protection than using either technique independently."
            )
            st.caption("**Keywords:** Steganography · Cryptography · Encryption · Information Security · "
                       "Image Steganography · LSB · Data Protection")
        with c2:
            st.subheader("Project card")
            st.markdown(
                f"""
                | | |
                |---|---|
                | **Student** | {STUDENT} |
                | **Matric No.** | {MATRIC} |
                | **Institution** | {INSTITUTION} |
                | **Language** | Python |
                | **Interface** | Streamlit |
                | **Encryption** | AES-256-GCM |
                | **Key derivation** | PBKDF2-HMAC-SHA256 |
                | **Steganography** | LSB image steganography |
                | **Methodology** | Waterfall model |
                """
            )
            st.info("**Two security layers**\n\n🔐 Encryption protects the *content* of the message.\n\n"
                    "🖼️ Steganography conceals the *existence* of the message.")

        st.subheader("How the system works")
        a, b = st.columns(2, gap="large")
        with a:
            st.markdown("**Sending (embedding)**")
            st.code("Plain Message → Cryptographic Encryption → Encrypted Message\n"
                    "              → LSB Embedding → Stego Image", language=None)
        with b:
            st.markdown("**Receiving (recovery)**")
            st.code("Stego Image → LSB Extraction → Encrypted Message\n"
                    "            → Cryptographic Decryption → Original Message", language=None)

    # =========================================================================== CHAPTER 1
    with tabs[1]:
        st.header("Chapter One — Introduction")

        with st.expander("1.1 Background of the Study", expanded=True):
            st.write(
                "The rapid development of information and communication technology has significantly "
                "changed the way information is created, processed, stored, and transmitted. Individuals, "
                "businesses, educational institutions, financial organizations, and government agencies "
                "increasingly depend on digital communication for the exchange of important and confidential "
                "information. However, the widespread use of digital communication has also increased the risk "
                "of unauthorized access, interception, modification, and disclosure of sensitive information."
            )
            st.write(
                "**Cryptography** is the process of transforming readable information (plaintext) into an "
                "unreadable form called ciphertext using an encryption algorithm and a key. Although it provides "
                "strong protection for the content of information, the encrypted message may attract attention "
                "because its existence is obvious."
            )
            st.write(
                "**Steganography** focuses on hiding the existence of secret information. The word is derived "
                "from Greek words meaning *“covered writing.”* A common image steganography technique is the "
                "Least Significant Bit (LSB) method, where secret information is embedded into the least "
                "significant bits of selected pixels of an image."
            )
            st.write(
                "Combining the two provides an additional layer of security: the secret message is first "
                "encrypted and then embedded into an image. Even if an unauthorized person extracts the hidden "
                "data, it remains encrypted and cannot easily be understood without the appropriate key. "
                "The combination provides both **confidentiality** and **concealment**."
            )

        with st.expander("1.2 Statement of the Problem"):
            st.write(
                "Confidential information such as passwords, business information, personal records, financial "
                "information, and private communications may be exposed to unauthorized individuals during "
                "transmission or storage. Traditional cryptographic systems make the presence of confidential "
                "communication obvious, while conventional steganography may not protect a message once it is "
                "extracted. The major problems addressed are:"
            )
            st.markdown(
                "1. Unauthorized access to confidential digital information.\n"
                "2. Exposure of encrypted communication during transmission.\n"
                "3. The possibility of extracting hidden information from steganographic media.\n"
                "4. Insufficient protection when steganography is used without encryption.\n"
                "5. The need for a simple and user-friendly system for securely hiding confidential information.\n"
                "6. The need to maintain reasonable image quality after secret information has been embedded."
            )

        with st.expander("1.3 Aim and 1.4 Objectives of the Study"):
            st.success("**Aim:** To design and implement a secure steganography system that combines "
                       "cryptographic encryption with image steganography to protect confidential "
                       "information from unauthorized access.")
            st.markdown(
                "**Objectives** — to:\n"
                "1. Design a secure system for protecting confidential digital messages.\n"
                "2. Implement a cryptographic encryption mechanism for converting plaintext into ciphertext.\n"
                "3. Implement an image-based steganography technique for hiding encrypted information.\n"
                "4. Develop a mechanism for extracting hidden encrypted information from a stego-image.\n"
                "5. Implement a decryption mechanism for recovering the original message.\n"
                "6. Ensure that the embedded information causes minimal visible distortion to the cover image.\n"
                "7. Test the system to determine its functionality, reliability, and effectiveness.\n"
                "8. Provide a simple user interface that allows users to encrypt, embed, extract, and decrypt "
                "confidential messages."
            )

        with st.expander("1.5 Research Questions"):
            st.markdown(
                "1. How can cryptographic encryption be combined with image steganography to improve information security?\n"
                "2. How effectively can encrypted information be hidden inside a digital image?\n"
                "3. Can the hidden information be successfully extracted and decrypted by an authorized recipient?\n"
                "4. What effect does embedding secret information have on the quality of the cover image?\n"
                "5. How can the proposed system provide a simple and reliable method for protecting confidential information?"
            )

        with st.expander("1.6 Significance of the Study"):
            st.markdown(
                "- **Individuals** — protect private messages and other sensitive information before transmitting or storing them.\n"
                "- **Businesses** — an additional security layer for confidential business information, internal communication, and sensitive documents.\n"
                "- **Educational institutions** — transmitting confidential academic, administrative, or student-related information.\n"
                "- **Security and IT professionals** — a practical demonstration of combining cryptography and steganography.\n"
                "- **Researchers and students** — a reference for information security, cryptography, image processing, and steganography."
            )

        with st.expander("1.7 Scope of the Study"):
            st.write("The project focuses on a secure **image** steganography system that uses cryptographic "
                     "encryption to protect secret messages before they are hidden inside a digital image. "
                     "Major operations covered:")
            st.markdown(
                "- Input of a secret message\n- Encryption of the secret message\n- Selection of a suitable cover image\n"
                "- Embedding of the encrypted message into the image\n- Generation of a stego-image\n"
                "- Extraction of the hidden encrypted message\n- Decryption of the extracted information\n"
                "- Display of the original message to an authorized user"
            )
            st.caption("Audio and video steganography are outside the main scope of this project.")

        with st.expander("1.8 Limitations of the Study"):
            st.markdown(
                "- The amount of information that can be hidden depends on the size and properties of the cover image.\n"
                "- Excessive modification of pixels may affect the quality of the stego-image — a balance between capacity and quality is needed.\n"
                "- Security depends partly on the strength of the cryptographic algorithm and the protection of the key.\n"
                "- Basic LSB steganography may be vulnerable to statistical or steganalysis attacks; the project demonstrates the combination of encryption and concealment rather than claiming complete protection.\n"
                "- Compression, resizing, cropping, or format conversion of the stego-image may destroy the hidden data."
            )

        with st.expander("1.9 Definition of Terms"):
            terms = {
                "Cryptography": "The science and practice of protecting information by transforming it into a form that unauthorized individuals cannot easily understand.",
                "Encryption": "Converting readable information (plaintext) into an encoded form (ciphertext) using an algorithm and key.",
                "Decryption": "Converting encrypted information back into its original readable form using an appropriate key.",
                "Plaintext": "The original readable message before encryption.",
                "Ciphertext": "The encrypted and generally unreadable form of a plaintext message.",
                "Steganography": "A technique used to conceal the existence of secret information within another medium such as an image, audio, video, or document.",
                "Cover Image": "The original image used as the carrier for hiding secret information.",
                "Stego-Image": "The image produced after secret information has been embedded into a cover image.",
                "Least Significant Bit (LSB)": "The bit with the smallest numerical value; changing it causes only a very small change in a pixel value.",
                "Embedding": "The process of inserting secret information into a cover medium.",
                "Extraction": "The process of retrieving hidden information from a stego-medium.",
                "Cryptographic Key": "A value used by a cryptographic algorithm to encrypt or decrypt information.",
                "Information Security": "Protecting information from unauthorized access, disclosure, modification, destruction, or disruption.",
                "Confidentiality": "Ensuring that information is accessible only to authorized individuals.",
                "Authentication": "Verifying the identity of a user or system.",
                "Data Integrity": "Assurance that information has not been improperly altered or corrupted.",
                "Digital Image": "A representation of a visual picture in digital form, consisting of pixels containing numerical values.",
            }
            for k, v in terms.items():
                st.markdown(f"**{k}** — {v}")

        with st.expander("1.10 Organization of the Study"):
            st.markdown(
                "- **Chapter One** — Introduction: background, problem, aim and objectives, research questions, significance, scope, limitations, definitions, organization.\n"
                "- **Chapter Two** — Literature review: cryptography, encryption, steganography, image steganography, LSB techniques, existing approaches.\n"
                "- **Chapter Three** — System analysis and design: existing/proposed system, requirements, architecture, flowcharts, algorithms.\n"
                "- **Chapter Four** — Implementation and testing: environment, procedures, interfaces, test cases and results.\n"
                "- **Chapter Five** — Summary, conclusion, recommendations, contribution, further research."
            )

    # =========================================================================== CHAPTER 2
    with tabs[2]:
        st.header("Chapter Two — Literature Review")

        with st.expander("2.2 Concept of Information Security — the CIA Triad", expanded=True):
            c1, c2, c3 = st.columns(3)
            c1.markdown("##### 🔒 Confidentiality\nInformation is accessible only to authorized users. Encryption is a major technique for maintaining it.")
            c2.markdown("##### ✅ Integrity\nInformation remains accurate and has not been improperly modified in storage or transmission.")
            c3.markdown("##### 🟢 Availability\nAuthorized users can access information and services whenever required.")
            st.caption("The proposed system primarily focuses on confidentiality while also considering integrity and reliable recovery of hidden information.")

        with st.expander("2.3 – 2.5 Cryptography and Encryption"):
            st.write("Cryptography protects information through mathematical techniques that transform it into a form "
                     "unauthorized individuals cannot easily understand.")
            st.code("Plaintext  + Key → Encryption → Ciphertext\nCiphertext + Key → Decryption → Plaintext", language=None)
            st.markdown(
                "**Types of cryptography**\n"
                "- **Symmetric-key** — the same secret key encrypts and decrypts. Efficient for larger data; key exchange must be managed securely (e.g. AES).\n"
                "- **Asymmetric-key** — a public/private key pair (e.g. RSA, elliptic-curve). Used for key exchange, digital signatures, authentication.\n"
                "- **Hash functions** — one-way fixed-length digests for integrity verification and password protection; not reversible, so not encryption."
            )
            st.write("Instead of directly hiding readable text inside an image, the system first encrypts the "
                     "message and then hides the encrypted information.")

        with st.expander("2.6 – 2.8 Steganography: concept, history and types"):
            st.write("Steganography conceals secret information within another apparently ordinary medium so that "
                     "its existence is not obvious. A simple steganographic system consists of: *secret message, "
                     "cover medium, embedding algorithm, stego-medium,* and *extraction algorithm*.")
            st.code("Secret Message + Cover Image → Embedding Process → Stego-Image", language=None)
            st.write("The idea of hiding information dates back to ancient times (hidden messages in physical "
                     "objects, invisible writing). Digital communication made it possible to modify selected bits "
                     "of digital media without producing significant visible or audible changes.")
            st.markdown(
                "**Types by carrier:** Image · Audio · Video · Text (least capacity) · Network steganography."
            )

        with st.expander("2.9 – 2.10 Image Steganography and the LSB technique"):
            st.write("A successful image steganography system should balance three objectives:")
            c1, c2, c3 = st.columns(3)
            c1.metric("Security", "🛡️", help="Unauthorized users should have difficulty recovering the hidden information.")
            c2.metric("Capacity", "📦", help="Enough space for the intended secret message.")
            c3.metric("Imperceptibility", "👁️", help="Changes to the cover image should be difficult to notice.")
            st.write("These objectives conflict: hiding more information can mean larger changes to the carrier.")
            st.markdown("**LSB example** — an 8-bit pixel value where only the last bit changes:")
            st.code("Original pixel : 1 0 1 1 0 1 1 0   (182)\nSecret bit = 1 : 1 0 1 1 0 1 1 1   (183)   ← numerical difference of only 1", language=None)
            st.code("Cover Image → Convert Secret to Binary → Modify Selected LSBs → Stego-Image\n"
                    "Stego-Image → Read Selected LSBs → Reconstruct Binary Data → Recover Encrypted Message", language=None)
            st.caption("LSB is simple and keeps good visual quality, but basic LSB can be vulnerable to statistical "
                       "analysis when much data is embedded or the embedding pattern is predictable.")

        with st.expander("2.11 – 2.12 Combining Cryptography and Steganography"):
            st.markdown(
                "1. User enters a secret message.\n2. The message is encrypted using a cryptographic algorithm.\n"
                "3. The ciphertext is converted into a binary representation.\n4. The ciphertext is embedded into a cover image.\n"
                "5. The stego-image is transmitted or stored.\n6. The recipient selects the stego-image.\n"
                "7. The system extracts the hidden ciphertext.\n8. The ciphertext is decrypted with the appropriate key.\n"
                "9. The original message is displayed to the authorized user."
            )
            st.markdown(
                "**Advantages:** dual-layer security · concealment of communication · protection after extraction · flexible applications."
            )

        with st.expander("2.13 Image Quality — MSE and PSNR"):
            st.write("**Mean Squared Error (MSE)** — average squared difference between the original image *I* and stego-image *K*:")
            st.latex(r"MSE = \frac{1}{MN}\sum_{i=1}^{M}\sum_{j=1}^{N}\left[I(i,j)-K(i,j)\right]^2")
            st.write("**Peak Signal-to-Noise Ratio (PSNR)** — for an 8-bit image, MAX = 255:")
            st.latex(r"PSNR = 10\log_{10}\left(\frac{MAX_I^{2}}{MSE}\right)")
            st.caption("Smaller MSE and higher PSNR mean the stego-image is closer to the original. "
                       "This app reports both for every image it produces.")

        with st.expander("2.14 Security Requirements of the Proposed System"):
            st.markdown(
                "- **Confidentiality** — only a user with the correct key can recover the message.\n"
                "- **Integrity** — hidden data is preserved so the recovered message matches the original.\n"
                "- **Authentication** — where implemented, only authorized users can access protected functions.\n"
                "- **Data privacy** — minimize unnecessary exposure of confidential information.\n"
                "- **Usability** — usable without advanced knowledge of cryptography or steganography."
            )

        with st.expander("2.15 – 2.17 Existing Approaches, Comparison and Gaps"):
            st.table({
                "Feature": ["Hides message content", "Hides existence of communication", "Uses encryption",
                            "Requires a carrier medium", "Protection after data extraction", "Main purpose"],
                "Cryptography": ["Yes", "Generally no", "Yes", "No", "Depends on encryption", "Protect information content"],
                "Steganography": ["Not necessarily", "Yes", "Not necessarily", "Yes", "Often limited", "Conceal information existence"],
                "Combined Approach": ["Yes", "Yes", "Yes", "Yes", "Stronger when encryption is properly implemented", "Layered protection"],
            })
            st.markdown(
                "**Gaps addressed by this project**\n"
                "1. Steganography alone may not protect hidden information if the carrier is analysed and the data recovered.\n"
                "2. Cryptography alone makes the existence of encrypted information apparent.\n"
                "3. Some implementations sacrifice image quality to increase capacity.\n"
                "4. Some systems have complicated interfaces that are difficult for ordinary users."
            )

        with st.expander("2.18 Conceptual Model of the Proposed System"):
            st.code(
                "Plaintext\n   ↓  Cryptographic Encryption\nCiphertext\n   ↓  Binary Conversion\n"
                "   ↓  LSB Embedding\nStego-Image\n   ↓  LSB Extraction\nCiphertext\n   ↓  Cryptographic Decryption\nOriginal Plaintext",
                language=None)

    # =========================================================================== CHAPTER 3
    with tabs[3]:
        st.header("Chapter Three — System Analysis and Design")

        with st.expander("3.2 – 3.4 Existing system, problems and proposed system", expanded=True):
            c1, c2 = st.columns(2, gap="large")
            with c1:
                st.markdown("**Problems identified in the existing system**")
                st.markdown(
                    "1. Encrypted messages attract attention because their existence is obvious.\n"
                    "2. Information hidden with basic steganography may become readable after extraction.\n"
                    "3. Some approaches do not give sufficient protection against unauthorized access.\n"
                    "4. Excessive embedding may cause noticeable image distortion.\n"
                    "5. Some security systems are complicated for ordinary users.\n"
                    "6. Separate encryption and steganography tools force users to operate multiple applications."
                )
            with c2:
                st.markdown("**Proposed system**")
                st.write("A software application that securely conceals confidential messages inside digital images, "
                         "integrating encryption and steganography in one tool.")
                st.markdown(
                    "- **Encoding / Embedding:** sender enters message and key → system encrypts → converts to binary → embeds with LSB → outputs stego-image.\n"
                    "- **Decoding / Extraction:** recipient selects stego-image and key → system extracts hidden data → decrypts → original message (error if the key is invalid)."
                )

        with st.expander("3.5 Development Methodology — Waterfall Model"):
            st.write("The Waterfall model is adopted because the requirements can be identified and documented before implementation.")
            st.markdown(
                "1. **Requirements analysis** — encryption, embedding, extraction, decryption, image handling, user interaction.\n"
                "2. **System design** — architecture, algorithms, user interface, input/output structure, data flow.\n"
                "3. **Implementation** — design converted to executable software.\n"
                "4. **Testing** — verify encryption, embedding, extraction and decryption.\n"
                "5. **Deployment** — installed and used on a compatible computer.\n"
                "6. **Maintenance** — future improvements to security, usability, compatibility and performance."
            )

        with st.expander("3.6 System Requirements"):
            c1, c2 = st.columns(2, gap="large")
            with c1:
                st.markdown("**Hardware (minimum)**")
                st.table({"Component": ["Processor", "RAM", "Storage", "Display", "Keyboard", "Mouse", "Operating System"],
                          "Minimum requirement": ["Intel Core i3 or equivalent", "4 GB", "500 GB HDD or 128 GB SSD",
                                                  "Standard monitor", "Standard keyboard", "Standard mouse",
                                                  "Windows / Linux / macOS"]})
            with c2:
                st.markdown("**Software**")
                st.markdown(
                    "- Operating system: Windows 10/11 or compatible Linux\n"
                    "- Programming language: **Python**\n"
                    "- Code editor / IDE: Visual Studio Code or equivalent\n"
                    "- Image processing library: **Pillow (PIL)** (+ NumPy)\n"
                    "- Cryptographic library: Python **cryptography** library\n"
                    "- Interface: **Streamlit** (runs in the browser)\n"
                    "- Database: not required — images and encrypted data are stored as files"
                )

        with st.expander("3.7 – 3.8 Functional and Non-Functional Requirements"):
            c1, c2 = st.columns(2, gap="large")
            with c1:
                st.markdown("**Functional**")
                st.markdown(
                    "- User registration / login (where authentication is included)\n- Message input\n- Key input\n"
                    "- Encryption\n- Image selection\n- Message embedding\n- Stego-image generation\n"
                    "- Message extraction\n- Decryption\n- Message display"
                )
            with c2:
                st.markdown("**Non-functional**")
                st.markdown(
                    "- **Security** — protect secret messages from unauthorized access\n- **Usability** — simple, understandable interface\n"
                    "- **Reliability** — consistent encryption, embedding, extraction, decryption\n"
                    "- **Performance** — reasonable messages/images processed in acceptable time\n"
                    "- **Maintainability** — organised for future modification\n- **Portability** — runs on supported systems without major change"
                )

        with st.expander("3.9 System Architecture"):
            st.write("Major components: User Interface · Encryption Module · Steganography Module · "
                     "Extraction Module · Decryption Module · File Storage Module.")
            st.graphviz_chart(ARCHITECTURE_DOT, width="stretch")

        with st.expander("3.10 – 3.11 Input and Output Design"):
            c1, c2 = st.columns(2, gap="large")
            with c1:
                st.markdown(
                    "**Inputs:** secret message · cryptographic key/password · cover image · stego-image (extraction) · output location.\n\n"
                    "**Validation:** message entered · valid image selected · message within image capacity · key supplied · supported image format."
                )
            with c2:
                st.markdown(
                    "**Outputs:** encrypted message (internal) · generated stego-image · extracted encrypted data · decrypted original message · success / error notifications."
                )
                st.code("Message encrypted successfully.\nMessage embedded successfully.\n"
                        "Stego-image saved successfully.\nMessage extracted and decrypted successfully.", language=None)

        with st.expander("3.12 Use Case Description"):
            st.write("The major actor is the **User**, who can open the application, enter a secret message, select an "
                     "image, enter a key, encrypt and hide the message, save the stego-image, open a stego-image, "
                     "extract hidden data, decrypt it and view the original message.")
            st.graphviz_chart(USECASE_DOT, width="stretch")

        with st.expander("3.13 Data Flow Diagram"):
            st.graphviz_chart(DFD_DOT, width="stretch")

        with st.expander("3.14 System Flowchart"):
            st.graphviz_chart(FLOWCHART_DOT, width="stretch")

        with st.expander("3.15 – 3.16 Algorithms"):
            c1, c2 = st.columns(2, gap="large")
            with c1:
                st.markdown("**Algorithm 1: Secure Message Embedding**")
                st.code(
                    "Input : secret message, key, cover image\nOutput: stego-image\n"
                    " 1. Start\n 2. Accept secret message\n 3. Accept cryptographic key\n"
                    " 4. Validate message and key\n 5. Encrypt the message\n"
                    " 6. Convert ciphertext to binary\n 7. Load the cover image\n"
                    " 8. Check image capacity\n 9. If insufficient → error, stop\n"
                    "10. Modify selected LSBs to represent the data\n11. Generate the stego-image\n"
                    "12. Save the stego-image\n13. Display success message\n14. Stop", language=None)
            with c2:
                st.markdown("**Algorithm 2: Extraction and Decryption**")
                st.code(
                    "Input : stego-image, key\nOutput: original secret message\n"
                    " 1. Start\n 2. Load the stego-image\n 3. Accept the key\n"
                    " 4. Read the designated pixel bits\n 5. Extract the hidden binary data\n"
                    " 6. Reconstruct the encrypted message\n 7. Decrypt using the supplied key\n"
                    " 8. If key invalid → error message\n 9. If key correct → show original message\n10. Stop",
                    language=None)

        with st.expander("3.17 – 3.18 LSB Embedding Procedure and Message Capacity"):
            st.code("Pixel value       : 1 1 0 1 0 1 1 0\nSecret bit = 1    : 1 1 0 1 0 1 1 1   (LSB changed)\n"
                    "Secret bit = 0    : 1 1 0 1 0 1 1 0   (unchanged)", language=None)
            st.write("The implementation includes a mechanism for determining where the hidden message ends — an explicit "
                     "message length stored in a small header.")
            st.latex(r"Capacity = Width \times Height \times Channels \times Bits")
            st.caption("The usable capacity is lower than the raw capacity because space is reserved for metadata, "
                       "the message length and authentication information.")

        with st.expander("3.19 Security Design"):
            st.markdown(
                "- **Encryption before embedding** — plaintext is never embedded directly; an attacker who extracts the data obtains ciphertext only.\n"
                "- **Key protection** — the key is never stored with the stego-image; users should avoid sharing it over insecure channels.\n"
                "- **Input validation** — invalid files, unsupported formats and oversized messages are rejected.\n"
                "- **Error handling** — clear error messages that do not expose sensitive information."
            )

        with st.expander("3.20 Database / Data Storage Design"):
            st.write("The basic implementation needs no relational database because messages are encrypted and embedded "
                     "directly into image files. If user accounts and activity records are added, the following tables apply "
                     "(the app keeps a session activity log with these fields).")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**User table**")
                st.table({"Field": ["User_ID", "Username", "Password_Hash", "Date_Created"],
                          "Description": ["Unique identifier", "User's login name", "Secure representation of password", "Account creation date"]})
            with c2:
                st.markdown("**Activity table**")
                st.table({"Field": ["Activity_ID", "User_ID", "Operation", "File_Name", "Date_Time", "Status"],
                          "Description": ["Unique activity identifier", "Associated user", "Embed / Extract",
                                          "Processed image", "Date and time", "Success / Failure"]})

        with st.expander("3.21 User Interface Design"):
            st.markdown(
                "**Main menu:** Encrypt & Hide Message · Extract & Decrypt Message · Exit\n\n"
                "**Encrypt & Hide:** message field · key field · select image · encrypt · hide message · save stego-image · status display.\n\n"
                "**Extract & Decrypt:** select stego-image · key field · extract · decrypt · recovered-message display · save/copy message."
            )

        with st.expander("3.22 System Security and Ethical Considerations"):
            st.warning("The system is intended for legitimate information protection and privacy applications. Use it "
                       "only to protect information you are authorized to handle. It is not a guarantee of complete "
                       "security against all forms of steganalysis or cryptographic attack; overall security depends on "
                       "algorithm selection, secure key management, implementation quality, and the security of the device "
                       "and communication channel.")

    # =========================================================================== MAP
    with tabs[4]:
        st.subheader("How each chapter requirement is implemented in this application")
        st.table({
            "Chapter reference": [
                "3.7.2 Message input", "3.7.3 Key input", "3.7.4 Encryption", "3.7.5 Image selection",
                "3.7.6 / 3.7.7 Embedding + stego-image", "3.7.8 Extraction", "3.7.9 Decryption", "3.7.10 Message display",
                "3.10 Input validation", "3.17 End-of-message mechanism", "3.18 Capacity formula",
                "3.19.1 Encryption before embedding", "3.19.2 Key protection", "3.19.4 Error handling",
                "2.13 MSE / PSNR", "1.8 Predictable LSB pattern", "3.20 Activity table", "3.7.1 Login (optional)",
            ],
            "Implementation": [
                "Hide Message page — text box or .txt upload", "Password field (+ confirmation and strength meter)",
                "AES-256-GCM, key from PBKDF2-HMAC-SHA256 (stego_core.embed)", "Image uploader (PNG / JPG / BMP)",
                "LSB embedding (1–4 bits/channel) → downloadable lossless PNG", "stego_core.extract — reads header, then body bits",
                "AES-GCM decrypt; authentication tag verifies key and integrity", "Extract Message page with copy / download",
                "Format, size, capacity, empty message/key checks", "21-byte header stores payload length, bit-depth and salt",
                "stego_core.raw_capacity_bits / payload_capacity_bytes — live capacity bar", "Only ciphertext is ever written to the image (test TC14)",
                "Key never stored; salt (non-secret) only", "Typed exceptions → friendly messages",
                "Image Quality page + metrics after every embed", "Key-dependent pseudo-random scattering of carrier bytes",
                "Session activity log on the Home page", "Not included — marked “where authentication is included” in the report",
            ],
        })
