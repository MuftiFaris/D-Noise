# Penjelasan Struktur File D-Noice

## Backend / Server-Side

### `server.py`
**Fungsi Utama:** HTTP server lokal yang menghubungkan frontend dengan image processing logic.

**Deskripsi:**
- Simple HTTP server berbasis `SimpleHTTPRequestHandler` dan `ThreadingHTTPServer`
- Serve static files (HTML, CSS, JS) dari root directory
- Handle API endpoints untuk image processing
- Manage session storage untuk perhitungan filter

**Endpoints:**
- `GET /` - Serve `index.html` (UI utama)
- `GET /api/images` - Return list PNG dari `data/Set12/`
- `GET /data/Set12/*.png` - Serve static image files
- `POST /api/prepare` - Setup eksperimen: baca gambar, buat noise, hitung baseline
- `POST /api/process` - Process gambar dengan satu filter, stream hasil real-time
- `POST /api/trace` - Debug trace untuk pixel tertentu

**Key Methods:**
- `do_GET()` - Handle GET requests
- `do_POST()` - Route POST requests ke endpoint yang sesuai
- `do_lesson()` - Core processing logic dengan streaming output
- `send_json()` - Utility untuk send JSON responses

**Flow:**
1. Browser buka http://127.0.0.1:8000
2. Server serve index.html + CSS + JS
3. Frontend fetch `/api/images` untuk daftar gambar
4. User pilih gambar + noise level → POST `/api/prepare`
5. Backend read PNG, add noise, kirim session ID ke frontend
6. Frontend loop POST `/api/process` untuk 3 filter
7. Backend stream hasil real-time (NDJSON format)
8. Frontend update UI sambil menerima data

---

### `denoise_manual.py`
**Fungsi Utama:** PNG codec + filter runner untuk CLI atau batch processing.

**Deskripsi:**
- Manual PNG encode/decode (zlib + struct parsing)
- Paeth filter untuk PNG decompression
- Color space conversion (RGB → grayscale)
- CLI interface untuk batch denoising

**Key Functions:**
- `read_png_gray(path)` - Decode PNG dari bytes, return grayscale matrix
  * Validate PNG signature
  * Parse IHDR chunk (dimensions, color type, bit depth)
  * Decompress IDAT chunk pake zlib
  * Reverse PNG filters (Sub, Up, Average, Paeth)
  * Convert RGB → grayscale (ITU-R BT.601 formula)

- `write_png_gray(path, image)` - Encode grayscale matrix ke PNG file
  * Create IHDR chunk dengan metadata
  * Compress raw scanline data pake zlib
  * Generate IDAT chunk dengan CRC32
  * Write PNG file ke disk

- `paeth(a, b, c)` - Paeth predictor filter untuk PNG
  * Input: left, up, upper_left pixels
  * Output: predicted value untuk filter reversal

- `png_gray_bytes(image)` - Encode ke PNG bytes (in-memory)
  * Tanpa tulis ke disk, return bytes langsung

**Usage:**
```bash
# CLI batch processing
python denoise_manual.py --input data/Set12 --output hasil --levels "5,10,20,30"
```

**Data Flow:**
1. Read PNG bytes → parse header → decompress → reverse filter → convert color
2. Result: list[list[int]] = 2D matrix piksel grayscale

---

### `rumus_manual/` (Folder - Core Algorithms)

#### `rumus_manual/__init__.py`
**Fungsi:** Central import point untuk semua modules.

**Export:**
```python
from .noise import add_salt_pepper
from .filters import median_filter, adaptive_median_filter, gaussian_filter, ...
from .metrics import psnr, ssim_block_average
from .common import insertion_sort, pad_image, neighborhood
from .analysis import image_analysis
from .trace import filter_trace
```

**Benefit:** Semua imports cukup dari `rumus_manual`, ga perlu specify submodule.

---

#### `rumus_manual/noise.py`
**Fungsi Utama:** Generate salt-and-pepper noise.

