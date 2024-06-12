import jieba
from collections import Counter
import pandas as pd
import re
import string
import streamlit as st
from streamlit_echarts import st_echarts
from streamlit.logger import get_logger

# jieba用于中文分词，Counter用于统计词频，pandas用于数据处理，re用于正则表达式匹配，string提供字符串操作

# 自定义词典，添加不应该被分开的词汇，定义一个列表custom_words，包含不应该被分开的词汇。
# 通过jieba.add_word函数将这些词汇添加到jieba的分词词典中，确保分词时这些词汇不会被错误地切分
custom_words = ["对比研究", "非言语", "教学研究", "影响研究", "多模态研究", "行为研究", "编码与分析", "评价研究", "影响",
                "应用调查", "调查研究", "案例研究", "作用"]
for word in custom_words:
    jieba.add_word(word)

# 定义一个函数load_stop_words，用于从文件stop_words.txt中加载停用词列表。
def load_stop_words():
    stop_words = []
    with open('stop_words.txt', 'r', encoding='utf-8') as f:
        for line in f:
            stop_words.append(line.strip())
    return stop_words

stopwords = load_stop_words()

# with语句打开指定路径下的文本文件，并读取其内容，存储在变量content中使用原始字符串指定文件路径，以避免转义字符的问题
with open(r'C:\Users\越好\Downloads\CNKI-20240509140652944.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# 使用re.sub函数和正则表达式去除文本中的HTML标签。
# 正则表达式<[^<]+?>匹配HTML标签，re.sub将这些匹配到的内容替换为空字符串，即移除它们
content = re.sub('<[^<]+?>', '', content)

# 定义一个函数remove_stopwords，用于从文本中去除停用词。
# 调用remove_stopwords函数，并将处理后的文本存储在cleaned_text
def remove_stopwords(text, stopwords):
    words = text.split()
    # 用于创建一个新的列表cleaned_words，其中包含原始列表words中所有不在停用词列表stopwords中的单词。
    cleaned_words = [word for word in words if word.lower() not in stopwords]
    return ' '.join(cleaned_words)
cleaned_text = remove_stopwords(content, stopwords)
print("After removing stopwords:", cleaned_text)

# 使用jieba进行分词，使用jieba.cut函数对去除停用词后的文本进行分词。
# cut_all=False参数表示使用精确模式进行分词。将分词结果转换为列表，并存储在word_list中
words = jieba.cut(cleaned_text, cut_all=False)
word_list = list(words)

# 再次过滤word_list中的停用词，确保最终的词列表中不包含停用词
word_list = [word for word in word_list if word not in stopwords]

# 统计词频
word_counts = Counter(word_list)

# 创建一个DataFrame来存储词频，columns=['Word', 'Frequency']定义了DataFrame的列名
df = pd.DataFrame(list(word_counts.items()), columns=['Word', 'Frequency'])

# 对DataFrame按照’Frequency’列进行降序排序
df = df.sort_values(by='Frequency', ascending=False)

# 将DataFrame保存到CSV文件
# UTF-8和UTF-8-SIG的主要区别在于对BOM的处理方式不同。 在大多数情况下，推荐使用UTF-8-SIG来编码和保存文本文件，因为它可以更好地处理BOM问题，提高文件的兼容性和可读性。
df.to_csv('word_frequencies.csv', index=False, encoding='utf-8-sig')


def run():
    st.set_page_config(
        page_title="Hello",
        page_icon="👋",
    )

    st.write("# Welcome to Streamlit! 👋")

    url = st.text_input('Enter URL:')

    if url:
        r = requests.get(url)
        r.encoding = 'utf-8'
        text = r.text
        text = extract_body_text(text)

        text = remove_html_tags(text)
        text = remove_punctuation(text)
        # words = tokenize(text)
        # # words = stem_words(words)
        # words = remove_stopwords(text.split())

        # # 识别中英文，判断分词方式
        # import chardet
        # encoding = chardet.detect(text)['encoding']
        # if encoding == 'utf-8':
        #     words = jieba.cut(text)
        # else:
        #     words = text.split()

        # words = text.split()
        text = clean_text(text)
        words = segment(text)
        word_counts = Counter(words)

        top_words = word_counts.most_common(20)

        wordcloud_options = {
            "tooltip": {
                "trigger": 'item',
                "formatter": '{b} : {c}'
            },
            "xAxis": [{
                "type": "category",
                "data": [word for word, count in top_words],
                "axisLabel": {
                    "interval": 0,
                    "rotate": 30
                }
            }],
            "yAxis": [{"type": "value"}],
            "series": [{
                "type": "bar",
                "data": [count for word, count in top_words]
            }]
        }

        st_echarts(wordcloud_options, height='500px')

    # read_txtfile()

if __name__ == "__main__":
    run()