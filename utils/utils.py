import json
from fastapi import HTTPException
from schemas import ResultBase

from utils.checks import (
    check_if_duplicate_key, check_if_duplicate_src_targ,
    check_if_empty
    )


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
    ''' Если файл создан и в нем есть элементы то добавить в существующий файл '''
    with open(fileName, 'a+') as base_file:
        base_file.seek(0)
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
    

def delete(new_data, mainFile, fieldName, fileName):
    ''' Отметить node или edge для удаления '''

    ready_new_data = [{"key": key} for key in new_data]
    
    with open(fileName, "a+") as base_file:
        base_file.seek(0)
        old_data = base_file.readlines()
        if check_if_duplicate_key(
                old_data=old_data, 
                new_data=ready_new_data, 
                fieldName=fieldName,
                fileName=fileName) is True:
            raise HTTPException(
                    status_code=403, 
                    detail="Forbidden, already marked for deletion")
        [base_file.write(json.dumps(i) + "\n") for i in ready_new_data]


def submit_to_base_file(element, main, name):
    ''' Занести новые элементы в главный файл '''
    with open(main, "r+") as main_file:
        read_main_data = json.load(main_file)

        elements_base = open(element, "r").readlines()
        element_base = [json.loads(piece) for piece in elements_base]

        [read_main_data[name].append(piece) for piece in element_base]

        main_file.seek(0)
        json.dump(read_main_data, main_file, indent=2)


def clear_deleted(fileName, elmenetDeleted, name):
    ''' Очистить файлы помеченные для удаления из главного файла'''
    if check_if_empty(fileName=fileName) is True:
        return {'message': 'No data'}

    with open(fileName, 'r') as base_data:
        read_data = json.load(base_data)

        turn_to_json = lambda data : [json.loads(i) for i in data]
        get_deleted_keys = lambda data : [i["key"] for i in data]
        get_results = lambda data, name, deleted : \
            [element \
            for i, element in enumerate(data[name]) \
            if element["key"] not in deleted]

        element_deleted = open(elmenetDeleted).readlines()
        element_deleted = turn_to_json(element_deleted)
        element_deleted_keys = get_deleted_keys(element_deleted)

        return get_results(
            data=read_data, 
            name=name, 
            deleted=element_deleted_keys)