**Key Functions:**
- `add_salt_pepper(image, percent, seed)` - Add impulse noise
  * Input: grayscale matrix, noise percentage (0-100), seed untuk reproducibility
  * Process:
    1. Hitung jumlah piksel: `count = ceil(W × H × percent / 100)`
    2. Set seed untuk deterministic randomness
    3. Random select `count` lokasi (x, y)
    4. Set piksel jadi 0 (black) atau 255 (white) random
  * Output: noisy matrix

**Rumus:**
```
noise_count = ceil(width × height × percent / 100)
for i in range(noise_count):
    random_index = random_between(0, width×height-1)
    x, y = convert_linear_to_2d(random_index)
    noisy[y][x] = 0 if i%2==0 else 255
```

**Seed Behavior:**
- Same seed → reproducible noise pattern
- Different seed → different noise pattern
- Used untuk scientific repeatability

---

#### `rumus_manual/common.py`
**Fungsi Utama:** Utility functions untuk image processing.

**Key Functions:**
- `pad_image(image, radius, fill=128)` - Add border padding
  * Extend image dengan replicate edge values
  * Used untuk handle window operations di tepi gambar
  * Example: 3×3 filter perlu neighbor, tepi pixel ga punya semua neighbor
  * Solution: replicate tepi pixel

- `insertion_sort(values)` - Manual sorting ascending
  * No built-in sort, implement manual insertion sort
  * Digunakan untuk median filter
  * Complexity: O(n²) tapi n kecil (9 untuk 3×3 window)

- `neighborhood(padded, y, x, radius)` - Extract window values
  * Get semua pixel dalam radius × radius window
  * Input: padded image, center pixel (y, x), radius (1 untuk 3×3)
  * Output: list of pixel values (e.g., 9 values untuk 3×3)

- `validate_window_size(size)` - Check window size valid
  * Ensure odd number (3, 5, 7, etc)
  * Ensure >= 3

**Rumus Padding:**
```
padded[y][x] = image[clamp(y, 0, h-1)][clamp(x, 0, w-1)]
```

---

#### `rumus_manual/filters.py`
**Fungsi Utama:** Implementasi 3 filter denoising.

**Key Functions:**

