import json
from fastapi import HTTPException
from schemas import ResultBase

from checks import (
    check_if_duplicate_key, check_if_duplicate_src_targ,
    check_if_empty
    )


def create_file(data, write_to, fileName):
    """ В случае если нет файла json или он пустой создать json и его базовые состовляющие"""

    with open(fileName, "w+") as base_file:
        
        if fileName == "main":
            # Взять ResultBase и конвертировать её в json
            base = json.loads(ResultBase().json())

            # Записать ResultBase в base_file
            json.dump(base, base_file, indent=2)

        new_data = [i.dict() for i in data]

        for i, ready_data in enumerate(new_data):
            if (len(new_data) - 1) == i:
                base_file.write(json.dumps(ready_data))
            else:
                base_file.write(json.dumps(ready_data) + "\n")
        return base_file


def post_data(data, write_to, fileName):
    with open(fileName, 'a+') as base_file:
        base_file.seek(0)

        # read_data = json.load(base_file)
        read_data = base_file.readlines()
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


        for i, ready_data in enumerate(new_data):
            if len(new_data) == 1:
                base_file.write("\n" + json.dumps(ready_data))
            elif (len(new_data) - 1) == i:
                base_file.write(json.dumps(ready_data))
            elif i == 0:
                base_file.write("\n" + json.dumps(ready_data) + "\n")
            else:
                base_file.write(json.dumps(ready_data) + "\n")
        return base_file
    

def delete(new_data, mainFile, fieldName, fileName):
    ready_new_data = []
    [ready_new_data.append({"key": key}) for key in new_data]
    
    with open(fileName, "a+") as base_file:
        old_data = base_file.readlines()
        print(old_data)
        if check_if_duplicate_key(
                old_data=old_data, 
                new_data=ready_new_data, 
                fieldName=fieldName,
                fileName=fileName) is True:
            raise HTTPException(
                    status_code=403, 
                    detail="Forbidden, already exists")
        print(1)
        [base_file.write(json.dumps(i) + "\n") for i in ready_new_data]
