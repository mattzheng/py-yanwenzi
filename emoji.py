
# 测试Emoji表情符号包Emojis的功能

import emoji
print(emoji.emoji_count('Python is fun 👍'))


# ---

from collections import defaultdict
import re

frequencies = defaultdict(int)

#判断是否是表情
def isEmoji(content):
    if not content:
        return False
    if u"\uE000" <= content and content <= u"\uE900":
        return True
    if u"\U0001F000" <= content and content <= u"\U0001FA99":
        return True
    #以下代码被上面的范围包含了
    if u"\U0001F600" <= content and content <= u"\U0001F64F":
        return True
    elif u"\U0001F300" <= content and content <= u"\U0001F5FF":
        return True
    elif u"\U0001F680" <= content and content <= u"\U0001F6FF":
        return True
    elif u"\U0001F1E0" <= content and content <= u"\U0001F1FF":
        return True
    else:
        return False


content = "👍"
isEmoji(content)
# True
content = "python is 👍"
isEmoji(content)
# False


'''
获取SoftBank与WeChat的Emoji映射表
'''

from collections import defaultdict

frequency = defaultdict(int)
frequency1 = defaultdict(int)
frequency2 = defaultdict(int)

def getReflactTbl(filename):
    frequencies = defaultdict(int)
    with open(filename, 'r', encoding='utf-8-sig') as f:
        for line in f:
            line = line.split()
            frequencies[line[0]] = line[1]
        print(frequencies)
    return frequencies

def getStandordTbl(filename):
    frequency1 = defaultdict(int)
    with open(filename, 'r', encoding='utf-8-sig') as f:
        for newline in f:
            while newline.find('fully-qualified     # ') > -1 or newline.find('; non-fully-qualified # ') > -1:
                startpos = newline.find('# ') + 2
                # print(startpos)
                endpos = newline.find(' ', startpos + 1)
                # print(endpos)
                meaning = newline[startpos:endpos]
                emoji_value = newline[endpos + 1:len(newline)]
                emoji_value = meaning.encode('unicode-escape').decode('utf-8').replace('\\U','').upper()
                frequency1[meaning] = emoji_value.replace('\n', '')
                newline = f.readline()
    print(frequency1)
    return frequency1
def getWechatTbl(filename):
    frequency2 = defaultdict(int)
    with open(filename, 'r', encoding='utf-8-sig') as f:
        for newline in f:
            while newline.find('fully-qualified     # ') > -1 or newline.find('; non-fully-qualified # ') > -1:
                startpos = newline.find('# ') + 2
                # print(startpos)
                endpos = newline.find(' ', startpos + 1)
                # print(endpos)
                emoji_value = newline[startpos:endpos]
                meaning = emoji_value.encode('unicode-escape').decode('utf-8').replace('\\u','').upper()
                frequency2[meaning] = emoji_value
                newline = f.readline()
    print(frequency2)
    return frequency2
frequency = getReflactTbl('data\emoji.txt')
frequency1 = getStandordTbl('data\emoji-test.txt')
frequency2 = getWechatTbl('data\emoji-wechat.txt')





import re


def identifyEmoji(desstr):
    '''
    识别表情
    '''

    co = re.compile(r'\\u\w{4}|\\U\w{8}')
    print(co.findall(desstr))
    if len(co.findall(desstr)):
        return True
    else:
        return False



print(u'\U00010000')
a = '😁'.encode('unicode-escape').decode('utf-8')
print(a)
print(identifyEmoji(a))



'''
ustring = unicode('好','utf-8')
#print(a.unicode())

# 直接定义unicode字符串，通过在字符串前加 u 的方式
unicodestring = u"Hello world"

utf8string = '好人'  # 可以这样直接写，是因为在py文件的开头写了 #encoding=utf-8, 这样在整个py
# 文件中，所有的字符串的编码编码方式都设置为了utf-8

# 将某种字符集编码的字符串转化为unicode字符串， 即“解码”
ustring = unicode(utf8string, "utf-8")

ustring  # 输出 u'\u597d\u4eba'
print(type(ustring))  # 输出 <type 'unicode'>

# 将unicode字符串转化为某种字符集编码的字符串，即“编码”
unicodestring.encode("utf-8")
ustring.encode('utf-8')

print(ustring.encode('utf-8'))  # 输出 好人， 解码到unicode和从unicode编码的字符集相同
print(ustring.encode('gbk'))  # 输出乱码 濂戒汉， 解码到unicode和从unicode编码的字符集不同

#'''



