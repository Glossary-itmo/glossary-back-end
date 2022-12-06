from fastapi import HTTPException

from schemas import ResultBase
import json


def check_if_duplicate_key(old_data, new_data, fieldName, fileName):
    """ Проверить если присланые ключи уже есть,
    True - есть дубликаты в новых данных
    False - нет дубликатов в новых данных"""

    extract = lambda data : list(map(lambda x : x["key"], data))
    old_keys = extract(old_data) 
    new_keys = extract(new_data)
    for key in new_keys:
        if key in old_keys:
            return True
    return False


def check_if_duplicate_src_targ(new_data, old_data, fileName):
    """ Проверить если присланные связи уже есть
    True - есть дубликаты новых связей
    False - нет дубликатов новых связей """

    # Взять указаное "field" поле из "data" и записать в лист "x" и вернуть из lambda функции
    # в переменную "extract"
    extract = lambda data, field : list(map(lambda x : x[field], data))

    temp_new_data = zip(
            extract(new_data, "source"), 
            extract(new_data, "source"))
    temp_old_data = zip(
            extract(old_data["edges"], "source"), 
            extract(old_data["edges"], "target"))

    for data in temp_new_data:
        if data in temp_old_data:
            return True

    return False


def create_file(data, write_to, fileName):
    """ В случае если нет файла json или он пустой создать json и его базовые состовляющие"""

    with open(fileName, "w+") as base_file:
        # Взять ResultBase и конвертировать её в json
        base = json.loads(ResultBase().json())
        new_data = [i.dict() for i in data]
        base_file.seek(0)
        json.dump(new_data, base_file, indent=2)
        return base_file


def post_data(data, write_to, fileName):
    with open(fileName, 'a+') as base_file:
        base_file.seek(0)
        read_data = json.load(base_file)
        print(read_data)
        new_data = [i.dict() for i in data]

        if check_if_duplicate_key(
                old_data=read_data, 
                new_data=new_data, 
                fieldName=write_to,
                fileName=fileName) is True:
            raise HTTPException(
                    status_code=403, 
                    detail="Forbidden, already exists")
        if write_to == "edges":
            if check_if_duplicate_src_targ(
                old_data=read_data, 
                new_data=new_data,
                fileName=fileName) is True:
                raise HTTPException(
                        status_code=403, 
                        detail="Forbidden, this direction already exists")
        
        # [read_data.append(i) for i in new_data]
        # base_file.seek(0, 2)
        # json.dump(new_data, base_file, indent=2)
        [base_file.write(json(ready_data)) for ready_data in new_data]
        return base_file
    

def check_if_empty(fileName):
    """ Проверить что json пустой,
    пустой - True
    не пустой - False"""

    try:
        with open(fileName, "r") as check:
            if len(json.load(check)) == 2:
                return False
    except: 
        return True
    

def delete_edges(new_data, fieldName, fileName):
    with open("data.json", "r+") as base_file:
        new_data = new_data
        base_data = json.load(base_file)

        for key, dictionary in enumerate(base_data[fieldName]):
            if dictionary["key"] in new_data:
                base_data[fieldName].pop(key)
            raise HTTPException(status_code=404, detail="Key not found")

        open("data.json", "w").close()

        base_file.seek(0)
        json.dump(base_data, base_file, indent=2)
        return base_file


# End of secondary functions
# Start of the utils


def get_data(fileName):
    with open(fileName, 'r') as data:
        read_data = json.load(data)
        return read_data
    

def post_node(nodes, fileName):
    name = "nodes"
    if check_if_empty(fileName=fileName) is True:
        return create_file(data=nodes, write_to=name, fileName=fileName)
    return post_data(data=nodes, write_to=name, fileName=fileName)
            
        

def post_edge(edges, fileName):
    name = "edges"
    if check_if_empty(fileName) is True:
        print("true")
        return create_file(data=edges, write_to=name, fileName=fileName)
    return post_data(data=edges, write_to=name, fileName=fileName)


def delete_node(nodes, fileName):
    name = "nodes"


def delete_edge(edges, fileName):
    name = "edges"

    if check_if_empty(fileName=fileName) is True:
        raise HTTPException(status_code=404, detail="Edges not found")
    return delete_edges(new_data=edges, fieldName=name, fileName=fileName)
    