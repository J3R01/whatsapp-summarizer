#!/bin/bash
Xvfb :99 &  # virtual display
echo "Starting bot..."
python3 main.py
