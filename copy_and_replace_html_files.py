import os
import re
import pandas as pd

def copy_and_replace(csv_path, source_folder, destination_folder):
    # Create the destination folder if it doesn't exist
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    
    # Read the CSV file using pandas
    df = pd.read_csv(csv_path)
    
    for index, row in df.iterrows():
        html_file_path = row['Answer__c']
        source_path = os.path.join(source_folder, html_file_path)
        destination_path = os.path.join(destination_folder, html_file_path)
        
        # Create the directory structure in the destination folder
        destination_dir = os.path.dirname(destination_path)
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)
        
        # Read the HTML file, replace '/n/n' with '<br/>', and write to the destination path
        with open(source_path, 'r', encoding='utf-8') as file:
            content = file.read().replace('\n\n', '<br/>')

        # Regular expression to find [Text of link] (link)
        pattern = re.compile(r'\[([^\]]+)\]\s*\((https?://[^\)]+)\)')

        # Replace with <a href="link">Text of link</a>
        content = pattern.sub(r'[<a href="\2">\1</a>]', content)

        # Regular expression to find **bold text** and replace with <b>bold text</b>
        bold_pattern = re.compile(r'\*\*(.*?)\*\*')
        content = bold_pattern.sub(r'<b>\1</b>', content)
        
        with open(destination_path, 'w', encoding='utf-8') as file:
            file.write(content)

# Example usage
csv_path = '/Users/macbook/Desktop/Import PWA/sample final/For PP/1/Email/import_1_Email.csv'  # Path to the CSV file
source_folder = ''  # Folder containing the original HTML files
destination_folder = '/Users/macbook/Desktop/Import PWA/sample final/For PP/1/Email'  # Folder to copy the HTML files to

copy_and_replace(csv_path, source_folder, destination_folder)