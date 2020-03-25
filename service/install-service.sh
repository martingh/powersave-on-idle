#!/bin/sh

# customization
INSTALL_PREFIX=/usr/local
SYSCONF_DIR=/etc
SERVICE_DIR=/etc/systemd/system

BIN_DIR="$INSTALL_PREFIX/bin"
LIB_DIR="$INSTALL_PREFIX/lib"
PYTHON_LIB_DIR="$LIB_DIR/python"

SERVICE_SRC_DIR=$(dirname $0)
PYTHON_SRC_DIR="$SERVICE_SRC_DIR/../python"

set -xe
install "$SERVICE_SRC_DIR/systemd/powersave-on-idle.service" "$SERVICE_DIR"
install "$SERVICE_SRC_DIR/powersave-on-idle.sh" "$BIN_DIR"
install -d "$SYSCONF_DIR/powersave-on-idle"
install "$SERVICE_SRC_DIR/powersave-on-idle.conf" "$SYSCONF_DIR/powersave-on-idle"
install "$PYTHON_SRC_DIR/idle.py" "$BIN_DIR"
install -d "$PYTHON_LIB_DIR"
install "$PYTHON_SRC_DIR/diskstats.py" "$PYTHON_SRC_DIR/pnd.py" "$PYTHON_LIB_DIR"
