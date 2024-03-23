from lxml import html
import csv
import re
import os
import json

"""берет html-страницу, возвращает словарь вида {лемма из онлайн-словаря: ссылка на pdf-страницу словаря}"""


def getlinks(relpath):
    linkdict = {}
    for f in os.listdir(relpath):
        page = open(relpath + f, 'r', encoding='windows-1251').read()
        tree = html.fromstring(page)

        # собирает леммы и ссылки со страницы
        lemmata = tree.xpath('//a[starts-with(@href, "/hist/xi-xvii/Vol")]/text()')
        links = tree.xpath('//a[starts-with(@href, "/hist/xi-xvii/Vol")]/@href')

        # меняет ссылки из онлайн-словаря на локальные ссылки
        loclinks = [re.sub('/hist/xi-xvii/', '/src/xi-xvii/pdf/', l) for l in links]

        for i in range(len(lemmata)):
            try:
                if lemmata[i] == '2':
                    linkdict.update({lemmata[i - 1]: (loclinks[i - 1], loclinks[i])})  # если слово на двух страницах,
                    # лемме приписываются ссылки на обе
                else:
                    lemmata[i] = re.sub('\d', '', lemmata[i]).lower()
                    linkdict.update({lemmata[i]: loclinks[i]})
            except IndexError:
                continue  # для некоторых слов нет ссылок на пдф

    del linkdict['']
    del linkdict[' ']
    # проверка двойных ссылок
    # print(linkdict['амбарное (онбарное)'])
    return linkdict


"""в словаре со ссылками заменяет леммы из онлайн-словаря на LemmaIndex по соотвертствиям в csv-файле"""


def onlinedict2lemma(linkdict, wl):
    linkdict2 = {}
    with open(wl, encoding='utf-8') as wl:
        wl_file = csv.reader(wl, delimiter=',')

        for row in wl_file:
            if row[3] == 'LemmaIndex':
                continue
            elif row[2] == '' or row[2] == ' ':
                continue
            else:
                try:
                    lemma = row[3]
                    link = linkdict[row[2].lower()]
                    linkdict2.update({lemma: link})
                except KeyError:
                    continue
                    # print(linkdict2['основание (-ье)'])
    return linkdict2


"""вставляет в json-файл со словарем ссылки на pdf страницы словаря 11-17"""


def insert_links(ld, js):
    with open(js, 'r', encoding='utf-8') as matched:
        data = json.load(matched)

    for key in data:
        '''
        try:
            del data[key]["XVII_link"]
        except KeyError:
            continue
        '''
        # print(data[key])
        if "XVII_lemma" in data[key]:
            try:
                link = ld[data[key]["XVII_lemma"]]
                data[key].update({'XVII_link': link})
            except KeyError:
                continue
    with open(js, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


"""общая функция"""


def update_js():
    ld = getlinks('../src/xi-xvii/html/')
    ld2 = onlinedict2lemma(ld, 'wordlist_linked.csv')
    insert_links(ld2, 'matched.json')


update_js()
