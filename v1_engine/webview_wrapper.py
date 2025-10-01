"""Simple webview wrapper for compatibility."""
import webview

def create_window(*args, **kwargs):
    return webview.create_window(*args, **kwargs)

def start():
    return webview.start()
