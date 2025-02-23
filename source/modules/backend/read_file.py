import pandas as pd

class Reader:
    def __init__(self, file) -> None:
        self.file = file
        self.engine = 'openpyxl'
        
    def get_data_file(self):
        if isinstance(self.file, str):
            df = pd.read_excel(self.file, engine=self.engine)
        else:
            df = pd.read_excel(self.file, engine=self.engine)
        return df