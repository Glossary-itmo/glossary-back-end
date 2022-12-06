from fastapi import APIRouter
from typing import List

from utils import (
        get_data, post_node, post_edge,
        delete_node, delete_edge)
from schemas import ResultBase, NodeBase, EdgeBase



def file_name(file):
    if file == "main":
        return "data.json"
    elif file == "node":
        return  "node_data.json"
    elif file == "edge":
        return "edge_data.json"
    else:
        return {f"No file with the name { file }"}


router = APIRouter()


@router.get('/get/all', response_model=ResultBase)
async def get_all():
    """ Вывести все содержимое base.json"""
    return get_data(fileName=file_name("main"))


@router.post('/post/nodes')
async def post_nodes(nodes: List[NodeBase]):
    return post_node(nodes=nodes, fileName=file_name("node"))


@router.post('/post/edges')
async def post_edges(edges: List[EdgeBase]):
    return post_edge(edges, fileName=file_name("edge"))


@router.delete('/delete/nodes')
async def delete_nodes(nodes: List[str]):
    return delete_node(nodes, fileName=file_name("node"))


@router.delete('/delete/edges')
async def delete_edges(edges: List[str]):
    return delete_edge(edges, fileName=file_name("edg"))
