from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain,ConversationChain
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate,FewShotChatMessagePromptTemplate,MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from pydantic import BaseModel,Field
from typing import List
import pandas as pd

def article_reader(temp_file_path:str)->str: # 返回一个文章信息总结字符串
    # 定义参数
    chat_m = 'qwen-plus'
    embeddings_m = 'text-embedding-v4'
    api_k = 'sk-e20782e92bb845d5844b02ef9d60975c'
    base_u = 'https://dashscope.aliyuncs.com/compatible-mode/v1'
    # 创建聊天模型
    read_model = ChatOpenAI(
        model = chat_m,
        openai_api_key = api_k,
        base_url = base_u,
        temperature = 0
    )
    # 创建嵌入模型
    embeddings_model = DashScopeEmbeddings(
        model = embeddings_m,
        dashscope_api_key = api_k,
    )
    # 加载文本
    loader_p = PyPDFLoader(temp_file_path)
    doc_p = loader_p.load()
    # 对文本进行分割
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1000,
        chunk_overlap = 100,
        separators = ['\n\n','\n','。','！','？']
    )
    text_list = text_splitter.split_documents(doc_p)
    # 文本向量化
    db = FAISS.from_documents(text_list,embeddings_model)
    retriever = db.as_retriever()
    # 构建记忆体
    chat_memory = ConversationBufferMemory(
        return_messages = True,
        memory_key = 'chat_history',
        output_key = 'answer'
    )
    # 调用对话链
    ga = ConversationalRetrievalChain.from_llm(
        llm = read_model,
        retriever = retriever,
        memory = chat_memory
    )
    # 创建提示词模板
    prompt_j = ('文章标题：文章名\n'
                '文章类型：类型\n'
                '刊物名称：刊物名称（刊物名称不带书名号《》）\n'
                '发文时间：发文时间\n'
                '作者：作者1，作者2，……\n'
                '摘要：摘要\n'
                '关键词：关键词1，关键词2，关键词3\n'
                '文章概览：文章概览')
    prompt_n = ('文章标题：文章名\n'
                '文章类型：类型\n'
                '发刊单位：发刊单位\n'
                '发文时间：发文时间\n'
                '话题：话题\n'
                '文章概览：文章概览')
    prompt_g = ('文章标题：文章名\n'
                '文章类型：类型\n'
                '发文单位：发文单位\n'
                '发文字号：发文字号\n'
                '发文时间：发文时间\n'
                '是否有效：是否有效\n'
                '是否有附件：是否有附件\n'
                '文章概览：文章概览')
    prompt_o = ('文章标题：文章名\n'
                '文章类型：类型\n'
                '文章概览：文章概览')
    prompt = ('请对上传的文档内容进行全文总结。'
              '先判断该文章的【类型】（期刊论文、新闻报道、政府文件、其他文章），'
              '一般而言，期刊论文通常包括期刊名称、摘要和关键词，'
              '新闻报道包括发刊单位（例如：人民日报）、某人发言（例如：XX指出XX），'
              '政府文件包括发文字号（例如：国家税务总局公告2025年第20号）、是否有效（例如：全文有效、部分有效）。'
              '判断完成后再对内容根据类型不同进行总结，'
              '若判断文章类型为“期刊论文”，则提取该文章的【文章名】、【刊物名称】、【发文时间】、【作者】、'
              '【摘要】、【关键词】，'
              '其中，若有两个及以上作者的，注意作者排序，【摘要】有时候也会以【内容提示】、【内容提要】的形式出现，'
              '【文章名】是这篇文章的标题，一般出现在第一页，可能会以“……研究”结尾。'
              '完成后，对全文总结一个【文章概览】，内容按照“写作背景→实验设计→研究方法→研究结论”的框架排布，'
              '字数大概不超过500字；'
              '若判断文章类型为“新闻报道”，则提取该文的【文章名】、【发刊单位】、【发文时间】、【话题】，'
              '其中【话题】是概括性的内容，需要你先对文章进行总结，再从总结中提炼出该文围绕的话题，'
              '完成后，对全文内容总结一个【文章概览】，字数大概不超过500字；'
              '若判断文章类型为“政府文件”，则提取【文章名】、【发文单位】、【发文字号】、【发文时间】、【是否有效】'
              '、【是否有附件】，'
              '完成后，对全文内容总结一个【文章概览】，字数不超过500字；'
              '若判断文章类型为“其他文章”，则提取【文章名】，然后对全文内容总结【文章概览】，字数不超过500字。'
              '注意，【文章名】是这篇文章的标题，通常是第一页页眉下第一行标题，所有的【文章名】都要与原文一致，不要自行发挥进行总结。'
              '对于“其他文章”，有时候不会直接出现【文章名】，你要在总结全文的基础上凝练出一个标题。'
              '完成后，根据文章类型，按照以下格式进行输出，格式模板用#号包围：\n'
              '#\n'
              f'若文章类型为“期刊论文”，则按照模板{prompt_j}；'
              f'若文章类型为“新闻报道”，则按照模板{prompt_n}；'
              f'若文章类型为“政府文件”，则按照模板{prompt_g}；'
              f'若文章类型为“其他文章”，则按照模板{prompt_o}。\n'
              f'#')
    result = ga.invoke(
        {
            'chat_history':chat_memory,
            'question':prompt
        }
    )
    summary_text = result['answer']
    return summary_text

