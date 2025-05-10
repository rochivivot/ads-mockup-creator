# Render inside a simulated iPhone frame (non-stretched ad look, no upload option)
import streamlit as st
from PIL import Image, ImageDraw
import numpy as np
from io import BytesIO
from zipfile import ZipFile
from pathlib import Path

# Define stored paths and expected ad sizes
stored_paths = {
    "Sudoku": ("sudoku_sample.jpg", (320, 50)),
    "Weather_Banner": ("weather_banner_sample.jpg", (300, 50)),
    "OneFootball": ("onefootball_sample.jpg", (300, 250)),
    "PLAYit": ("playit_sample.jpg", (300, 250))
}

# Ensure app uses only Jampp stored screenshots (no upload option)
screenshot_files = [Path(f"static/{p[0]}") for p in stored_paths.values() if Path(f"static/{p[0]}").exists()]
expected_size_map = {Path(f"static/{fname}").name: size for fname, size in stored_paths.values()}

# Paste ad with preserved aspect ratio
aspect_ratio = ad_img.width / ad_img.height
slot_ratio = w / h
if aspect_ratio > slot_ratio:
    new_w = w
    new_h = int(w / aspect_ratio)
else:
    new_h = h
    new_w = int(h * aspect_ratio)
resized_ad = ad_img.resize((new_w, new_h))
pad_x = x + (w - new_w) // 2
pad_y = y + (h - new_h) // 2
base.paste(resized_ad, (pad_x, pad_y))

# Render inside iPhone frame
frame_margin = 40
max_preview_width = 360
scaled_height = int(base.height * max_preview_width / base.width)
scaled_img = base.resize((max_preview_width, scaled_height))

frame_width = scaled_img.width + 2 * frame_margin
frame_height = scaled_img.height + 2 * frame_margin
iphone = Image.new("RGB", (frame_width, frame_height), color=(20, 20, 20))
corner = Image.new("L", (20, 20), 0)
ImageDraw.Draw(corner).pieslice((0, 0, 20, 20), 0, 360, fill=255)
mask = Image.new("L", iphone.size, 255)
mask.paste(corner, (0, 0))
mask.paste(corner.rotate(90), (0, frame_height - 20))
mask.paste(corner.rotate(180), (frame_width - 20, frame_height - 20))
mask.paste(corner.rotate(270), (frame_width - 20, 0))
iphone.paste(scaled_img, (frame_margin, frame_margin))

st.image(iphone, caption=name, use_container_width=True)
