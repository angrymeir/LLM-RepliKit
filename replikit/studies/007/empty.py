import os
import sys

def find_empty_files(directory):
    """Find and list all empty files in the specified directory and its subdirectories. used for debugging."""
    if not os.path.isdir(directory):
        print(f"Error: '{directory}' is not a valid directory.")
        return

    print(f"Scanning '{directory}' for empty files...\n")

    empty_files = []
    for root, _, files in os.walk(directory):
        for filename in files:
            file_path = os.path.join(root, filename)
            if os.path.isfile(file_path) and os.path.getsize(file_path) == 0:
                empty_files.append(file_path)

    if empty_files:
        print("Empty files found:")
        for path in empty_files:
            print(path)
    else:
        print("No empty files found.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python find_empty_files.py <directory_path>")
    else:
        find_empty_files(sys.argv[1])