def info_organize(text:str) -> tuple: # 输入一个字符串，返回一个属性字典
    result_dict = {}
    # 创建聊天模型
    chat_model = ChatOpenAI(
        model = 'qwen-plus',
        openai_api_key = 'sk-e20782e92bb845d5844b02ef9d60975c',
        base_url = 'https://dashscope.aliyuncs.com/compatible-mode/v1',
        temperature = 0
    )
    # 创建关键类
    class ArticleInfo_j(BaseModel):
        title:str = Field(description = '文章名',
                          examples = ['三只小猪'])
        genre:str = Field(description = '文章类型',
                          examples = ['期刊论文'])
        journal:str = Field(description = '刊物名称',
                            examples = ['税务研究'])
        publication_time:str = Field(description = '发文时间',
                                     examples = ['2025年第2期'])
        author:List[str]= Field(description = '作者',
                           examples = [['小白','小黑']])
        abstract:str = Field(description = '摘要',
                             examples = ['这篇论文……'])
        key_word:List[str] = Field(description = '关键词',
                                   examples = [['关键词1','关键词2']])
        summary:str = Field(description = '文章概览',
                            examples = ['这篇文章……'])
    class ArticleInfo_n(BaseModel):
        title:str = Field(description='文章名',
                          examples=['三只小猪'])
        genre:str = Field(description = '文章类型',
                          examples = ['新闻报道'])
        journal:str = Field(description = '发刊单位',
                            examples = ['人民日报'])
        publication_time:str = Field(description = '发文时间',
                                     examples = ['2025年2月1日'])
        topic:str = Field(description = '话题',
                          examples = ['天宫上天'])
        summary:str = Field(description = '文章概览',
                            examples = ['这篇文章……'])
    class ArticleInfo_g(BaseModel):
        title:str = Field(description='文章名',
                          examples=['三只小猪'])
        genre:str = Field(description = '文章类型',
                          examples = ['政府文件'])
        department:str = Field(description = '发文单位',
                               examples = ['国家税务总局'])
        proof:str = Field(description='发文字号',
                          examples=['国家税务总局第50号文'])
        publication_time:str = Field(description = '发文时间',
                                     examples = ['2025年2月1日'])
        effective:str = Field(description = '是否有效',
                              examples = ['全文有效','部分有效','全文无效'])
        attachment:str = Field(description = '是否有附件',
                               examples = ['有附件','没有附件'])
        summary:str = Field(description = '文章概览',
                            examples = ['这篇文章……'])
    class ArticleInfo_o(BaseModel):
        title:str = Field(description='文章名',
                          examples=['三只小猪'])
        genre:str = Field(description = '文章类型',
                          examples = ['其他文章'])
        summary:str = Field(description = '文章概览',
                            examples = ['这篇文章……'])
    # 创建小样本提示
    example_prompt = ChatPromptTemplate(
        [
            ('human','请对一段文字进行分析，'
                     '确认这段文字中的“文章类型”是[期刊论文，新闻报道，政府文件，其他文章]中的哪类，'
                     '直接返回答案结果，所要分析的文字将用#号包围：#{text}#'),
            ('ai','{answer}')
        ]
    )
    examples = [
        {
            'text':'文章类型：期刊论文 刊物名称：税务研究 发文时间：2025年第2期 ……',
            'answer':'期刊论文'
        },
        {
            'text': '文章类型：新闻报道 发刊单位：人民日报 发文时间：2025年2月1日 ……',
            'answer': '新闻报道'
        }
    ]
    few_shot_template = FewShotChatMessagePromptTemplate(
        example_prompt = example_prompt,
        examples = examples
    )
    # 创建提示词模板
    final_prompt_template = ChatPromptTemplate(
        [
            few_shot_template,
            ('human','分析这段文字：{text}')
        ]
    )
    final_prompt = final_prompt_template.invoke(
        {'text':text}
    )
    response = chat_model.invoke(final_prompt)
    article_type = response.content
    # 创建解析器
    user_text = ''
    parser_instruction = ''
    output_parser = ''
    if article_type == '期刊论文':
        output_parser = PydanticOutputParser(pydantic_object = ArticleInfo_j)
        parser_instruction = output_parser.get_format_instructions()
        user_text = ('帮我从下面给出的文本中，'
                     '提取出文章名、文章类型、刊物名称、发文时间、作者、摘要、关键词、文章概览，'
                     '要求一字不动从源文本中摘出，'
                     '文本将会以三个#号包围。\n###{text}###')
    if article_type == '新闻报道':
        output_parser = PydanticOutputParser(pydantic_object = ArticleInfo_n)
        parser_instruction = output_parser.get_format_instructions()
        user_text = ('帮我从下面给出的文本中，'
                     '提取出文章名、文章类型、发刊单位、发文时间、话题、文章概览，'
                     '要求一字不动从源文本中摘出，'
                     '文本将会以三个#号包围。\n###{text}###')
    if article_type == '政府文件':
        output_parser = PydanticOutputParser(pydantic_object = ArticleInfo_g)
        parser_instruction = output_parser.get_format_instructions()
        user_text = ('帮我从下面给出的文本中，'
                     '提取出文章名、文章类型、发文单位、发文字号、发文时间、是否有效、是否有附件、文章概览，'
                     '要求一字不动从源文本中摘出，'
                     '文本将会以三个#号包围。\n###{text}###')
    if article_type == '其他文章':
        output_parser = PydanticOutputParser(pydantic_object = ArticleInfo_o)
        parser_instruction = output_parser.get_format_instructions()
        user_text = ('帮我从下面给出的文本中，'
                     '提取出文章名、文章类型、文章概览，'
                     '要求一字不动从源文本中摘出，'
                     '文本将会以三个#号包围。\n###{text}###')
    # 创建提示词模板
    prompt_template = ChatPromptTemplate.from_messages(
        [
            ('system','{parser_instructions}。输出的结果请使用中文。'),
            ('user',user_text)
        ]
    )
    final_prompt = prompt_template.invoke(
        {
            'parser_instructions': parser_instruction,
            'text': text,
        }
    )
    # 取出结果对象
    response = chat_model.invoke(final_prompt)
    result = output_parser.invoke(response)
    article_title = result.title
    result_dict[result.title] = result
    return article_title,result_dict
