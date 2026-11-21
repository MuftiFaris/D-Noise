# D-Noice: Dokumentasi Lengkap Sistem Denoising Citra

## 📋 Daftar Isi
1. [Ringkasan Proyek](#ringkasan-proyek)
2. [Persyaratan & Batasan](#persyaratan--batasan)
3. [Arsitektur Sistem](#arsitektur-sistem)
4. [Alur Web Aplikasi](#alur-web-aplikasi)
5. [Rumus & Algoritma](#rumus--algoritma)
6. [Implementasi Filter](#implementasi-filter)
7. [Metrik Kualitas](#metrik-kualitas)
8. [Format PNG Manual](#format-png-manual)

---

## 🎯 Ringkasan Proyek

**D-Noice** adalah aplikasi web untuk membandingkan tiga metode penyaringan (denoising) citra yang terkena noise salt-and-pepper, semuanya diimplementasikan **tanpa library eksternal** seperti NumPy, OpenCV, atau scikit-image.

### Tujuan Akademis
- Memahami operasi dasar pemrosesan citra pada level piksel
- Belajar implementasi algoritma filter tradisional secara manual
- Membandingkan efektivitas berbagai pendekatan denoising menggunakan metrik standar industri
- Mendemonstrasikan bahwa operasi citra dapat dilakukan dengan Python standard library

### Output
- Citra yang sudah difilter (3 metode)
- Metrik perbandingan: MSE, PSNR, SSIM
- Visualisasi hasil dan grafik perbandingan

---

## 📌 Persyaratan & Batasan

### Library yang Digunakan
**HANYA** Python standard library:
- `struct` - parsing binary PNG
- `zlib` - dekompresi PNG IDAT chunk
- `json` - komunikasi server-client
- `math` - operasi trigonometri (Gaussian kernel)
- `random` - pseudo-random noise generation
- `pathlib` - file path handling
- `http.server` - web server

### TIDAK Boleh Digunakan
- ❌ NumPy - tidak ada operasi vektor/matriks
- ❌ Pillow/PIL - setelah imread awal, semua operasi manual
- ❌ OpenCV - semua filter manual
- ❌ scikit-image - semua metrik manual
- ❌ pandas - semua analisis manual

### Format Citra Didukung
- **Input PNG**: 8-bit, grayscale/RGB/RGBA, non-interlaced
- **Processing**: Selalu di-convert ke grayscale (8-bit)
- **Output PNG**: 8-bit grayscale non-interlaced

### Batasan Teknis
- Tidak ada zero-padding implisit; gunakan replicate padding di tepi
- Semua operasi menggunakan integer arithmetic (kecuali Gaussian kernel)
- Hasil akhir di-clamp ke range [0, 255]

---

## 🏗️ Arsitektur Sistem

```
┌─────────────────────────────────────────────────────────┐
│  Frontend (Browser)                                     │
│  ├─ index.html (UI + galeri citra)                     │
│  ├─ app.js (event handling + API calls)                │
│  ├─ charts.js (visualisasi grafik)                     │
│  └─ *.css (styling)                                    │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP (JSON)
                       ↓
┌─────────────────────────────────────────────────────────┐
│  Backend (Python HTTP Server)                           │
│  server.py / ThreadingHTTPServer                        │
│  ├─ GET /api/images (list dataset)                     │
│  └─ POST /api/run (process + return results)           │
└──────────────────────┬──────────────────────────────────┘
                       │ Python
                       ↓
┌─────────────────────────────────────────────────────────┐
│  Image Processing Module (rumus_manual/)               │
│  ├─ noise.py (add_salt_pepper)                         │
│  ├─ filters.py (median, adaptive, gaussian)            │
│  ├─ metrics.py (MSE, PSNR, SSIM)                       │
│  ├─ common.py (utilities)                              │
│  └─ denoise_manual.py (PNG I/O)                        │
└─────────────────────────────────────────────────────────┘
```

### Struktur Folder
```
d:\KULIAH\SEMESTER 5\PCD\D-Noice\
├── server.py                 # HTTP server (entry point web)
├── app.js                     # Frontend logic
├── charts.js                  # Chart rendering
├── index.html                 # UI HTML
├── *.css                      # Styling files
├── denoise_manual.py          # PNG I/O + CLI runner
├── rumus_manual/              # Core algorithms
│   ├── __init__.py            # Exports
│   ├── noise.py               # Salt-pepper noise
│   ├── filters.py             # 3 filter implementations
│   ├── metrics.py             # Quality metrics
│   ├── common.py              # Utilities (pad, sort)
│   ├── analysis.py            # Debug analysis
│   └── trace.py               # Execution tracing
├── data/Set12/                # Input PNG dataset
└── hasil/                     # Output PNGs & CSV
```

---

## 🌐 Alur Web Aplikasi

### Tahap 1: Browser Buka Halaman

```
User: http://127.0.0.1:8000
       ↓
Server.do_GET('/') → serve index.html
       ↓
Browser render UI + load app.js + charts.js
       ↓
app.js jalankan loadGallery() → GET /api/images
       ↓
Server respons JSON: {"images": ["01.png", "02.png", ...]}
       ↓
Browser tampil thumbnail galeri + tombol noise (5%, 10%, 20%, 30%)
```

### Tahap 2: User Klik Gambar

```
Browser:
  state.name = "01.png"
  $('#original-image').src = '/data/Set12/01.png'
  
Server:
  do_GET('/data/Set12/01.png') → serve static file
```

### Tahap 3: User Klik Tombol Noise

```
Browser kirim POST /api/run:
{
  "image": "01.png",
  "noise": 10,      # persentase 0-100
  "seed": 42        # reproducible randomness
}
```

### Tahap 4: Server Proses (Backend Processing)

```python
# 4a. Baca PNG original
clean = read_png_gray("data/Set12/01.png")
# Result: list[list[int]] = matrix 512×512, nilai 0-255

# 4b. Tambah salt-pepper noise
noisy = add_salt_pepper(clean, 10, 42)
# Result: 10% piksel random jadi 0 atau 255

# 4c. Jalankan 3 filter (synchronous)
results = {
  "Median Filter": median_filter(noisy, 3),
  "Adaptive Median": adaptive_median_filter(noisy, 7),
  "Gaussian Filter": gaussian_filter(noisy)
}

# 4d. Hitung metrik untuk masing-masing
methods = {}
for label, restored in results.items():
  methods[label] = {
    "mse": calculate_mse(clean, restored),
    "psnr": calculate_psnr(clean, restored),
    "ssim": calculate_ssim(clean, restored)
  }

# 4e. Encode semua citra ke PNG + base64
images = {
  "original": base64_encode_png(clean),
  "noisy": base64_encode_png(noisy),
  "method0": base64_encode_png(results[0]),
  "method1": base64_encode_png(results[1]),
  "method2": base64_encode_png(results[2])
}
```

### Tahap 5: Server Kirim Hasil

```python
send_json(200, {
  "image": "01.png",
  "noise": 10,
  "seed": 42,
  "width": 512,
  "height": 512,
  "images": {
    "original": "data:image/png;base64,iVBORw0KGgo...",
    "noisy": "data:image/png;base64,iVBORw0KGgo...",
    "method0": "data:image/png;base64,iVBORw0KGgo...",
    "method1": "data:image/png;base64,iVBORw0KGgo...",
    "method2": "data:image/png;base64,iVBORw0KGgo..."
  },
  "methods": {
    "Median Filter": {
      "mse": 45.23,
      "psnr": 31.58,
      "ssim": 0.8954,
      "sum_squared_error": 11779456,
      "pixel_count": 262144,
      "samples": [...detailed error samples...]
    },
    "Adaptive Median": {
      "mse": 32.15,
      "psnr": 33.06,
      "ssim": 0.9201,
      ...
    },
    "Gaussian Filter": {
      "mse": 56.78,
      "psnr": 30.59,
      "ssim": 0.8756,
      ...
    }
  }
})
```

### Tahap 6: Browser Render Hasil

```javascript
// Tampil citra asli & bernoisy
$('#original-image').src = data.images.original;
$('#noisy-image').src = data.images.noisy;

// Tampil 3 hasil filter di kartu
for (let i = 0; i < 3; i++) {
  $('#result-' + i).src = data.images['method' + i];
  $('#scores-' + i).textContent = `
    MSE ${data.methods[labels[i]].mse.toFixed(3)}
    PSNR ${data.methods[labels[i]].psnr.toFixed(3)} dB
    SSIM ${data.methods[labels[i]].ssim.toFixed(5)}
  `;
}

// Render tabel perbandingan
// Render grafik MSE vs PSNR vs SSIM
```

### HTTP API Endpoints

#### GET `/api/images`
Daftar semua PNG di `data/Set12/`.

**Request:**
```http
GET /api/images HTTP/1.1
```

**Response:**
```json
{
  "images": ["01.png", "02.png", "03.png", ...]
}
```

#### POST `/api/run`
Proses citra: buat noise, jalankan 3 filter, hitung metrik.

**Request:**
```json
{
  "image": "01.png",
  "noise": 10,
  "seed": 42
}
```

**Validation:**
- `image`: nama file di `data/Set12/`, harus `.png`
- `noise`: integer 5, 10, 20, atau 30 (persentase)
- `seed`: integer 0-2147483647

**Response Success (200):**
```json
{
  "image": "01.png",
  "noise": 10,
  "seed": 42,
  "width": 512,
  "height": 512,
  "images": {
    "original": "data:image/png;base64,...",
    "noisy": "data:image/png;base64,...",
    "method0": "data:image/png;base64,...",
    "method1": "data:image/png;base64,...",
    "method2": "data:image/png;base64,..."
  },
  "methods": {
    "Median Filter": {...metrics...},
    "Adaptive Median": {...metrics...},
    "Gaussian Filter": {...metrics...}
  }
}
```

**Response Error (400/500):**
```json
{
  "error": "Deskripsi error"
}
```

---

## 🧮 Rumus & Algoritma

### A. Noise Generation: Salt-and-Pepper

**Definisi:**
Salt-and-pepper noise adalah tipe impulsive noise di mana beberapa piksel diubah menjadi nilai ekstrem (0 = hitam atau 255 = putih) secara acak.

**Rumus:**
```
Untuk persentase p% dari total piksel:
  count = ceil(width × height × p / 100)
  
  Pilih count lokasi (x, y) secara acak:
    for i in range(count):
      x = random(0, width)
      y = random(0, height)
      noisy[y][x] = 0 (jika i genap) atau 255 (jika i ganjil)
```

**Kode Python:**
```python
def add_salt_pepper(image, percent, seed):
    h, w = len(image), len(image[0])
    out = [row[:] for row in image]
    count = round(h * w * percent / 100)
    
    # Seed untuk reproducibility
    positions = random.Random(seed).sample(range(h * w), count)
    
    for i, p in enumerate(positions):
        y, x = divmod(p, w)  # Convert linear index ke (y, x)
        out[y][x] = 0 if i % 2 == 0 else 255
    
    return out
```

**Contoh:**
- Original: `[128, 150, 180, 120, ...]`
- Noise 10%: `[128, 255, 180, 0, ...]` (2 dari ~100 piksel jadi salt/pepper)

---

### B. Padding Citra (Replicate Edge)

Ketika kernel mencapai tepi citra, kita tidak bisa ambil neighbor yang cukup. Solusi: **replicate edge values**.

**Definisi:**
```
padded[y][x] = image[clamp(y, 0, height-1)][clamp(x, 0, width-1)]
```

**Rumus:**
```
clamp(v, min, max) = 
  min(max(v, min), max)
  
Contoh: 
  clamp(-1, 0, 10) = 0
  clamp(11, 0, 10) = 10
  clamp(5, 0, 10) = 5
```

**Kode Python:**
```python
def pad_image(image, radius):
    h, w = len(image), len(image[0])
    
    # Buat matriks pad yang lebih besar
    padded = []
    for y in range(-radius, h + radius):
        row = []
        for x in range(-radius, w + radius):
            # Clamp y dan x ke boundary
            clamped_y = min(max(y, 0), h - 1)
            clamped_x = min(max(x, 0), w - 1)
            row.append(image[clamped_y][clamped_x])
        padded.append(row)
    
    return padded
```

**Visualisasi (radius=1, 3×3 window di tepi):**
```
Original:        Padded (2D):
┌─────────┐     ┌───────────────┐
│ 100 200 │     │ 100 100 200 200│
│ 150 250 │     │ 100 100 200 200│
└─────────┘     │ 150 150 250 250│
                │ 150 150 250 250│
                └───────────────┘
```

---

### C. Insertion Sort Manual

Digunakan untuk mengurutkan nilai dalam window sebelum mengambil median.

**Rumus:**
```
Insertion Sort (ascending):
  for i = 1 to n-1:
    key = arr[i]
    j = i - 1
    while j >= 0 AND arr[j] > key:
      arr[j+1] = arr[j]
      j = j - 1
    arr[j+1] = key
```

**Kode Python:**
```python
def insertion_sort(values):
    ordered = list(values)
    for i in range(1, len(ordered)):
        current = ordered[i]
        j = i - 1
        while j >= 0 and ordered[j] > current:
            ordered[j + 1] = ordered[j]
            j -= 1
        ordered[j + 1] = current
    return ordered
```

**Contoh:**
```
Input:   [200, 100, 150, 0, 255, 128]
Pass 1:  [100, 200, 150, 0, 255, 128]
Pass 2:  [100, 150, 200, 0, 255, 128]
Pass 3:  [0, 100, 150, 200, 255, 128]
Pass 4:  [0, 100, 150, 200, 255, 128]
Pass 5:  [0, 100, 128, 150, 200, 255]
Output:  [0, 100, 128, 150, 200, 255]
```

---

## 🔧 Implementasi Filter

### Filter 1: Median Filter (3×3)

**Konsep:**
Median adalah nilai tengah dari suatu dataset yang sudah diurutkan. Untuk setiap piksel, ambil 9 nilai tetangganya (3×3 window), urutkan, dan ganti piksel dengan nilai tengah.

**Rumus:**
```
Untuk setiap piksel (x, y):
  1. Ambil window 3×3 di sekitar (x, y)
  2. Kumpulkan 9 nilai: N = [v1, v2, ..., v9]
  3. Urutkan: sorted_N = insertion_sort(N)
  4. Ambil median: median = sorted_N[4]  (indeks tengah = 9 // 2)
  5. output[y][x] = median
```

**Kode Python:**
```python
def median_filter(image, size=3, on_progress=None, on_preview=None):
    """Ambil tetangga, urutkan manual, pilih nilai tengah."""
    radius = size // 2  # 3 → radius 1
    src = pad_image(image, radius)  # Pad dengan replicate edge
    
    h, w = len(image), len(image[0])
    result = []
    
    for y in range(h):
        row = []
        for x in range(w):
            # Ambil window 3×3
            neighbors = neighborhood(src, y, x, radius)
            # neighbors = [v1, v2, v3, v4, center, v6, v7, v8, v9] (9 elemen)
            
            # Urutkan manual
            ordered = insertion_sort(neighbors)
            
            # Ambil median (indeks 4 dari 0-8)
            median = ordered[len(ordered) // 2]
            
            row.append(median)
        
        result.append(row)
    
    return result
```

**Neighborhood Extraction:**
```python
def neighborhood(padded, y, x, radius, pad_radius=None):
    offset = radius if pad_radius is None else pad_radius
    yy, xx = y + offset, x + offset
    
    # Kumpulkan semua nilai dalam jendela radius×radius
    values = []
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            values.append(padded[yy + dy][xx + dx])
    return values
```

**Visualisasi:**
```
Original padded (3×3 window di piksel (1,1)):
┌─────────────┐
│100 100 200│
│100 150 200│     Neighbors = [100, 100, 200,
│150 150 250│                  100, 150, 200,
└─────────────┘                 150, 150, 250]
                  
                  Sorted = [100, 100, 100, 150, 150, 150, 200, 200, 250]
                  Median = Sorted[4] = 150
                  Output = 150
```

**Efektivitas terhadap Salt-Pepper:**
- ✅ Sangat efektif menghilangkan impulsive noise
- ✅ Mempertahankan edge (kecuali di corner sharp)
- ❌ Bias terhadap nilai yang banyak (mode)

---

### Filter 2: Adaptive Median Filter (3×7)

**Konsep:**
Adaptive median menggunakan pendekatan dua tahap (Stage A & B) dan adaptif memperbesar window hingga 7×7 jika perlu.

**Tahap A (Impulse Detection):**
```
A = median(window)
B = min(window)
C = max(window)
x = nilai piksel asli

IF B < A < C:
  (noise terdeteksi)
  IF B < x < C:
    output = x  (retain: piksel asli mungkin valid)
  ELSE:
    output = A  (median jadi pengganti)
ELSE:
  (kondisi gagal, naikkan window size)
```

**Rumus Lengkap:**
```
for window_size = 3, 5, 7:
  A = median(neighborhood)
  B = min(neighborhood)
  C = max(neighborhood)
  
  IF B < A < C:
    IF B < x < C:
      return x
    ELSE:
      return A
  
  IF window_size < 7:
    lanjut ke window_size berikutnya
  ELSE:
    return A  (fallback)
```

**Kode Python:**
```python
def adaptive_pixel(src, center, y, x, max_size, trace=False):
    levels = []
    chosen = center
    
    # Coba ukuran window: 3, 5, 7 (asumsi max_size=7)
    for size in range(3, max_size + 1, 2):
        radius = size // 2
        
        # Ambil neighborhood
        values = neighborhood(src, y, x, radius)
        ordered = insertion_sort(values)
        
        # Hitung A, B, C
        low = ordered[0]           # B (min)
        high = ordered[-1]         # C (max)
        med = ordered[len(ordered) // 2]  # A (median)
        
        # Tahap A: test kondisi
        a1 = med - low  # med > low?
        a2 = med - high # med < high?
        b1 = center - low
        b2 = center - high
        
        passed_a = (a1 > 0 and a2 < 0)  # B < A < C?
        passed_b = (b1 > 0 and b2 < 0)  # B < x < C?
        
        if passed_a:
          chosen = center if passed_b else med
          if trace:
            levels.append({...})
          break  # Berhasil, keluar loop
        
        # Jika gagal, lanjut ke window size berikutnya
        if trace:
          levels.append({...})
    
    return {"levels": levels, "value": chosen} if trace else chosen
```

**Visualisasi Tahap A & B:**
```
Contoh 1: Salt noise di center
Neighborhood 3×3: [100, 150, 200, 100, 255, 150, 120, 140, 100]
Sorted:          [100, 100, 100, 120, 140, 150, 150, 200, 255]

B = 100, A = 140, C = 255, x = 255
A1 = 140 - 100 = 40 > 0 ✓
A2 = 140 - 255 = -115 < 0 ✓
→ passed_a = True

B1 = 255 - 100 = 155 > 0 ✓
B2 = 255 - 255 = 0 < 0 ✗
→ passed_b = False

Output = A = 140 (ganti 255 dengan median)

---

Contoh 2: Valid piksel (tidak noise)
Neighborhood 3×3: [128, 132, 130, 125, 130, 135, 128, 129, 131]
Sorted:          [125, 128, 128, 129, 130, 130, 131, 132, 135]

B = 125, A = 130, C = 135, x = 130
A1 = 130 - 125 = 5 > 0 ✓
A2 = 130 - 135 = -5 < 0 ✓
→ passed_a = True

B1 = 130 - 125 = 5 > 0 ✓
B2 = 130 - 135 = -5 < 0 ✓
→ passed_b = True

Output = x = 130 (retain: piksel asli)
```

**Efektivitas:**
- ✅ Lebih baik dari median untuk citra noise rendah
- ✅ Adaptif terhadap berbagai level noise
- ✅ Mempertahankan detail lebih baik
- ❌ Kompleks, overhead komputasi lebih tinggi

---

### Filter 3: Gaussian Filter (3×3)

**Konsep:**
Gaussian filter adalah operasi konvolusi menggunakan kernel Gaussian yang smooth. Berbeda dengan median (nonlinear), Gaussian adalah filter linear.

**Rumus Gaussian Kernel:**
```
G(u, v) = (1 / (2π × σ²)) × exp(-(u² + v²) / (2 × σ²))

Untuk kernel 3×3 dengan σ standar:
        1      2      1
K = 1/16 × 2    4      2
        1      2      1
```

**Normalisasi Kernel:**
```
Total weights = 1 + 2 + 1 + 2 + 4 + 2 + 1 + 2 + 1 = 16
Normalized kernel = [[1/16, 2/16, 1/16],
                      [2/16, 4/16, 2/16],
                      [1/16, 2/16, 1/16]]
```

**Konvolusi (Pixel Computation):**
```
Untuk piksel output di (x, y):
  output[y][x] = Σ Σ (input[y+dy][x+dx] × kernel[dy][dx])
                 dy dx
  
  Untuk 3×3:
  output[y][x] = input[y-1][x-1]×(1/16)  + input[y-1][x]×(2/16)  + input[y-1][x+1]×(1/16)
               + input[y  ][x-1]×(2/16)  + input[y  ][x]×(4/16)  + input[y  ][x+1]×(2/16)
               + input[y+1][x-1]×(1/16)  + input[y+1][x]×(2/16)  + input[y+1][x+1]×(1/16)
```

**Kode Python:**
```python
def gaussian_kernel(size=3, sigma=None):
    """Buat kernel Gaussian dengan normalisasi."""
    if sigma is None:
      sigma = math.sqrt(1.0 / (2.0 * math.log(2.0)))
    
    radius = size // 2
    kernel = []
    total_weight = 0.0
    
    # Hitung weight untuk setiap posisi
    for v in range(-radius, radius + 1):
        row = []
        for u in range(-radius, radius + 1):
            scaled_u = u / sigma
            scaled_v = v / sigma
            distance_squared = scaled_u * scaled_u + scaled_v * scaled_v
            weight = math.exp(-0.5 * distance_squared)
            row.append(weight)
            total_weight += weight
        kernel.append(row)
    
    # Normalisasi sehingga jumlah = 1.0
    for y in range(size):
        for x in range(size):
            kernel[y][x] = kernel[y][x] / total_weight
    
    return kernel

def gaussian_pixel(src, y, x, kernel):
    """Hitung output pixel via konvolusi manual."""
    radius = len(kernel) // 2
    total = 0.0
    
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            weight = kernel[radius - dy][radius - dx]
            pixel = src[y + radius + dy][x + radius + dx]
            total += weight * pixel
    
    # Clamp ke [0, 255] dan round ke integer
    value = max(0, min(255, int(total + 0.5)))
    return value

def gaussian_filter(image, size=3, sigma=None):
    """Aplikasikan Gaussian filter ke seluruh citra."""
    kernel = gaussian_kernel(size, sigma)
    radius = size // 2
    src = pad_image(image, radius)
    
    h, w = len(image), len(image[0])
    result = []
    
    for y in range(h):
        row = []
        for x in range(w):
            row.append(gaussian_pixel(src, y, x, kernel))
        result.append(row)
    
    return result
```

**Visualisasi Konvolusi:**
```
Neighborhood 3×3:     Kernel (normalized):
[200  255   100]      [1/16  2/16  1/16]
[100  150   50]   ×   [2/16  4/16  2/16]
[120  180   140]      [1/16  2/16  1/16]

Computation:
  = 200×(1/16) + 255×(2/16) + 100×(1/16)
  + 100×(2/16) + 150×(4/16) + 50×(2/16)
  + 120×(1/16) + 180×(2/16) + 140×(1/16)
  
  = 12.5 + 31.875 + 6.25
  + 12.5 + 37.5 + 6.25
  + 7.5 + 22.5 + 8.75
  
  = 145.625
  
  Rounded: 146
  Clamped: 146 (dalam range)
```

**Efektivitas:**
- ✅ Smooth noise secara lembut
- ✅ Preservasi edge lebih baik dari median
- ❌ Kurang efektif untuk impulse noise
- ❌ Bisa blur citra terlalu banyak

---

## 📊 Metrik Kualitas

### Metrik 1: MSE (Mean Squared Error)

**Definisi:**
MSE mengukur rata-rata kuadrat perbedaan antara citra original dan restored.

**Rumus:**
```
MSE = (1 / (H × W)) × Σ Σ (original[y][x] - restored[y][x])²
                      y x

Rentang: [0, 65025]
- MSE = 0 → citra identik (noise-free perfect restoration)
- MSE = 65025 → citra sebaliknya (worst case)
```

**Kode Python:**
```python
def calculate_mse(original, restored):
    h, w = len(original), len(original[0])
    sum_squared_error = 0
    
    for y in range(h):
        for x in range(w):
            diff = original[y][x] - restored[y][x]
            sum_squared_error += diff * diff
    
    mse = sum_squared_error / (h * w)
    return mse
```

**Interpretasi:**
- MSE rendah → restoration bagus
- MSE tinggi → restoration jelek
- Mudah dihitung tapi tidak sesuai persepsi visual manusia

---

### Metrik 2: PSNR (Peak Signal-to-Noise Ratio)

**Definisi:**
PSNR adalah rasio peak signal (max value = 255) terhadap noise (MSE). Dinyatakan dalam dB.

**Rumus:**
```
PSNR = 20 × log₁₀(MAX / √MSE)

Dimana MAX = 255 (peak value citra 8-bit)

Sehingga:
PSNR = 20 × log₁₀(255 / √MSE)
     = 10 × log₁₀(255² / MSE)
     = 10 × log₁₀(65025 / MSE)

Rentang: (0, ∞) dB
- PSNR = ∞ → MSE = 0 (identik)
- PSNR > 40 dB → restoration sangat bagus
- PSNR 30-40 dB → restoration baik
- PSNR < 20 dB → restoration jelek
```

**Kode Python:**
```python
import math

def calculate_psnr(original, restored):
    h, w = len(original), len(original[0])
    
    # Hitung MSE dulu
    sum_squared_error = 0
    for y in range(h):
        for x in range(w):
            diff = original[y][x] - restored[y][x]
            sum_squared_error += diff * diff
    
    mse = sum_squared_error / (h * w)
    
    # Handle case MSE = 0
    if mse == 0:
        return float('inf')
    
    # PSNR formula
    psnr = 10 * math.log10(65025 / mse)  # 65025 = 255²
    return psnr
```

**Contoh:**
```
Citra 512×512 = 262144 pixels

Restoration 1:
  sum_squared_error = 11779456
  MSE = 11779456 / 262144 = 45.0
  PSNR = 10 × log₁₀(65025 / 45) = 10 × log₁₀(1444.8) = 31.60 dB

Restoration 2:
  sum_squared_error = 8421376
  MSE = 8421376 / 262144 = 32.1
  PSNR = 10 × log₁₀(65025 / 32.1) = 10 × log₁₀(2026.0) = 33.07 dB
  
→ Restoration 2 lebih baik (PSNR lebih tinggi)
```

---

### Metrik 3: SSIM (Structural Similarity Index)

**Definisi:**
SSIM mengukur similarity struktur antara dua citra, lebih sesuai dengan persepsi visual manusia daripada MSE/PSNR.

**Rumus Lengkap:**
```
SSIM(x, y) = (2μₓμᵧ + C₁)(2σₓᵧ + C₂) / ((μₓ² + μᵧ² + C₁)(σₓ² + σᵧ² + C₂))

Dimana:
  μₓ = mean dari blok x (original)
  μᵧ = mean dari blok y (restored)
  σₓ² = variance dari blok x
  σᵧ² = variance dari blok y
  σₓᵧ = covariance antara x dan y
  C₁ = (0.01 × 255)² = 6.5025
  C₂ = (0.03 × 255)² = 58.5225

SSIM dihitung per block 8×8, lalu di-average.

Rentang: [-1, 1]
- SSIM = 1 → citra identik
- SSIM = -1 → citra sebaliknya (sangat berbeda)
- SSIM 0.8-1.0 → similarity tinggi
- SSIM 0.5-0.8 → similarity sedang
- SSIM < 0.5 → similarity rendah
```

**Kode Python (Block-wise SSIM):**
```python
import math

def calculate_ssim_block_average(original, restored, block_size=8):
    """Hitung SSIM per block 8×8, average hasilnya."""
    h, w = len(original), len(restored)
    k1, k2 = 0.01, 0.03
    L = 255  # Peak value
    
    c1 = (k1 * L) ** 2
    c2 = (k2 * L) ** 2
    
    ssim_values = []
    
    # Iterate per block 8×8
    for y0 in range(0, h, block_size):
        for x0 in range(0, w, block_size):
            # Kumpulkan values di block ini
            original_block = []
            restored_block = []
            
            for y in range(y0, min(y0 + block_size, h)):
                for x in range(x0, min(x0 + block_size, w)):
                    original_block.append(float(original[y][x]))
                    restored_block.append(float(restored[y][x]))
            
            n = len(original_block)
            
            # Hitung mean
            mu_x = sum(original_block) / n
            mu_y = sum(restored_block) / n
            
            # Hitung variance
            var_x = sum((v - mu_x) ** 2 for v in original_block) / (n - 1) if n > 1 else 0.0
            var_y = sum((v - mu_y) ** 2 for v in restored_block) / (n - 1) if n > 1 else 0.0
            
            # Hitung covariance
            cov_xy = sum((original_block[i] - mu_x) * (restored_block[i] - mu_y) 
                         for i in range(n)) / (n - 1) if n > 1 else 0.0
            
            # Hitung SSIM untuk block ini
            numerator = (2 * mu_x * mu_y + c1) * (2 * cov_xy + c2)
            denominator = (mu_x**2 + mu_y**2 + c1) * (var_x + var_y + c2)
            
            ssim_block = numerator / denominator
            ssim_values.append(ssim_block)
    
    # Average semua block
    return sum(ssim_values) / len(ssim_values)
```

**Visualisasi Perhitungan SSIM (Block First 8×8):**
```
Original Block (8×8):
[128 130 125 132 135 128 130 129]
[130 132 128 135 130 132 131 133]
[125 128 130 132 128 130 129 131]
...

Restored Block (8×8):
[130 131 126 133 134 129 131 130]
[131 133 129 136 131 133 132 134]
[126 129 131 133 129 131 130 132]
...

μₓ = sum(all original pixels) / 64
μᵧ = sum(all restored pixels) / 64

σₓ² = variance(original pixels)
σᵧ² = variance(restored pixels)
σₓᵧ = covariance(original, restored)

SSIM_block = (2μₓμᵧ + C₁)(2σₓᵧ + C₂) / ((μₓ² + μᵧ² + C₁)(σₓ² + σᵧ² + C₂))

Ulangi untuk semua block 8×8, lalu average hasil.
```

---

## 🔐 Format PNG Manual

### Struktur PNG File

PNG file tersusun dari signature + chunks.

```
[PNG Signature (8 bytes)]
[IHDR Chunk (13 bytes data)]
[IDAT Chunk (compressed data, >1 chunk possible)]
[IEND Chunk (0 bytes data)]
```

### PNG Signature
```
0x89 0x50 0x4E 0x47 0x0D 0x0A 0x1A 0x0A
"\x89PNG\r\n\x1a\n"
```

### Chunk Structure
```
[4 bytes: Length of data]
[4 bytes: Chunk type (ASCII)]
[N bytes: Chunk data]
[4 bytes: CRC32 checksum]

Total: N + 12 bytes
```

### IHDR Chunk (Image Header)
```
Format (13 bytes):
  0-3:   Width (32-bit big-endian)
  4-7:   Height (32-bit big-endian)
  8:     Bit depth (8)
  9:     Color type (0=grayscale, 2=RGB, 4=gray+alpha, 6=RGBA)
  10:    Compression (0=deflate)
  11:    Filter (0=standard)
  12:    Interlace (0=none)

Kode parsing:
  width, height, depth, color, compression, filtering, interlace = 
    struct.unpack(">IIBBBBB", ihdr_payload)
```

### IDAT Chunk (Image Data)
```
Compressed dengan zlib (RFC 1951 deflate)

Raw data format per scanline:
  [1 byte: Filter type] [Width pixels]
  
Filter types:
  0 = None (copy as-is)
  1 = Sub (subtract left pixel)
  2 = Up (subtract pixel above)
  3 = Average (subtract average of left & above)
  4 = Paeth (subtract Paeth predictor)
```

### Paeth Predictor Filter

Digunakan untuk optimasi kompresi PNG.

**Rumus:**
```
Paeth(a, b, c) =
  p = a + b - c
  pa = |p - a|
  pb = |p - b|
  pc = |p - c|
  
  IF pa <= pb AND pa <= pc:
    return a
  ELSE IF pb <= pc:
    return b
  ELSE:
    return c

Dimana:
  a = left pixel
  b = above pixel
  c = above-left pixel
```

**Kode Python:**
```python
def paeth(a, b, c):
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    return a if pa <= pb and pa <= pc else (b if pb <= pc else c)
```

### PNG Encoding Process

**Step 1: Prepare Raw Data**
```python
h, w = len(image), len(image[0])

# Setiap scanline: [filter_type] [pixel values]
raw = b""
for row in image:
    raw += b"\0"  # Filter type 0 (None)
    for pixel in row:
        pixel_value = max(0, min(255, int(pixel)))
        raw += bytes([pixel_value])
```

**Step 2: Compress dengan zlib**
```python
import zlib
compressed = zlib.compress(raw, 6)  # Level 6 = balanced compression
```

**Step 3: Create IHDR Chunk**
```python
import struct
ihdr_data = struct.pack(">IIBBBBB", w, h, 8, 0, 0, 0, 0)
# Width, Height, BitDepth=8, ColorType=0(grayscale), 
# Compression=0, Filter=0, Interlace=0
```

**Step 4: Create IDAT Chunk**
```python
def png_chunk(kind, payload):
    body = kind + payload
    crc = zlib.crc32(body) & 0xffffffff
    return struct.pack(">I", len(payload)) + body + struct.pack(">I", crc)

idat_chunk = png_chunk(b"IDAT", compressed)
```

**Step 5: Create IEND Chunk**
```python
iend_chunk = png_chunk(b"IEND", b"")
```

**Step 6: Assemble Final PNG**
```python
png_bytes = b"\x89PNG\r\n\x1a\n"  # Signature
png_bytes += png_chunk(b"IHDR", ihdr_data)
png_bytes += idat_chunk
png_bytes += iend_chunk
```

### PNG Decoding Process

**Step 1: Validate Signature**
```python
data = Path("image.png").read_bytes()
if not data.startswith(b"\x89PNG\r\n\x1a\n"):
    raise ValueError("Not a PNG file")
```

**Step 2: Parse Chunks**
```python
pos = 8  # After signature
width, height, color = None, None, None
compressed = bytearray()

while pos < len(data):
    length = struct.unpack_from(">I", data, pos)[0]
    chunk_type = data[pos + 4:pos + 8]
    payload = data[pos + 8:pos + 8 + length]
    pos += 12 + length
    
    if chunk_type == b"IHDR":
        width, height, depth, color, ... = struct.unpack(">IIBBBBB", payload)
    elif chunk_type == b"IDAT":
        compressed.extend(payload)
    elif chunk_type == b"IEND":
        break
```

**Step 3: Decompress**
```python
raw = zlib.decompress(bytes(compressed))
```

**Step 4: Apply PNG Filters (Row by Row)**
```python
rows = []
offset = 0
previous_row = bytearray(width)

for _ in range(height):
    filter_type = raw[offset]
    scanline = bytearray(raw[offset + 1:offset + 1 + width])
    offset += width + 1
    
    # Undo filter
    for i in range(width):
        left = scanline[i - 1] if i > 0 else 0
        up = previous_row[i]
        upper_left = previous_row[i - 1] if i > 0 else 0
        
        if filter_type == 0:  # None
            pass
        elif filter_type == 1:  # Sub
            scanline[i] = (scanline[i] + left) & 255
        elif filter_type == 2:  # Up
            scanline[i] = (scanline[i] + up) & 255
        elif filter_type == 3:  # Average
            scanline[i] = (scanline[i] + ((left + up) // 2)) & 255
        elif filter_type == 4:  # Paeth
            scanline[i] = (scanline[i] + paeth(left, up, upper_left)) & 255
    
    rows.append(list(scanline))
    previous_row = scanline
```

**Step 5: Convert to Grayscale (if needed)**
```python
# Jika color=2 (RGB)
if color == 2:
    grayscale_rows = []
    for row in rows:
        grayscale_row = []
        for i in range(0, len(row), 3):
            r, g, b = row[i], row[i+1], row[i+2]
            # ITU-R BT.601 luma formula
            gray = (299*r + 587*g + 114*b + 500) // 1000
            grayscale_row.append(gray)
        grayscale_rows.append(grayscale_row)
    rows = grayscale_rows
```

---

## 📝 Ringkasan Implementasi

| Aspek | Detil |
|-------|-------|
| **Bahasa** | Python 3 |
| **Dependencies** | Hanya standard library (struct, zlib, json, math, random, pathlib, http.server) |
| **Format Input** | PNG 8-bit (grayscale/RGB/RGBA) non-interlaced |
| **Format Output** | PNG 8-bit grayscale non-interlaced |
| **Noise Type** | Salt-and-pepper (impulse) |
| **Filter 1** | Median 3×3 (linear order-based) |
| **Filter 2** | Adaptive Median 3×7 (nonlinear adaptive) |
| **Filter 3** | Gaussian 3×3 (linear convolutional) |
| **Metrics** | MSE, PSNR (dB), SSIM (block-wise 8×8) |
| **Web Server** | ThreadingHTTPServer (standard library) |
| **API** | RESTful JSON (GET /api/images, POST /api/run) |

---

## 🔍 Contoh Eksekusi End-to-End

### User Input
```
- Image: "01.png" (512×512 pixels)
- Noise: 10%
- Seed: 42
```

### Backend Processing

**Step 1: Load Image**
```
read_png_gray("data/Set12/01.png")
→ Matrix 512×512, grayscale values 0-255
```

**Step 2: Add Noise**
```
count = ceil(512 × 512 × 10 / 100) = ceil(26214.4) = 26214 pixels
random.Random(42).sample(range(262144), 26214) → [12345, 67890, ...]

for i, pos in enumerate(positions):
  y, x = divmod(pos, 512)
  noisy[y][x] = 0 if i % 2 == 0 else 255
```

**Step 3: Apply Filters**
```
median_result = median_filter(noisy, 3)
  - Untuk setiap pixel: window 3×3 → 9 values → sort → median
  - 262144 operations

adaptive_result = adaptive_median_filter(noisy, 7)
  - Untuk setiap pixel: test tahap A dengan window 3, 5, 7
  - Adaptive based on noise detection

gaussian_result = gaussian_filter(noisy, 3)
  - Kernel: [[1/16, 2/16, 1/16], [2/16, 4/16, 2/16], [1/16, 2/16, 1/16]]
  - Untuk setiap pixel: konvolusi 3×3
```

**Step 4: Calculate Metrics**
```
For each restored image:
  MSE = Σ(original - restored)² / count
  PSNR = 10 × log₁₀(255² / MSE)
  SSIM = average SSIM dari blocks 8×8
```

**Step 5: Encode to PNG Base64**
```
For each image (original, noisy, 3 filtered):
  - Create matrix list
  - Compress with zlib
  - Create PNG chunks (IHDR, IDAT, IEND)
  - Encode to base64 data URI
  - Include in JSON response
```

### Response to Browser
```json
{
  "image": "01.png",
  "noise": 10,
  "seed": 42,
  "width": 512,
  "height": 512,
  "images": {
    "original": "data:image/png;base64,iVBORw0KGgo...",
    "noisy": "data:image/png;base64,iVBORw0KGgo...",
    "method0": "data:image/png;base64,iVBORw0KGgo...",
    "method1": "data:image/png;base64,iVBORw0KGgo...",
    "method2": "data:image/png;base64,iVBORw0KGgo..."
  },
  "methods": {
    "Median Filter": {
      "mse": 45.23,
      "psnr": 31.58,
      "ssim": 0.8954
    },
    "Adaptive Median": {
      "mse": 32.15,
      "psnr": 33.06,
      "ssim": 0.9201
    },
    "Gaussian Filter": {
      "mse": 56.78,
      "psnr": 30.59,
      "ssim": 0.8756
    }
  }
}
```

### Browser Rendering
- Display 5 images (original, noisy, 3 filtered)
- Show metrics di setiap kartu
- Render tabel perbandingan
- Draw charts (MSE vs PSNR vs SSIM)
- User bisa download CSV results

---

## 🎓 Kesimpulan Akademis

Proyek ini mendemonstrasikan:

1. **Algoritma Dasar**: Bagaimana median, adaptive median, dan Gaussian filters bekerja pada level piksel
2. **Operasi Manual**: Sorting, padding, konvolusi tanpa bantuan library
3. **Metrik Kualitas**: MSE, PSNR, SSIM sebagai standar industri untuk evaluasi restoration
4. **Format File**: Pemahaman mendalam tentang struktur PNG dan compression zlib
5. **Web Architecture**: RESTful API, client-server communication dengan JSON
6. **Reproducibility**: Seed-based random noise untuk experiment yang dapat diulang

Semua dilakukan dengan **zero external image processing libraries** untuk menunjukkan fundamental understanding.

---

**Dibuat untuk:** PCD (Pengolahan Citra Digital) - Semester 5  
**Tanggal:** 2026  
**Format:** Markdown Documentation
