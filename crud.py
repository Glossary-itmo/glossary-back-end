import json
from fastapi import HTTPException

from utils import (
    check_if_duplicate_key, check_if_duplicate_src_targ,
    create_file, post_data, check_if_empty,
    delete
    )


def get_data(fileName):
    if check_if_empty(fileName=fileName) is True:
        return {'message': 'No data'}

    with open(fileName, 'r') as data:
        read_data = json.load(data)
        return read_data


def unload(edges, nodes, main):
    nodes_name = "nodes"
    edges_name = "edges"

    with open(main, "r+") as main_file:
        read_main_data = json.load(main_file)

        nodes_base = open(nodes, "r").readlines()
        node_base = [json.loads(node) for node in nodes_base]

        edges_base = open(edges, "r").readlines()
        edge_base = [json.loads(edge) for edge in edges_base]

        [read_main_data[nodes_name].append(piece) for piece in node_base]
        [read_main_data[edges_name].append(piece) for piece in edge_base]

        main_file.seek(0)
        json.dump(read_main_data, main_file, indent=2)



def post_node(nodes, fileName):
    name = "nodes"

    if check_if_empty(fileName=fileName) is True:
        return create_file(data=nodes, write_to=name, fileName=fileName)
    return post_data(data=nodes, write_to=name, fileName=fileName)
            
        

def post_edge(edges, fileName):
    name = "edges"

    if check_if_empty(fileName) is True:
        return create_file(data=edges, write_to=name, fileName=fileName)
    return post_data(data=edges, write_to=name, fileName=fileName)


def delete_node(nodes, mainFile, fileName):
    name = "nodes"

    if check_if_empty(fileName=mainFile) is True:
        raise HTTPException(status_code=404, detail="Nodes not found")
    return delete(new_data=nodes, mainFile=mainFile, fieldName=name, fileName=fileName)


def delete_edge(edges, mainFile, fileName):
    name = "edges"

    if check_if_empty(fileName=mainFile) is True:
        raise HTTPException(status_code=404, detail="Edges not found")
    return delete(new_data=edges, mainFile=mainFile, fieldName=name, fileName=fileName)
    