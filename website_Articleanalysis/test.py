import pandas as pd

df = pd.read_csv('C:\\Users\\lxlzl\\Desktop\\test\\新建文件夹\\streamlit_download.csv')
df.rename(columns={'Unnamed: 0':'标题'},inplace=True)
df.set_index('标题',inplace=True)
print(df.index)
df_o = df.copy()
df.rename(index={'善':'全球最低税的倒逼机制'},inplace=True)
print(df.index)
print(df_o.index)