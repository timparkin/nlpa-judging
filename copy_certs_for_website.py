import os
import shutil

# paths
src_root = "photo_certs_test"
dst_root = "photo_certs_for_website"

# make sure destination exists
os.makedirs(dst_root, exist_ok=True)

# walk through the source directory
for user_id in os.listdir(src_root):
    src_user_dir = os.path.join(src_root, user_id)
    dst_user_dir = os.path.join(dst_root, user_id)

    # only handle subdirectories
    if os.path.isdir(src_user_dir):
        os.makedirs(dst_user_dir, exist_ok=True)

        # check files in this subdirectory
        for fname in os.listdir(src_user_dir):
            if "crop" in fname.lower():  # case-insensitive match
                src_file = os.path.join(src_user_dir, fname)
                dst_file = os.path.join(dst_user_dir, fname)
                shutil.copy2(src_file, dst_file)  # copy with metadata
