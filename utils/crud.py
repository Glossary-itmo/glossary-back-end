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
        read_file[node_name] = clear_deleted(fileName=fileName,
                                             elementDeleted=nodeDeleted,
                                             name=node_name).copy()
        read_file[edge_name] = clear_deleted(fileName=fileName,
                                             elementDeleted=edgeDeleted,
                                             name=edge_name).copy()

        return read_file


def create_file(fileName):
    """ В случае если нет файла json или он пустой создать json и его базовые составляющие"""

    if fileName == file_name("main"):
        with open(fileName, "w+") as base_file:
            # Взять ResultBase и конвертировать её в json и записать в файл
            base = json.loads(ResultBase().json())
            json.dump(base, base_file, indent=2)
    else:
        open(fileName, "w").close()


def post_data(data, write_to, mainFile, fileName, fileDeleted):
    ''' Если файл создан и в нем есть элементы то добавить в существующий файл '''

    with open(fileName, 'a+') as base_file:
        base_file.seek(0)
        read_data = base_file.readlines()
        new_data = [i.dict() for i in data]

        files_to_check = [mainFile, fileName, fileDeleted]
        for file in files_to_check:
            if check_if_empty(file) is True:
                create_file(file)
            if check_if_duplicate_key(old_data=file,
                                      new_data=new_data,
                                      fieldName=write_to) is True:
                raise HTTPException(status_code=403,
                                    detail=f"Forbidden, already exists in { file }")

            if write_to == "edges":
                if check_if_duplicate_src_targ(old_data=file,
                                               new_data=new_data,
                                               fileName=fileName,
                                               fieldName=write_to) is True:
                    raise HTTPException(status_code=403,
                                        detail="Forbidden, this direction already exists")

        [base_file.write(json.dumps(ready_data) + "\n")
         for i, ready_data in enumerate(new_data)]
        return base_file


def delete(new_data, mainFile, secondaryFile, fieldName, fileName):
    ''' Отметить node или edge для удаления '''

    ready_new_data = [{"key": key} for key in new_data]
    main_and_secondary = [mainFile, secondaryFile]

    with open(fileName, "a+") as base_file:
        if check_if_duplicate_key(old_data=fileName,
                                  new_data=ready_new_data,
                                  fieldName=fieldName) is True:
            raise HTTPException(status_code=403,
                                detail="Forbidden, already marked for deletion")

        for file in main_and_secondary:
            print(file)
            if check_if_duplicate_key(old_data=file,
                                      new_data=ready_new_data,
                                      fieldName=fieldName) is True:
                [base_file.write(json.dumps(i) + "\n") for i in ready_new_data]
                return
            else:
                raise HTTPException(status_code=404,
                                    detail="Not found")


def clear_deleted(fileName, elementDeleted, name):
    ''' Очистить файлы помеченные для удаления из главного файла'''

    # Lambdas
    turn_to_json = lambda data: [json.loads(i) for i in data]
    get_deleted_keys = lambda data: [i["key"] for i in data]
    get_results = lambda data, deleted: [element for i, element
                                         in enumerate(data)
                                         if element["key"] not in deleted]

    # Execution
    if check_if_empty(fileName=fileName) is True:
        return {}

    # Check file extension
    if fileName.endswith(".txt"):
        file_name_temp = open(fileName, "r").readlines()
        file_name_ready = [json.loads(i) for i in file_name_temp]
    else:
        file_name_temp = json.load(open(fileName, "r"))
        file_name_ready = file_name_temp[name]

    element_deleted = open(elementDeleted).readlines()
    element_deleted = turn_to_json(element_deleted)
    element_deleted_keys = get_deleted_keys(element_deleted)

    return get_results(data=file_name_ready,
                       deleted=element_deleted_keys)


def submit_to_base_file(elements, elements_deleted, main, names):
    ''' Занести новые элементы в главный файл '''

    with open(main, "r+") as main_file:
        read_main_data = json.load(main_file)

        merge = lambda main, secondary: [
            main.append(i) for i in secondary]

        ready_secondary = json.loads(ResultBase().json())

        for i, name in enumerate(names):
            # Clear main
            # if check_if_empty(main) is True: return
            read_main_data[name].clear()
            read_main_data[name] = clear_deleted(fileName=main,
                                                 elementDeleted=elements_deleted[i],
                                                 name=name).copy()

            # Clear secondary
            ready_secondary[name] = clear_deleted(fileName=elements[i],
                                                  elementDeleted=elements_deleted[i],
                                                  name=name).copy()

            # Merge the two
            merge(main=read_main_data[name], secondary=ready_secondary[name])

        open(main, 'w').close()
        main_file.seek(0)
        json.dump(read_main_data, main_file, indent=2)
        [open(element, 'w').close() for element in elements]
