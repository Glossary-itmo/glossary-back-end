import os
import json


def check_if_duplicate_key(old_data, new_data, fieldName):
    """ Проверить если присланые ключи уже есть,
    True - есть дубликаты в новых данных
    False - нет дубликатов в новых данных"""

    extract = lambda data : list(map(lambda x : x["key"], data))

    # Check file extension
    if old_data.endswith(".txt"):
        old_data_temp = open(old_data, "r").readlines()
        old_data_ready = [json.loads(i) for i in old_data_temp]
    else:
        old_data_temp = json.load(open(old_data, "r"))
        old_data_ready = old_data_temp[fieldName]

    old_keys = extract(old_data_ready) 
    new_keys = extract(new_data)
    for key in new_keys:
        if key in old_keys:
            return True
    return False


def check_if_duplicate_src_targ(new_data, old_data, fileName):
    """ Проверить если присланные связи уже есть
    True - есть дубликаты новых связей
    False - нет дубликатов новых связей """

    # Взять указаное "field" поле из "data" и записать в лист "x" и вернуть из lambda функции
    # в переменную "extract"
    extract = lambda data, field : list(map(lambda x : x[field], data))

    temp_new_data = zip(
            extract(new_data, "source"), 
            extract(new_data, "target"))
    temp_old_data = zip(
            extract([json.loads(i) for i in old_data], "source"), 
            extract([json.loads(i) for i in old_data], "target"))
    temp_old_data_reverse = zip(
            extract([json.loads(i) for i in old_data], "target"),
            extract([json.loads(i) for i in old_data], "source")) 

    for data in temp_new_data:
        if data in temp_old_data or data in temp_old_data_reverse:
            return True

    return False


def check_if_empty(fileName):
    """ Проверить что json пустой,
    пустой - True
    не пустой - False"""

    # check if size of file is 0
    if os.stat(fileName).st_size == 0:
        return True
    return False