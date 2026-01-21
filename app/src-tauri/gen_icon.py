from PIL import Image
import os

src = r"c:\PicoPass\app\src-tauri\icons\icon.png"
dst = r"c:\PicoPass\app\src-tauri\icons\icon.ico"

if os.path.exists(src):
    try:
        img = Image.open(src)
        # Create a proper ICO containing multiple sizes
        img.save(dst, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
        print("Success")
    except Exception as e:
        print(f"Error: {e}")
else:
    print("Source not found")
