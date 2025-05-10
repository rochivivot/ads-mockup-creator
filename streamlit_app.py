# streamlit_app.py — Ad Mockup Creator (Streamlit Cloud Compatible, no OpenCV)
import streamlit as st
from PIL import Image, ImageDraw
import numpy as np
from io import BytesIO
from zipfile import ZipFile

st.set_page_config(page_title="Ad Mockup Creator", layout="centered")
st.title("📱 Ad Mockup Creator")
st.markdown("Upload one ad and any number of screenshots with **red boxes** marking ad slots.")

# Upload inputs
ad_file = st.file_uploader("Upload ad image (PNG or JPG)", type=["png", "jpg", "jpeg"])
screenshot_files = st.file_uploader("Upload screenshot(s)", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

# Function: detect red box area
def detect_red_rectangle(img_np):
    red_mask = (
        (img_np[:, :, 0] > 100) &
        (img_np[:, :, 1] < 50) &
        (img_np[:, :, 2] < 50)
    )
    ys, xs = np.where(red_mask)
    if ys.size == 0 or xs.size == 0:
        return None
    x1, y1 = np.min(xs), np.min(ys)
    x2, y2 = np.max(xs), np.max(ys)
    return x1, y1, x2 - x1, y2 - y1

if ad_file and screenshot_files:
    ad_img = Image.open(ad_file).convert("RGB")
    ad_w, ad_h = ad_img.size

    previews = []
    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, "w") as zipf:
        for ss in screenshot_files:
            base = Image.open(ss).convert("RGB")
            base_np = np.array(base)

            rect = detect_red_rectangle(base_np)
            if not rect:
                st.warning(f"❌ No red slot found in {ss.name}, skipped.")
                continue

            x, y, w, h = rect
            if abs(ad_w - w) > 15 or abs(ad_h - h) > 15:
                st.info(f"⚠️ {ss.name} skipped — ad size mismatch with slot ({w}x{h})")
                continue

            resized_ad = ad_img.resize((w, h))
            base.paste(resized_ad, (x, y))

            previews.append((ss.name, base))

            # Save for zip
            buffer = BytesIO()
            base.save(buffer, format="JPEG")
            zipf.writestr(f"mockup_{ss.name}.jpg", buffer.getvalue())

    if previews:
        st.subheader("🔍 Previews")
        for name, img in previews:
            st.image(img, caption=name, use_column_width=True)

        st.subheader("📦 Download All Mockups")
        st.download_button("Download ZIP", data=zip_buffer.getvalue(), file_name="mockups.zip")
    else:
        st.warning("⚠️ No valid mockups generated.")
