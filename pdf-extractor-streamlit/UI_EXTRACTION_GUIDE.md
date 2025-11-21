# UI Guide: Understanding Table Extraction Flow

## What You'll See in the Interface

When you extract a table, here's exactly what happens and what you'll see:

---

## 1. Upload & Extract Tab

### Upload Phase
```
1. Choose image file (PNG, JPG, JPEG)
2. Set Job Name
3. Click "🔍 Extract Data"
```

### Extraction Progress
```
As extraction runs, you'll see:
- Progress bar (0% → 100%)
- Status message: "Processing file 1/1: image.jpg"
```

### After Extraction
```
✅ Extracted 3 rows, 4 columns

📖 How Table Was Extracted (expandable section)
├─ 1️⃣ Image Upload
├─ 2️⃣ OCR Processing
├─ 3️⃣ Text Parsing
├─ 4️⃣ Row Detection
└─ 5️⃣ Table Building

Then shows:
- 📊 Extraction Metrics
  • Rows: 3
  • Columns: 4
  • OCR Chars: 245
  • Status: table_found

- 📋 Preview (first 5 rows)
```

### If Extraction Fails
```
⚠️ No table rows found. Detection status: no_table_found

🔍 Debug Info (expandable)
├─ Detection Status: no_table_found
├─ OCR Text Length: 0 chars
├─ Raw Lines Found: 0
├─ Extracted Rows: 0
└─ First 500 chars of OCR text: [empty]
```

---

## 2. Data Viewer Tab

### Extraction Flow Diagram
```
📸 Image → 🔤 OCR → 📝 Parse → 🔍 Detect → ✅ Table
```

### Three Tabs Inside

#### Tab A: 📋 Table Data
**Shows:** The final extracted table

```
┌─────────┬────┬────┬────────┐
│ Label   │ Q1 │ Q2 │   Q3   │
├─────────┼────┼────┼────────┤
│ North   │100 │120 │  150   │
│ South   │150 │200 │  250   │
│ East    │120 │145 │  175   │
└─────────┴────┴────┴────────┘

Statistics:
• Rows: 3
• Columns: 4
• Total Cells: 12
```

#### Tab B: 🔤 OCR Text
**Shows:** Raw text extracted by Tesseract

```
OCR Output (raw text extracted from image):

[Large text box showing:]
Quarterly Sales Results
Region Q1 Q2 Q3
North 100 120 150
South 150 200 250
East 120 145 175
```

#### Tab C: 📊 Extraction Details
**Shows:** How extraction worked

```
Left Column:
- Extraction Statistics:
  • OCR Text Length: 245 characters
  • Extracted Rows: 3
  • Columns per Row: 4
  • Total Cells: 12

Right Column:
- How It Works:
  1. OCR Processing: Tesseract reads text
  2. Line Detection: Finds consistent columns
  3. Row Parsing: Each line becomes a row
  4. Column Mapping: Values map to headers
  5. Data Cleaning: Numbers converted
  6. Output: Clean table

- Extraction Process:
  
  Step 1: OCR captures text from image
    Region Q1 Q2 Q3...
    
  Step 2: System parses and structures it
    Label: North
    Q1: 100
    Q2: 120
    Q3: 150
```

---

## 3. Understanding the Sections

### 📸 Image Upload Section
- Original image with table visible

### 🔤 OCR Text Section
- Raw text extracted by Tesseract
- Shows exactly what OCR "saw"
- If empty, OCR failed (bad image quality)

### 📝 Text Parsing Section
- System reads OCR text line by line
- Identifies table structure
- Groups related lines together

### 🔍 Row Detection Section
- Finds which lines are headers
- Which lines are data rows
- Validates consistency

### ✅ Table Building Section
- Converts parsed text to table format
- Maps values to columns
- Converts data types

---

## What Each Metric Means

| Metric | What It Shows |
|--------|---|
| **Rows** | Number of data rows (excluding header) |
| **Columns** | Number of columns in the table |
| **OCR Chars** | Total characters captured by OCR |
| **Total Cells** | Rows × Columns |
| **Status** | Result of extraction (table_found, no_table_found, etc.) |

---

## Status Messages Explained

### ✅ Success Messages

**"table_found"**
- Table successfully detected and extracted
- Data is ready to use

**"Extracted X rows, Y columns"**
- Final result with exact counts

### ⚠️ Warning Messages

**"no_table_found"**
- OCR returned text, but no table structure detected
- Check image quality or table format

**"no_valid_rows"**
- Table structure detected but couldn't parse rows
- Data might be in unusual format

**"detection_status: unknown"**
- Unexpected result
- Check debug info for more details

