import os
import argparse

def remove_empty_and_specific_file_dirs(root_dir, specific_file_name, check_only=False):
    directories_to_remove = []
    
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        # Remove empty directories
        if not any((dirnames, filenames)):
            directories_to_remove.append(dirpath)
        # Remove directories with exactly one specific file
        elif len(filenames) == 1 and filenames[0] == specific_file_name:
            directories_to_remove.append(dirpath)

    if check_only:
        if directories_to_remove:
            print("Directories to be removed:")
            for directory in directories_to_remove:
                print(directory)
        else:
            print("No directories to be removed.")
    else:
        for directory in directories_to_remove:
            print(f"Removing directory: {directory}")
            check_file = os.path.join(directory,specific_file_name)
            if os.path.exists(check_file):
                print(f"Removing file: {specific_file_name}")
                os.remove(check_file)
            os.rmdir(directory)

def main():
    parser = argparse.ArgumentParser(description='Remove empty directories and directories with only one specific file.')
    parser.add_argument('directory', metavar='DIRECTORY', type=str, help='Path to the directory to clean up')
    parser.add_argument('--check', action='store_true', help='Only list directories to be removed without deleting them')
    parser.add_argument('--file', type=str, required=True, help='Name of the specific file to check')

    args = parser.parse_args()
    directory_to_clean = args.directory
    check_only = args.check
    specific_file_name = args.file
    
    if not os.path.isdir(directory_to_clean):
        print(f"Error: {directory_to_clean} is not a valid directory.")
        return
    
    remove_empty_and_specific_file_dirs(directory_to_clean, specific_file_name, check_only)

if __name__ == "__main__":
    main()

