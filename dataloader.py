# %%
# data_loader.py
import pandas as pd
import numpy as np
import os

#folder_path = 'data/'
#os.chdir(folder_path)
asr_file='asr_th_vol6_11.xlsx'
asr_age_file='asr_th_vol6_11_agegroup.xlsx'
asr_region='all_region.xlsx'
surv_hr='surv_table_hr.xlsx'

# %%
def load_thai_asr_data(file_path=asr_file):
    """
    Load ASR cancer data from Excel file
    
    Args:
        file_path (str): Path to the Excel file
        
    Returns:
        pandas.DataFrame: Loaded and processed dataframe
    """
    try:
        df = pd.read_excel(file_path)
        df=df[['Population', 'Sex', 'Site', 'Year', 'ASR World']]
        df=df[df['Population']=='Thailand']
        df['Year'] = df['Year'].astype(str)
        return df
        
    except Exception as e:
        print(f"Error loading data: {e}")

# %%
def load_thai_asr_age_data(file_path=asr_age_file):
    """
    Load ASR cancer data by age group from Excel file
    
    Args:
        file_path (str): Path to the Excel file
    Returns:
        pandas.DataFrame: Loaded and processed dataframe
    """
    try:
        df = pd.read_excel(file_path)
        df['Year'] = df['Year'].astype(str)
        return df
    except Exception as e:
        print(f"Error loading data: {e}")


# %%
def get_dropdown_options(df):
    """
    Extract unique values for dropdown options
    
    Args:
        df (pandas.DataFrame): Input dataframe
        
    Returns:
        dict: Dictionary containing dropdown options
    """
    options = {}
    
    if 'Site' in df.columns:
        options['cancer_types'] = sorted(df['Site'].dropna().unique())
    
    if 'Sex' in df.columns:
        options['sex_options'] = sorted(df['Sex'].dropna().unique())

    if 'Age_Group' in df.columns:
        options['age_groups'] = sorted(df['Age_Group'].dropna().unique())


    if 'Year' in df.columns:
        options['years'] = sorted(df['Year'].dropna().unique())

    if 'healthregion' in df.columns:
        options['health_regions'] = sorted(df['healthregion'].dropna().unique())
    
    if 'Stage' in df.columns:
        options['stages'] = sorted(df['Stage'].dropna().unique())

    return options

def get_dropdown_options2(df):
    """
    Extract unique values for dropdown options
    
    Args:
        df (pandas.DataFrame): Input dataframe
        
    Returns:
        dict: Dictionary containing dropdown options
    """
    options = {}
    
    if 'cancer' in df.columns:
        options['cancer_types'] = sorted(df['cancer'].dropna().unique())
    
    if 'region' in df.columns:
        options['health_regions'] = sorted(df['region'].dropna().unique())
    
    if 'stage' in df.columns:
        options['stages'] = sorted(df['stage'].dropna().unique())

    return options

# %%
def load_region_data(file_path=asr_region):
    """
    Load ASR cancer data by region from Excel file
    
    Args:
        file_path (str): Path to the Excel file
    Returns:
        pandas.DataFrame: Loaded and processed dataframe
    """
    try:
        df = pd.read_excel(file_path)
        df=df[['healthregion', 'Sex', 'Site', 'ASR World']]
        df['healthregion'] = df['healthregion'].astype(str)
        return df
    except Exception as e:
        print(f"Error loading data: {e}")

def load_prov_data(folder=folder_path):
    prov_hr=pd.read_excel(os.path.join(folder, "provice_healthregion.xlsx"))
    prov_hr['provine_code']=prov_hr['provine_code'].astype(str)
    prov_hr['health_region']=prov_hr['health_region'].astype(str)       
    return prov_hr

def load_survival_data(file_path=surv_hr):
    """
    Load survival data from Excel file
    
    Args:
        file_path (str): Path to the Excel file
    Returns:

        pandas.DataFrame: Loaded and processed dataframe
    """
    try:
        df = pd.read_excel(file_path)
        #df=df[['healthregion', 'Site', 'Survival Rate']]
        df['region'] = df['region'].astype(str)
        return df
    except Exception as e:
        print(f"Error loading data: {e}")





