# streamlit_app.py — Ad Mockup Creator (Streamlit Cloud Compatible, no OpenCV)
import streamlit as st
from PIL import Image, ImageDraw
import numpy as np
from io import BytesIO
from zipfile import ZipFile
from pathlib import Path

st.set_page_config(page_title="Ad Mockup Creator", layout="centered")
st.title("📱 Ad Mockup Creator")
st.markdown("Upload one ad and use stored Jampp templates with marked slots.")

# Upload ad input
ad_file = st.file_uploader("Upload ad image (PNG or JPG)", type=["png", "jpg", "jpeg"])

# Define stored screenshot paths with expected ad sizes
stored_paths = {
    "Sudoku": ("sudoku_sample.jpg", (320, 50)),
    "Weather_Banner": ("weather_banner_sample.jpg", (300, 50)),
    "OneFootball": ("onefootball_sample.jpg", (300, 250)),
    "PLAYit": ("playit_sample.jpg", (300, 250))
}

screenshot_files = [Path(f"static/{p[0]}") for p in stored_paths.values() if Path(f"static/{p[0]}").exists()]
expected_size_map = {Path(f"static/{fname}").name: size for fname, size in stored_paths.values()}

# Function: detect red box area
def detect_red_rectangle(img_np):
    red_mask = (
        (img_np[:, :, 0] > 100) &
        (img_np[:, :, 1] < 100) &
        (img_np[:, :, 2] < 100)
    )
    ys, xs = np.where(red_mask)
    if ys.size == 0 or xs.size == 0:
        return None
    x1, y1 = np.min(xs), np.min(ys)
    x2, y2 = np.max(xs), np.max(ys)
    return x1, y1, x2 - x1, y2 - y1

if ad_file and screenshot_files and st.button("Generate Mockups"):
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

            ss_name = ss.name
            expected = expected_size_map.get(ss_name, None)
            if expected and (abs(ad_w - expected[0]) > 20 or abs(ad_h - expected[1]) > 20):
                st.info(f"⚠️ {ss_name} skipped — ad size {ad_w}x{ad_h} doesn't match expected {expected[0]}x{expected[1]}")
                continue

            resized_ad = ad_img.resize((w, h))
            base.paste(resized_ad, (x, y))

            previews.append((ss_name, base))

            # Save for zip
            buffer = BytesIO()
            base.save(buffer, format="JPEG")
            zipf.writestr(f"mockup_{ss_name}.jpg", buffer.getvalue())

    if previews:
        st.subheader("🔍 Previews")
        for name, img in previews:
            st.image(img, caption=name, use_container_width=True, width=300)

        st.subheader("📦 Download All Mockups")
        st.download_button("Download ZIP", data=zip_buffer.getvalue(), file_name="mockups.zip")
    else:
        st.warning("⚠️ No valid mockups generated.")
