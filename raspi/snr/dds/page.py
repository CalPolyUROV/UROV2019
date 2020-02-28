
MAX_PRINTABLE_DATA_LEN = 60


class Page:
    def __init__(self, key: str, data):
        self.fresh = True
        self.key = key
        self.data = data

    def __repr__(self):
        s = str(self.data)
        if len(s) > MAX_PRINTABLE_DATA_LEN:
            return f"k: {self.key},\t v:{type(self.data)}"
        return f"k: {self.key},\t v:{self.data}"
