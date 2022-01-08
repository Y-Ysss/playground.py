from typing import TextIO, Union, cast
import json
from dotted_data_object import DottedDataObject

# def data_from_json(data: Union[str, TextIO], *, from_file: bool = False, lowercase: bool = False) -> DottedDataObject:
#     if from_file:
#         if isinstance(data, str):
#             result = json.load(open(data, "rt"))
#         else:
#             result = json.load(data)
#     else:
#         result = json.loads(cast(str, data))
#     return DottedDataObject(result, lowercase=lowercase)

if __name__ == '__main__':
    data = DottedDataObject.data_from_json('C:\\Users\\Ys\\Projects\\PythonProjects\\playground.py\\data\\json\\Aa1.json', from_file=True)
    print(data.as_attrdict())
    data = DottedDataObject.data_from_json('{"format": {"true": "t2", "false": "f2"}, "ver.name": "v1", "ver.date": "2022"}')
    print(data.as_attrdict())