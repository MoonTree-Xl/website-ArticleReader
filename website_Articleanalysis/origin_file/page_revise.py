import streamlit as st
from utils_preview import csv_loader,data_revise

# 将页面设置为宽屏
st.set_page_config(layout="wide")
# 初始化选单状态
if 'check' not in st.session_state: # “信息修改”勾选框
    st.session_state.check = False
if 'select' not in st.session_state: # “索引列表”单选列表
    st.session_state.select = None
# 定义回调函数
def reset_values(): # 功能是使“索引列表”取值回到“默认页”
    del st.session_state.select
    if 'select' not in st.session_state:
        st.session_state.select = '默认页'
# 创建侧边栏
with st.sidebar: # 文件上传侧边栏
    # 上传csv文件
    loader_csv_i = st.file_uploader('上传CSV文件：',type=['csv','CSV'])
    # 创建临时dataframe
    if loader_csv_i:
        if 'df_article' not in st.session_state:
            st.session_state.df_article = csv_loader(loader_csv_i)
        # 备份原dataframe
        if 'df_o' not in st.session_state:
            st.session_state.df_o = st.session_state.df_article.copy()
        # 创建过渡dataframe
        if 'temp_df' not in st.session_state:
            st.session_state.temp_df = None
    # 创建索引列表
    index_list = []
    if loader_csv_i: # 文件上传后，df_article会同步创建完成
        for i in st.session_state.df_article.index:
            index_list.append(i)
    # 创建单选菜单
    if loader_csv_i:
        select_index_i = st.selectbox('所要查询的文章',index_list,index=None,key='select')
    # 创建勾选框
    if loader_csv_i:
        check_revise_i = st.checkbox('修改信息',key='check')
    
# 初始化变量
if loader_csv_i and select_index_i and check_revise_i: # 文件、索引、勾选框均打开
    if 'initialized' not in st.session_state: # 初始化initial标识
        st.session_state.initialized = False
    if select_index_i: # 每更换一次索引，重置一次initial表示
        st.session_state.initialized = False
    if st.session_state.initialized == False:
        st.session_state.title_r = st.session_state['df_article'].文章标题[select_index_i]
        st.session_state.genre_r = st.session_state['df_article'].文章类型[select_index_i]
        st.session_state.journal_r_j = st.session_state['df_article'].刊物名称[select_index_i]
        st.session_state.journal_r_n = st.session_state['df_article'].发刊单位[select_index_i]
        st.session_state.department_r = st.session_state['df_article'].发文单位[select_index_i]
        st.session_state.proof_r = st.session_state['df_article'].发文字号[select_index_i]
        st.session_state.publication_time_r = st.session_state['df_article'].发文时间[select_index_i]
        st.session_state.author_r = st.session_state['df_article'].作者[select_index_i]
        st.session_state.abstract_r = st.session_state['df_article'].摘要[select_index_i]
        st.session_state.keyword_r = st.session_state['df_article'].关键词[select_index_i]
        st.session_state.topic_r = st.session_state['df_article'].话题[select_index_i]
        st.session_state.effective_r = st.session_state['df_article'].是否有效[select_index_i]
        st.session_state.attachment_r = st.session_state['df_article'].是否有附件[select_index_i]
        st.session_state.summary_r = st.session_state['df_article'].文章概览[select_index_i]
        st.session_state.editing = False # 编辑模式标识
        st.session_state.attribute_list = []
        st.session_state.revalue_list = []
        st.session_state.re_dict = {}
        st.session_state.initialized = True
# 调整模式表示
if loader_csv_i and select_index_i and check_revise_i: # 文件、索引、勾选框均打开
    st.session_state.editing = True # 进入编辑模式
    if select_index_i == '默认页':
        col1,col2,col3 = st.columns([1,3,1])
        with col2:
            st.title('数据库修改页⭐')
            st.write('Notice：')
            st.image('C:\\Users\\lxlzl\\Desktop\\test\\新建文件夹\\小猫.png')
        st.session_state.editing = False # 如果索引在“默认页”，关闭编辑模式
