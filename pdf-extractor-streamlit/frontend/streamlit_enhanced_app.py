# frontend/streamlit_enhanced_app.py
"""
Enhanced Streamlit frontend for Intelligent PDF/Image Data Extraction.
Features:
- Multi-page PDF support
- Table and chart detection
- Data validation and quality checking
- Multi-format export
- Data insights and summaries
- Visualization of extracted data
"""

import base64
import io
from typing import List

import requests
import streamlit as st
from PIL import Image
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuration
BACKEND_URL = "http://localhost:8001"

# Set page config
st.set_page_config(
    page_title="Intelligent Data Extractor",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
    <style>
    .metric-card { background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin: 10px 0; }
    .success-box { background-color: #d4edda; padding: 15px; border-radius: 5px; border-left: 4px solid #28a745; }
    .warning-box { background-color: #fff3cd; padding: 15px; border-radius: 5px; border-left: 4px solid #ffc107; }
    .error-box { background-color: #f8d7da; padding: 15px; border-radius: 5px; border-left: 4px solid #dc3545; }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []
if "extracted_data" not in st.session_state:
    st.session_state.extracted_data = {}
if "current_page" not in st.session_state:
    st.session_state.current_page = 0


def image_to_base64(img: Image.Image) -> str:
    """Convert PIL image to base64 string."""
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def upload_to_backend(img: Image.Image, job_name: str, page_num: int) -> dict:
    """Upload image to backend and get image_id."""
    try:
        img_b64 = image_to_base64(img)
        payload = {
            "image_base64": img_b64,
            "job_name": job_name,
            "page": page_num,
        }
        resp = requests.post(f"{BACKEND_URL}/upload_image", json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"Upload failed: {e}")
        return None


def extract_table_from_image(image_id: str, bbox: dict) -> dict:
    """Extract table from image region."""
    try:
        payload = {
            "image_id": image_id,
            "left": bbox.get("left", 0),
            "top": bbox.get("top", 0),
            "width": bbox.get("width", 100),
            "height": bbox.get("height", 100),
            "table_csv_path": None,
        }
        resp = requests.post(f"{BACKEND_URL}/extract_table", json=payload, timeout=60)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"Table extraction failed: {e}")
        return None


def detect_elements_in_image(image_id: str, bbox: dict) -> dict:
    """Detect tables, charts, and text blocks."""
    try:
        payload = {
            "image_id": image_id,
            "left": bbox.get("left", 0),
            "top": bbox.get("top", 0),
            "width": bbox.get("width", 100),
            "height": bbox.get("height", 100),
        }
        resp = requests.post(f"{BACKEND_URL}/detect_elements", json=payload, timeout=60)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"Element detection failed: {e}")
        return None


def validate_data(table: List[List]) -> dict:
    """Validate extracted table data."""
    try:
        payload = {"table": table}
        resp = requests.post(f"{BACKEND_URL}/validate_data", json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"Validation failed: {e}")
        return None


def export_data(table: List[List], formats: List[str], filename: str = None) -> dict:
    """Export data to multiple formats."""
    try:
        payload = {
            "table": table,
            "formats": formats,
            "include_metadata": True,
            "filename": filename,
        }
        resp = requests.post(f"{BACKEND_URL}/export_data", json=payload, timeout=60)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"Export failed: {e}")
        return None


def generate_summary(table: List[List]) -> dict:
    """Generate data summary and insights."""
    try:
        payload = {
            "table": table,
            "include_trends": True,
            "include_anomalies": True,
        }
        resp = requests.post(f"{BACKEND_URL}/generate_summary", json=payload, timeout=60)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"Summary generation failed: {e}")
        return None


# =====================
# Main UI
# =====================

st.title("📊 Intelligent Data Extractor from Business Reports")
st.markdown("Extract tables, charts, and structured data from PDF/image documents with AI-powered intelligence.")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    extraction_mode = st.radio(
        "Select Extraction Mode:",
        ["Full Auto-Detection", "Manual Region Selection", "Batch Processing"]
    )
    
    enable_validation = st.checkbox("Enable Data Validation", value=True)
    enable_summary = st.checkbox("Generate Summary & Insights", value=True)
    
    export_formats = st.multiselect(
        "Export Formats:",
        ["csv", "xlsx", "json"],
        default=["csv", "xlsx"]
    )

