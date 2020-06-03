

from tqdm import tqdm
import jieba_fast as jieba
from flashtext import KeywordProcessor
from rouge import Rouge
from collections import Counter
import re
import numpy as np

class yanwenzi():
    '''
    flashtext比  常规的用[for]的方式要快：6-7倍
    
    yanwenzi_dict,颜文字字典,{'w(ﾟДﾟ)w': '啊啊', '(ノへ￣、)': '抽泣', '(￣_,￣ )': '蔑视'}
    
    '''
    def __init__(self,yanwenzi_dict):
        self.yanwenzi_dict = yanwenzi_dict
        self.actree = self.init_processor(yanwenzi_dict)
        self.add_words(yanwenzi_dict,freq = 100,tag = 'ywz')
        
        
    def init_processor(self,yanwenzi_dict):
        actree = KeywordProcessor()
        for word,r_word in yanwenzi_dict.items():
            actree.add_keyword(word,'_{}_'.format(r_word))     # 向trie树中添加单词
        print('success loaded. keyword num : ',len(actree))
        return actree
    
    def actree_add_word(self,yanwenzi_dict_list,tag = '颜文字'):
        '''
        actree词典中新增词
        
        新增词到检索的词典之中方便检索使用
        yanwenzi_dict_list,dict/list,同时一开始没有定义颜文字的属性,那么属性统一定义为"_颜文字_"
        
        '''
        if isinstance(yanwenzi_dict_list,dict):
            for word,r_word in yanwenzi_dict_list.items():
                self.actree.add_keyword(word,'_{}_'.format(r_word))     # 向trie树中添加单词
        elif isinstance(yanwenzi_dict_list,list):
            for word in yanwenzi_dict_list:
                self.actree.add_keyword(word,'_{}_'.format(tag))     # 向trie树中添加单词
        else:
            raise Exception('yanwenzi_dict_list format must be dict or list.')
        print('success loaded. keyword num : ',len(yanwenzi_dict_list))
    
    def add_words(self,yanwenzi_dict_list,freq = 100,tag = 'ywz'):
        '''
        分词词典中加入新增的词
        yanwenzi_dict_list,dict/list都可以,新增到分词的词典之中
        '''
        if isinstance(yanwenzi_dict_list,dict):
            for k,v in yanwenzi_dict_list.items():
                jieba.add_word('_{}_'.format(v),freq = freq,tag = tag)
        elif isinstance(yanwenzi_dict_list,list):
            for word in yanwenzi_dict_list:
                jieba.add_word('_{}_'.format(word),freq = freq,tag = tag)
        else:
            raise Exception('yanwenzi_dict_list format must be dict or list.')
        print('jieba add words. length :',len(yanwenzi_dict_list))

    def detect(self,text,span_info=True):
        '''
        span_info:是否标记位置
        '''
        out = self.actree.extract_keywords(text,span_info=span_info)
        return out

    def ywz_replace(self,text):
        return self.actree.replace_keywords(text)

    def jieba_cut(self,text):
        '''
        2020-6-3 发现'İrem 艾丽' - ywz_replace 报错：IndexError: string index out of range
        '''
        try:
            text = self.ywz_replace(text)
        except:
            pass
        return list(jieba.cut(text))

    '''  新颜文发现  '''
    @staticmethod
    def is_special_char(text):
        '''
        特殊符号检测
        text = '小猪哥🍹'
        is_special_char(text)
        >>> ['🍹']

        text = text = '♪ ٩(｡•ˇ‸ˇ•｡)۶'
        [['♪', 0],
         ['٩', 2],
         ['(', 3]...]

        其中:
        list(re.finditer(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])",text))
        [<_sre.SRE_Match object; span=(2, 3), match='╭'>,
         <_sre.SRE_Match object; span=(3, 4), match='('>,]
        '''
        m_text = list(re.finditer(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])",text))
        if len(m_text) > 0:
            return [[mt.group(),mt.span()[1]] for mt in m_text]
        else:
            return []
    
    @staticmethod
    def group_consecutive(a):
        '''
        分离数列中连续的整数
        fyi:https://zhuanlan.zhihu.com/p/29558169

        group_consecutive([1,2,3,5,6,7,9,54,215,872,246])
        [array([1, 2, 3]),
         array([5, 6, 7]),
         array([9]),
         array([54]),
         array([215]),
         array([872]),
         array([246])]
        '''
        return np.split(a, np.where(np.diff(a) != 1)[0] + 1)

    def yanwenzi_find(self,text,min_n = 2,remove_spacing = True):
        '''
        颜文字发现函数
            - min_n,特殊字符数量大于2
            - remove_spacing,颜文字中间是否去掉空格
        '''
        # 识别 + 序列
        spe_out = self.is_special_char(text)
        split_group = self.group_consecutive([s[1] for s in spe_out])
        ywz_out = []
        for sp in split_group:
            if remove_spacing:
                ywz_t = text[sp[0]-1:sp[-1]].replace(' ','')
            else:
                ywz_t = text[sp[0]-1:sp[-1]]

            if len(ywz_t)> min_n:
                ywz_out.append(ywz_t)
        return ywz_out

    def yanwenzi_new_discovery(self,corpus,min_n = 2,remove_spacing = True,topn = 200):
        '''
        颜文字发现函数
            - min_n,特殊字符数量大于2
            - remove_spacing,颜文字中间是否去掉空格
            - topn = 200,返回排名topn的颜文字表情
            
        返回:
            [('(^_^)', 1837),
             ('(∩_∩)', 617),
             ('(๑•.•๑)', 314),
             ('(☆_☆)', 291),
             ('(*^ω^*)', 282),
        '''
        ywz_discovery = []
        for text in tqdm(corpus):
            ywz_discovery.extend(self.yanwenzi_find(text,min_n = min_n,remove_spacing = remove_spacing))
            #print(text,'result ==> ',yanwenzi_find(text,min_n = 2))
        return Counter(ywz_discovery).most_common(topn)
    
    '''颜文字属性识别:新颜文字识别'''

    @staticmethod
    def rouge_score(text_a,text_b):
        rouge = Rouge()
        rouge_score = rouge.get_scores(' '.join([t for t in text_a]), ' '.join([t for t in text_b]))
        rouge_1 = rouge_score[0]["rouge-1"]
        rouge_2 = rouge_score[0]["rouge-2"]
        return {'rouge-1':rouge_1,'rouge-2':rouge_2}

    def new_yanwenzi_find(self,text_a,min_s = 0.35,\
                          score_type = 'rouge-2',stat = 'f'):
        '''
        通过相似找到最相似表情

        从rouge的评分来看，rouge-1太粗糙；rouge-2比较合适，
        且几个统计量中，f/p/r,f效果比较好，p/r可能会有比较多的选项，也就是差异性不明显

        参数:
            - min_s = 0.35,阈值，一定要相似性大于才会给出；如果是'rouge-1'比较合适的阈值在0.75
            - score_type = 'rouge-2',rouge的得分类型,n-grams
            - stat = 'f',采用的统计量

        统计量:
            text_a = '(^_^)'
            new_yanwenzi_find(text_a,min_s = 0.35)
            >>> [['(^&^)/', '噢耶',0.75]]
        '''
        # 根据已知的表情包属性求rouge得分
        scores = []
        for k,v in self.yanwenzi_dict.items():
            score = self.rouge_score(text_a,k)
            scores.append(score[score_type][stat])

        # 找到最大值族群
        max_n = [n for n,s in enumerate(scores) if s == max(scores) and max(scores) > min_s]
        # 定位到表情
        detect = [[[k,v,max(scores)] for k,v in  self.yanwenzi_dict.items()][mn]  for mn in max_n]
        #print(text_a,'==>',detect,max_n)
        return detect

    
