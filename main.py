# coding:utf-8
import downloader
import para
import random


if __name__ == "__main__":
    para.ip = random.choices(para.ips)[0]
    downloader.question_downloader(para.LEVEL, para.TERM)  