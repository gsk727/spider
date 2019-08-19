# coding:utf-8
# 参数文件
import json

LEVEL = 3  # 年级
TERM = 1  # 1上册2下册
COOKIE = 'lupld=1; voxauth=JiU/QoAUua3bCs5qkKBbY5aqfPBOO/nRLmxplumBOe8jYJDTO2fMCP2WEiemB6b/RnHZjD2m1Z8iDQqqHz/rPg; va_sess=JiU/QoAUua3bCs5qkKBbY5aqfPBOO/nRLmxplumBOe8jYJDTO2fMCP2WEiemB6b/RnHZjD2m1Z8iDQqqHz/rPg; uid=14823108; ugcxxAty=1'
UA = 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
path = "./zhixueips.txt"
HEADERS = {
    'Cookie': COOKIE,
    'User-Agent': UA,
    'content-type': 'application/x-www-form-urlencoded',
}
with open(path, 'r') as file:
    ips = json.load(file)

ip = ips[1]