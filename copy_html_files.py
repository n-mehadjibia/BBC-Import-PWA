# IMPORTS ==========================================================
import pandas as pd
import os
import shutil

# CONSTS ==========================================================
PATH_TO_MACROS = '/Users/macbook/Desktop/Import PWA/sample final/Test room/import.csv'
MACROS_CSV_SEP = ','

# IMPORT CSV FILES ==========================================================
macros_df = pd.read_csv(PATH_TO_MACROS, sep=MACROS_CSV_SEP)

# FUNCTIONS ==========================================================
def copy_html_files(file_paths, destination_folder):
    for file_path in file_paths:
        # Ensure the file is an HTML file
        if file_path.endswith('.html'):
            # Get the directory structure of the file path
            relative_path = os.path.relpath(file_path, start=os.path.commonpath(file_paths))
            # Create the full destination path
            dest_path = os.path.join(destination_folder, relative_path)
            # Create any necessary directories in the destination path
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            # Copy the file to the destination path
            shutil.copy2(file_path, dest_path)
            print(f"Copied {file_path} to {dest_path}")

# ===============================================================================
# ============================== PROCESSING =====================================
# ===============================================================================

html_files = macros_df['Answer__c'].to_list()

destination_folder = '/Users/macbook/Desktop/Import PWA/sample final/Test room'

copy_html_files(html_files, destination_folder)