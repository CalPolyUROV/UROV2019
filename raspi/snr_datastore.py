from typing import Union, Callable, Any

from snr_utils import debug


class Page:
    def __init__(self, data):
        self.fresh = True
        self.data = data


class Datastore:
    def __init__(self):
        self.database = {}

    def store(self, key: str, data):
        try:
            old_page = self.database[key]
            self.database[key + "_previous"] = old_page
        except KeyError:
            debug("datastore_event", "Adding new key: {}", [key])

        self.database[key] = Page(data)

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
            debug("datastore_event", "Page for {} was empty", [key])
            return None
        return page.data

    def use(self, key: str):
        """Get a value from the datastore and mark it as unfresh/used
        """
        try:
            self.database[key].fresh = False
        except KeyError:
            debug("datastore_error", "Cannot mark unfresh, key not found")
        return self.get(key)

# Sets data with a given key
DatastoreSetter = Callable[[str, Any], None]
# Calls a DatastoreSetter with a set key
DataSetter = Callable[[Any], None]

# Gets data with a given key from data store
DatastoreGetter = Callable[[str], Any]
# Calls a DatastoreGetter with set key
DataGetter = Callable[[], Any]
