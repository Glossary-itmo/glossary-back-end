import json
from fastapi import HTTPException

from utils.utils import (
    create_file, post_data, delete, 
    submit_to_base_file, clear_deleted
)
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
            elmenetDeleted=nodeDeleted, 
            name=node_name).copy()
        read_file[edge_name] = clear_deleted(
            fileName=fileName, 
            elmenetDeleted=edgeDeleted, 
            name=edge_name).copy()

        return read_file


def unload(edges, nodes, main):
    ''' Очистить помеченное на удаление и добавить новые элементы в главный файл '''
    nodes_name = "nodes"
    edges_name = "edges"

    submit_to_base_file(element=nodes, main=main, name=nodes_name)
    submit_to_base_file(element=edges, main=main, name=edges_name)


def post_node(nodes, fileName):
    ''' Добавить один или несколько "node(s)" '''
    name = "nodes"

    if check_if_empty(fileName=fileName) is True:
        return create_file(data=nodes, write_to=name, fileName=fileName)
    return post_data(data=nodes, write_to=name, fileName=fileName)
            
        

def post_edge(edges, fileName):
    ''' Добавить один или несколько "edge(s)" '''
    name = "edges"

    if check_if_empty(fileName) is True:
        return create_file(data=edges, write_to=name, fileName=fileName)
    return post_data(data=edges, write_to=name, fileName=fileName)


def delete_node(nodes, mainFile, fileName):
    ''' Удалить один или несоколько "node(s)" '''
    name = "nodes"

    if check_if_empty(fileName=mainFile) is True:
        raise HTTPException(status_code=404, detail="Nodes not found")
    return delete(new_data=nodes, mainFile=mainFile, fieldName=name, fileName=fileName)


def delete_edge(edges, mainFile, fileName):
    ''' Удалить один или несоколько "edge(s)" '''
    name = "edges"

    if check_if_empty(fileName=mainFile) is True:
        raise HTTPException(status_code=404, detail="Edges not found")
    return delete(new_data=edges, mainFile=mainFile, fieldName=name, fileName=fileName)
    