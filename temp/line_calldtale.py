import dtale
import pandas as pd

if __name__ == '__main__':
    file = 'ThongchanThananate_LineAssignment.xlsx'
    df = pd.read_excel(file, sheet_name='TrafficChannelFixed')
    dtale.show(df)