# IMPORTS ==========================================================
import pandas as pd
import os

# CONSTS ==========================================================
PATH_TO_EXCLUDED_PRODUCTS = 'Inputs/Category1 to delete.csv'
EXCLUDED_PRODUCTS_CSV_SEP = ','
PATH_PRODUCT_MAPPING = 'Inputs/Product Mapping.csv'
PRODUCT_MAPPING_CSV_SEP = ','
PATH_CSAT_TAGS = 'Inputs/CSAT tags.csv'
CSAT_TAGS_CSV_SEP = ','
PATH_TO_DATA_CATEGORIES = 'Inputs/data_categories.csv'
DATA_CATEGORIES_CSV_SEP = ','
#PATH_TO_MACROS = 'Inputs/export_data_1.csv'
PATH_TO_MACROS = 'Inputs/export_data_2.csv'
MACROS_CSV_SEP = ';'

RECORD_TYPE_ID = '012AP000001WGCL'

DELETE_MOCROS = True
#EXPORT_NUMBER = 1
EXPORT_NUMBER = 2

#CHANNEL = "Email"
CHANNEL = "Social media"

# IMPORT CSV FILES ==========================================================
excluded_products_df = pd.read_csv(PATH_TO_EXCLUDED_PRODUCTS, sep=EXCLUDED_PRODUCTS_CSV_SEP)
product_mapping_df = pd.read_csv(PATH_PRODUCT_MAPPING, sep=PRODUCT_MAPPING_CSV_SEP)
csat_tags_df = pd.read_csv(PATH_CSAT_TAGS, sep=CSAT_TAGS_CSV_SEP)
data_categories_df = pd.read_csv(PATH_TO_DATA_CATEGORIES, sep=DATA_CATEGORIES_CSV_SEP)
macros_df = pd.read_csv(PATH_TO_MACROS, sep=MACROS_CSV_SEP)

data_categories_df = data_categories_df.fillna('')
macros_df = macros_df.fillna('')

excluded_products = excluded_products_df['Category1__c'].tolist()
csat_tags = csat_tags_df['Tag__c'].tolist()

# FUNCTIONS ==========================================================

def format_language(language):
    if language:
        if '_' in language:
            language_split = language.split('_')
            language = language_split[0].lower() + '_' + language_split[1].upper()
        elif '-' in language:
            language_split = language.split('-')
            language = language_split[0].lower() + '_' + language_split[1].upper()
        else:
            language = language.lower()
        
        # Languages with different Salesforce code
        if language == 'pt':
            language = 'pt_PT'
        elif language == 'nl':
            language = 'nl_NL'
        elif language == 'sr':
            language = 'sh'
    
    return language

def get_csat_tag(tags):
    tags = str(tags)
    for tag in csat_tags:
        if tag in tags:
            return tag
    return ''

def map_zendesk_category1(category1):
    mapping = product_mapping_df[product_mapping_df['Zendesk'] == category1]
    if not mapping.empty:
        return mapping.iloc[0]['Salesforce']
    return category1

def keep_macro(macro):
    if macro['Category1__c'] in excluded_products:
        return False
    return True

def extract_zendesk_id(answer_path):
    start = answer_path.rfind('/') + 1
    end = answer_path.find('.html')
    # Extract the ID using slicing
    id_value = answer_path[start:end]
    return id_value

