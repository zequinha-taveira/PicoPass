#!/bin/bash

# Setup script for PicoPass development environment (Linux/WSL)

echo "🚀 Setting up PicoPass development environment..."

# 1. Install Rust
if ! command -v cargo &> /dev/null; then
    echo "🦀 Installing Rust..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source "$HOME/.cargo/env"
else
    echo "✅ Rust already installed"
fi

# 2. Install Node.js via NVM
if ! command -v nvm &> /dev/null; then
    echo "📦 Installing NVM..."
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
else
    echo "✅ NVM already installed"
fi

if ! command -v node &> /dev/null; then
    echo "🟢 Installing Node.js 18..."
    nvm install 18
    nvm use 18
else
    echo "✅ Node.js already installed"
fi

# 3. Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip3 install pyserial

echo "✨ Environment setup complete!"
echo "Please run: source ~/.bashrc"
