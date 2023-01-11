import json
from file_names import file_name
from utils.checks import check_if_txt, check_if_empty, extract_new_old


def clear_deleted(fileName, elementDeleted, name):
    ''' Очистить файлы помеченные для удаления из главного файла'''

    # Lambdas
    turn_to_json = lambda data: [json.loads(i) for i in data]
    get_deleted_keys = lambda data: [i["key"] for i in data]
    get_results = lambda data, deleted: [element for i, element
                                         in enumerate(data)
                                         if element["key"] not in deleted]
    # End of lambdas

    if check_if_empty(fileName=fileName) is True:
        return {}

    # Check file extension
    if fileName.endswith(".txt"):
        file_name_ready = turn_to_json(open(fileName, "r").readlines())
    else:
        file_name_temp = json.load(open(fileName, "r"))
        file_name_ready = file_name_temp[name]

    element_deleted = open(elementDeleted).readlines()
    element_deleted = turn_to_json(element_deleted)
    element_deleted_keys = get_deleted_keys(element_deleted)

    return get_results(data=file_name_ready,
                       deleted=element_deleted_keys)


def cascade_delete(new_data, old_data):
    ''' Каскадное удаление edge при удалении node '''

    extract = lambda data, field: list(map(lambda x: x[field], data))

    ready_new_data = [i['key'] for i in new_data]
    temp_old_keys = list(
        extract([i for i in old_data["edges"]], "key"))
    temp_old_data = list(zip(
        extract([i for i in old_data["edges"]], "source"),
        extract([i for i in old_data["edges"]], "target")))

    with open(file_name("edge_delete"), "a+") as base_file:
        for i, data in enumerate(temp_old_data):
            [base_file.write(json.dumps({"key": temp_old_keys[i]}) + "\n") 
            for j, _ in enumerate(ready_new_data)
            if ready_new_data[j] in data]
    return