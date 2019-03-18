"""Скрипт, который идёт по двум словарям и метчит их. Работает очень долго. Результат записывается в prematched.json.

Пояснение: Idle это не запускает, запускать можно просто интерпретатором python3.
Внешние зависимости: cython3.
Переменные:
    avanesov: dict
        JSON со словарём Аванесова.
    CPU_CORES: int
        Количество ядер процессора (меньше четырёх не рекомендую).
    lengt: int
        Количество статей в словаре Аванесова, нужно для отображения прогресса.
    pool:
        Пул процессов.
    matched:
        Итоговый словарь.

Функции:
    split_dict(dict, int)
        Делит словарь на n частей.
    match_(dict)
        Функция на языке Cython из модуля match_cython. Принимает часть словаря Аванесова (или весь словарь),
        возвращает словарь, где для всех (по возможности) лемм были найдены соответствия из словаря XI-XVII.
"""
__author__ = "Michael Voronov, Anna Sorokina"
__license__ = "GPLv3"

#Библиотеки для чтения исходных файлов
import json
import pandas

#С помощью Cython компилируем match_cython.pyx
import pyximport; pyximport.install()
import match_cython

#Библиотеки для распоточивания задач
from multiprocessing import Pool, cpu_count
import os

def split_dict(d, n):
    it = list(d.items())
    lent = len(it)
    avg = lent / float(n)
    out = []
    last = 0.0

    while last < lent:
        out.append(it[int(last): int(last + avg)])
        last += avg
    dicts = []
    for items in out:
        dicts.append({key: value for key, value in items})
    return dicts

'''
┌————————————————————————————————————┐
│ Читаем исходные файлы двух словарей│
└————————————————————————————————————┘
—————————————————————————————————————————————————————————————————————————————————————┐
'''

with open('avanesov2.json', 'r', encoding='utf-8') as f:
    avanesov = json.loads(f.read())

match_cython.shit = pandas.read_csv('wordlist_linked.csv', delimiter=',', header=0)

match_cython.x11 = list(match_cython.shit.LemmaIndex)

'''
—————————————————————————————————————————————————————————————————————————————————————┘
┌———————————————————————————————————————————————————————————┐
│ Делим словарь Аванесова на столько частей, сколько потоков│
└———————————————————————————————————————————————————————————┘
—————————————————————————————————————————————————————————————————————————————————————┐
'''

avanesovs = split_dict(avanesov, CPU_CORES)

'''
—————————————————————————————————————————————————————————————————————————————————————┘
┌——————————————————————————————————————————————————————————┐
│ 1. Создаём пул процессов                                 │
│ 2. Обрабатываем часть словаря Аванесова на каждом потоке │
└——————————————————————————————————————————————————————————┘
—————————————————————————————————————————————————————————————————————————————————————┐
'''

CPU_CORES = cpu_count()

match_ = match_cython.match_

lengt = len(avanesov)
print('Total:')
print(lengt)

pool = Pool(processes=CPU_CORES)
matches = pool.map(match_, avanesovs)
matched = {}

'''
—————————————————————————————————————————————————————————————————————————————————————┘
┌—————————————————————————————————————————————————┐
│ Склеиваем словарь и сохраняем в prematched.json │
└—————————————————————————————————————————————————┘
—————————————————————————————————————————————————————————————————————————————————————┐
'''

for d in matches:
    matched = {**matched, **d}

with open('prematched.json', 'w') as f:
    json.dump(matched, f, indent=4, ensure_ascii=False)

'''
—————————————————————————————————————————————————————————————————————————————————————┘
'''


