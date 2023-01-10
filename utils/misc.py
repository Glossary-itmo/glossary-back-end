import json
from utils.checks import check_if_empty


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