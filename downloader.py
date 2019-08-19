# coding:utf-8
import requests
import urllib
import json
import time
import random
import os
import para
import re
import traceback
from imp import reload

def ip_set(op):
    def wrapper(*args):
        para.ip = random.choices(para.ips)[0]
        while True:
            try:
                proxy = para.ip
                print(op.__name__)
                return op(*args)
            except:
                print(*args)
                traceback.print_exc()
                para.ip = random.choices(para.ips)[0]
                x_time = random.randint(2, 5)
                time.sleep(x_time)
                continue
    return wrapper


@ip_set
def get_book_list(level, term):
    '''
    STEP 1:
    get book list.
    Args:
        level: 年级
        term: 上下册
    Return:
        book_list: A list of dict
        {
            book_id:
            section_id:
            name: 书名
        }
    '''
    proxy = para.ip
    url = 'http://www.17zuoye.com/teacher/new/homework/sortbook.api'
    data = 'level={}&term={}&subject=MATH'.format(level, term)
    request = requests.get(url+"?"+data,headers=para.HEADERS, proxies=proxy)
    datas = request.json()
    if datas["success"] is True: 
        book_list = list()  
        for book_info in datas["rows"]:
            if re.search(r'人教版', book_info["name"]) is None:
                book = dict()
                book["book_id"] = book_info["id"]
                book["section_id"] = book_info["seriesId"]
                book["name"] = book_info["name"]
                book_list.append(book)
        return book_list
    else:
        print("ERROR:Get book list error")
        return


@ip_set
def get_keypoint_list(book_id, section_id):
    '''
    STEP 2:
    get keypoint list from unit list.
    Args:
        book_id: A parameter.
        section_id: A parameter.
    Return:
        unit_list: A list of dict
        {
            id:
            name: 单元名
            knowledgePoint:[
                id:
                name:知识点名
                typeId:
            ]
        }
    '''
    proxy = para.ip
    url = 'http://www.17zuoye.com/teacher/new/homework/objective/content.api'
    data = 'bookId={}&unitId=BKC_10200084434000&sections={}&type=MENTAL_ARITHMETIC&subject=MATH&objectiveConfigId=OCN_02582477972'.format(
        book_id, section_id
    )
    request = requests.get(url+"?"+data,headers=para.HEADERS, proxies=proxy)
    datas = request.json()
    if datas["success"] is True:
        unit_datas = datas["content"][0]["kpTrees"]
        unit_list = list()
        for _unit in unit_datas:
            unit = dict()
            unit["id"] = _unit["unitId"]
            unit["name"] = _unit["unitName"]
            unit["knowledgePoint"] = list()
            knowledgePoints = _unit["knowledgePoints"]
            for _kPoint in knowledgePoints:
                knowledgePoint = dict()
                knowledgePoint["id"] = _kPoint["kpId"]
                knowledgePoint["name"] = _kPoint["kpName"]
                knowledgePoint["typeId"] = _kPoint["contentTypeId"]
                unit["knowledgePoint"].append(knowledgePoint)
            unit_list.append(unit)
        return unit_list
    else:
        print("ERROR:Get unit list error")
        return


@ip_set
def get_question_list(contentTypeId, knowledgePoint, count=999):

    
    '''
    STEP 3:
    Get question list.
    Arg:
        contentTypeId: A parameter.
        knowledgePoint: A parameter.
        count: get question number.
    Return:
        question_list: A list of dict
        {
            typeId:
            id: question id.
        }
    '''
    proxy = para.ip
    url = 'http://www.17zuoye.com/teacher/new/homework/mental/question.api'
    data = 'contentTypeId={}&knowledgePoint={}&newQuestionCount={}'.format(
        contentTypeId, knowledgePoint, count
    )
    request = requests.post(url=url, data=data, headers=para.HEADERS, proxies=proxy)
    datas = request.json()
    if datas["success"] is True:
        question_list = list()
        for _question in datas["questions"]:
            question_list.append(_question["questionId"])
        if len(question_list) != len(set(question_list)):
            print("题目列表重复")
            input()
        return question_list
    else:
        print("ERROR:Get question list error")
        return


@ip_set
def get_question_info(ids):
    '''
    STEP 4:
    Get question information.
    Args:
        ids: A list include question id.
    return:
        question_info_list: A list of dict
        {
            content: 题目
            answer: 答案
        }
    '''
    proxy = para.ip
    question_info_list = list()
    for idss in ids:
        idstring = "[\"" + "\",\"".join(idss) + "\"]"
        url = 'https://www.17zuoye.com/exam/flash/load/newquestion/byids.api'
        data = '{"ids":' + str(idstring) + ',"containsAnswer":true}'
        data_u = urllib.parse.quote(data)
        request = requests.get(url+"?data="+data_u,headers=para.HEADERS, proxies=proxy)
        datas = request.json()
        if datas["success"] is True:
            for _info in datas["result"]:
                question_info = dict()
                content = _info["content"]["subContents"][0]
                question_info["content"] = content["content"]
                question_info["answer"] = _info["answers"]
                question_info_list.append(question_info)
        else:
            print("ERROR:Get question information error")
            print("检查未被限制后，按任意键继续爬虫。")
            input()
            reload(para)
            continue
    check_list = list()
    for _check in question_info_list:
        check_list.append(_check["content"])
    return question_info_list


def build_dir(level, book_name, unit_name):
    path = "./data/{}年级/{}/{}".format(
        str(level), str(book_name), str(unit_name)
    )
    if os.path.exists(path) is False:
        try:
            os.makedirs(path)
            print(path, "build succeed")
        except:
            print(path, "build error")
    return path


def question_downloader(level, term):
    book_list = get_book_list(level, term)
    for _book in book_list:
        book_name = _book["name"]
        print(book_name)
        book_id = _book["book_id"]
        section_id = _book["section_id"]
        unit_list = get_keypoint_list(book_id, section_id)
        for _unit in unit_list:
            unit_name = _unit["name"]
            for _keypoint in _unit["knowledgePoint"]:
                keypoint_name = _keypoint["name"]
                keypoint_id = _keypoint["id"]
                contentTypeId = _keypoint["typeId"]
                question_list = []
                question_list = get_question_list(
                    contentTypeId, keypoint_id)
                ids = [question_list[i:i+5] for i in range(0,len(question_list),5)]
                question_info_list = get_question_info(ids)
                path = build_dir(
                    level, book_name, unit_name
                )
                question_path = path + "/" + keypoint_name + ".txt"
                with open(question_path, "w") as file:
                    file.write(json.dumps(question_info_list))
                print(question_path, "write succeed")
                x_time = random.randint(15, 20)
                print("sleep", x_time)
                time.sleep(x_time)


if __name__ == "__main__":
    book_list = get_book_list(para.LEVEL,para.TERM)
    #k_list = get_keypoint_list("BK_10200001553794", "BKC_10200065042116")
    #ids = ["Q_10213973262920-1","Q_10213973240902-1","Q_10213973231658-1","Q_10213973192769-1","Q_10213973209380-1"]
    #output = get_question_info(ids)
    #print(get_question_list(0,"KP_10200115968402"))
    #print(output)    