def dataframe_model(): # 空白dataframe模板，返回一个dataframe
    df_model = pd.DataFrame({'文章标题':{'White':''},
                             '文章类型':{'White':''},
                             '刊物名称':{'White':''},
                             '发刊单位':{'White':''},
                             '发文单位':{'White':''},
                             '发文字号':{'White':''},
                             '发文时间':{'White':''},
                             '作者':{'White':''},
                             '摘要':{'White':''},
                             '关键词':{'White':''},
                             '话题':{'White':''},
                             '是否有效':{'White':''},
                             '是否有附件':{'White':''},
                             '文章概览':{'White':''}})
    return df_model
def csv_maker(file_path): # 在制定路径创建一个空白dataframe生成的csv文件
    # 创建格式化dataframe
    df = dataframe_model()
    # 保存为模板csv文件
    df.to_csv(file_path)
def info_store(dict,article_title,csv_path):
    # 判断传入的JSON文件的格式
    try:
        df_a = pd.read_csv(csv_path)
        df_a.rename(columns={'Unnamed: 0':'标题'},inplace = True)
        df_a.set_index('标题',inplace = True)
        if 'White' in df_a.index:
            df_a = df_a.drop('White')
    except BaseException:
        df_a = dataframe_model()
        df_a = df_a.drop('White')
    # 取出信息
    article = dict[article_title] # 取出文章类对象
    article_genre = article.genre # 文章类型
    if article_genre == '期刊论文':
        # 提取属性
        title = article_title
        genre = article.genre
        journal = article.journal
        publication_time = article.publication_time
        author = article.author
        abstract = article.abstract
        key_word = article.key_word
        summary = article.summary
        # 创建属性列表
        attribute_list = [title,genre,journal,publication_time,author,abstract,key_word,summary]
        columns_name = ['文章标题','文章类型','刊物名称','发文时间','作者','摘要','关键词','文章概览']
        # 向dataframe中写入信息
        df_a.loc[f'{title}'] = pd.Series(attribute_list,index=columns_name)
    if article_genre == '新闻报道':
        # 提取属性
        title = article_title
        genre = article.genre
        journal = article.journal
        publication_time = article.publication_time
        topic = article.topic
        summary = article.summary
        # 创建属性列表
        attribute_list = [title,genre,journal,publication_time,topic,summary]
        columns_name = ['文章标题','文章类型','发刊单位','发文时间','话题','文章概览']
        # 向dataframe中写入信息
        df_a.loc[f'{title}'] = pd.Series(attribute_list, index=columns_name)
    if article_genre == '政府文件':
        # 提取属性
        title = article_title
        genre = article.genre
        department = article.department
        proof = article.proof
        publication_time = article.publication_time
        effective = article.effective
        attachment = article.attachment
        summary = article.summary
        # 创建属性列表
        attribute_list = [title,genre,department,proof,publication_time,effective,attachment,summary]
        columns_name = ['文章标题','文章类型','发文单位','发文字号','发文时间','是否有效','是否有附件','文章概览']
        # 向dataframe中写入信息
        df_a.loc[f'{title}'] = pd.Series(attribute_list, index=columns_name)
    if article_genre == '其他文章':
        # 提取属性
        title = article_title
        genre = article.genre
        summary = article.summary
        # 创建属性列表
        attribute_list = [title,genre,summary]
        columns_name = ['文章标题','文章类型','文章概览']
        # 向dataframe中写入信息
        df_a.loc[f'{title}'] = pd.Series(attribute_list, index=columns_name)
    # 保存CSV文件
    df_a.to_csv(csv_path,encoding='utf-8')

