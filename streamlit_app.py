import streamlit as st
from PIL import Image, ImageDraw
import numpy as np
from io import BytesIO
from zipfile import ZipFile
from pathlib import Path

st.set_page_config(page_title="Ad Mockup Creator", layout="centered")
st.title("Ad Mockup Creator")
st.markdown("Upload one or more ads. Screenshots will be matched automatically from Jampp templates.")

ad_files = st.file_uploader("Upload ad images (PNG or JPG)", type=["png", "jpg", "jpeg", "gif"], accept_multiple_files=True)

stored_paths = {
    "Sudoku": ("sudoku_sample.jpg", (320, 50), (60, 1226, 520, 80)),
    "Weather_Banner": ("weather_banner_sample.jpg", (320, 50), (50, 1289, 544, 85)),
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
            ad_img = Image.open(ad_file)
            ad_format = ad_img.format
            if ad_format == "GIF":
                st.warning(f"⚠️ {ad_file.name} is a GIF. We only support static JPG and PNG.")
                continue

            ad_size = detect_ad_size(ad_img)
            ad_base_name = Path(ad_file.name).stem

            for ss in screenshot_files:
                base = Image.open(ss).convert("RGBA")
                ss_name = ss.name
                expected_tuple = expected_size_map.get(ss_name, None)
                if not expected_tuple:
                    continue

                expected_ad_size, rect = expected_tuple
                expected_w, expected_h = expected_ad_size

                # Support retina 2x ads (e.g. 640x960)
                if ad_size == expected_ad_size:
                    pass
                elif ad_size == (expected_w * 2, expected_h * 2):
                    ad_img = ad_img.resize((expected_w, expected_h), Image.LANCZOS)
                else:
                    continue

                ad_img = ad_img.convert("RGBA")
                x, y, w, h = rect
                resized_ad = ad_img.resize((w, h), Image.LANCZOS)
                debug_base = base.copy()
                debug_base.alpha_composite(resized_ad, dest=(x, y))

                # Add small transparent X for interstitials
                if ss_name == "interstitial_sample.jpg":
                    draw = ImageDraw.Draw(debug_base)
                    x_icon_y_offset = 2
                    circle_left = x + w - 30
                    circle_top = y + x_icon_y_offset
                    circle_right = x + w - 10
                    circle_bottom = y + x_icon_y_offset + 20
                    x_icon_box = [(circle_left, circle_top), (circle_right, circle_bottom)]
                    draw.ellipse(x_icon_box
