import os
import sys
import webview

# Determine the current directory whether running as script or bundled exe
if getattr(sys, 'frozen', False):
    # If bundled by PyInstaller, sys._MEIPASS is a temp folder where files are extracted
    base_path = sys._MEIPASS
else:
    # If running as plain script, use the script's directory
    base_path = os.path.dirname(os.path.abspath(__file__))

# Path to the frontend folder relative to this file/executable
index_file = os.path.join(base_path, "index.html")
print(index_file)

# Create a window loading the local index.html
window = webview.create_window(
    title="Candidate requirements viewer",
    url=f"file://{index_file}",
    width=1000,
    height=800,
    resizable=True
)

def maximize(window):
    window.maximize()

webview.start(maximize, window)
