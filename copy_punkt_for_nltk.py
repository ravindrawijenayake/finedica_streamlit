import shutil
import os

# Define source and destination paths
src = os.path.join('nltk_data', 'tokenizers', 'punkt', 'english.pickle')
dst_dir = os.path.join('nltk_data', 'tokenizers', 'punkt_tab', 'english')
os.makedirs(dst_dir, exist_ok=True)
dst = os.path.join(dst_dir, 'english.pickle')

# Copy the file
shutil.copyfile(src, dst)
print(f"Copied {src} to {dst}")
