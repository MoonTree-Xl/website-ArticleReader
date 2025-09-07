import streamlit as st
from utils_preview import csv_loader,show_data

# 将页面设置为宽屏
st.set_page_config(layout="wide")
# 创建侧边栏
with st.sidebar:
    # 文件上传入口
    file_csv_input = st.file_uploader('请上传CSV文件',type = ['CSV','csv'])
# 创建dataframe
if file_csv_input is not None:
    if 'df_article' not in st.session_state:
        st.session_state['df_article'] = csv_loader(file_csv_input)
# 创建索引列表
col1,col2 = st.columns(2)
with col1:
    index_list = []
    if file_csv_input is not None:
        for i in st.session_state['df_article'].index:
            index_list.append(i)
    # 创建单选菜单
    select_article_input = st.selectbox('所要查询的文章：',index_list,index=None)
    check_info_input = st.checkbox('展示信息')
with col2:
    st.markdown('# <center>🌳 数据库展示页面 🌳<center>',unsafe_allow_html=True)
# 展示信息
if file_csv_input and check_info_input:
    result_text = show_data(st.session_state['df_article'],select_article_input)
    text_show = st.empty()
    text_show.markdown(result_text)
# 重置df
if not file_csv_input:
    if 'df_article' in st.session_state:
        del st.seesion_state.df_article
    if 'df_article' not in se.session_state:
        pass
