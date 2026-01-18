#!/bin/bash

# Forex Engine - Auto Setup Script for Ubuntu/Debian VPS
# Run this after connecting to your fresh VPS

echo "================================="
echo "Forex Engine - VPS Setup Script"
echo "================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (or use sudo)"
    exit 1
fi

# Update system
echo "Step 1: Updating system..."
apt update && apt upgrade -y

# Install Python and dependencies
echo "Step 2: Installing Python..."
apt install python3 python3-pip git sqlite3 -y

# Create directory
echo "Step 3: Creating application directory..."
mkdir -p /opt/forex-engine
cd /opt/forex-engine

# Install Python packages
echo "Step 4: Installing Python dependencies..."
cat > requirements.txt << 'EOF'
requests
schedule
colorama
pandas
python-dotenv
EOF

pip3 install -r requirements.txt

echo ""
echo "Step 5: Now you need to upload your code files"
echo "From your Windows machine, run:"
echo ""
echo "  scp -r C:\\Users\\rajpa\\Desktop\\Engine\\* root@YOUR_SERVER_IP:/opt/forex-engine/"
echo ""
read -p "Press Enter after you've uploaded your files..."

# Create systemd service
echo "Step 6: Creating systemd service..."
cat > /etc/systemd/system/forex-engine.service << 'EOF'
[Unit]
Description=Forex AI Decision Engine
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/forex-engine
ExecStart=/usr/bin/python3 /opt/forex-engine/main.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/forex-engine.log
StandardError=append:/var/log/forex-engine-error.log

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
echo "Step 7: Configuring service..."
systemctl daemon-reload

# Enable service
systemctl enable forex-engine

echo ""
echo "================================="
echo "Setup Complete!"
echo "================================="
echo ""
echo "To start the engine:"
echo "  systemctl start forex-engine"
echo ""
echo "To check status:"
echo "  systemctl status forex-engine"
echo ""
echo "To view logs:"
echo "  tail -f /var/log/forex-engine.log"
echo ""
echo "To stop:"
echo "  systemctl stop forex-engine"
echo ""
echo "To restart:"
echo "  systemctl restart forex-engine"
echo ""
