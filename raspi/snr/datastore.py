"""Store a dictionary for a Node

Provides extra information for items in dictionary including freshness
and previous value
"""

from typing import Callable, Any
from multiprocessing import Manager
# TODO: Synchronize datastore for multiprocessing


class Page:
    def __init__(self, data):
        self.fresh = True
        self.data = data


class Datastore:
    def __init__(self, dbg: Callable):
        self.dbg = dbg
        # self.sync_manager = Manager()
        # self.database = self.sync_manager.dict()
        self.database = {}

    def store(self, key: str, data):
        d = self.database
        try:
            old_page = d[key]
            d[key + "_previous"] = old_page

        except KeyError:
            self.dbg("datastore_event", "Adding new key: {}", [key])

        d[key] = Page(data)
        self.database = d

    def is_fresh(self, data_type: str) -> bool:
        page = self.database.get(data_type)
        if page is not None:
            return page.fresh
        return False

    def get(self, key: str):
        """Get a value from the data store without marking it as unfresh
        """
        page = self.database.get(key)

        if page is None:
            self.dbg("datastore_event", "Page for {} was empty", [key])
            return None
        return page.data

    def use(self, key: str):
        """Get a value from the datastore and mark it as unfresh/used
        """
        try:
            self.database[key].fresh = False
        except KeyError:
            self.dbg("datastore_error",
                     "Cannot mark unfresh, key {} not found",
                     [key])
        return self.get(key)

    def terminate(self):
        self.dump()
        # self.sync_manager.shutdown()

    def dump(self):
        d = self.database
        for k in d.keys():
            self.dbg("datastore_dump", "k: {} v: {}",
                     [k, self.get(k)])

# # Sets data with a given key
# DatastoreSetter = Callable[[str, Any], None]
# # Calls a DatastoreSetter with a set key
# DataSetter = Callable[[Any], None]

# # Gets data with a given key from data store
# DatastoreGetter = Callable[[str], Any]
# # Calls a DatastoreGetter with set key
# DataGetter = Callable[[], Any]
