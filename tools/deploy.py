#!/usr/bin/env python3
import os
import subprocess
import sys

def run_command(cmd):
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing: {cmd}")
        sys.exit(1)

def deploy():
    print("🚀 PicoPass CLI Deployer")
    print("-----------------------")
    
    # Check if mpremote is installed
    try:
        subprocess.run("mpremote --version", shell=True, check=True, capture_output=True)
    except:
        print("❌ mpremote not found. Installing...")
        run_command("pip install mpremote")

    firmware_dir = "firmware/micropython"
    if not os.path.exists(firmware_dir):
        print(f"❌ Firmware directory not found: {firmware_dir}")
        sys.exit(1)

    print(f"📂 Preparing to upload files from {firmware_dir}...")
    
    # Simple strategy: Sync the whole directory
    # We use mpremote fs cp -r
    print("⏳ Syncing files to Pico/RP2350... (This may take a few seconds)")
    
    # Change to firmware dir to make paths relative on the device
    original_cwd = os.getcwd()
    os.chdir(firmware_dir)
    
    try:
        # Upload all files and folders recursively
        # . refers to everything in firmware/micropython
        run_command("mpremote fs cp -r . :")
        print("✅ Files uploaded successfully!")
        
        print("🔄 Resetting device...")
        run_command("mpremote reset")
        print("🎉 Done! Your PicoPass is now running the latest firmware.")
    finally:
        os.chdir(original_cwd)

if __name__ == "__main__":
    deploy()
