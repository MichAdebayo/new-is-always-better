from sklearn.base import BaseEstimator, TransformerMixin

# Custom transformer pour supprimer des colonnes
class ColumnDropper(BaseEstimator, TransformerMixin):
    def __init__(self, columns_to_drop):
        self.columns_to_drop = columns_to_drop

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X.drop(columns=self.columns_to_drop)
     
def get_year(date_obj) -> int :
    date_str = str(date_obj)
    tab = date_str.split('/')
    if len(tab)==0 :
        return 0
    
    year_part = str(tab[-1])
    if year_part.isdigit() :
        return int(year_part)
    
    return 0

def get_minutes(period) -> int:  
    period_str = str(period)
    tab = period_str.split('h')
    if len(tab) ==0 :
        return 0
        
    total = 0
    for content in tab : 
        number = 0
        is_minutes=False
        if content.find('min') :
            is_minutes = True
            number = content.replace("min", "").strip()
     
        if number.isdigit() :
            number = int(number)
            if not is_minutes :
                number *= 60

            total+=number

    return total

def get_number(spaced_num) -> int:
    spaced_num = str(spaced_num)
    number = spaced_num.replace('$', '')
    number = number.replace(' ', '')
    if not number.isdigit() :
        return 0
    
    return int(number)

import pandas as pd

def get_year_tab(date_columns : pd.DataFrame):
    return date_columns.applymap(get_year).to_numpy()

def get_minutes_tab(date_columns : pd.DataFrame):
    return date_columns.applymap(get_minutes).to_numpy()

def get_number_tab(number_columns : pd.DataFrame):
    return number_columns.applymap(get_number).to_numpy()