if __name__ == '__main__':
    '''颜文识别'''
    # 初始化
    json_data = {'w(ﾟДﾟ)w': '啊啊', '(ノへ￣、)': '抽泣', '(￣_,￣ )': '蔑视'}
    import json
    json_data = open("data/yanwenzi_2.json", "r", encoding="utf-8").read()
    json_data = eval(json_data)
    ywz = yanwenzi(json_data)
    
    # 检测位置
    text = '^O^佳^O^'
    text = '^O^佳^O^w(ﾟДﾟ)w'
    ywz.detect(text,span_info=True)
    # [('_吼吼_', 0, 3), ('_吼吼_', 4, 7)]
    
    # 特殊位置进行替换
    ywz.ywz_replace(text)
    
    # 特殊符号替换 + 分词
    ywz.jieba_cut(text)
    
    '''新颜文发现'''
    # 单文本 颜文字发现
    text = '璇哥！加油↖(^ω^)↗'
    ywz.yanwenzi_find(text,min_n = 2,remove_spacing = True)
    
    # 批量文本 颜文字发现
    corpus = ['d(ŐдŐ๑)crush', '♪ ٩(｡•ˇ‸ˇ•｡)۶', '〜(￣▽￣〜)', '木木╭(╯ε╰)╮', 'ToT(^(エ)^)', 'HLYS(ー`´ー)',
     'O(∩_∩)O', '(^^)笔尖', '璇哥！加油↖(^ω^)↗', '蜕变(^_^) \ufeff']
    ywz_new_list = ywz.yanwenzi_new_discovery(corpus,min_n = 2,remove_spacing = True,topn = 200)
    
    # 新颜文添加到分词词典
    yanwenzi_dict_list = [ynl[0] for ynl in ywz_new_list]
    ywz.add_words(yanwenzi_dict_list,freq = 100,tag = 'ywz')

    # 新颜文添加到检测词典
    ywz.actree_add_word(yanwenzi_dict_list,tag = '颜文字')

    # 新颜文字属性识别
    text_a = '(^_^)'
    ywz.new_yanwenzi_find(text_a,min_s = 0.35)

