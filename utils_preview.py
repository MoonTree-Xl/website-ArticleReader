import pandas as pd

# 创建CSV文件读取工具
def csv_loader(file): # 用途是创建一个从csv文件中提取出的dataframe
    # 创建临时文件
    csv_content = file.read() # 用户上传的csv文件的内容
    temp_csv_path = 'website_Articleanalysis\\temp_csv_user.CSV' # 临时文件存放路径
    with open(temp_csv_path,'wb') as file:
        file.write(csv_content) # 向临时文件中写入用户上传的csv文件内容
    # 创建dataframe
    df_csv = pd.read_csv(temp_csv_path)
    df_csv.rename(columns={'Unnamed: 0':'标题'},inplace=True)
    df_csv.set_index('标题',inplace=True)
    # 在dataframe中插入默认行
    df_csv.loc['默认页'] = ['','','','','','','','','','','','','','']
    return df_csv
# 创建数据库修改工具
def data_revise(dataframe,index,re_dict):
    temp_df = dataframe.copy()
    # 取出键列表
    attribute_list = []
    for i in re_dict.keys():
        attribute_list.append(i)
    # 修改dataframe数据
    for i in attribute_list: # 对应各columns列名
        temp_df[i][index] = re_dict[i]
    # 修改dataframe索引（涉及文章标题更改）
    index_o = index
    index_r = re_dict['文章标题']
    temp_df.rename(index={index_o:index_r},inplace=True)
    return temp_df

# 创建数据展示工具
def show_data(dataframe,index):
    output_text = '' # 结果字符串
    if index == None:
        output_text = '请选择要查询的文章！'
        return output_text
    # 定义展示文本创建函数
    def text_maker(dataframe,index):
        article = dataframe
        article_genre = article.文章类型[index] # 文章类型
        output_text = '' # 结果字符串
        # 定义字符串拼接函数
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
        # 定义列表格式化函数
        def list_format(text):
            text = text.replace('，', ',')
            text_list = eval(text)
            return text_list
        if article_genre == '期刊论文':
            author_list = list_format(article.作者[index])
            author_text = str_maker(author_list)
            keyword_list = list_format(article.关键词[index])
            keyword_text = str_maker(keyword_list)
            output_text = (f'【文章标题】：{article.文章标题[index]}  \n'
                           f'【文章类型】：{article.文章类型[index]}  \n'
                           f'【刊物名称】：{article.刊物名称[index]}  \n'
                           f'【发文时间】：{article.发文时间[index]}  \n'
                           f'【作者】：{author_text}  \n'
                           f'【摘要】：{article.摘要[index]}  \n'
                           f'【关键词】：{keyword_text}  \n'
                           f'【文章概览】：{article.文章概览[index]}')
        if article_genre == '新闻报道':
            output_text = (f'【文章标题】：{article.文章标题[index]}  \n'
                           f'【文章类型】：{article.文章类型[index]}  \n'
                           f'【发刊单位】：{article.发刊单位[index]}  \n'
                           f'【发文时间】：{article.发文时间[index]}  \n'
                           f'【话题】：{article.话题[index]}  \n'
                           f'【文章概览】：{article.文章概览[index]}')
        if article_genre == '政府文件':
            output_text = (f'【文章标题】：{article.文章标题[index]}  \n'
                           f'【文章类型】：{article.文章类型[index]}  \n'
                           f'【发文单位】：{article.发文单位[index]}  \n'
                           f'【发文字号】：{article.发文字号[index]}  \n'
                           f'【发文时间】：{article.发文时间[index]}  \n'
                           f'【是否有效】：{article.是否有效[index]}  \n'
                           f'【是否有附件】：{article.是否有附件[index]}  \n'
                           f'【文章概览】：{article.文章概览[index]}')
        if article_genre == '其他文章':
            output_text = (f'【文章标题】：{article.文章标题[index]}  \n'
                           f'【文章类型】：{article.文章类型[index]}  \n'
                           f'【文章概览】：{article.文章概览[index]}')
        return output_text
    output_text = text_maker(dataframe,index)
    return output_text
