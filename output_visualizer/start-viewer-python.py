import os
import sys
import webview

# Determine the current directory whether running as script or bundled exe
if getattr(sys, 'frozen', False):
    # Running as PyInstaller executable
    base_path = os.path.dirname(sys.executable)
else:
    # Running as normal script
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

# Force backend on Linux and disable debug mode
if sys.platform.startswith("linux"):
    webview.start(maximize, window, gui='gtk', debug=False)
else:
    webview.start(maximize, window)
