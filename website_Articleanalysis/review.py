import pandas as pd

df = pd.read_csv('C:\\Users\\lxlzl\\Desktop\\test\\新建文件夹\\streamlit_download.csv')
df.rename(columns={'Unnamed: 0':'标题'},inplace=True)
df.set_index('标题',inplace=True)
print(df.index,type(df.index))
for i in df.index:
    print(i,type(i))
for i in df.columns:
    print(i,type(i))

df_1 = pd.read_csv('temp_attachment.CSV')
print(df_1)