#!/bin/bash
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
if [ -f "$script_dir/lwvpn" ]; then
    echo "lwvpn is compiled, skipping making..."
else
    echo "lwvpn is not compiled, making..."
    make
fi
sudo python main.py

