import json
import uuid
from fastapi import HTTPException
from schemas import ResultBase

from file_names import file_name
from routers import file_name
from utils.checks import (
    check_if_duplicate_key, check_if_duplicate_src_targ,
    check_if_empty
)
from utils.misc import clear_deleted, cascade_delete


def get_data(names, fileName, secondaries, secondaryDeleted):
    ''' Получить все что есть в главном файле за исключением помеченного на удаление '''
    
    read_and_turn_to_json = lambda to_read : [json.loads(i) for i in open(to_read, "r").readlines()]

    with open(fileName, "r+") as base_data:
        read_file = json.load(base_data)
        
        
        for i, name in enumerate(names):
            new_data = read_and_turn_to_json(to_read=secondaries[i])
            read_file[name] = clear_deleted(fileName=fileName,
                                            elementDeleted=secondaryDeleted[i],
                                            name=names[i]).copy()

            [read_file[name].append(i) for i in new_data]

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

    ### Подменить значение key на uuid
    key_to_uuid = lambda data : [key.update({"key": uuid.uuid4().hex}) for key in data]

    with open(fileName, 'a+') as base_file:
        new_data = [i.dict() for i in data]

        nodes = [file_name("main"), file_name("node")]
        files_to_check = [mainFile, fileName, fileDeleted]
        for file in files_to_check:
            if check_if_empty(file) is True:
                create_file(file)
            if check_if_duplicate_key(old_data=file,
                                      new_data=new_data,
                                      fieldName=write_to) \
                    is True:
                raise HTTPException(status_code=403,
                                    detail=f"Forbidden, already exists in { file }")

            if file == fileDeleted:
                break

            if write_to == "edges":
                if check_if_duplicate_src_targ(old_data=file,
                                               new_data=new_data,
                                               fileName=fileName,
                                               fieldName=write_to,
                                               nodes=nodes) is True:
                    raise HTTPException(status_code=403,
                                        detail="Forbidden, this direction already exists")
                elif check_if_duplicate_src_targ(old_data=file,
                                                 new_data=new_data,
                                                 fileName=fileName,
                                                 fieldName=write_to,
                                                 nodes=nodes) == 2:
                    raise HTTPException(status_code=404,
                                        detail="No corresponding node is found")

        key_to_uuid(data=new_data)

        [base_file.write(json.dumps(ready_data, ensure_ascii=False) + "\n")
         for i, ready_data in enumerate(new_data)]
        return base_file


def edit_data(data, write_to, mainFile, fileName, fileDeleted):
    pass


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
            if check_if_duplicate_key(old_data=file,
                                      new_data=ready_new_data,
                                      fieldName=fieldName) is True:
                # Записать данные в файл и закончить выполнение функции
                [base_file.write(json.dumps(i) + "\n") for i in ready_new_data]
                if secondaryFile == file_name("node"):
                    cascade_delete(
                        new_data=ready_new_data,
                        old_data=get_data(
                            names=["nodes", "edges"], 
                            fileName=mainFile, 
                            secondaries=[file_name("node"), file_name("edge")], 
                            secondaryDeleted=[file_name("node_delete"), file_name("edge_delete")]))
                return
            else:
                raise HTTPException(status_code=404,
                                    detail="Not found")


def submit_to_base_file(elements, elements_deleted, main, names):
    ''' Занести новые элементы в главный файл '''

    with open(main, "r+") as main_file:
        read_main_data = json.load(main_file)

        merge = lambda main, secondary: \
            [main.append(i) for i in secondary]

        ready_secondary = json.loads(ResultBase().json())

        for i, name in enumerate(names):
            # Clear main
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

        # Clear main file, dump everything into it and clear secondary files
        open(main, 'w').close()
        main_file.seek(0)
        json.dump(read_main_data, main_file, ensure_ascii=False, indent=2)
        [open(element, 'w').close() for element in elements]
