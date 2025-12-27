#!/usr/bin/env python3
"""
Rufus AI Robot - Main Entry Point
Run this to start Rufus!
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run Rufus
from rufus import main

if __name__ == "__main__":
    main()
