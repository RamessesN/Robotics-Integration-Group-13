import os
import random
import shutil

# Original Folder
images_dir = "../dataset/mouse/train/images"
labels_dir = "../dataset/mouse/train/labels"

# Combined Folder
images_new_dir = "/Users/stanley/Downloads/images"
labels_new_dir = "/Users/stanley/Downloads/labels"

# Get the name of the file
images_files = {os.path.splitext(f)[0]: f for f in os.listdir(images_dir) if os.path.isfile(os.path.join(images_dir, f))}
labels_files = {os.path.splitext(f)[0]: f for f in os.listdir(labels_dir) if os.path.isfile(os.path.join(labels_dir, f))}

# Compare the name of img and label
common_files = list(set(images_files.keys()) & set(labels_files.keys()))

sample_files = random.sample(common_files, min(300, len(common_files)))

for name in sample_files:
    shutil.copy(os.path.join(images_dir, images_files[name]), os.path.join(images_new_dir, images_files[name]))
    shutil.copy(os.path.join(labels_dir, labels_files[name]), os.path.join(labels_new_dir, labels_files[name]))