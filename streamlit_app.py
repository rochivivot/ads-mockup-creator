import streamlit as st
from PIL import Image, ImageDraw
import numpy as np
from io import BytesIO
from zipfile import ZipFile
from pathlib import Path

st.set_page_config(page_title="Ad Mockup Creator", layout="centered")
st.title("📱 Ad Mockup Creator")
st.markdown("Upload one or more ads. Screenshots will be matched automatically from Jampp templates.")

ad_files = st.file_uploader("Upload ad images (PNG or JPG)", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

stored_paths = {
    "Sudoku": ("sudoku_sample.jpg", (320, 50), (60, 1242, 320, 50)),
    "Weather_Banner": ("weather_banner_sample.jpg", (320, 50), (60, 1242, 320, 50)),
    "OneFootball": ("onefootball_sample.jpg", (300, 250), (54, 715, 498, 416)),
    "PLAYit": ("playit_sample.jpg", (300, 250), (60, 600, 300, 250))
}

screenshot_files = [Path(f"static/{p[0]}") for p in stored_paths.values() if Path(f"static/{p[0]}").exists()]
expected_size_map = {Path(f"static/{fname}").name: (size, coords) for fname, size, coords in stored_paths.values()}

def detect_ad_size(img):
    return img.size

if ad_files and screenshot_files and st.button("Generate Mockups"):
    previews = []
    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, "w") as zipf:
        for ad_file in ad_files:
            ad_img = Image.open(ad_file).convert("RGBA")
            ad_size = detect_ad_size(ad_img)
            ad_base_name = Path(ad_file.name).stem

            for ss in screenshot_files:
                base = Image.open(ss).convert("RGBA")
                ss_name = ss.name
                expected_tuple = expected_size_map.get(ss_name, None)
                if not expected_tuple:
                    continue

                expected_ad_size, rect = expected_tuple
                if ad_size != expected_ad_size:
                    continue

                x, y, w, h = rect
                aspect_ratio = ad_img.width / ad_img.height
                target_ratio = w / h

                if aspect_ratio > target_ratio:
                    new_width = w
                    new_height = int(w / aspect_ratio)
                else:
                    new_height = h
                    new_width = int(h * aspect_ratio)

                resized_ad = ad_img.resize((new_width, new_height), Image.LANCZOS)
                offset_x = x + (w - new_width) // 2
                offset_y = y + (h - new_height) // 2

                debug_base = base.copy()
                debug_base.alpha_composite(resized_ad, dest=(offset_x, offset_y))

                label = f"{ad_base_name} on {ss_name}"
                previews.append((label, debug_base))

                buffer = BytesIO()
                debug_base.convert("RGB").save(buffer, format="JPEG")
                zipf.writestr(f"mockup_{label}.jpg", buffer.getvalue())

    if previews:
        st.subheader("🔍 Previews")
        col1, col2 = st.columns(2)
        for i, (name, img) in enumerate(previews):
            preview_width = 120
            scaled_height = int(img.height * preview_width / img.width)
            scaled_img = img.resize((preview_width, scaled_height))

            frame = Image.new("RGB", (scaled_img.width + 30, scaled_height + 30), (20, 20, 20))
            frame.paste(scaled_img, (15, 15))
            (col1 if i % 2 == 0 else col2).image(frame, caption=name, use_container_width=False)

        st.subheader("📦 Download All Mockups")
        st.download_button("Download ZIP", data=zip_buffer.getvalue(), file_name="mockups.zip")
    else:
        st.warning("⚠️ No valid mockups generated.")
