from fastapi import APIRouter, HTTPException
from typing import List

from utils.misc import FileNames
from utils.crud import (
    get_data, create_file, submit_to_base_file, 
    post_data, edit_data, delete
)
from utils.checks import check_if_empty
from schemas import ResultBase, NodeBase, EdgeBase

from enum import Enum


router = APIRouter(
    prefix="/glossary",
)


class Tags(Enum):
    glossary = 'Glossary'


@router.get('/get/all', response_model=ResultBase, tags=[Tags.glossary])
async def get_all():
    """ Вывести все содержимое base.json за исключением элементов помеченных на удаление"""

    if check_if_empty(FileNames.mainFileName) == True:
        return {"message": "Main file is empty or doesn't exist"}
    return get_data(names=["nodes", "edges"],
                    fileName=FileNames.mainFileName,
                    secondaries=[FileNames.nodeFileName, FileNames.edgeFileName],
                    secondaryDeleted=[FileNames.deletedNodeFileName, FileNames.deletedEdgeFileName]
                    )


@router.get('/get/unloading', status_code=201, tags=[Tags.glossary])
async def unloading():
    """ Удалить помеченное для удаления и обновить информацию в base.json"""

    if check_if_empty(FileNames.mainFileName) == True:
        create_file(FileNames.mainFileName)

    submit_to_base_file(elements=[FileNames.nodeFileName, FileNames.edgeFileName],
                        elements_deleted=[
                            FileNames.deletedNodeFileName, FileNames.deletedEdgeFileName],
                        main=FileNames.mainFileName,
                        names=["nodes", "edges"]
                        )
    return {"detail": "Cleared deleted and unloaded new submissions"}


@router.post('/post/nodes', status_code=201, tags=[Tags.glossary])
async def post_nodes(nodes: List[NodeBase]):
    ''' Добавить один или несколько узлов '''

    name = "nodes"

    return post_data(data=nodes,
                     write_to=name,
                     mainFile=FileNames.mainFileName,
                     fileName=FileNames.nodeFileName,
                     fileDeleted=FileNames.deletedNodeFileName)


@router.post('/post/edges', status_code=201, tags=[Tags.glossary])
async def post_edges(edges: List[EdgeBase]):
    ''' Добавить одно или несколько соединений '''

    name = "edges"

    return post_data(data=edges,
                     write_to=name,
                     mainFile=FileNames.mainFileName,
                     fileName=FileNames.edgeFileName,
                     fileDeleted=FileNames.deletedEdgeFileName
                     )


@router.put('/edit/nodes', status_code=201, tags=[Tags.glossary])
async def edit_nodes(nodes: List[NodeBase]):
    ''' Изменить один или несколько узлов '''

    name = "nodes"
    edgeName = "edges"

    return edit_data(new_data=nodes,
                     fieldName=[name, edgeName],
                     mainFile=FileNames.mainFileName,
                     secondaryFile=[FileNames.nodeFileName, FileNames.edgeFileName],
                     fileDeleted=[FileNames.deletedNodeFileName, FileNames.deletedEdgeFileName]
                     )


@router.delete('/delete/nodes', status_code=204, tags=[Tags.glossary])
async def delete_nodes(nodes: List[str]):
    ''' Удалить один или несколько узлов '''

    name = "nodes"

    if check_if_empty(fileName=FileNames.deletedNodeFileName) is True:
        create_file(FileNames.deletedNodeFileName)
    return delete(new_data=nodes,
                  mainFile=FileNames.mainFileName,
                  secondaryFile=FileNames.nodeFileName,
                  fieldName=name,
                  fileName=FileNames.deletedNodeFileName
                  )


@router.delete('/delete/edges', status_code=204, tags=[Tags.glossary])
async def delete_edges(edges: List[str]):
    ''' Удалить одно или несколько соединений '''

    name = "edges"

    if check_if_empty(fileName=FileNames.deletedEdgeFileName) is True:
        create_file(FileNames.deletedEdgeFileName)
    return delete(new_data=edges,
                  mainFile=FileNames.mainFileName,
                  secondaryFile=FileNames.edgeFileName,
                  fieldName=name,
                  fileName=FileNames.deletedEdgeFileName
                  )
