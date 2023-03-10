import os
import json


# Взять указанное "field" поле из "data" и записать в лист "x" и вернуть из lambda функции
# в переменную "extract_field"
extract_field = lambda data, field: list(map(lambda x: x[field], data))


def check_if_txt_and_return(fileName, fieldName):
    ''' Проверить если fileName имеет расширение .txt,
    загрузить соответствующим образом данные и вернуть их '''
    
    # Взять указанное "field" поле из "data" и записать в лист "x" и вернуть из lambda функции
    # в переменную "extract"
    # Check file extension
    if fileName.endswith(".txt"):
        old_data_temp = open(fileName, "r").readlines()
        return [json.loads(i) for i in old_data_temp]
    else:
        old_data_temp = json.load(open(fileName, "r"))
        return old_data_temp[fieldName]


def extract_new_old(new_data, old_data, fieldName):

    temp_new_data = list(zip(
        extract_field(new_data, "source"),
        extract_field(new_data, "target")))
    temp_old_data = list(zip(
        extract_field([i for i in check_if_txt_and_return(fileName=old_data, fieldName=fieldName)], "source"),
        extract_field([i for i in check_if_txt_and_return(fileName=old_data, fieldName=fieldName)], "target")))
    temp_old_data_reverse = list(zip(
        extract_field([i for i in check_if_txt_and_return(fileName=old_data, fieldName=fieldName)], "target"),
        extract_field([i for i in check_if_txt_and_return(fileName=old_data, fieldName=fieldName)], "source")))
    return temp_new_data, temp_old_data, temp_old_data_reverse


def check_if_duplicate_key(old_data, new_data, fieldName):
    """ Проверить если присланные ключи уже есть,
    True - есть дубликаты в новых данных
    False - нет дубликатов в новых данных"""

    old_keys = extract_field(check_if_txt_and_return(fileName=old_data, fieldName=fieldName), "key")
    new_keys = extract_field(new_data, "key")

    for key in new_keys:
        if key in old_keys:
            return True
    return False


def check_if_duplicate_src_targ(new_data, old_data, fileName, fieldName, nodes):
    """ Проверить если присланные связи уже есть
    True - есть дубликаты новых связей
    False - нет дубликатов новых связей
    2 - source или target не найдены в существующих нодах """

    temp_new_data, temp_old_data, temp_old_data_reverse = extract_new_old(
        new_data=new_data, old_data=old_data, fieldName=fieldName)

    temp_old_node_keys = []
    for name in nodes:
        temp_old_node_keys += list(
            extract_field([i for i in check_if_txt_and_return(fileName=name, fieldName="nodes")], "key"))

    for data in temp_new_data:
        if data in temp_old_data or data in temp_old_data_reverse:
            return True
        if data[0] not in temp_old_node_keys or data[1] not in temp_old_node_keys:
            return 2

    return False


def check_if_empty(fileName):
    """ Проверить что json пустой,
    пустой - True
    не пустой - False"""

    # check if size of file is 0
    if os.stat(fileName).st_size == 0:
        return True
    return False
