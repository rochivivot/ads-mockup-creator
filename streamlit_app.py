import streamlit as st
from PIL import Image, ImageDraw
import numpy as np
from io import BytesIO
from zipfile import ZipFile
from pathlib import Path

st.set_page_config(page_title="Ad Mockup Creator", layout="centered")
st.title("Ad Mockup Creator")
st.markdown("Upload one or more ads. Screenshots will be matched automatically from Jampp templates.")

ad_files = st.file_uploader("Upload ad images (PNG or JPG or GIF)", type=["png", "jpg", "jpeg", "gif"], accept_multiple_files=True)

stored_paths = {
    "Sudoku": ("sudoku_sample.jpg", (320, 50), (60, 1226, 520, 80)),
    "Weather_Banner": ("weather_banner_sample.jpg", (320, 50), (60, 1292, 528, 83)),
    "OneFootball": ("onefootball_sample.jpg", (300, 250), (60, 715, 498, 416)),
    "PLAYit": ("playit_sample.jpg", (300, 250), (35, 580, 450, 375)),
    "Weather_300x250": ("weather_300x250_sample.jpg", (300, 250), (60, 430, 416, 346)),
    "Interstitial": ("interstitial_sample.jpg", (320, 480), (0, 100, 313, 470))
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
                resized_ad = ad_img.resize((w, h), Image.LANCZOS)
                debug_base = base.copy()
                debug_base.alpha_composite(resized_ad, dest=(x, y))

                # Add X icon to Interstitial ad
                if ss_name == "interstitial_sample.jpg":
                    draw = ImageDraw.Draw(debug_base)
                    x_icon_y_offset = 6  # Slightly higher
                    x_icon_box = [(x + w - 36, y + x_icon_y_offset), (x + w - 4, y + x_icon_y_offset + 32)]
                    draw.ellipse(x_icon_box, fill=None, outline="black")
                    draw.line((x + w - 30, y + x_icon_y_offset + 8, x + w - 10, y + x_icon_y_offset + 28), fill="black", width=2)
                    draw.line((x + w - 30, y + x_icon_y_offset + 28, x + w - 10, y + x_icon_y_offset + 8), fill="black", width=2)

                label = f"{ad_base_name} on {ss_name}"
                previews.append((label, debug_base))

                buffer = BytesIO()
                debug_base.convert("RGB").save(buffer, format="JPEG")
                zipf.writestr(f"mockup_{label}.jpg", buffer.getvalue())

    if previews:
        st.subheader("Previews")
        col1, col2 = st.columns(2)
        for i, (name, img) in enumerate(previews):
            (col1 if i % 2 == 0 else col2).image(img, caption=name, use_container_width=True)

        st.subheader("Download All Mockups")
        st.download_button("Download ZIP", data=zip_buffer.getvalue(), file_name="mockups.zip")
    else:
        st.warning("⚠️ No valid mockups generated. \n\nOnly the following ad sizes are currently supported for mockups:\n"
    "- 320×50\n- 300×250\n- 320×480")