def map_data_category(category1, category2, category3, category4, category5):
    def add_spaces_around_char(input_string, char):
        # Replace '*' with ' * ' ensuring spaces around it
        output_string = input_string.replace(char, f' {char} ')
        # Replace multiple spaces with single space
        output_string = ' '.join(output_string.split())
        return output_string
    
    result = { 'is_category_changed': False, 'category_name': '', 'mapping': {} }
    # map product
    category1 = map_zendesk_category1(category1)

    # Make sure a space exists befor and after '&' chacarter
    category2 = add_spaces_around_char(category2, '&')
    category3 = add_spaces_around_char(category3, '&')
    category4 = add_spaces_around_char(category4, '&')
    category5 = add_spaces_around_char(category5, '&')

    data_category_mapping = data_categories_df[
        (data_categories_df['label1'].str.lower() == category1.lower()) &
        (data_categories_df['label2'].str.lower() == category2.lower()) &
        (data_categories_df['label3'].str.lower() == category3.lower()) &
        (data_categories_df['label4'].str.lower() == category4.lower()) &
        (data_categories_df['label5'].str.lower() == category5.lower())
    ]

    if data_category_mapping.empty:
        result['is_category_changed'] = True
        data_category_mapping = data_categories_df[
            (data_categories_df['label1'].str.lower() == category1.lower()) &
            (data_categories_df['label2'].str.lower() == category2.lower()) &
            (data_categories_df['label3'].str.lower() == category3.lower()) &
            (data_categories_df['label4'].str.lower() == category4.lower()) &
            (data_categories_df['label5'].str.lower() == '')
        ]
    if data_category_mapping.empty:
        data_category_mapping = data_categories_df[
            (data_categories_df['label1'].str.lower() == category1.lower()) &
            (data_categories_df['label2'].str.lower() == category2.lower()) &
            (data_categories_df['label3'].str.lower() == category3.lower()) &
            (data_categories_df['label4'].str.lower() == '') &
            (data_categories_df['label5'].str.lower() == '')
        ]  
    if data_category_mapping.empty:
        data_category_mapping = data_categories_df[
            (data_categories_df['label1'].str.lower() == category1.lower()) &
            (data_categories_df['label2'].str.lower() == category2.lower()) &
            (data_categories_df['label3'].str.lower() == '') &
            (data_categories_df['label4'].str.lower() == '') &
            (data_categories_df['label5'].str.lower() == '')
        ]
    if data_category_mapping.empty:
        data_category_mapping = data_categories_df[
            (data_categories_df['label1'].str.lower() == category1.lower()) &
            (data_categories_df['label2'].str.lower() == '') &
            (data_categories_df['label3'].str.lower() == '') &
            (data_categories_df['label4'].str.lower() == '') &
            (data_categories_df['label5'].str.lower() == '')
        ]
    if not data_category_mapping.empty:
        mapping = data_category_mapping.iloc[0]
        result['mapping'] = mapping
        if mapping['name5']:
            result['category_name'] = mapping['name5']
        elif mapping['name4']:
            result['category_name'] = mapping['name4']
        elif mapping['name3']:
            result['category_name'] = mapping['name3']
        elif mapping['name2']:
            result['category_name'] = mapping['name2']
        elif mapping['name1']:
            result['category_name'] = mapping['name1']

    return result

# ===============================================================================
# ============================== PROCESSING =====================================
# ===============================================================================

columns_macro =  ['IsMasterLanguage', 'Title', 'Language', 'Answer__c', 'RecordTypeId', 'Permission__c', 'Tags__c', 'Category1__c', 'Category2__c', 'Category3__c', 'Category4__c', 'Category5__c']
kept_macros = pd.DataFrame(columns = columns_macro)
macros_to_delete = pd.DataFrame(columns = columns_macro)
changed_category_macros = pd.DataFrame(columns = columns_macro)

columns_pwa = ['IsMasterLanguage', 'Title', 'Language', 'Answer__c', 'RecordTypeId', 'CSATTag2__c', 'datacategorygroup.PreWrittenAnswer', 'ZendeskId__c', "Channel__c", "Product__c", "Category__c", "SubCategory1__c", "SubCategory2__c", "SubCategory3__c"]
pwa_df = pd.DataFrame(columns = columns_pwa)

