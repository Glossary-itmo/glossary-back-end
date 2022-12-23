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
    return get_data(names=["nodes", "edges"],
                    fileName=file_name("main"),
                    secondaries=[file_name("node"), file_name("edge")],
                    secondaryDeleted=[file_name("node_delete"), file_name("edge_delete")]
                    )


@router.get('/get/unloading', status_code=201)
async def unloading():
    """ Удалить помеченные для удаления и обновить информацию в base.json"""

    if check_if_empty(file_name("main")) == True:
        create_file(fileName=file_name("main"))

    submit_to_base_file(elements=[file_name("node"), file_name("edge")],
                        elements_deleted=[
                            file_name("node_delete"), file_name("edge_delete")],
                        main=file_name("main"),
                        names=["nodes", "edges"]
                        )
    return {"detail": "Cleared deleted and unloaded new submissions"}


@router.post('/post/nodes')
async def post_nodes(nodes: List[NodeBase]):
    ''' Добавить один или несколько "node(s)" '''

    name = "nodes"

    return post_data(data=nodes,
                     write_to=name,
                     mainFile=file_name("main"),
                     fileName=file_name("node"),
                     fileDeleted=file_name("node_delete"))


@router.post('/post/edges')
async def post_edges(edges: List[EdgeBase]):
    ''' Добавить один или несколько "edge(s)" '''

    name = "edges"

    return post_data(data=edges,
                     write_to=name,
                     mainFile=file_name("main"),
                     fileName=file_name("edge"),
                     fileDeleted=file_name("edge_delete")
                     )


@router.delete('/delete/nodes')
async def delete_nodes(nodes: List[str]):
    ''' Удалить один или несколько "node(s)" '''

    name = "nodes"

    if check_if_empty(fileName=file_name("node_delete")) is True:
        create_file(file_name("node_delete"))
    return delete(new_data=nodes,
                  mainFile=file_name("main"),
                  secondaryFile=file_name("node"),
                  fieldName=name,
                  fileName=file_name("node_delete")
                  )


@router.delete('/delete/edges')
async def delete_edges(edges: List[str]):
    ''' Удалить один или несколько "edge(s)" '''

    name = "edges"

    if check_if_empty(fileName=file_name("edge_delete")) is True:
        create_file(file_name("edge_delete"))
    return delete(new_data=edges,
                  mainFile=file_name("main"),
                  secondaryFile=file_name("edge"),
                  fieldName=name,
                  fileName=file_name("edge_delete")
                  )
