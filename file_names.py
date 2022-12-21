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