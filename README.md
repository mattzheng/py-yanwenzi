# py-yanwenzi

网络表情NLP，颜文字识别，颜文字表情实体识别、属性检测、新颜发现


相关CSDN博客：https://mattzheng.blog.csdn.net/article/details/106494970

# 0 更新日志

## 2020-6-2

整个项目 + `data`目录有两个数据源:

- 颜文字,yanwenzi_2.json
- 一些特殊符号,special_symbols.xlsx

## 2020-6-3

- emoji相关：emoji.py + data/emoji.txt + data/emoji-test.txt + data/emoji-wechat.txt 


> 相关文章：

> [网络表情NLP（一）︱颜文字表情实体识别、属性检测、新颜发现](https://mattzheng.blog.csdn.net/article/details/106494970)

> [网络表情NLP（二）︱特殊表情包+emoji识别](https://mattzheng.blog.csdn.net/article/details/106499412)

# 1 混用的几个库

这里混用了几个笔者常用的文本处理的库，
- jieba_fast,相比jieba，jieba_fast 使用cpython重写了jieba分词库中计算DAG和HMM中的vitrebi函数，速度得到大幅提升
- flashtext，Flashtext：大规模数据清洗的利器，正则表达式在一个 10k 的词库中查找 15k 个关键词的时间差不多是 0.165 秒。但是对于 Flashtext 而言只需要 0.002 秒。因此，在这个问题上 Flashtext 的速度大约比正则表达式快 82 倍。可参考：[python︱flashtext高效关键词查找与替换](https://blog.csdn.net/sinat_26917383/article/details/78521871)
- rouge，Rouge-1、Rouge-2、Rouge-L分别是：生成的摘要的1gram-2gram在真实摘要的1gram-2gram的准确率召回率和f1值，还有最长公共子序列在预测摘要中所占比例是准确率，在真实摘要中所占比例是召回率，然后可以计算出f1值。

## 1.1 模块一：rouge 
rouge是自动文本摘要算法的评估指标：
```
from rouge import Rouge

a = ["i am a student from xx school"]  # 预测摘要 （可以是列表也可以是句子）
b = ["i am a student from school on china"] #真实摘要

rouge = Rouge()
rouge_score = rouge.get_scores(a, b)
print(rouge_score[0]["rouge-1"])
print(rouge_score[0]["rouge-2"])
print(rouge_score[0]["rouge-l"])

>>> {'f': 0.7999999950222222, 'p': 0.8571428571428571, 'r': 0.75}
>>> {'f': 0.6153846104142012, 'p': 0.6666666666666666, 'r': 0.5714285714285714}
>>> {'f': 0.7929824561399953, 'p': 0.8571428571428571, 'r': 0.75}



```
该模块是使用在颜文字相似性匹配的时候，当然这边从实验效果来看，2-grams的效果比较好。

## 1.2 模块二：jieba_fast
使用 c 重写了jieba分词库中的核心函数，速度得到大幅提升。
特点
- 对两种分词模式进行的加速：精确模式，搜索引擎模式
- 利用cpython重新实现了 viterbi 算法，使默认带 HMM 的切词模式速度提升 60%左右
- 利用cpython重新实现了生成 DAG 以及从 DAG 计算最优路径的算法，速度提升 50%左右
- 基本只是替换了核心函数，对源代码的侵入型修改很少
- 使用import jieba_fast as jieba 可以无缝衔接原代码。

其中，
github：https://github.com/deepcs233/jieba_fast
代码示例：
```
# encoding=utf-8
import jieba_fast as jieba

text = u'在输出层后再增加CRF层，加强了文本间信息的相关性，针对序列标注问题，每个句子的每个词都有一个标注结果，对句子中第i个词进行高维特征的抽取，通过学习特征到标注结果的映射，可以得到特征到任>      意标签的概率，通过这些概率，得到最优序列结果'

print("-".join(jieba.lcut(text, HMM=True))
print('-'.join(jieba.lcut(text, HMM=False)))
```
与jieba基本一致
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200602145454628.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3NpbmF0XzI2OTE3Mzgz,size_16,color_FFFFFF,t_70)

## 1.3 关键词查询组件：flashtext

详情可参考笔者博客：[python︱flashtext高效关键词查找与替换](https://blog.csdn.net/sinat_26917383/article/details/78521871)

```
from flashtext import KeywordProcessor

def build_actree(wordlist):
    '''
        AC自动机进行关键词匹配
        构造AC trie
    '''
    actree = KeywordProcessor()
    for index, word in enumerate(wordlist):
        actree.add_keyword(word)     # 向trie树中添加单词
    #self.actree = actree
    return actree

def ac_detect(actree,text,span_info = True):
    '''
        AC自动机进行关键词匹配
        文本匹配
    '''
    region_wds = []
    for w1 in actree.extract_keywords(text,span_info = span_info):
        if len(w1) > 0:
            region_wds.append(w1[0])
    return region_wds

wordlist = ['健康','减肥']
text = '今天你减肥了吗，今天你健康了吗，减肥 = 健康！'
actree = build_actree(wordlist)
%time ac_detect(actree,text)

>>> CPU times: user 41 µs, sys: 0 ns, total: 41 µs
>>> Wall time: 47.2 µs
>>> ['减肥', '健康', '减肥', '健康']

```

---

# 2 颜文字检测与识别
之前文本较多的情况，很多颜文字都是当作停用词进行删除；也有一些对表情进行研究，但是颜文字比较麻烦的一点是，如果是特殊符号，☆，这类的只是一个字符，分词的时候可以分开；
但是颜文字会占用多个字符，分词的时候，自己就会分得非常分散`'↖', '(', '^', 'ω', '^', ')', '↗'`，这个问题就有点像新词发现中出现得问题，如何分词得到有效的实体，颜文字本身就是一种带有情感色彩的实体。
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200602150156830.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3NpbmF0XzI2OTE3Mzgz,size_16,color_FFFFFF,t_70)
所以比较理想的是不同的表情符号可以对应一些实体词，比如[颜文字网站](http://www.yanwenzi.com/zan/)中标记的一样。

## 2.1 颜文字检测
直接上代码来说明使用方式：

```
# 初始化
json_data = {'w(ﾟДﾟ)w': '啊啊', '(ノへ￣、)': '抽泣', '(￣_,￣ )': '蔑视'}
ywz = yanwenzi(json_data)
    
# 检测位置
text = 'w(ﾟДﾟ)w^O^佳^O^w(ﾟДﾟ)w'
ywz.detect(text,span_info=True)
# [('_啊啊_', 0, 7), ('_啊啊_', 14, 21)]
ywz.detect(text,span_info=False)
# ['_啊啊_', '_啊啊_']
ywz.ywz_replace(text)
# '_啊啊_^O^佳^O^_啊啊_'
```
该模块初始化的时候，需要将一些`{表情:属性}`作为输入，笔者这边自己整理了1800+，整理的一部分是抓取的，还有一部分是新颜文发现而补充进去的。初始化输入之后，就会将这些表情包作为关键词进行匹配，同时这里是不支持模糊匹配的，只能精准匹配，譬如`^O^`如果这边表情没有计入，则不会被匹配到。

这里可以看到，`detect`将表情包`w(ﾟДﾟ)w`变成了中文属性`_啊啊_`，因为`_`方便分词使用，其中参数`span_info`代表是否返回角标，便于定位该表情包的文字。

另外，`ywz_replace`是将文本中的表情包直接替换成中文字，并返回原文。


## 2.2 颜文字实体分词
```
ywz.jieba_cut(text)
#['_啊啊_', '^', 'O', '^', '佳', '^', 'O', '^', '_啊啊_']
```
初始化之后，分词其实就是`jieba.cut`，这里会分出`_啊啊_`这样的实体词。

---
# 3 新颜文字发现
上面的匹配都是精准匹配，所以需要新颜文字发现，来不断扩充颜文字词典。

## 3.1 新颜文字发现
```
text = '璇哥！加油↖(^ω^)↗'
ywz.yanwenzi_find(text,min_n = 2,remove_spacing = True)
>>> ['↖(^ω^)↗']
```
这里判定的逻辑还是比较简单的，是通过正则的方式，最少3个（min_n ）连续的特殊字符；

当然这里要深挖也可以参考：[如何精准地识别出文本中的颜文字？](https://www.zhihu.com/question/355169976)和[glove embedding时候的清洗逻辑](https://nlp.stanford.edu/projects/glove/preprocess-twitter.rb)

```
input = input
	.gsub(/https?:\/\/\S+\b|www\.(\w+\.)+\S*/,"<URL>")
	.gsub("/"," / ") # Force splitting words appended with slashes (once we tokenized the URLs, of course)
	.gsub(/@\w+/, "<USER>")
	.gsub(/#{eyes}#{nose}[)d]+|[)d]+#{nose}#{eyes}/i, "<SMILE>")
	.gsub(/#{eyes}#{nose}p+/i, "<LOLFACE>")
	.gsub(/#{eyes}#{nose}\(+|\)+#{nose}#{eyes}/, "<SADFACE>")
	.gsub(/#{eyes}#{nose}[\/|l*]/, "<NEUTRALFACE>")
	.gsub(/<3/,"<HEART>")
	.gsub(/[-+]?[.\d]*[\d]+[:,.\d]*/, "<NUMBER>")
	.gsub(/#\S+/){ |hashtag| # Split hashtags on uppercase letters
		# TODO: also split hashtags with lowercase letters (requires more work to detect splits...)

		hashtag_body = hashtag[1..-1]
		if hashtag_body.upcase == hashtag_body
			result = "<HASHTAG> #{hashtag_body} <ALLCAPS>"
		else
			result = (["<HASHTAG>"] + hashtag_body.split(/(?=[A-Z])/)).join(" ")
		end
		result
```


当有了单个表情识别，如果在比较多的文本下，就可以根据频次发现一些高频出现的表情包了：
```
corpus = ['d(ŐдŐ๑)crush', '♪ ٩(｡•ˇ‸ˇ•｡)۶', '〜(￣▽￣〜)', '木木╭(╯ε╰)╮', 'ToT(^(エ)^)', 'HLYS(ー`´ー)',
 'O(∩_∩)O', '(^^)笔尖', '璇哥！加油↖(^ω^)↗', '蜕变(^_^) \ufeff']
ywz_new_list = ywz.yanwenzi_new_discovery(corpus,min_n = 2,remove_spacing = True,topn = 200)
ywz_new_list

>>> [('(ŐдŐ๑)', 1), ('♪٩(｡•ˇ‸ˇ•｡)۶', 1), ('〜(￣▽￣〜)', 1), ('╭(╯ε╰)╮', 1),
 ('(^(エ)^)', 1), ('(ー`´ー)', 1), ('(∩_∩)', 1), ('(^^)', 1), ('↖(^ω^)↗', 1), ('(^_^)\ufeff', 1)]
```
其中,`remove_spacing `是否移除空格；`topn `一次性返回top多少的高频表情包


如果有新颜文要新增，那么需要新增到两个模块：分词模块 + 颜文识别模块，

```
# 新颜文添加到分词词典
yanwenzi_dict_list = [ynl[0] for ynl in ywz_new_list]
ywz.add_words(yanwenzi_dict_list,freq = 100,tag = 'ywz')

# 新颜文添加到检测词典
ywz.actree_add_word(yanwenzi_dict_list,tag = '颜文字')
```
当然这里遇到的问题，颜文字识别出来，是不带属性的（`{'↖(^ω^)↗':'_高兴_'}`），所以要么就是人工打标然后给入，当然也可以直接list方式，此时属性就会都指定为`_颜文字_`

## 3.2 颜文字属性识别
上面3.1提及到一个问题是新颜文字识别出来之后，没有附带上属性，就像实体词没有定义词性一样。
所以，这边通过求相似的方式来找到最相似的表情，将最相似的表情属性，继承过来。这边求相似的方式是使用`rouge`这是文本摘要评价指标。
从rouge的评分来看，rouge-1太粗糙；rouge-2比较合适，
且几个统计量中，f/p/r,f效果比较好，p/r可能会有比较多的选项，也就是差异性不明显

```
参数:
    - min_s = 0.35,阈值，一定要相似性大于才会给出；如果是'rouge-1'比较合适的阈值在0.75
    - score_type = 'rouge-2',rouge的得分类型,n-grams
    - stat = 'f',采用的统计量

统计量:
    text_a = '(^_^)'
    new_yanwenzi_find(text_a,min_s = 0.35)
    >>> [['(^&^)/', '噢耶',0.75]]

```
其中返回的是[最相似颜文字,中文属性,f值]



最后，
该想法到实践做的时间比较少，2天时间里面可能会出现很多瑕疵，
欢迎觉得网络表情需要深挖得网友，一起来演进~



