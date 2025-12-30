from PIL import Image, ImageDraw
import os
import io
from collatz_crypto import SecureCollatzCipher

def create_test_image(width=512, height=512):
    """Creates a simple gradient test image."""
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    for i in range(height):
        r = int(255 * (i / height))
        g = int(255 * ((height - i) / height))
        b = (i // 2) % 256
        draw.line([(0, i), (width, i)], fill=(r, g, b))
    
    # Add some text/shapes to make it complex
    draw.rectangle([100, 100, 400, 400], outline='black', width=5)
    draw.ellipse([200, 200, 300, 300], fill='red')
    return img

def get_standard_quantization_table():
    # Standard JPEG Luminance Quantization Table (approx)
    # This is often scaled by quality factor. At Q=50, this is the table.
    std_q = [
        16, 11, 10, 16, 24, 40, 51, 61,
        12, 12, 14, 19, 26, 58, 60, 55,
        14, 13, 16, 24, 40, 57, 69, 56,
        14, 17, 22, 29, 51, 87, 80, 62,
        18, 22, 37, 56, 68, 109, 103, 77,
        24, 35, 55, 64, 81, 104, 113, 92,
        49, 64, 78, 87, 103, 121, 120, 101,
        72, 92, 95, 98, 112, 100, 103, 99
    ]
    return std_q

def run_experiment():
    print("--- Starting JPEG Compression Experiment ---")
    
    # 1. Prepare Image
    img = create_test_image()
    img_path = "test_image.png"
    img.save(img_path)
    original_size = os.path.getsize(img_path)
    print(f"Original PNG Size: {original_size} bytes")

    # 2. Setup Collatz Cipher
    cipher = SecureCollatzCipher()
    collatz_q_table = cipher.generate_quantization_table()
    
    # Ensure values are within byte range 1-255 (0 not allowed in some implementations, 1 is fine)
    collatz_q_table = [max(1, min(255, x)) for x in collatz_q_table]

    # Standard Table
    std_table = get_standard_quantization_table()

    # 3. Compress with Standard
    # Note: Pillow handles qtables as a list of lists if multiple tables (luma/chroma)
    # or simple list. We will try passing just luma for simplicity or let it default.
    # Actually, to force a custom table, we pass `qtables=[table]`.
    
    std_jpg_path = "output_std.jpg"
    img.save(std_jpg_path, "JPEG", quality=75, subsampling=0)
    std_size = os.path.getsize(std_jpg_path)
    
    # 4. Compress with Collatz Table
    collatz_jpg_path = "output_collatz.jpg"
    try:
        # We need to replicate the table for chroma if we want full control, 
        # or Pillow might just use it for everything logic-wise.
        img.save(collatz_jpg_path, "JPEG", qtables=[collatz_q_table], subsampling=0)
        collatz_size = os.path.getsize(collatz_jpg_path)
        collatz_success = True
    except Exception as e:
        print(f"Collatz compression failed: {e}")
        collatz_size = 0
        collatz_success = False

    # 5. Results
    print("\n--- Results ---")
    print(f"Standard JPEG Size: {std_size} bytes")
    if collatz_success:
        print(f"Collatz JPEG Size: {collatz_size} bytes")
        diff = std_size - collatz_size
        print(f"Difference: {diff} bytes ({'Saved space' if diff > 0 else 'Increased size'})")
        
        # Analyze why
        avg_std = sum(std_table)/len(std_table)
        avg_collatz = sum(collatz_q_table)/len(collatz_q_table)
        print(f"\nAvg Quantization Value (Higher = More Compression/Lower Quality):")
        print(f"Standard: {avg_std:.2f}")
        print(f"Collatz:  {avg_collatz:.2f}")
    else:
        print("Collatz JPEG generation failed.")

if __name__ == "__main__":
    run_experiment()
