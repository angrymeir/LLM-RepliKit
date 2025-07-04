#!/bin/bash

echo "Generating modified scripts..."
python modifier.py ChatGPT_on_binary_vulner_detection.py

SCRIPTS_DIR="scripts"

if [ ! -d "$SCRIPTS_DIR" ]; then
    echo "Error: '$SCRIPTS_DIR' directory does not exist."
    exit 1
fi

for script in "$SCRIPTS_DIR"/*.py; do
    if [ -f "$script" ]; then
        echo "Running $script..."
        python "$script"
        echo "Finished $script"
        echo "---------------------"
    else
        echo "No Python scripts found in $SCRIPTS_DIR"
        exit 1
    fi
done
