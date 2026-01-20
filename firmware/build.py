import os
import shutil
import zipfile

def build_micropython():
    print("📦 Packaging MicroPython Firmware...")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(base_dir, "micropython")
    build_dir = os.path.join(base_dir, "builds/micropython_bundle")
    
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir)
    
    # Copy all .py files
    for item in os.listdir(src_dir):
        if item.endswith(".py"):
            shutil.copy(os.path.join(src_dir, item), build_dir)
            
    # Create zip
    zip_name = os.path.join(base_dir, "builds/picopass_micropython_v0.1.0")
    shutil.make_archive(zip_name, 'zip', build_dir)
    print(f"✅ MicroPython bundle created in {zip_name}.zip")

def build_c():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    print("🚧 C/C++ Firmware (Semana 9) is ready!")
    print(f"To compile, ensure PICO_SDK_PATH is set and run:")
    print(f"cd {os.path.join(base_dir, 'c')} && mkdir -p build && cd build && cmake .. && make")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    builds_path = os.path.join(base_dir, "builds")
    if not os.path.exists(builds_path):
        os.makedirs(builds_path)
    build_micropython()
    build_c()