def summary_model(api_key,memory,question,file=None,attachment=None,summary_button=None,store_button=None):
    # 创建临时文档
    temp_file_path = 'temp.pdf' # 临时文件路径
    if file:
        file_content = file.read() # 读取用户上传的文件，返回二进制数据
        with open(temp_file_path,'wb') as temp_file:
            temp_file.write(file_content) # 向临时文件写入内容
    temp_attachment_path = '/mount/src/website-articlereader/temp_attachment.CSV' # 临时附件路径
    if attachment:
        attachment_content = attachment.read() # 附件内容
        with open(temp_attachment_path,'wb') as temp_file:
            temp_file.write(attachment_content) # 向附件临时文件写入内容
        temp_df = pd.read_csv(temp_attachment_path)
        temp_df.rename(columns={'Unnamed: 0': '标题'}, inplace=True)
        temp_df.set_index('标题', inplace=True)
        if 'White' in temp_df.index:
            temp_df.drop('White')
    if attachment == None:
        csv_maker(temp_attachment_path)
    # 创建聊天模型
    chat_model = ChatOpenAI(
        model = 'qwen-plus',
        openai_api_key = api_key,
        base_url = 'https://dashscope.aliyuncs.com/compatible-mode/v1'
    )
    output_text = ''
    if file: # 用户上传了pdf
        # 读取文件
        loader_p = PyPDFLoader(temp_file_path)
        doc_p = loader_p.load()
        # 创建文本分割器
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = 1000,
            chunk_overlap = 100,
            separators = ['\n\n','\n','。','！','？']
        )
        # 分割文本
        text_t = text_splitter.split_documents(doc_p)
        # 文本向量化
        embeddings_model = DashScopeEmbeddings(
            model = 'text-embedding-v4',
            dashscope_api_key = api_key
        )
        db = FAISS.from_documents(text_t,embeddings_model)
        retriever = db.as_retriever()
        # 构建对话链
        qa =ConversationalRetrievalChain.from_llm(
            llm =chat_model,
            retriever = retriever,
            memory = memory
        )
        response = qa.invoke({'chat_history':memory,'question':question})
        output_text = response['answer']
        if summary_button:
            # 定义工具函数
            # 字符串拼接函数
            def str_maker(text_list):
                text = ''
                if len(text_list) > 1:
                    for i in text_list:
                        text += i
                        text += '，'
                if len(text_list) == 1:
                    text += text_list[0]
                text_final = text.rstrip('，')
                return text_final
            # 执行AI函数
            summary_text = article_reader(temp_file_path) # 生成文章总结字符串
            article_title,article_dict = info_organize(summary_text) # 生成关键信息字典
            # 生成最终结果
            article = article_dict[article_title] # 文章的类信息
            article_genre = article.genre
            a = article_genre
            output_text = str(a)
            if article_genre == '期刊论文':
                author_text = str_maker(article.author)
                keywords_text = str_maker(article.key_word)
                output_text = (f'【文章名】：{article.title}  \n'
                               f'【文章类型】：{article.genre}  \n'
                               f'【刊物名称】：{article.journal}  \n'
                               f'【发文时间】：{article.publication_time}  \n'
                               f'【作者】：{author_text}  \n'
                               f'【摘要】：{article.abstract}  \n'
                               f'【关键词】：{keywords_text}  \n'
                               f'【文章概览】：{article.summary}')
            if article_genre == '新闻报道':
                output_text = (f'【文章名】：{article.title}  \n'
                               f'【文章类型】：{article.genre}  \n'
                               f'【发刊单位】：{article.journal}  \n'
                               f'【发文时间】：{article.publication_time}  \n'
                               f'【话题】：{article.topic}  \n'
                               f'【文章概览】：{article.summary}')
            if article_genre == '政府文件':
                output_text = (f'【文章名】：{article.title}  \n'
                               f'【文章类型】：{article.genre}  \n'
                               f'【发文单位】：{article.department}  \n'
                               f'【发文字号】：{article.proof}  \n'
                               f'【发文时间】：{article.publication_time}  \n'
                               f'【是否有效】：{article.effective}  \n'
                               f'【是否有附件】：{article.attachment}  \n'
                               f'【文章概览】：{article.summary}')
            if article_genre == '其他文章':
                output_text = (f'【文章名】：{article.title}  \n'
                               f'【文章类型】：{article.genre}  \n'
                               f'【文章概览】：{article.summary}')
            # 将信息存储
            if store_button:
                info_store(article_dict,article_title,temp_attachment_path)
        if not summary_button:
            response = qa.invoke({'chat_history':memory,'question':question})
            output_text = response['answer']
    if not file:
        prompt_template = ChatPromptTemplate(
            [
                MessagesPlaceholder(variable_name='history'),
                ('human', '{input}')
            ]
        )
        normal_chain = ConversationChain(
            llm = chat_model,
            memory = memory,
            prompt = prompt_template,
        )
        result = normal_chain.invoke({'input':question})
        output_text = result['response']
    return output_text





