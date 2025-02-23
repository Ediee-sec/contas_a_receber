from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[3]))
from source.modules.backend.read_file import Reader
import pandas as pd

class Transformer:
    def __init__(self, file) -> None:
        self.df = Reader(file).get_data_file()
    
    def remove_all_nans(self):
        self.df = self.df.dropna(how='all')
        return self.df
    
    def remove_unnecessary_columns(self):
        self.df = self.df[['Unnamed: 0', 'Unnamed: 3']]
        return self.df
    
    def rename_columns(self):
        self.df = self.df.rename(columns={'Unnamed: 0': 'Nome', 'Unnamed: 3': 'Celular'})
        return self.df
    
    def remove_unnecessary_rows(self):
        self.df = self.df[~self.df['Nome'].str.contains('Nome|Fone Cel', case=False, na=False)]
        return self.df
    
    def remove_leading_zeros(self):
        self.df['Celular'] = self.df['Celular'].astype(str).str.lstrip('0')
        return self.df
    
    def create_validation_column(self):
        def validation(number):
            if len(number) == 11 and number.isdigit():
                return 'OK'
            else:
                return 'NOK'
            
        self.df['Validação'] = self.df['Celular'].apply(validation)
        return self.df
    
    def transform_dataframe(self):
        self.remove_all_nans()
        self.remove_unnecessary_columns()
        self.rename_columns()
        self.remove_unnecessary_rows()
        self.remove_leading_zeros()
        self.create_validation_column()
        
        return self.df
        