---

## How to Read the Extraction Flow

### The Visual Flow
```
📸 IMAGE
  ↓
🔤 OCR  (Tesseract reads text)
  ↓
📝 PARSE (System analyzes text)
  ↓
🔍 DETECT (Finds table structure)
  ↓
✅ TABLE (Final output)
```

### What Happens at Each Step

**📸 Image**
```
Input: Picture of a table
Status: Ready for processing
```

**🔤 OCR**
```
Input: Image pixels
Process: Tesseract analyzes image
Output: "Region Q1 Q2 Q3\nNorth 100 120..."
Status: Depends on image quality
```

**📝 Parse**
```
Input: Raw OCR text
Process: Split into lines, tokenize
Output: List of lines with tokens
Status: Looking for structure
```

**🔍 Detect**
```
Input: Tokenized lines
Process: Find headers and data rows
Output: Identified structure
Status: Table found or not
```

**✅ Table**
```
Input: Identified structure
Process: Build final table format
Output: Structured table with headers
Status: Ready for analysis
```

---

## Real Example: Step by Step

### Your Image
```
┌──────────────────────────┐
│  Product Sales Report    │
├────────┬────┬────┬────┤
│Product │ Q1 │ Q2 │ Q3 │
├────────┼────┼────┼────┤
│Widget  │100 │120 │150 │
│Gadget  │150 │180 │210 │
└────────┴────┴────┴────┘
```

### Step 1: OCR Output
```
Product Sales Report
Product Q1 Q2 Q3
Widget 100 120 150
Gadget 150 180 210
```

### Step 2: Line Parsing
```
Line 1: "Product Sales Report" → Skip (header/title)
Line 2: "Product Q1 Q2 Q3" → Found! (4 tokens)
Line 3: "Widget 100 120 150" → Found! (4 tokens)
Line 4: "Gadget 150 180 210" → Found! (4 tokens)
```

### Step 3: Structure Detection
```
First table line: "Product Q1 Q2 Q3"
  → Headers: [Product, Q1, Q2, Q3]

Following lines:
  → Row 1: Widget, 100, 120, 150
  → Row 2: Gadget, 150, 180, 210
```

### Step 4: Table Building
```
[
  {"Product": "Widget", "Q1": 100, "Q2": 120, "Q3": 150},
  {"Product": "Gadget", "Q1": 150, "Q2": 180, "Q3": 210}
]
```

### Step 5: Display in UI
```
Tab: 📋 Table Data
┌─────────┬────┬────┬────┐
│Product  │ Q1 │ Q2 │ Q3 │
├─────────┼────┼────┼────┤
│Widget   │100 │120 │150 │
│Gadget   │150 │180 │210 │
└─────────┴────┴────┴────┘

Tab: 🔤 OCR Text
Product Sales Report
Product Q1 Q2 Q3
Widget 100 120 150
Gadget 150 180 210

Tab: 📊 Extraction Details
• OCR Text Length: 78 characters
• Extracted Rows: 2
• Columns per Row: 4
• Total Cells: 8
```

---

## Troubleshooting from UI

### I don't see anything in "OCR Text" tab
**Problem:** OCR failed
**Check:** Is image visible? Is text readable?
**Solution:** Use clearer image

### I see OCR text but empty table
**Problem:** Table structure not detected
**Check:** Are rows aligned consistently?
**Solution:** Crop to just the table

### Numbers look wrong in table
**Problem:** OCR misread characters (0→O, 1→I)
**Check:** Compare OCR text with original
**Solution:** Use higher quality image

### Wrong number of columns
**Problem:** Spacing or alignment issues
**Check:** Columns in OCR text
**Solution:** Ensure consistent spacing

---

## Tips for Best Results

✅ **For Clear Extraction:**
1. Use high-quality image (300+ DPI)
2. Ensure good lighting
3. Table should be straight (not rotated)
4. Clear, distinct column separation
5. Professional printed text (not handwritten)

❌ **What Doesn't Work Well:**
- Blurry images
- Low resolution
- Handwritten tables
- Tables with merged cells
- Very small fonts
- Multiple overlapping tables

---

## Quick Reference

| If You See | It Means | Next Step |
|---|---|---|
| "✅ Extracted..." | Table found successfully | View in Data Viewer tab |
| "⚠️ No table rows found" | OCR worked but table not detected | Check image/crop region |
| "Detection Status: no_table_found" | Complete failure | Use higher quality image |
| Empty OCR text | Tesseract failed | Verify image quality |
| Partial data in table | Parsing issue | Check extraction details tab |

---

**Now you understand exactly how tables are extracted!** 📊✨
