from fastapi import APIRouter, HTTPException
from typing import List

from file_names import file_name
from utils.crud import (
    get_data, create_file, post_data, delete, submit_to_base_file
)
from utils.checks import (
    check_if_duplicate_key, check_if_duplicate_src_targ,
    check_if_empty
)
from schemas import ResultBase, NodeBase, EdgeBase


router = APIRouter()


@router.get('/get/all', response_model=ResultBase)
async def get_all():
    """ Вывести все содержимое base.json за исключением элементов помеченных на удаление"""

    if check_if_empty(file_name("main")) == True:
        return {"message": "Main file is empty or doesn't exist"}
    return get_data(
        fileName=file_name("main"),
        nodeDeleted=file_name("node_delete"),
        edgeDeleted=file_name("edge_delete")
    )


@router.get('/get/unloading', status_code=201)
async def unloading():
    """ Удалить помеченые для удаления и обновить информацию в base.json"""

    nodes_name = "nodes"
    edges_name = "edges"

    if check_if_empty(file_name("main")) == True:
        create_file(fileName=file_name("main"))

    submit_to_base_file(
        element=file_name("node"), element_deleted=file_name("node_delete"),
        main=file_name("main"), name=nodes_name
    )
    submit_to_base_file(
        element=file_name("edge"), element_deleted=file_name("edge_delete"),
        main=file_name("main"), name=edges_name)
    return {"detail": "Cleared deleted and unloaded new submitions"}


@router.post('/post/nodes')
async def post_nodes(nodes: List[NodeBase]):
    ''' Добавить один или несколько "node(s)" '''

    name = "nodes"

    if check_if_empty(fileName=file_name("node")) is True:
        create_file(fileName=file_name("node"))
        return post_data(
            data=nodes,
            write_to=name,
            mainFile = file_name("main"),
            fileName=file_name("node"),
            fileDeleted=file_name("node_delete")
            )
    return post_data(
        data=nodes,
        write_to=name,
        mainFile = file_name("main"),
        fileName=file_name("node"),
        fileDeleted=file_name("node_delete"))


@router.post('/post/edges')
async def post_edges(edges: List[EdgeBase]):
    ''' Добавить один или несколько "edge(s)" '''

    name = "edges"

    if check_if_empty(fileName=file_name("edge")) is True:
        create_file(fileName=file_name("edge"))
        return post_data(
            data=edges, 
            write_to=name, 
            mainFile = file_name("main"),
            fileName=file_name("edge"), 
            fileDeleted=file_name("edge_delete")
            )
    return post_data(
        data=edges, 
        write_to=name, 
        mainFile = file_name("main"),
        fileName=file_name("edge"), 
        fileDeleted=file_name("edge_delete")
        )


@router.delete('/delete/nodes')
async def delete_nodes(nodes: List[str]):
    ''' Удалить один или несоколько "node(s)" '''

    name = "nodes"

    if check_if_empty(fileName=file_name("node_delete")) is True:
        raise HTTPException(status_code=404, detail="Nodes not found")
    return delete(
        new_data=nodes,
        mainFile=file_name("main"),
        fieldName=name,
        fileName=file_name("node_delete")
    )


@router.delete('/delete/edges')
async def delete_edges(edges: List[str]):
    ''' Удалить один или несоколько "edge(s)" '''

    name = "edges"

    if check_if_empty(fileName=file_name("edge_delete")) is True:
        raise HTTPException(status_code=404, detail="Edges not found")
    return delete(
        new_data=edges,
        mainFile=file_name("main"),
        fieldName=name,
        fileName=file_name("edge_delete")
    )
