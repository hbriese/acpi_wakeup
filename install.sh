#!/bin/sh

INSTALL_DIR="/opt/acpi_wakeup"
CONFIG="acpi_wakeup.conf"
CONFIG_DIR="/etc"
SERVICE="acpi_wakeup.service"
SERVICE_DIR="/etc/systemd/system"

if [ $(id -u) != 0 ]; then
    echo "root required!"
    exit
fi

if ! pidof systemd 2>&1 1>/dev/null; then
    echo "Systemd is required!"
    exit
fi

echo "Installing in $INSTALL_DIR"
systemctl stop "$SERVICE" >/dev/null 2>&1

mkdir -p "$INSTALL_DIR" >/dev/null 2>&1
set -e

cd "$(dirname "$0")"

cp -f ./acpi_wakeup.py ./LICENSE ./README.md ./install.sh "$INSTALL_DIR"
cp -f ./$SERVICE "$SERVICE_DIR"

if [ ! -f "$CONFIG_DIR/$CONFIG" ]; then
    echo "Copying config to $CONFIG_DIR/$CONFIG"
    cp ./$CONFIG "$CONFIG_DIR/$CONFIG"
else
    echo "Config already exists at $CONFIG_DIR/$CONFIG"
fi

echo "Building virtual env"
cd "$INSTALL_DIR"
python3 -m venv venv
. ./venv/bin/activate

systemctl daemon-reload
systemctl enable "$SERVICE"
systemctl start "$SERVICE"

echo "Success"

