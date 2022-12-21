import json
from fastapi import HTTPException

from utils.utils import (create_file, post_data, delete)
from utils.checks import (
    check_if_duplicate_key, check_if_duplicate_src_targ,
    check_if_empty,
)


def get_data(fileName, nodeDeleted, edgeDeleted):
    node_name = "nodes"
    edge_name = "edges"
    if check_if_empty(fileName=fileName) is True:
        return {'message': 'No data'}

    with open(fileName, 'r') as base_data:
        read_data = json.load(base_data)

        turn_to_json = lambda data : [json.loads(i) for i in data]
        get_deleted_keys = lambda data : [i["key"] for i in data]
        get_results = lambda data, name, deleted : \
            [element \
            for i, element in enumerate(data[name]) \
            if element["key"] not in deleted]

        node_deleted = open(nodeDeleted).readlines()
        edge_deleted = open(edgeDeleted).readlines()
        node_deleted = turn_to_json(node_deleted)
        edge_deleted = turn_to_json(edge_deleted)
        node_deleted_keys = get_deleted_keys(node_deleted)
        edge_deleted_keys = get_deleted_keys(edge_deleted)

        nodes_result, edges_result = [], []
        nodes_result = get_results(
            data=read_data, 
            name=node_name, 
            deleted=node_deleted_keys)
        edges_result = get_results(
            data=read_data, 
            name=edge_name, 
            deleted=edge_deleted_keys) 

        read_data[node_name] = nodes_result.copy()
        read_data[edge_name] = edges_result.copy()

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
    