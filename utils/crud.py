import json
from fastapi import HTTPException
from schemas import ResultBase

from file_names import file_name
from routers import file_name
from utils.checks import (
    check_if_duplicate_key, check_if_duplicate_src_targ,
    check_if_empty
)


def get_data(fileName, nodeDeleted, edgeDeleted):
    ''' Получить все что есть в главном файле за исключением помеченного на удаление '''

    node_name = "nodes"
    edge_name = "edges"

    with open(fileName, "r+") as base_data:
        read_file = json.load(base_data)
        read_file[node_name] = clear_deleted(
            fileName=fileName,
            elementDeleted=nodeDeleted,
            name=node_name).copy()
        read_file[edge_name] = clear_deleted(
            fileName=fileName,
            elementDeleted=edgeDeleted,
            name=edge_name).copy()

        return read_file


def create_file(fileName):
    """ В случае если нет файла json или он пустой создать json и его базовые состовляющие"""

    with open(fileName, "w+") as base_file:
        # Взять ResultBase и конвертировать её в json и записать в файл
        base = json.loads(ResultBase().json())
        json.dump(base, base_file, indent=2)


def post_data(data, write_to, mainFile, fileName, fileDeleted):
    ''' Если файл создан и в нем есть элементы то добавить в существующий файл '''

    with open(fileName, 'a+') as base_file:
        base_file.seek(0)
        read_data = base_file.readlines()
        new_data = [i.dict() for i in data]

        files_to_check = [mainFile, fileName, fileDeleted]
        for file in files_to_check:
            if check_if_duplicate_key(
                    old_data=file,
                    new_data=new_data,
                    fieldName=write_to)\
                    is True:
                raise HTTPException(
                    status_code=403,
                    detail=f"Forbidden, already exists in { file }")

            if write_to == "edges":
                # Check duplicates source-target pair
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


def clear_deleted(fileName, elementDeleted, name):
    ''' Очистить файлы помеченные для удаления из главного файла'''

    # print(fileName)
    if check_if_empty(fileName=fileName) is True:
        return {'message': 'No data'}

    if fileName == file_name("main"):
        with open(fileName, 'r') as base_data:
            read_data = json.load(base_data)

            def turn_to_json(data): return [json.loads(i) for i in data]
            def get_deleted_keys(data): return [i["key"] for i in data]

            def get_results(data, name, deleted): return \
                [element for i, element in enumerate(data[name])
                 if element["key"] not in deleted]

            element_deleted = open(elementDeleted).readlines()
            element_deleted = turn_to_json(element_deleted)
            element_deleted_keys = get_deleted_keys(element_deleted)

            return get_results(
                data=read_data,
                name=name,
                deleted=element_deleted_keys)


def submit_to_base_file(element, element_deleted, main, name):
    ''' Занести новые элементы в главный файл '''

    with open(main, "r+") as main_file:
        # clear_deleted(fileName=main, elementDeleted=element, name=name)
        read_main_data = json.load(main_file)

        elements_base = open(element, "r").readlines()
        element_base = [json.loads(piece) for piece in elements_base]

        # clear_deleted(fileName=element_deleted, elementDeleted=element, name=name)

        [read_main_data[name].append(piece) for piece in element_base]

        main_file.seek(0)
        open(main, "w").close() # Supposedly to clear the main file
        json.dump(read_main_data, main_file, indent=2)
