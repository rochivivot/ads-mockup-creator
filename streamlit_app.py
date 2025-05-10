# streamlit_app.py — Ad Mockup Creator Prototype
import streamlit as st
import cv2
import numpy as np
import tempfile
import os
from zipfile import ZipFile
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="Ad Mockup Creator", layout="centered")
st.title("📱 Ad Mockup Creator")
st.markdown("Upload one ad and any number of screenshots with **red boxes** marking ad slots.")

# Upload inputs
ad_file = st.file_uploader("Upload ad image (PNG or JPG)", type=["png", "jpg", "jpeg"])
screenshot_files = st.file_uploader("Upload screenshot(s)", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

if ad_file and screenshot_files:
    temp_ad = Image.open(ad_file).convert("RGB")
    ad_np = np.array(temp_ad)[..., ::-1]
    ad_h, ad_w = ad_np.shape[:2]

    previews = []
    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, "w") as zipf:
        for ss in screenshot_files:
            ss_img = Image.open(ss).convert("RGB")
            ss_np = np.array(ss_img)[..., ::-1]

            # Red detection
            lower_red = np.array([0, 0, 120])
            upper_red = np.array([100, 100, 255])
            mask = cv2.inRange(ss_np, lower_red, upper_red)
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if not contours:
                st.warning(f"❌ No red slot found in {ss.name}, skipped.")
                continue

            x, y, w, h = cv2.boundingRect(contours[0])
            if abs(ad_w - w) > 15 or abs(ad_h - h) > 15:
                st.info(f"⚠️ {ss.name} skipped — ad size mismatch with slot ({w}x{h})")
                continue

            resized = cv2.resize(ad_np, (w, h), interpolation=cv2.INTER_AREA)
            mock = ss_np.copy()
            mock[y:y+h, x:x+w] = resized

            # Show preview
            previews.append((ss.name, mock))

            # Save for zip
            isave = Image.fromarray(cv2.cvtColor(mock, cv2.COLOR_BGR2RGB))
            with BytesIO() as img_bytes:
                isave.save(img_bytes, format="JPEG")
                zipf.writestr(f"mockup_{ss.name}.jpg", img_bytes.getvalue())

    if previews:
        st.subheader("🔍 Previews")
        for name, img in previews:
            st.image(img[..., ::-1], caption=name, use_column_width=True)

        st.subheader("📦 Download All Mockups")
        st.download_button("Download ZIP", data=zip_buffer.getvalue(), file_name="mockups.zip")
    else:
        st.warning("⚠️ No valid mockups generated.")
