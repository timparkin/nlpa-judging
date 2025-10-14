import os
import argparse

def remove_empty_files(root_dir, check_only=False):
    empty_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            try:
                if os.path.getsize(file_path) == 0:
                    if check_only:
                        empty_files.append(file_path)
                    else:
                        print(f"Removing empty file: {file_path}")
                        os.remove(file_path)
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")

    if check_only:
        if empty_files:
            print("Empty files found:")
            for file_path in empty_files:
                print(file_path)
        else:
            print("No empty files found.")

def main():
    parser = argparse.ArgumentParser(description='Remove or list all empty files recursively from a directory.')
    parser.add_argument('directory', metavar='DIRECTORY', type=str, help='Path to the directory to clean up')
    parser.add_argument('--check', action='store_true', help='Only list empty files without deleting them')

    args = parser.parse_args()
    directory_to_clean = args.directory
    check_only = args.check
    
    if not os.path.isdir(directory_to_clean):
        print(f"Error: {directory_to_clean} is not a valid directory.")
        return
    
    remove_empty_files(directory_to_clean, check_only)

if __name__ == "__main__":
    main()