for index, row in macros_df.iterrows():
    if keep_macro(row):
        kept_macros.loc[len(kept_macros)] = row

        pwa_row = {}
        pwa_row['IsMasterLanguage'] = row['IsMasterLanguage']
        pwa_row['Channel__c'] = CHANNEL
        if CHANNEL == "Social media":
            pwa_row['Title'] = 'SM - ' + row['Title']
        else:
            pwa_row['Title'] = row['Title']
        pwa_row['Language'] = format_language(row['Language'])
        pwa_row['Answer__c'] = row['Answer__c']
        pwa_row['RecordTypeId'] = RECORD_TYPE_ID
        pwa_row['CSATTag2__c'] = get_csat_tag(row['Tags__c'])

        data_category_mapping_result = map_data_category(
            row['Category1__c'],
            row['Category2__c'],
            row['Category3__c'],
            row['Category4__c'],
            row['Category5__c']
        )
        if  row['IsMasterLanguage']:
            pwa_row['datacategorygroup.PreWrittenAnswer'] = data_category_mapping_result['category_name']
            if data_category_mapping_result['is_category_changed']:
                changed_category_macros.loc[len(changed_category_macros)] = row

        # Fill category fields
        if data_category_mapping_result['mapping'] is not None and len(data_category_mapping_result['mapping']) > 0:
            pwa_row['Product__c'] = data_category_mapping_result['mapping']['label1']
            pwa_row['Category__c'] = data_category_mapping_result['mapping']['label2']
            pwa_row['SubCategory1__c'] = data_category_mapping_result['mapping']['label3']
            pwa_row['SubCategory2__c'] = data_category_mapping_result['mapping']['label4']
            pwa_row['SubCategory3__c'] = data_category_mapping_result['mapping']['label5']

        pwa_row['ZendeskId__c'] = extract_zendesk_id(row['Answer__c'])

        # Add en_US
        if  pwa_row['Language'] == 'en_GB':
            pwa_row['Language'] = 'en_US'
            pwa_df.loc[len(pwa_df)] = pwa_row
            pwa_row['Language'] = 'en_GB'
            pwa_row['datacategorygroup.PreWrittenAnswer'] = ''
            pwa_row['IsMasterLanguage'] = 0
            pwa_df.loc[len(pwa_df)] = pwa_row
        else :
            pwa_df.loc[len(pwa_df)] = pwa_row
    else:
        macros_to_delete.loc[len(macros_to_delete)] = row

pwa_df = pwa_df.sort_values(by=['ZendeskId__c', 'IsMasterLanguage'], ascending=[True, False])

pwa_df.to_csv(f'Outputs/import_{EXPORT_NUMBER}_{CHANNEL}.csv',index=False)
kept_macros.to_csv(f'Outputs/kept_macros_{EXPORT_NUMBER}_{CHANNEL}.csv',index=False)
macros_to_delete.to_csv(f'Outputs/macros_to_delete_{EXPORT_NUMBER}_{CHANNEL}.csv',index=False)
changed_category_macros.to_csv(f'Outputs/changed_category_macros_{EXPORT_NUMBER}_{CHANNEL}.csv',index=False)

# delete macros html files
if DELETE_MOCROS:
    macros_deleted = pd.DataFrame(columns=columns_macro)
    mocros_not_deleted = pd.DataFrame(columns=columns_macro)
    for index, row in macros_to_delete.iterrows():
        file_path = row['Answer__c']
        try:
            os.remove(file_path)
            macros_deleted.loc[len(macros_deleted)] = row
            # print(f"File {file_path} has been deleted successfully.")
        except Exception as e:
            mocros_not_deleted.loc[len(mocros_not_deleted)] = row
            # print(f"An error occurred: {e}")
    macros_deleted.to_csv(f'Outputs/macros_deleted_{EXPORT_NUMBER}_{CHANNEL}.csv',index=False)
    mocros_not_deleted.to_csv(f'Outputs/mocros_not_deleted_{EXPORT_NUMBER}_{CHANNEL}.csv',index=False)