##### 1. `median_filter(image, size=3)`
- **Konsep:** Ambil window, sort, pilih median
- **Rumus:** output = sorted(window)[len(window)//2]
- **Complexity:** O(W × H × n² log n) ≈ O(W × H) karena n kecil (9)
- **Efektivitas:** Bagus untuk salt-pepper noise, tapi blur sharp edges

##### 2. `adaptive_median_filter(image, max_size=7)`
- **Konsep:** Tahap A & B dengan adaptive window size
- **Tahap A (Impulse Detection):**
  ```
  A = median(window)
  B = min(window)
  C = max(window)
  x = original pixel
  
  IF B < A < C:
    IF B < x < C:
      output = x (retain)
    ELSE:
      output = A (replace)
  ELSE:
    naikkan window size, coba lagi
  ```
- **Window Sizes:** 3×3 → 5×5 → 7×7
- **Efektivitas:** Better edge preservation, adaptive ke noise level

##### 3. `gaussian_filter(image, size=3, sigma=None)`
- **Konsep:** Smooth via weighted average
- **Kernel:** 3×3 Gaussian dengan weight [1,2,1; 2,4,2; 1,2,1] / 16
- **Rumus Konvolusi:**
  ```
  output[y][x] = Σ Σ input[y+dy][x+dx] × kernel[dy][dx]
  ```
- **Complexity:** O(W × H × kernel_size²)
- **Efektivitas:** Smooth tapi bisa blur, less effective untuk impulse noise

**Common Parameters:**
- `on_progress(done, total)` - Callback untuk progress tracking
- `on_preview(rows, done, total)` - Callback untuk live preview rows

---

#### `rumus_manual/metrics.py`
**Fungsi Utama:** Calculate quality metrics.

**Key Functions:**

##### 1. `psnr(original, restored)` - Peak Signal-to-Noise Ratio
**Rumus:**
```
MSE = Σ Σ (original[y][x] - restored[y][x])² / (W × H)
PSNR = 10 × log₁₀(255² / MSE) dB

Special case:
IF MSE == 0: PSNR = ∞ (identical images)
```
**Range:** 0 dB (worst) → ∞ dB (best)
**Interpretation:**
- PSNR > 40 dB: Excellent
- PSNR 30-40 dB: Good
- PSNR < 20 dB: Poor

##### 2. `ssim_block_average(original, restored, block_size=8)` - Structural Similarity
**Process:**
- Split gambar jadi non-overlapping 8×8 blocks
- Hitung SSIM untuk setiap block
- Average semua SSIM values

**Rumus per block:**
```
μₓ = mean(block_x)
μᵧ = mean(block_y)
σₓ² = variance(block_x)
σᵧ² = variance(block_y)
σₓᵧ = covariance(block_x, block_y)
C₁ = (0.01 × 255)²
C₂ = (0.03 × 255)²

SSIM = (2×μₓ×μᵧ + C₁) × (2×σₓᵧ + C₂) /
       ((μₓ²+μᵧ²+C₁) × (σₓ²+σᵧ²+C₂))
```

**Range:** -1 (worst) → 1 (best)
**Interpretation:**
- SSIM 0.8-1.0: Similarity tinggi
- SSIM 0.5-0.8: Similarity sedang
- SSIM < 0.5: Similarity rendah

##### 3. `manual_metrics(original, restored, on_progress=None)` - All metrics
**Output Dict:**
```python
{
  "mse": float,
  "psnr": float,
  "ssim": float,
  "sum_squared_error": int,
  "pixel_count": int,
  "samples": [{"x": int, "y": int, "original": int, "result": int}],
  "ssim_block": {"mean_original": float, "mean_result": float, ...}
}
```

---

#### `rumus_manual/analysis.py`
**Fungsi Utama:** Analyze image properties (histogram, distribution).

**Key Functions:**
- `image_analysis(image)` - Compute histogram + statistics
  * Histogram: frequency of each pixel value (0-255)
  * Min, max, mean, variance
  * Used untuk debug dan understanding image content

---

#### `rumus_manual/trace.py`
**Fungsi Utama:** Debug trace untuk specific pixel.

**Key Functions:**
- `filter_trace(image, method, x, y)` - Step-by-step filter computation
  * Input: noisy image, filter method (0=median, 1=adaptive, 2=gaussian), pixel (x,y)
  * Output: detailed computation steps (window values, sorting, final result)
  * Used untuk educational debugging, understanding filter behavior

---

## Frontend / Client-Side

### `app.js`
**Fungsi Utama:** UI logic dan API communication.

**Global State:**
```javascript
state = {
  name: null,           // selected image filename
  noise: null,          // noise percentage (5, 10, 20, 30)
  session: null,        // server session ID
  busy: false,          // processing flag
  results: [null, null, null]  // filter results untuk 3 metode
}
```

**Key Functions:**

#### UI Management:
- `renderCards()` - Render 3 method cards (Median, Adaptive, Gaussian)
- `clearResults()` - Clear all results, reset state
- `renderSummary()` - Show metrics table + charts

#### API Communication:
- `loadGallery()` - GET `/api/images`, populate gallery
- `post(path, body)` - POST JSON, return parsed response
- `runExperiment()` - Main flow: prepare noise → process 3 filters
- `processMethod(method)` - Process satu filter, stream hasil

#### Event Handlers:
- Gallery click: select image, show preview
- Noise button click: select noise level, trigger runExperiment()
- Seed input change: invalidate results (seed berubah)

**Flow:**
```
1. Load gallery → user click image
2. User click noise button → POST /api/prepare
3. Server kirim session ID + images
4. Frontend loop POST /api/process untuk 3 filter
5. Stream NDJSON: progress updates → preview images → metrics
6. Frontend update cards real-time
7. Final: render summary table + charts
```

---

### `charts.js`
**Fungsi Utama:** Data visualization (SVG charts).

**Chart Types:**
- **Line Chart:** MSE / PSNR / SSIM vs blocks atau rows
- **Bar Chart:** Comparison antar filter
- **Scatter Plot:** Correlation analysis

**Key Functions:**
- `renderCombinedAnalysis()` - Render selected chart based on user choice
- `downloadChartCsv()` - Export chart data as CSV

**Data Series:**
- Series 0: Original (reference)
- Series 1: Noisy
- Series 2: Median Filter
- Series 3: Adaptive Median
- Series 4: Gaussian Filter

**Color Coding:**
```javascript
--series-0: #0F172A (deep slate)
--series-1: #E11D48 (crimson, noisy)
--series-2: #0D9488 (teal, median)
--series-3: #2563EB (blue, adaptive)
--series-4: #D97706 (amber, gaussian)
```

---

## Data Flow Diagram

```
User Browser
    ↓
index.html (UI)
    ↓
app.js (event handlers)
    ↓
POST /api/prepare
    ↓
server.py (do_lesson)
    ↓
denoise_manual.read_png_gray() [load image]
    ↓
rumus_manual.add_salt_pepper() [create noise]
    ↓
Return: session_id, images (base64)
    ↓
Browser show original + noisy images
    ↓
User click filter button
    ↓
POST /api/process (stream NDJSON)
    ↓
server.py processing loop
    ↓
rumus_manual.filters.median_filter() [or adaptive/gaussian]
    ↓
Emit: type=progress (live progress)
    ↓
Emit: type=preview (partial result)
    ↓
rumus_manual.metrics (calculate MSE/PSNR/SSIM)
    ↓
Emit: type=result (final result)
    ↓
Browser receive streams → update UI real-time
    ↓
Show final image + metrics
    ↓
Repeat untuk 3 filter
    ↓
Show comparison table + charts
```

---

## Dependency Graph

```
server.py
  ├─ denoise_manual.py
  │   ├─ read_png_gray() → PNG decode
  │   └─ write_png_gray() → PNG encode
  │
  └─ rumus_manual/
      ├─ __init__.py (imports all)
      ├─ noise.py → add_salt_pepper()
      ├─ filters.py → median/adaptive/gaussian filters
      ├─ metrics.py → psnr, ssim_block_average
      ├─ common.py → insertion_sort, pad_image, neighborhood
      ├─ analysis.py → image_analysis()
      └─ trace.py → filter_trace()

index.html
  ├─ app.js (main logic)
  │   ├─ loadGallery() → GET /api/images
  │   ├─ runExperiment() → POST /api/prepare
  │   └─ processMethod() → POST /api/process
  │
  └─ charts.js (visualization)
      └─ renderCombinedAnalysis()
```

---

## Zero-Library Implementation

**Tanpa external library untuk image processing:**
- ❌ No NumPy (manual array operations)
- ❌ No Pillow/PIL (PNG codec manual)
- ❌ No OpenCV (filter manual)
- ❌ No scikit-image (metrics manual)

**Using ONLY Python stdlib:**
- `struct` - parse PNG binary format
- `zlib` - decompress PNG data
- `json` - API communication
- `math` - logarithm untuk PSNR
- `random` - noise generation
- `pathlib` - file operations
- `http.server` - web server

---

## Running the Project

```bash
# Start web server
python server.py

# Browser: http://127.0.0.1:8000

# Or batch process (CLI)
python denoise_manual.py --input data/Set12 --output hasil --levels "5,10,20,30"
```

---

**Created for:** PCD (Pengolahan Citra Digital) course  
**Institution:** [University]  
**Date:** 2026
