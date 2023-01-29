import json
import uuid
from fastapi import HTTPException
from schemas import ResultBase, NodeBase, AttributesNode, EdgeBase, AttributesEdge

from file_names import file_name
from routers import file_name
from utils.checks import (
    check_if_duplicate_key, check_if_duplicate_src_targ,
    check_if_empty, check_if_txt_and_return, extract_field
)
from utils.misc import clear_deleted, cascade_delete


# Подменить значение key на uuid
key_to_uuid = lambda data : [key.update({"key": uuid.uuid4().hex}) for key in data]


def get_data(names, fileName, secondaries, secondaryDeleted):
    ''' Получить все что есть в главном файле за исключением помеченного на удаление '''

    read_and_turn_to_json = lambda to_read: [
        json.loads(i) for i in open(to_read, "r").readlines()]

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
                                      fieldName=fieldName) is False:
                continue
            else:
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

            raise HTTPException(status_code=404, detail="Not found")


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


def edit_data(new_data, fieldName, mainFile, secondaryFile, fileDeleted):

    ready_new_data = [i.dict() for i in new_data]
    new_data_attributes = [i["attributes"] for i in ready_new_data]
    secondaryEdgeFile = file_name("edge")
    main_and_secondary = [mainFile, secondaryFile, secondaryEdgeFile]
    
    old_keys = extract_field(ready_new_data, "key")
    old_labels = extract_field(new_data_attributes, "label")
    old_texts = extract_field(new_data_attributes, "text")

    # Catch the "key" of the node that is being edited, ### done
    # create new node with new "key" and "edited" data, ### done
    # find element with they old key and put it into the "delete" function,
    # catch keys of all edges that cascade deletion finds,
    # create new edges while replacing deleted key from src or targ with the new one,

    if check_if_duplicate_key(old_data=mainFile,
                              new_data=ready_new_data,
                              fieldName=fieldName) is False:
        raise HTTPException(status_code=404, detail="Not found")

    base = check_if_txt_and_return(fileName=mainFile, fieldName=fieldName)
    nodeSecondary = check_if_txt_and_return(fileName=secondaryFile, fieldName=fieldName)
    # edgeSecondary = 
#######################################################################
    # print(edgeSecondary)

    ### Load the base schema for Nodes and change keys
    node_base_origin = [NodeBase(
        key=uuid.uuid4().hex, 
        attributes=AttributesNode(
            label=old_labels[i],
            text=old_texts[i])) 
            for i, key in enumerate(old_keys)]

    ### Load the base schema for Edges and change key for edge itself and key of 
    ### corresponding node that was edited
    edge_base_origin = [EdgeBase(
        key=uuid.uuid4().hex,
        source="str",
        target="str",
        attributes=AttributesEdge(size=0))]
    print(edge_base_origin)

    ### Write new elements with changed keys and delete old ones with connected edges
    # [post_data(
    #     data=base_file, 
    #     write_to=fieldName, 
    #     mainFile=mainFile, 
    #     fileName=secondaryFile, 
    #     fileDeleted=fileDeleted) 
    # for base_file in [node_base_origin, edge_base_origin]]
    # delete(
    #     new_data=old_keys, 
    #     mainFile=mainFile, 
    #     secondaryFile=secondaryFile, 
    #     fieldName=fieldName, 
    #     fileName=fileDeleted)
