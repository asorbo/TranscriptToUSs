package main

import (
	"fmt"
	"log"
	"net"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
)

func openBrowser(url string) error {
	var cmd *exec.Cmd

	switch runtime.GOOS {
	case "windows":
		cmd = exec.Command("rundll32", "url.dll,FileProtocolHandler", url)
	case "darwin":
		cmd = exec.Command("open", url)
	default:
		cmd = exec.Command("xdg-open", url)
	}

	// Start the browser process
	if err := cmd.Start(); err != nil {
		return err
	}

	// Wait for the browser process to exit
	return cmd.Wait()
}

func main() {
	// Get folder of the running binary
	exePath, err := os.Executable()
	if err != nil {
		log.Fatal(err)
	}
	basePath := filepath.Dir(exePath)

	// Serve static files from the folder
	fs := http.FileServer(http.Dir(basePath))
	http.Handle("/", fs)

	// Listen on port 0 to get a free port dynamically
	listener, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		log.Fatal(err)
	}
	defer listener.Close()

	actualPort := listener.Addr().(*net.TCPAddr).Port
	url := fmt.Sprintf("http://localhost:%d/index.html", actualPort)
	log.Println("Serving frontend at", url)
	log.Println("Close this terminal to stop this requirement viewer instance")

	openBrowser(url)

	// Start the server
	log.Fatal(http.Serve(listener, nil))
}
