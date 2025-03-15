import subprocess
import sys
import site
import os
import importlib.util

def is_pillow_installed():
    """Check if Pillow is installed in Blender's Python environment."""
    return importlib.util.find_spec("PIL") is not None

def get_user_site_packages():
    """Return the user-writable site-packages path."""
    return site.getusersitepackages()  # Typically in AppData/Roaming/Python

def install_pillow_user():
    """Install Pillow in a user-writable location."""
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "pillow"])

def ensure_user_site_packages_in_sys_path():
    """Ensure Blender can find user-installed packages."""
    user_site_packages = get_user_site_packages()
    if user_site_packages not in sys.path:
        sys.path.append(user_site_packages)

def verify_pillow():
    """Verify that Pillow is installed and working."""
    ensure_user_site_packages_in_sys_path()
    
    try:
        import PIL
        print(f"Pillow is installed and working! Location: {PIL.__file__}")
    except ImportError:
        print("ERROR: Blender still cannot detect Pillow!")

# Main execution
if is_pillow_installed():
    print("Pillow is already installed in Blender.")
else:
    print("Pillow is not installed. Installing now...")
    install_pillow_user()

# Verify installation
verify_pillow()

import argparse
from concurrent.futures import ThreadPoolExecutor
from PIL import Image

# Attempt to retrieve paths from environment variables
ZOPFLI_PATH = os.getenv("ZOPFLIPNG", os.path.join(projectsfolder, r"Path\to\zopflipng.exe"))
PNGQUANT_PATH = os.getenv("PNGQUANT", os.path.join(projectsfolder, r"Path\to\pngquant.exe"))

# Validate that the executables exist before proceeding
if not os.path.exists(ZOPFLI_PATH):
    print(f"⚠️ Warning: Zopfli executable not found at {ZOPFLI_PATH}")
if not os.path.exists(PNGQUANT_PATH):
    print(f"⚠️ Warning: pngquant executable not found at {PNGQUANT_PATH}")

# Get CPU cores, leaving one free
NUM_THREADS = max(1, os.cpu_count() - 4)


def resize_image(input_path, output_path, size_percent):
    """ Resizes an image using Pillow. """
    with Image.open(input_path) as img:
        width, height = img.size
        new_size = (int(width * size_percent / 100), int(height * size_percent / 100))
        img = img.resize(new_size, Image.LANCZOS)
        img.save(output_path, "PNG")
        print(f"📏 Resized: {input_path} → {output_path} ({new_size[0]}x{new_size[1]})")


def compress_with_pngquant(input_path, quality):
    """ Compresses an image using pngquant with given quality. """
    output_path = input_path.replace(".png", "_pngquant.png")
    cmd = [PNGQUANT_PATH, f"--quality={quality}-100", "--force", "--output", output_path, input_path]
    
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if os.path.exists(output_path):
        os.replace(output_path, input_path)  # Overwrite original
        print(f"🎨 Pngquant compressed: {input_path} (Quality {quality})")
    else:
        print(f"❌ Pngquant failed: {input_path}\n{result.stderr}")


def compress_with_zopfli(input_path, iterations):
    """ Optimizes an image using zopflipng. """
    temp_output = input_path.replace(".png", "_optimized.png")
    cmd = [ZOPFLI_PATH, f"--iterations={iterations}", input_path, temp_output]
    
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if os.path.exists(temp_output):
        os.replace(temp_output, input_path)  # Overwrite original
        print(f"✅ Zopfli optimized: {input_path} (Iterations {iterations})")
    else:
        print(f"❌ Zopfli failed: {input_path}\n{result.stderr}")


def process_image(file_path, size, quality, iterations):
    """ Full pipeline: Resize (if needed) → pngquant (if requested) → zopflipng (always). """
    if size:
        resized_output = file_path.replace(".png", "_resized.png")
        resize_image(file_path, resized_output, size)
        os.replace(resized_output, file_path)  # Overwrite original

    if quality:
        compress_with_pngquant(file_path, quality)

    compress_with_zopfli(file_path, iterations)


def get_png_files(input_path, recursive):
    """ Returns a list of PNG files from the given input path. """
    if os.path.isfile(input_path) and input_path.lower().endswith(".png"):
        return [input_path]  # Single file mode

    elif os.path.isdir(input_path):
        png_files = []
        if recursive:
            for root, _, files in os.walk(input_path):
                png_files.extend([os.path.join(root, f) for f in files if f.lower().endswith(".png")])
        else:
            png_files = [os.path.join(input_path, f) for f in os.listdir(input_path) if f.lower().endswith(".png")]

        return png_files

    else:
        print(f"❌ Error: Invalid path {input_path}")
        return []


def parse_blender_args():
    """ Parses command-line arguments, ensuring Blender's args are skipped. """
    try:
        # Blender passes its own args first, our custom args are after "--"
        custom_args_index = sys.argv.index("--") + 1
        args = sys.argv[custom_args_index:]
    except ValueError:
        print("❌ Error: No `--` found to separate Blender and script arguments.")
        sys.exit(1)

    # Now, parse the custom args
    parser = argparse.ArgumentParser(description="Batch PNG Optimizer using Pillow, pngquant, and zopflipng")
    parser.add_argument("input_path", help="Path to a PNG file or folder containing PNG images")
    parser.add_argument("--iterations", type=int, default=15, help="Number of zopflipng iterations (default: 15)")
    parser.add_argument("--quality", type=int, help="Min quality for pngquant (1-100, optional)")
    parser.add_argument("--size", type=int, help="Resize percentage (1-100, optional)")
    parser.add_argument("--recursive", action="store_true", help="Process PNGs in subdirectories as well")

    return parser.parse_args(args)


def main():
    """ Main execution with Blender-friendly argument parsing. """
    args = parse_blender_args()

    # Get PNG files based on input type
    png_files = get_png_files(args.input_path, args.recursive)

    if not png_files:
        print("❌ No PNG files found. Exiting.")
        return

    # Multithreading execution
    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        executor.map(lambda f: process_image(f, args.size, args.quality, args.iterations), png_files)

    print("\n🎉 PNG processing complete!")


if __name__ == "__main__":
    main()