import base64
import io

import requests
import streamlit as st
from PIL import Image
import pandas as pd

BACKEND_URL = "http://localhost:8001"


def image_to_base64(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return b64


st.set_page_config(page_title="PDF Table Extractor", layout="wide")

st.title("📄 PDF / Image Table Extractor")

uploaded_file = st.file_uploader("Upload a page image (PNG/JPG) with a table", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # Open image with PIL
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded image", use_column_width=True)

    # Upload image to backend
    with st.spinner("Uploading image to backend..."):
        img_b64 = image_to_base64(image)
        upload_payload = {
            "image_base64": img_b64,
            "job_name": "job1",
            "page": 1,
        }
        r = requests.post(f"{BACKEND_URL}/upload_image", json=upload_payload)
        if r.status_code != 200:
            st.error(f"Upload failed: {r.status_code} {r.text}")
        else:
            upload_info = r.json()
            image_id = upload_info["image_id"]
            img_w = upload_info["width"]
            img_h = upload_info["height"]

            st.success(f"Image uploaded. ID: {image_id}")
            st.write(f"Image size: {img_w} × {img_h}")

            st.subheader("Select table region")

            col1, col2 = st.columns(2)

            with col1:
                left = st.number_input("Left (px)", min_value=0, max_value=img_w, value=0)
                top = st.number_input("Top (px)", min_value=0, max_value=img_h, value=0)

            with col2:
                width = st.number_input("Width (px)", min_value=1, max_value=img_w, value=img_w)
                height = st.number_input("Height (px)", min_value=1, max_value=img_h, value=img_h)

            if st.button("Extract table from selected region"):
                payload = {
                    "image_id": image_id,
                    "left": int(left),
                    "top": int(top),
                    "width": int(width),
                    "height": int(height),
                    "table_csv_path": "extracted_table.csv",
                }

                with st.spinner("Extracting table..."):
                    resp = requests.post(f"{BACKEND_URL}/extract_table", json=payload)

                if resp.status_code != 200:
                    st.error(f"Table extraction failed: {resp.status_code} {resp.text}")
                else:
                    data = resp.json()

                    st.markdown("### 📜 OCR Text (raw)")
                    st.text(data["ocr_text"])

                    st.markdown("### 🧱 Raw table lines detected")
                    if data["raw_table_lines"]:
                        for ln in data["raw_table_lines"]:
                            st.write(ln)
                    else:
                        st.info("No raw table lines detected.")

                    st.markdown("### 🧹 Cleaned table")
                    cleaned_table = data.get("cleaned_table", [])
                    if cleaned_table:
                        df = pd.DataFrame(cleaned_table)
                        st.dataframe(df, use_container_width=True)

                        st.markdown("### 📈 Simple chart (first numeric column)")

                        # Try to pick first numeric column
                        numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns
                        if len(numeric_cols) > 0:
                            st.line_chart(df[numeric_cols[0]])
                        else:
                            st.info("No numeric columns to chart.")
                    else:
                        st.info("No cleaned table produced.")

                    if data.get("csv_path"):
                        st.success(f"CSV saved at: {data['csv_path']}")
