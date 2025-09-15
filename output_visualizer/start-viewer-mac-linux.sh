#!/bin/sh

# Detect OS
OS=$(uname)

case "$OS" in
  "Linux")
    BINARY="webviewer-linux"
    ;;
  "Darwin")
    BINARY="webviewer-mac"
    ;;
  *)
    echo "Unsupported OS: $OS"
    exit 1
    ;;
esac

# Make binary executable
chmod +x "$BINARY"

# Run the binary
./"$BINARY"
