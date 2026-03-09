#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from ui.app import App

def main():
    app = App(sys.argv)
    if "--new" in sys.argv:
        app.new_postit()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
