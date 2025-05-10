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
    "Sudoku": ("sudoku_sample.jpg", (320, 50)),
    "Weather_Banner": ("weather_banner_sample.jpg", (300, 50)),
    "OneFootball": ("onefootball_sample.jpg", (300, 250)),
    "PLAYit": ("playit_sample.jpg", (300, 250))
}

screenshot_files = [Path(f"static/{p[0]}") for p in stored_paths.values() if Path(f"static/{p[0]}").exists()]
expected_size_map = {Path(f"static/{fname}").name: size for fname, size in stored_paths.values()}

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

if ad_files and screenshot_files and st.button("Generate Mockups"):
    previews = []
    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, "w") as zipf:
        for ad_file in ad_files:
            ad_img = Image.open(ad_file).convert("RGB")
            ad_w, ad_h = ad_img.size
            ad_base_name = Path(ad_file.name).stem

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
                    st.info(f"⚠️ {ss_name} skipped for {ad_base_name} — ad size {ad_w}x{ad_h} doesn't match expected {expected[0]}x{expected[1]}")
                    continue

                # Preserve aspect ratio
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

                label = f"{ad_base_name} on {ss_name}"
                previews.append((label, base))

                # Save to ZIP
                buffer = BytesIO()
                base.save(buffer, format="JPEG")
                zipf.writestr(f"mockup_{label}.jpg", buffer.getvalue())

    if previews:
        st.subheader("🔍 Previews")
        for name, img in previews:
            frame_margin = 40
            max_preview_width = 360
            scaled_height = int(img.height * max_preview_width / img.width)
            scaled_img = img.resize((max_preview_width, scaled_height))

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

        st.subheader("📦 Download All Mockups")
        st.download_button("Download ZIP", data=zip_buffer.getvalue(), file_name="mockups.zip")
    else:
        st.warning("⚠️ No valid mockups generated.")