# 执行调整程序
if loader_csv_i and select_index_i and check_revise_i == True: # 文件、索引、勾选框均打开
    if st.session_state.editing == True:
        button_return_i = st.button('退出修改模式') # 如果“编辑模式”打开，则增加推出模式按钮
        if button_return_i: # 点击按钮后将索引值重置为“默认页”
            reset_values()
            st.rerun()
    # 若索引不在“默认页”，则基于文章类型进行操作
    if st.session_state['df_article'].文章类型[select_index_i] == '期刊论文':
        # 创建输入窗口
        title_r = st.text_input('文章标题：',value=st.session_state.title_r)
        genre_r = st.selectbox('文章类型：',['期刊论文','新闻报道','政府文件','其他文章'],index=0)
        journal_r_j = st.text_input('刊物名称：',value=st.session_state.journal_r_j)
        publication_time_r = st.text_input('发文时间：',value=st.session_state.publication_time_r)
        author_r = st.text_input('作者：',value=st.session_state.author_r)
        abstract_r = st.text_input('摘要：',value=st.session_state.abstract_r)
        keyword_r = st.text_input('关键词：',value=st.session_state.keyword_r)
        summary_r = st.text_input('文章概览：',value=st.session_state.summary_r)
        attribute_list = ['文章标题','文章类型','刊物名称','发文时间','作者','摘要','关键词','文章概览']
        revalue_list = [title_r,genre_r,journal_r_j,publication_time_r,author_r,abstract_r,
                        keyword_r,summary_r]
        # 创建信息字典
        st.session_state.re_dict = dict(zip(attribute_list,revalue_list))
        # 调用后台修改函数
        st.session_state.temp_df = data_revise(st.session_state['df_article'],select_index_i,st.session_state.re_dict)
    if st.session_state['df_article'].文章类型[select_index_i] == '新闻报道':
        # 创建输入窗口
        title_r = st.text_input('文章标题：',value=st.session_state.title_r)
        genre_r = st.selectbox('文章类型：',['期刊论文','新闻报道','政府文件','其他文章'],index=1)
        journal_r_n = st.text_input('发刊单位：',value=st.session_state.journal_r_n)
        publication_time_r = st.text_input('发文时间：',value=st.session_state.publication_time_r)
        topic_r = st.text_input('话题：',value=st.session_state.topic_r)
        summary_r = st.text_input('文章概览：',value=st.session_state.summary_r)
        attribute_list = ['文章标题','文章类型','发刊单位','发文时间','话题','文章概览']
        revalue_list = [title_r,genre_r,journal_r_n,publication_time_r,topic_r,summary_r]
        # 创建信息字典
        st.session_state.re_dict = dict(zip(attribute_list,revalue_list))
        # 调用后台修改函数
        st.session_state.temp_df = data_revise(st.session_state['df_article'],select_index_i,st.session_state.re_dict)
    if st.session_state['df_article'].文章类型[select_index_i] == '政府文件':
        # 创建输入窗口
        title_r = st.text_input('文章标题：',value=st.session_state.title_r)
        genre_r = st.selectbox('文章类型：',['期刊论文','新闻报道','政府文件','其他文章'],index=2)
        department_r = st.text_input('发文单位：',value=st.session_state.department_r)
        proof_r = st.text_input('发文字号：',value=st.session_state.proof_r)
        publication_time_r = st.text_input('发文时间：',value=st.session_state.publication_time_r)
        effective_r = st.text_input('是否有效：',value=st.session_state.effective_r)
        attachment_r = st.text_input('是否有附件：',value=st.session_state.attachment_r)
        summary_r = st.text_input('文章概览：',value=st.session_state.summary_r)
        attribute_list = ['文章标题','文章类型','发文单位','发文字号','发文时间','是否有效','是否有附件','文章概览']
        revalue_list = [title_r,genre_r,department_r,proof_r,publication_time_r,effective_r,attachment_r,summary_r]
        # 创建信息字典
        st.session_state.re_dict = dict(zip(attribute_list,revalue_list))
        # 调用后台修改函数
        st.session_state.temp_df = data_revise(st.session_state['df_article'],select_index_i,st.session_state.re_dict)
    if st.session_state['df_article'].文章类型[select_index_i] == '其他文章':
        # 创建输入窗口
        title_r = st.text_input('文章标题：',value=st.session_state.title_r)
        genre_r = st.selectbox('文章类型：',['期刊论文','新闻报道','政府文件','其他文章'],index=3)
        summary_r = st.text_input('文章概览：',value=st.session_state.summary_r)
        attribute_list = ['文章标题','文章类型','文章概览']
        revalue_list = [title_r,genre_r,summary_r]
        # 创建信息字典
        st.session_state.re_dict = dict(zip(attribute_list,revalue_list))
        # 调用后台修改函数
        st.session_state.temp_df = data_revise(st.session_state['df_article'],select_index_i,st.session_state.re_dict)
if loader_csv_i and select_index_i and check_revise_i: # 文件、索引、勾选框均打开
    if st.session_state.editing == True: # 只有当“编辑模式”打开时才会出现“保存修改”和“取消修改”的按钮
        col1, col2, col3 = st.columns([13,1.5,1.5])
        with col2:
            button_save_input = st.button('保存修改')
            if button_save_input:
                st.info('修改成功!')
                st.session_state['df_article'] = st.session_state.temp_df.copy() # 替换为修改后的dataframe
                st.session_state.df_o = st.session_state.df_article.copy() # 备份修改后的dataframe
                st.session_state.editing = False
                st.session_state.initialized = False
                reset_values() # 回到默认页
                st.rerun()
        with col3:
            button_cancel_input = st.button('取消修改')
            if button_cancel_input:
                st.session_state['df_article'] = st.session_state.df_o.copy()
                st.session_state.editing = False
                st.session_state.initialized = False
                reset_values() # 回到默认页
                st.rerun()