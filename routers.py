from fastapi import APIRouter
from typing import List

from crud import (
        get_data, unload, post_node, post_edge,
        delete_node, delete_edge)
from schemas import ResultBase, NodeBase, EdgeBase



def file_name(file):
    if file == "main":
        return "static/data.json"
    elif file == "node":
        return  "static/node_data.txt"
    elif file == "edge":
        return "static/edge_data.txt"
    elif file == "node_delete":
        return "static/node_deleted.txt"
    elif file == "edge_delete":
        return "static/edge_deleted.txt"
    else:
        return {f"No file with the name { file }"}


router = APIRouter()


@router.get('/get/all', response_model=ResultBase)
async def get_all():
    """ Вывести все содержимое base.json за исключением элементов помеченных на удаление"""
    return get_data(
        fileName=file_name("main"), 
        nodeDeleted=file_name("node_delete"),
        edgeDeleted=file_name("edge_delete")
        )


@router.get('/get/unloading', status_code=201)
async def unloading():
    """ Удалить помеченые для удаления и обновить информацию в base.json"""
    unload(
        edges=file_name("edge"), 
        nodes=file_name("node"), 
        main=file_name("main")
        )
    return {"detail": "Cleared deleted and unloaded new submitions"}


@router.post('/post/nodes')
async def post_nodes(nodes: List[NodeBase]):
    ''' Добавить один или несколько "node(s)" '''
    return post_node(nodes=nodes, fileName=file_name("node"))


@router.post('/post/edges')
async def post_edges(edges: List[EdgeBase]):
    ''' Добавить один или несколько "edge(s)" '''
    return post_edge(edges, fileName=file_name("edge"))


@router.delete('/delete/nodes')
async def delete_nodes(nodes: List[str]):
    ''' Удалить один или несоколько "node(s)" '''
    return delete_node(nodes, mainFile=file_name("main"), fileName=file_name("node_delete"))


@router.delete('/delete/edges')
async def delete_edges(edges: List[str]):
    ''' Удалить один или несоколько "edge(s)" '''
    return delete_edge(edges, mainFile=file_name("main"), fileName=file_name("edge_delete"))
