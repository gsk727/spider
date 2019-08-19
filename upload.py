import os
import json
import re
import traceback
import requests
from bs4 import BeautifulSoup
import pymysql
import id_set
import html

db = pymysql.connect("127.0.0.1", "root", "123456", "KouSuan")
cursor = db.cursor()
id_set1 = id_set.IdSet(dataID="01")
id_set2 = id_set.IdSet(dataID="02")
id_set3 = id_set.IdSet(dataID="03")
id_set4 = id_set.IdSet(dataID="04")
id_set5 = id_set.IdSet(dataID="05")


def full2half(ustr):
    half = ""
    for u in ustr:
        num = ord(u)
        if num == 0x3000:    # 全角空格变半角
            num = 32
            print('Found something.')
        elif 0xFF01 <= num <= 0xFF5E:
            num -= 0xfee0
        u = chr(num)    # to unicode
        half += u
    return half
    

def read_file(file,id_set):
    text = file.read()
    json_in = json.loads(text)
    if json_in is None:
        success = False
        question_list = None
    else:
        question_list = list()
        for _info in json_in:
            question = dict()
            question["id"] = int(id_set.get_id())
            question["content"] = format(_info["content"])
            answer = _info["answer"]
            for _i in range(len(answer)):
                for _j in range(len(answer[_i])):
                    answer[_i][_j] = full2half(html.unescape(answer[_i][_j]))
            question["answer"] = answer
            question_list.append(question)
        success = True
    return success, question_list


def format(content):
    bs = BeautifulSoup(content, "html.parser")
    if bs.div is None:
        for _img in bs.find_all("img"):
            tex = BeautifulSoup("", "html.parser").new_tag("tex")
            tex.string = "\\" + _img["latex"]
            _img.replace_with(tex)
    strs = str(bs)
    return strs


def upload(sql): 
    try:
        cursor.execute(sql)
        db.commit()
    except:
        traceback.print_exc()
        print(sql)
        db.rollback()


def upload_grade(name):
    if name == "1年级":
        ids = 1
    elif name == "2年级":
        ids = 2
    elif name == "3年级":
        ids = 3
    elif name == "4年级":
        ids = 4
    elif name == "5年级":
        ids = 5
    elif name == "6年级":
        ids = 6
    sql = "INSERT INTO grades(id,name)VALUES('%d','%s')" % \
          (ids, name)
    upload(sql)
    return ids


def upload_section(name, u_id, id_set):
    d_id = id_set.get_id()
    d_id = int(d_id)
    name_end = re.search(r'.txt', name).span()[0]
    name = name[:name_end]
    sql = "INSERT INTO sections(id,name,unit_id)VALUES('%d','%s','%s')" % \
          (d_id, name, u_id)
    upload(sql)
    return d_id


def upload_book(name, grade, id_set):
    b_id = id_set.get_id()
    b_id = int(b_id)
    ebag_id = get_ebag_id(name, grade)
    sql = "INSERT INTO books(id,name,ebag_id)VALUES('%d','%s','%d')" % \
          (b_id, name, ebag_id)
    upload(sql)
    return b_id


def upload_unit(name, id_set, b_id):
    u_id = id_set.get_id()
    u_id = int(u_id)
    sql = "INSERT INTO units(id,name,book_id)VALUES('%d','%s','%d')" % \
          (u_id, name, b_id)
    upload(sql)
    return u_id


def upload_answer(question, g_id, b_id, u_id, s_id):
    q_id = question["id"]
    content = question["content"]
    answer = json.dumps(question["answer"])
    sqls = "SELECT content FROM questions \
    WHERE section_id = %s" % (s_id)
    cursor.execute(sqls)
    results = cursor.fetchall()
    for row in results:
        if row[0] == content:
            return
    sql = "INSERT INTO questions(id,content,answer,grade_id, \
        book_id,unit_id,section_id)VALUES('%d','%s','%s', \
        '%d','%d','%d','%d')" % (q_id, content, answer,
                                    g_id, b_id,
                                    u_id, s_id)
    upload(sql)


def get_ebag_id(bookname, grade, stage='xiaoxue', subject=2, sn='ebagtest', count=0):
    ebag_id = 0
    ename = re.match(r'.*?(.*制|版)', bookname).group()
    if ename == '北师版':
        ename = '北师大版'
    elif ename == '景山版':
        ename = '北京景山版'
    elif ename == '西师版':
        ename = '西南师大版'
    term = re.search(r'.年级[上,下]', bookname).group()
    url = "http://eschoolbag.readboy.com:8000/api/books"
    data = {'stage': stage, 'grade': grade, 'subject': subject,
            'ename': ename, 'sn': sn, 'count': count}
    request = requests.get(url, params=data)
    json = request.json()
    for _index in json['data']['book']:
        if re.search(term, _index['name']):
            ebag_id = _index["id"]
    return ebag_id


def upload_answers(question_list, grade_id, book_id, unit_id, section_id):
    new_question_list = list()
    for _question in question_list:
        flag = False
        for _new_question in new_question_list:
            if _new_question["content"] == _question["content"]:
                flag = True
                break
        if flag is False:
            new_question_list.append(_question)
    for _new_question in new_question_list:
        upload_answer(_new_question, grade_id, book_id, unit_id, section_id)


if __name__ == "__main__":
    work_dir = "./data"
    for _grade in os.listdir(work_dir):
        grade_id = upload_grade(_grade)
        grade_dir = work_dir + "/" + _grade
        for _book in os.listdir(grade_dir):
            book_id = upload_book(_book, grade_id, id_set4)
            book_dir = grade_dir + "/" + _book
            for _unit in os.listdir(book_dir):
                unit_id = upload_unit(_unit, id_set5, book_id)
                unit_dir = book_dir + "/" + _unit
                for _section in os.listdir(unit_dir):
                    section_dir = unit_dir + "/" + _section
                    with open(section_dir) as file:
                        try:
                            success, question_list = read_file(file, id_set1)
                        except:
                            traceback.print_exc()
                            print(section_dir)
                        if success is True:
                            section_id = upload_section(_section, unit_id, id_set2)
                            upload_answers(question_list, grade_id,
                                            book_id, unit_id,
                                            section_id)
                        else:
                            continue
    '''
    with open("./data/6年级/人教版六年级上（新版）/第三单元 分数除法/分数乘法分配律.txt") as file:
        _, r = read_file(file, id_set1)
        s = upload_answers(r, 1, 1, 1, 1)
        print(r)
        print(len(s))
  '''
'''
-- auto-generated definition
create table books
(
  id      char(16) not null
    primary key,
  name    text     null,
  ebag_id char(16) null
)
  charset = utf8;


-- auto-generated definition
create table questions
(
  id         char(16) not null    primary key,
  content    text     null,
  answer     text     null,
  grade_id   int      null,
  book_id    char(16) null,
  unit_id    char(16) null,
  section_id char(16) null
)
  charset = utf8;

-- auto-generated definition
create table sections
(
  id      char(16) not null
    primary key,
  name    text     null,
  unit_id char(16) null
)
  charset = utf8;


-- auto-generated definition
create table units
(
  id      char(16) not null    primary key,
  name    text     null,
  book_id char(16) null
)
  charset = utf8;
'''