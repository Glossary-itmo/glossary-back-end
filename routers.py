from fastapi import APIRouter
from typing import List

from utils import (
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
    """ Вывести все содержимое base.json"""
    return get_data(fileName=file_name("main"))


@router.get('/get/unloading', status_code=201)
async def unloading():
    """ Удалить помеченые для удаления и обновить информацию в base.json"""
    unload(
        edges=file_name("edge"), 
        nodes=file_name("node"), 
        main=file_name("main")
        )
    return {"detail": "Created"}


@router.post('/post/nodes')
async def post_nodes(nodes: List[NodeBase]):
    return post_node(nodes=nodes, fileName=file_name("node"))


@router.post('/post/edges')
async def post_edges(edges: List[EdgeBase]):
    return post_edge(edges, fileName=file_name("edge"))


@router.delete('/delete/nodes')
async def delete_nodes(nodes: List[str]):
    return delete_node(nodes, main_file=file_name("main"), fileName=file_name("node_delete"))


@router.delete('/delete/edges')
async def delete_edges(edges: List[str]):
    return delete_edge(edges, main_file=file_name("main"), fileName=file_name("edge_delete"))
