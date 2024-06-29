# Imports ==========================================================
import pandas as pd

# Consts ==========================================================
PATH_TO_EXCLUDED_PRODUCTS = '/Users/macbook/Desktop/Import PWA/Scripts/Inputs/Category1 to delete.csv'
EXCLUDED_PRODUCTS_CSV_SEP = ','
PATH_TO_DATA_CATEGORIES = 'data_categories.csv'
DATA_CATEGORIES_CSV_SEP = ','
PATH_TO_MACROS = '/Users/macbook/Desktop/Import PWA/Scripts/export_data_1.csv'
MACROS_CSV_SEP = ';'

# Import CSV Files ==========================================================
excluded_products_df = pd.read_csv(PATH_TO_EXCLUDED_PRODUCTS, sep=EXCLUDED_PRODUCTS_CSV_SEP)
data_categories_df = pd.read_csv(PATH_TO_DATA_CATEGORIES, sep=DATA_CATEGORIES_CSV_SEP)
macros_df = pd.read_csv(PATH_TO_MACROS, sep=MACROS_CSV_SEP)

excluded_products = excluded_products_df['Category1__c'].tolist()

# ===============================================================================

# Filter Macros 
kept_macros = macros_df[~macros_df['Category1__c'].isin(excluded_products)]

macros_to_delete = macros_df[macros_df['Category1__c'].isin(excluded_products)]

# Prepare PWA
columns = ['IsMasterLanguage', 'Title', 'Language', 'Answer__c', 'RecordTypeId', 'datacategorygroup.PreWrittenAnswer']

macros_to_delete.to_csv('test.csv',index=False)
