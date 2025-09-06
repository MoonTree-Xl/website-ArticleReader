import streamlit as st
from langchain.memory import ConversationBufferMemory
from utils_n import summary_model,dataframe_model

# 设置页面为宽屏模式
st.set_page_config(page_title='首页',layout='wide')
# 分列
col1,col2 = st.columns(2)
# 创建侧边栏
with st.sidebar:
    api_key_input = st.text_input('请输入API密钥：')
    check_key_input = st.checkbox('是否使用默认API密钥？')
    if check_key_input:
        api_key_input = 'sk-e20782e92bb845d5844b02ef9d60975c'
    st.markdown('[获取API密钥](https://platform.deepseek.com/api_keys)') # deepseek密钥获取网址
    st.divider() # 创建分割线
    st.write('⭐文章内容总结板块')
    file_csv_input = st.file_uploader('请上传CSV文件：',type = ['CSV','csv']) # 用户上传的csv文件
    check_csv_input = st.checkbox('储存文章内容信息')
    button_clear = st.button('重置CSV文件')

# 创建记忆体
if 'chat_memory' not in st.session_state:
    st.session_state['chat_memory'] = ConversationBufferMemory(
        return_messages = True,
        memory_key = 'chat_history',
        output_key = 'answer'
    )
if 'normal_memory' not in st.session_state:
    st.session_state['normal_memory'] = ConversationBufferMemory(return_messages = True)
# 第一列内容
with col1:
    # 插入标题
    st.title('智能文献阅读工具🦖')
    # 插入文件上传接口
    file_pdf_input = st.file_uploader('请上传PDF文件：',type = ['pdf']) # 用户上传的pdf文件
    # 插入提问框
    question_input = st.text_input('提问：')
    # 插入总结按钮
    button_summary = st.button('总结文档内容')
# 第二列内容
with col2:
    # 插入图片
    image = st.empty()
    if not question_input and not button_summary:
        image = st.image('/mount/src/website-articlereader/images/线条小狗.png')
    # 插入回复
    if api_key_input and question_input and not file_pdf_input: # 当api密钥和用户的问题均输入时
        image = st.empty()
        st.write('回复：')
        with st.spinner('AI正在思考，请稍等...'):
            result = summary_model(api_key_input,st.session_state['normal_memory'],question_input)
            st.write(result)
    if question_input and not api_key_input: # 用户的问题已输入，api密钥未输入
        image = st.empty()
        st.write('回复：')
        st.write('请先输入API密钥！')
    if api_key_input and file_pdf_input and button_summary: # api密钥、pdf文件、总结按钮同时激活
        image = st.empty()
        st.write('回复：')
        with st.spinner('AI正在思考，请稍等...'):
            result = summary_model(api_key_input,
                                   st.session_state['chat_memory'],
                                   question_input,file_pdf_input,file_csv_input,button_summary,
                                   check_csv_input)
            st.markdown(result)
    # 导出CSV文件
    file_path = '/mount/src/website-articlereader/temp_attachment.CSV'
    if button_summary:
        with open(file_path,'r',encoding='utf-8') as file:
            button_download_input = st.download_button(label = '导出CSV文件',data = file,mime = 'text/csv')
if button_clear:
    temp_df = dataframe_model()
    temp_df.to_csv(file_path)
