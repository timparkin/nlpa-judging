import os
import shutil
import argparse
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description='Extract files newer than a specified date.')
    parser.add_argument('source', help='Source directory to scan for files')
    parser.add_argument('destination', help='Destination directory to copy files')
    parser.add_argument('--date', required=True, help='Date in YYYY-MM-DD format to compare against')
    parser.add_argument('--check', action='store_true', help='Print files and dates to be extracted')
    
    args = parser.parse_args()
    
    try:
        compare_date = datetime.strptime(args.date, '%Y-%m-%d')
    except ValueError:
        print('Error: Date must be in YYYY-MM-DD format.')
        return
    
    if not os.path.exists(args.source):
        print(f'Error: Source directory "{args.source}" does not exist.')
        return
    
    if not os.path.exists(args.destination):
        print(f'Error: Destination directory "{args.destination}" does not exist.')
        return
    
    for root, _, files in os.walk(args.source):
        for file in files:
            file_path = os.path.join(root, file)
            modification_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            
            if modification_time > compare_date:
                if args.check:
                    print(f'File: {file_path}, Modified: {modification_time}')
                else:
                    relative_path = os.path.relpath(file_path, args.source)
                    destination_path = os.path.join(args.destination, relative_path)
                    
                    # Create directories if they don't exist
                    os.makedirs(os.path.dirname(destination_path), exist_ok=True)
                    
                    # Copy the file
                    shutil.copy2(file_path, destination_path)
                    print(f'Copied {file_path} to {destination_path}')

if __name__ == '__main__':
    main()

