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
    "Sudoku": ("sudoku_sample.jpg", (320, 50), (60, 1132, 320, 50)),
    "Weather_Banner": ("weather_banner_sample.jpg", (320, 50), (60, 1122, 320, 50)),
    "OneFootball": ("onefootball_sample.jpg", (300, 250), (60, 570, 300, 250)),
    "PLAYit": ("playit_sample.jpg", (300, 250), (60, 620, 300, 250))
}

screenshot_files = [Path(f"static/{p[0]}") for p in stored_paths.values() if Path(f"static/{p[0]}").exists()]
expected_size_map = {Path(f"static/{fname}").name: (size, coords) for fname, size, coords in stored_paths.values()}

if ad_files and screenshot_files and st.button("Generate Mockups"):
    previews = []
    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, "w") as zipf:
        for ad_file in ad_files:
            ad_img = Image.open(ad_file).convert("RGBA")
            ad_w, ad_h = ad_img.size
            ad_base_name = Path(ad_file.name).stem

            for ss in screenshot_files:
                base = Image.open(ss).convert("RGBA")
                ss_name = ss.name
                expected_tuple = expected_size_map.get(ss_name, None)
                if not expected_tuple:
                    continue
                expected_size, rect = expected_tuple
                x, y, w, h = rect

                if abs(ad_w - expected_size[0]) > 20 or abs(ad_h - expected_size[1]) > 20:
                    st.info(f"⚠️ {ss_name} skipped for {ad_base_name} — ad size {ad_w}x{ad_h} doesn't match expected {expected_size[0]}x{expected_size[1]}")
                    continue

                resized_ad = ad_img.resize((w, h))
                base.alpha_composite(resized_ad, dest=(x, y))

                label = f"{ad_base_name} on {ss_name}"
                previews.append((label, base))

                buffer = BytesIO()
                base.convert("RGB").save(buffer, format="JPEG")
                zipf.writestr(f"mockup_{label}.jpg", buffer.getvalue())

    if previews:
        st.subheader("🔍 Previews")
        col1, col2 = st.columns(2)
        for i, (name, img) in enumerate(previews):
            preview_width = 150
            scaled_height = int(img.height * preview_width / img.width)
            scaled_img = img.resize((preview_width, scaled_height))

            frame = Image.new("RGB", (scaled_img.width + 40, scaled_height + 40), (20, 20, 20))
            frame.paste(scaled_img, (20, 20))
            (col1 if i % 2 == 0 else col2).image(frame, caption=name, use_container_width=False)

        st.subheader("📦 Download All Mockups")
        st.download_button("Download ZIP", data=zip_buffer.getvalue(), file_name="mockups.zip")
    else:
        st.warning("⚠️ No valid mockups generated.")
