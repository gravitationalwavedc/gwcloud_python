from dataclasses import dataclass

@dataclass(init=False)
class BilbyJob:
    name: str
    description: str
    other: dict

    def __init__(self, name, description, **kwargs):
        self.name = name
        self.description = description
        self.other = kwargs

    def get_file_list():
        pass