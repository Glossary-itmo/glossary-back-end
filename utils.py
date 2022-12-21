import os
import json
from fastapi import HTTPException

from schemas import ResultBase



def check_if_duplicate_key(old_data, new_data, fieldName, fileName):
    """ Проверить если присланые ключи уже есть,
    True - есть дубликаты в новых данных
    False - нет дубликатов в новых данных"""

    extract = lambda data : list(map(lambda x : x["key"], data))
    old_keys = extract([json.loads(i) for i in old_data]) 
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


def create_file(data, write_to, fileName):
    """ В случае если нет файла json или он пустой создать json и его базовые состовляющие"""

    with open(fileName, "w+") as base_file:
        
        if fileName == "main":
            # Взять ResultBase и конвертировать её в json
            base = json.loads(ResultBase().json())

            # Записать ResultBase в base_file
            json.dump(base, base_file, indent=2)

        new_data = [i.dict() for i in data]

        for i, ready_data in enumerate(new_data):
            if (len(new_data) - 1) == i:
                base_file.write(json.dumps(ready_data))
            else:
                base_file.write(json.dumps(ready_data) + "\n")
        return base_file


def post_data(data, write_to, fileName):
    with open(fileName, 'a+') as base_file:
        base_file.seek(0)

        # read_data = json.load(base_file)
        read_data = base_file.readlines()
        new_data = [i.dict() for i in data]


        if check_if_duplicate_key(
                old_data=read_data, 
                new_data=new_data, 
                fieldName=write_to,
                fileName=fileName) is True:
            raise HTTPException(
                    status_code=403, 
                    detail="Forbidden, already exists")
        if write_to == "edges":
            if check_if_duplicate_src_targ(
                old_data=read_data, 
                new_data=new_data,
                fileName=fileName) is True:
                raise HTTPException(
                        status_code=403, 
                        detail="Forbidden, this direction already exists")


        for i, ready_data in enumerate(new_data):
            if len(new_data) == 1:
                base_file.write("\n" + json.dumps(ready_data))
            elif (len(new_data) - 1) == i:
                base_file.write(json.dumps(ready_data))
            elif i == 0:
                base_file.write("\n" + json.dumps(ready_data) + "\n")
            else:
                base_file.write(json.dumps(ready_data) + "\n")
        return base_file
    

def check_if_empty(fileName):
    """ Проверить что json пустой,
    пустой - True
    не пустой - False"""

    # check if size of file is 0
    if os.stat(fileName).st_size == 0:
        return True
    return False
    

def delete(new_data, mainFile, fieldName, fileName):
    ready_new_data = []
    [ready_new_data.append({"key": key}) for key in new_data]
    
    with open(fileName, "a+") as base_file:
        old_data = base_file.readlines()
        print(old_data)
        if check_if_duplicate_key(
                old_data=old_data, 
                new_data=ready_new_data, 
                fieldName=fieldName,
                fileName=fileName) is True:
            raise HTTPException(
                    status_code=403, 
                    detail="Forbidden, already exists")
        print(1)
        [base_file.write(json.dumps(i) + "\n") for i in ready_new_data]