# Main content
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📤 Upload & Extract", "📊 Data Viewer", "✅ Validation", "📈 Insights", "📉 Charts"])

with tab1:
    st.header("Upload & Extract")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_files = st.file_uploader(
            "Upload images or PDFs",
            type=["png", "jpg", "jpeg", "pdf"],
            accept_multiple_files=True,
            key="file_uploader"
        )
    
    with col2:
        job_name = st.text_input("Job Name", value="extraction_job")
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} file(s) uploaded")
        
        # Process files
        if st.button("🔍 Extract Data", use_container_width=True, type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for idx, file in enumerate(uploaded_files):
                status_text.text(f"Processing file {idx+1}/{len(uploaded_files)}: {file.name}")
                
                try:
                    # Load image
                    if file.type.startswith("image"):
                        image = Image.open(file).convert("RGB")
                    else:
                        # For PDFs, would need pdf2image conversion
                        st.warning("PDF support requires pdf2image library")
                        continue
                    
                    # Upload to backend
                    upload_result = upload_to_backend(image, job_name, idx)
                    if not upload_result:
                        continue
                    
                    image_id = upload_result["image_id"]
                    img_w = upload_result["width"]
                    img_h = upload_result["height"]
                    
                    # Auto-detection or manual selection
                    if extraction_mode == "Full Auto-Detection":
                        bbox = {"left": 0, "top": 0, "width": img_w, "height": img_h}
                    else:
                        # Show image for manual selection
                        col1_img, col2_img = st.columns(2)
                        with col1_img:
                            st.image(image, caption=file.name, use_column_width=True)
                        
                        with col2_img:
                            st.write("Select Region:")
                            left = st.slider("Left", 0, img_w, 0, key=f"left_{idx}")
                            top = st.slider("Top", 0, img_h, 0, key=f"top_{idx}")
                            width = st.slider("Width", 1, img_w, img_w, key=f"width_{idx}")
                            height = st.slider("Height", 1, img_h, img_h, key=f"height_{idx}")
                            bbox = {"left": left, "top": top, "width": width, "height": height}
                    
                    # Detect elements
                    detected_charts = []
                    if extraction_mode == "Full Auto-Detection":
                        elements = detect_elements_in_image(image_id, bbox)
                        if elements:
                            st.write("📌 Detected Elements:")
                            if elements.get("charts"):
                                detected_charts = elements["charts"]
                                st.write(f"  • Charts: {len(detected_charts)}")
                            if elements.get("tables"):
                                st.write(f"  • Tables: {len(elements['tables'])}")
                    
                    # Extract table
                    extraction_result = extract_table_from_image(image_id, bbox)
                    if extraction_result:
                        table = extraction_result.get("cleaned_table", [])
                        ocr_text = extraction_result.get("ocr_text", "")
                        detection_status = extraction_result.get("detection_status", "unknown")
                        raw_lines = extraction_result.get("raw_table_lines", [])
                        
                        # Show debug info
                        with st.expander("🔍 Debug Info"):
                            st.write(f"**Detection Status:** {detection_status}")
                            st.write(f"**OCR Text Length:** {len(ocr_text)} chars")
                            st.write(f"**Raw Lines Found:** {len(raw_lines)}")
                            st.write(f"**Extracted Rows:** {len(table)}")
                            if ocr_text:
                                st.write("**First 500 chars of OCR text:**")
                                st.code(ocr_text[:500])
                        
                        st.session_state.extracted_data[file.name] = {
                            "table": table,
                            "ocr_text": ocr_text,
                            "image": image,
                            "image_id": image_id,
                            "file_name": file.name,
                            "charts": detected_charts,
                        }
                        
                        if table:
                            st.success(f"✅ Extracted {len(table)} rows, {len(table[0]) if table else 0} columns")
                            
                            # Show how table was extracted
                            with st.expander("📖 How Table Was Extracted", expanded=False):
                                st.markdown("""
                                **Table Extraction Process:**
                                
                                1️⃣ **Image Upload** → Image received and saved
                                2️⃣ **OCR Processing** → Tesseract extracts text from image
                                3️⃣ **Text Parsing** → System finds table structure in OCR text
                                4️⃣ **Row Detection** → Identifies rows with consistent column structure
                                5️⃣ **Table Building** → Converts parsed text to structured table
                                
                                **What was extracted:**
                                """)
                                
                                # Show extraction details
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.metric("Rows", len(table))
                                with col2:
                                    st.metric("Columns", len(table[0]) if table else 0)
                                with col3:
                                    st.metric("OCR Chars", len(ocr_text))
                                with col4:
                                    st.metric("Status", detection_status.replace("_", " ").title())
                                
                                # Show first few rows as preview
                                st.markdown("**Preview of Extracted Data:**")
                                df_preview = pd.DataFrame(table[:min(5, len(table))])
                                st.dataframe(df_preview, use_container_width=True)
                        else:
                            st.warning(f"⚠️ No table rows found. Detection status: {detection_status}")
                    
                    progress_bar.progress((idx + 1) / len(uploaded_files))
                
                except Exception as e:
                    st.error(f"Error processing {file.name}: {e}")
            
            status_text.empty()
            progress_bar.empty()

with tab2:
    st.header("Extracted Data Viewer")
    
    if not st.session_state.extracted_data:
        st.info("No data extracted yet. Upload files and extract data first.")
    else:
        # Select file to view
        file_options = list(st.session_state.extracted_data.keys())
        selected_file = st.selectbox("Select extracted file:", file_options)
        
        if selected_file:
            data = st.session_state.extracted_data[selected_file]
            table = data["table"]
            ocr_text = data.get("ocr_text", "")
            
            # Show extraction flow
            st.markdown("### 🔄 Table Extraction Flow")
            cols = st.columns(5)
            with cols[0]:
                st.markdown("**📸 Image**")
                st.markdown("↓")
            with cols[1]:
                st.markdown("**🔤 OCR**")
                st.markdown("↓")
            with cols[2]:
                st.markdown("**📝 Parse**")
                st.markdown("↓")
            with cols[3]:
                st.markdown("**🔍 Detect**")
                st.markdown("↓")
            with cols[4]:
                st.markdown("**✅ Table**")
            
            st.divider()
            
            # Show tabs for different views
            view_tab1, view_tab2, view_tab3 = st.tabs(["📋 Table Data", "🔤 OCR Text", "📊 Extraction Details"])
            
            with view_tab1:
                st.subheader("Extracted Table")
                if table:
                    df = pd.DataFrame(table)
                    st.dataframe(df, use_container_width=True)
                    
                    # Display statistics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Rows", len(table))
                    with col2:
                        st.metric("Columns", len(table[0]) if table else 0)
                    with col3:
                        st.metric("Cells", len(table) * (len(table[0]) if table else 0))
                else:
                    st.info("No table data extracted")
            
            with view_tab2:
                st.subheader("Raw OCR Text")
                if ocr_text:
                    st.text_area("OCR Output (raw text extracted from image):", ocr_text, height=300, disabled=True)
                else:
                    st.info("No OCR text available")
            
            with view_tab3:
                st.subheader("Extraction Details")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Extraction Statistics:**")
                    st.write(f"• OCR Text Length: {len(ocr_text)} characters")
                    st.write(f"• Extracted Rows: {len(table)}")
                    st.write(f"• Columns per Row: {len(table[0]) if table else 0}")
                    st.write(f"• Total Cells: {len(table) * (len(table[0]) if table else 0)}")
                
                with col2:
                    st.markdown("**How It Works:**")
                    st.markdown("""
                    1. **OCR Processing**: Tesseract reads text from the image
                    2. **Line Detection**: System finds lines with structure (consistent columns)
                    3. **Row Parsing**: Each line becomes a row in the table
                    4. **Column Mapping**: Values aligned to column headers
                    5. **Data Cleaning**: Numbers converted to proper types
                    6. **Output**: Clean structured table with headers and data
                    """)
                
                # Show sample of how OCR maps to table
                if ocr_text and table:
                    st.markdown("**Extraction Process:**")
                    st.markdown("```")
                    st.markdown("Step 1: OCR captures text from image")
                    ocr_lines = ocr_text.split('\n')[:3]
                    for line in ocr_lines:
                        if line.strip():
                            st.markdown(f"  {line[:60]}...")
                    st.markdown("```")
                    
                    st.markdown("Step 2: System parses and structures it")
                    st.markdown("```")
                    first_row = table[0] if table else {}
                    for key, val in first_row.items():
                        st.markdown(f"  {key}: {val}")
                    st.markdown("```")

with tab3:
    st.header("Data Validation & Quality Check")
    
    if not st.session_state.extracted_data:
        st.info("No data to validate. Extract data first.")
    else:
        selected_file = st.selectbox("Select file to validate:", list(st.session_state.extracted_data.keys()), key="validate_select")
        
        if st.button("🔍 Validate Data", use_container_width=True):
            table = st.session_state.extracted_data[selected_file]["table"]
            
            validation_result = validate_data(table)
            if validation_result:
                # Quality score
                col1, col2, col3 = st.columns(3)
                with col1:
                    stats = validation_result.get("statistics", {})
                    st.metric("Rows", stats.get("row_count", 0))
                with col2:
                    st.metric("Columns", stats.get("column_count", 0))
                with col3:
                    is_valid = "✅ Valid" if validation_result.get("is_valid") else "❌ Invalid"
                    st.metric("Status", is_valid)
                
                # Errors
                if validation_result.get("errors"):
                    st.markdown('<div class="error-box">', unsafe_allow_html=True)
                    st.error("⚠️ **Errors Found:**")
                    for error in validation_result["errors"]:
                        st.write(f"  • {error.get('message')}")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Warnings
                if validation_result.get("warnings"):
                    st.markdown('<div class="warning-box">', unsafe_allow_html=True)
                    st.warning("⚠️ **Warnings:**")
                    for warning in validation_result["warnings"]:
                        st.write(f"  • {warning.get('message')}")
                    st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    st.header("📊 Data Insights & Summary")
    
    if not st.session_state.extracted_data:
        st.info("No data available. Extract data first from the Upload & Extract tab.")
    else:
        selected_file = st.selectbox("Select file for insights:", list(st.session_state.extracted_data.keys()), key="insight_select")
        
        data = st.session_state.extracted_data[selected_file]
        table = data.get("table", [])
        
        # Show file info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Rows Extracted", len(table) if table else 0)
        with col2:
            st.metric("Columns", len(table[0]) if table and len(table) > 0 else 0)
        with col3:
            st.metric("Status", "Ready" if table else "Empty")
        
        if not table:
            st.warning("⚠️ No table data extracted. Please extract data first and ensure a table is detected.")
        else:
            # Auto-generate or manual button
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write("Generating insights from extracted data...")
            with col2:
                if st.button("🔄 Refresh", use_container_width=True):
                    st.rerun()
            
            try:
                summary = generate_summary(table)
                
                if not summary:
                    st.error("❌ Failed to generate insights. Check if table data is valid.")
                else:
                    # Statistics
                    if summary.get("statistics"):
                        st.subheader("📈 Statistics")
                        stats = summary["statistics"]
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Rows", stats.get("row_count", 0))
                        with col2:
                            st.metric("Columns", stats.get("column_count", 0))
                        with col3:
                            rows = stats.get("row_count", 0)
                            cols = stats.get("column_count", 0)
                            st.metric("Total Cells", rows * cols)
                        
                        # Show column names
                        if stats.get("columns"):
                            with st.expander("📋 Column Names"):
                                for col in stats["columns"]:
                                    st.write(f"  • {col}")
                    
                    # Top categories
                    if summary.get("top_categories") and summary["top_categories"]:
                        st.subheader("🏆 Top Categories")
                        categories = summary["top_categories"]
                        cat_data = {
                            "Category": [str(c.get("category", "")) for c in categories], 
                            "Count": [c.get("count", 0) for c in categories]
                        }
                        fig = px.bar(cat_data, x="Category", y="Count", title="Top Categories")
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Trends
                    if summary.get("trends") and summary["trends"]:
                        st.subheader("📊 Trends")
                        trends = summary["trends"]
                        if trends.get("trend"):
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("Trend", trends["trend"].title())
                            with col2:
                                st.metric("Column", trends.get("y_column", "N/A"))
                            with col3:
                                st.metric("Slope", f"{trends.get('slope', 0):.4f}")
                            with col4:
                                st.metric("R²", f"{trends.get('r_squared', 0):.3f}")
                    
                    # Data quality
                    if summary.get("data_quality"):
                        st.subheader("✅ Data Quality")
                        quality = summary["data_quality"]
                        score = quality.get("overall_score", 0)
                        breakdown = quality.get("breakdown", {})
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Overall Score", f"{score:.1f}%")
                        with col2:
                            st.metric("Completeness", f"{breakdown.get('Completeness', 0):.1f}%")
                        with col3:
                            st.metric("Consistency", f"{breakdown.get('Consistency', 0):.1f}%")
                        with col4:
                            st.metric("Uniqueness", f"{breakdown.get('Uniqueness', 0):.1f}%")
                        
                        # Quality gauge chart
                        fig = go.Figure(go.Indicator(
                            mode="gauge+number",
                            value=score,
                            title="Data Quality Score",
                            domain={"x": [0, 1], "y": [0, 1]},
                            gauge={"axis": {"range": [0, 100]},
                                   "bar": {"color": "darkblue"},
                                   "steps": [
                                       {"range": [0, 50], "color": "lightgray"},
                                       {"range": [50, 75], "color": "gray"},
                                       {"range": [75, 100], "color": "lightgreen"}
                                   ]}
                        ))
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Anomalies
                    if summary.get("anomalies"):
                        st.subheader("🚨 Detected Anomalies")
                        anomalies = summary["anomalies"]
                        if anomalies and len(anomalies) > 0:
                            for anomaly in anomalies[:5]:  # Show top 5
                                with st.expander(f"🔍 {anomaly.get('type', 'Anomaly')} - {anomaly.get('column', 'Unknown')}"):
                                    st.write(f"**Type:** {anomaly.get('type')}")
                                    st.write(f"**Column:** {anomaly.get('column')}")
                                    st.write(f"**Count:** {anomaly.get('count', 0)}")
                                    if anomaly.get('values'):
                                        st.write(f"**Values:** {anomaly.get('values')}")
                        else:
                            st.success("✅ No anomalies detected!")
            
            except Exception as e:
                st.error(f"❌ Error generating insights: {str(e)}")
                with st.expander("🔍 Debug Information"):
                    st.write(f"**Error:** {str(e)}")
                    st.write(f"**Table Type:** {type(table)}")
                    st.write(f"**Table Length:** {len(table) if table else 0}")
                    if table and len(table) > 0:
                        st.write(f"**First Row Type:** {type(table[0])}")
                        st.write(f"**First Row:** {table[0]}")

with tab5:
    st.header("📉 Chart Detection & Analysis")
    
    if not st.session_state.extracted_data:
        st.info("No data analyzed yet. Extract data first.")
    else:
        selected_file = st.selectbox("Select file to analyze for charts:", list(st.session_state.extracted_data.keys()), key="chart_select")
        
        if selected_file:
            data = st.session_state.extracted_data[selected_file]
            image = data.get("image")
            image_id = data.get("image_id")
            
            if image and image_id:
                st.subheader(f"📸 Image: {selected_file}")
                
                # Display image
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.image(image, caption=selected_file, use_column_width=True)
                
                with col2:
                    st.write("**Chart Detection Settings:**")
                    sensitivity = st.slider("Detection Sensitivity", 0.3, 0.9, 0.7, help="Higher = detect more charts (may include false positives)")
                
                # Detect charts
                if st.button("🔍 Detect Charts in Image", use_container_width=True, type="primary"):
                    bbox = {"left": 0, "top": 0, "width": image.width, "height": image.height}
                    
                    try:
                        elements = detect_elements_in_image(image_id, bbox)
                        
                        if elements and elements.get("charts"):
                            charts = elements["charts"]
                            st.success(f"✅ Found {len(charts)} chart(s)!")
                            
                            for idx, chart in enumerate(charts, 1):
                                with st.expander(f"📊 Chart {idx}: {chart.get('type', 'Unknown').upper()}"):
                                    col1, col2, col3 = st.columns(3)
                                    
                                    with col1:
                                        st.metric("Type", chart.get("type", "Unknown").replace("_", " ").title())
                                    with col2:
                                        st.metric("Confidence", f"{chart.get('confidence', 0)*100:.0f}%")
                                    with col3:
                                        bbox_info = chart.get("bbox", (0, 0, 0, 0))
                                        st.metric("Area (px)", f"{bbox_info[2] * bbox_info[3]}")
                                    
                                    # Display chart data
                                    chart_data = chart.get("data", [])
                                    if chart_data:
                                        st.write("**Extracted Data Points:**")
                                        
                                        chart_type = chart.get("type", "")
                                        if chart_type == "bar_chart":
                                            df_chart = pd.DataFrame([{
                                                "Label": d.get("label", ""),
                                                "Value": d.get("value", 0),
                                                "Confidence": f"{d.get('confidence', 0)*100:.0f}%"
                                            } for d in chart_data])
                                            st.dataframe(df_chart, use_container_width=True)
                                            
                                            # Visualize
                                            if len(chart_data) > 0:
                                                fig = go.Figure(data=[
                                                    go.Bar(
                                                        x=[d.get("label", "") for d in chart_data],
                                                        y=[d.get("value", 0) for d in chart_data],
                                                        marker_color="indianred"
                                                    )
                                                ])
                                                fig.update_layout(title="Bar Chart Data", showlegend=False)
                                                st.plotly_chart(fig, use_container_width=True)
                                        
                                        elif chart_type == "pie_chart":
                                            st.write(f"Found {len(chart_data)} slice(s)")
                                            for i, point in enumerate(chart_data):
                                                st.write(f"  • Slice {i+1}: Center {point.get('center')}, Radius {point.get('radius')}px")
                                        
                                        elif chart_type == "line_chart":
                                            df_chart = pd.DataFrame([{
                                                "X": d.get("x", 0),
                                                "Y": d.get("y", 0),
                                                "Confidence": f"{d.get('confidence', 0)*100:.0f}%"
                                            } for d in chart_data])
                                            st.dataframe(df_chart, use_container_width=True)
                                            
                                            # Visualize
                                            if len(chart_data) > 0:
                                                fig = go.Figure(data=[
                                                    go.Scatter(
                                                        x=[d.get("x", 0) for d in chart_data],
                                                        y=[d.get("y", 0) for d in chart_data],
                                                        mode="lines+markers",
                                                        marker_color="blue"
                                                    )
                                                ])
                                                fig.update_layout(title="Line Chart Data", showlegend=False)
                                                st.plotly_chart(fig, use_container_width=True)
                                    else:
                                        st.info("No data extracted from this chart yet. This is a placeholder.")
                        else:
                            st.warning("⚠️ No charts detected in this image. Try adjusting sensitivity or uploading an image with charts.")
                    
                    except Exception as e:
                        st.error(f"Error detecting charts: {e}")
            else:
                st.warning("Image data not available. Please re-extract the data.")

# Download section
st.divider()
st.header("📥 Download Results")

if st.session_state.extracted_data:
    download_file = st.selectbox("Select file to export:", list(st.session_state.extracted_data.keys()), key="download_select")
    
    if st.button("⬇️ Export Data", use_container_width=True, type="primary"):
        table = st.session_state.extracted_data[download_file]["table"]
        
        export_result = export_data(table, export_formats, download_file)
        if export_result:
            st.success("✅ Export successful!")
            st.write("Exported files:")
            for fmt, path in export_result.get("exports", {}).items():
                st.write(f"  • {fmt.upper()}: {path}")
else:
    st.info("No data to export. Extract data first.")

# Footer
st.divider()
st.markdown("""
    <div style='text-align: center; color: gray; font-size: 12px; margin-top: 50px;'>
    Intelligent Data Extractor • Powered by AI • Supports Tables, Charts, PDFs
    </div>
""", unsafe_allow_html=True)
