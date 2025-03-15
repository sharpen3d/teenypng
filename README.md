# teenypng
Multithreaded combination of multiple png compression tools
Overview

This script optimizes PNG images using Blender's Python environment. It performs the following steps:

1. **Installs Pillow if necessary** (for image resizing)
2. **Processes PNG images in a specified directory or single file**
3. **Uses `pngquant` for lossy compression (if requested)**
4. **Uses `zopflipng` for final lossless compression**
5. **Supports multithreading for performance improvements**

---

## Requirements

### **1. Install Blender and Add to System PATH**

Blender must be installed and added to the system `PATH` for command-line execution.

1. Download Blender from: https://www.blender.org/download/
2. Add Blender to system `PATH` (so you can call it from CMD or PowerShell):
    - Open **Control Panel** → **System** → **Advanced system settings**
    - Click **Environment Variables**
    - Under **System variables**, find `Path`, click **Edit**
    - Click **New** and add the path to Blender's installation folder (e.g., `C:\Program Files\Blender Foundation\Blender 3.6`)
    - Click **OK**, restart CMD, and verify by running:
        
        ```
        blender --version
        
        ```
        

### **2. Install `pngquant` and `zopflipng` and Add to System PATH**

These tools handle PNG compression.

### **Install pngquant**

1. Download the Windows binary from [https://pngquant.org/](https://pngquant.org/pngquant-windows.zip)
2. Extract and place `pngquant.exe` somewhere like `C:\Tools\pngquant.exe`
3. Add the folder to the `PATH` (same process as Blender above)
4. Verify installation:
    
    ```
    pngquant --version
    
    ```
    

### **Install zopflipng**

1. Download Google's `zopfli` from: [https://github.com/google/zopfli/releases](https://drpleaserespect.github.io/drpleaserespect-webassets/compiled_binaries/google/zopflipng.exe)
2. Extract `zopflipng.exe` to a location like `C:\Tools\zopflipng.exe`
3. Add the folder to the `PATH`
4. Verify installation:
    
    ```
    zopflipng --version
    
    ```
    

Alternatively, you can set the script to use environment variables:

```
setx PNGQUANT "C:\Tools\pngquant.exe"
setx ZOPFLIPNG "C:\Tools\zopflipng.exe"

```

## Usage

### **Command Structure**

```
blender --background --python myscript.py -- <input_path> [OPTIONS]

```

### **Required Arguments**

| Flag | Description | Type |
| --- | --- | --- |
| `<input_path>` | Path to a PNG file or directory | str |

### **Optional Arguments**

| Flag | Description | Type | Min | Max | Default |
| --- | --- | --- | --- | --- | --- |
| `--iterations` | zopflipng compression iterations | int | 1 | 500 | 15 |
| `--quality` | pngquant quality (for lossy compression) | int | 1 | 100 | None |
| `--size` | Resize percentage | int | 1 | 100 | None |
| `--recursive` | Process PNGs in subdirectories | flag | - | - | False |

### **Lossless vs. Lossy Compression**

- **Lossless:** Default behavior (zopflipng only).
- **Lossy:** Use `-quality` (e.g., `-quality 70`) to apply pngquant.

### **Metadata Stripping**

- **pngquant** removes unnecessary metadata to reduce file size.
- **zopflipng** further optimizes image structure without losing pixel data.

### **Why Use Both pngquant and zopflipng?**

- **pngquant** provides significant file size reduction by applying lossy quantization.
- **zopflipng** applies additional lossless compression, ensuring further size reduction without quality loss.
- **Combining both** achieves the best balance between file size and quality, especially for game assets and web graphics.

### **Multithreading Advantage**

- Running `pngquant` and `zopflipng` separately processes images sequentially, leading to long wait times.
- This script **parallelizes** the processing, allowing multiple images to be optimized simultaneously.
- Each image completes its entire pipeline (resize → pngquant → zopflipng) within its own thread, ensuring efficiency.
- **Benefit:** Faster batch processing compared to running each tool separately on large datasets.

### **Known Issues**

- **Alpha Transparency:** pngquant may produce banding in semi-transparent images.
- **Indexed PNGs:** Indexed color PNGs may lose palette information when optimized.
- **Large Images:** Very large images may exceed memory limits when resizing.

---

## Example Commands

### **1. Lossless Compression (Default)**

```
blender --background --python path\to\teenypng.py -- "C:\Images" --iterations 20

```

### **2. Lossy Compression (Higher Compression, Some Quality Loss)**

```
blender --background --python path\to\teenypng.py -- "C:\Images" --iterations 20 --quality 70

```

### **3. Resize and Compress**

```
blender --background --python path\to\teenypng.py -- "C:\Images" --size 80 --quality 80

```

### **4. Process All PNGs in Subdirectories**

```
blender --background --python path\to\teenypng.py -- "C:\Images" --recursive

```

---
