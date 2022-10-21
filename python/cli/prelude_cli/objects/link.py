from datetime import datetime


class Result:

    def __init__(self):
        pass


class Test:

    def __init__(self, day: datetime, tag: str, test: str, code: int, volume: int, endpoints: int):
        self.day = day
        self.tag = tag
        self.test = test
        self.code = code
        self.volume = volume
        self.endpoints = endpoints

