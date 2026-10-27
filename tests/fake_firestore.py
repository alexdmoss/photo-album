"""Just enough of the Firestore client for the queries the app makes."""


class FakeDoc:
    def __init__(self, data):
        self._data = data

    @property
    def exists(self):
        return self._data is not None

    def to_dict(self):
        return dict(self._data) if self._data is not None else None


class FakeDocRef:
    def __init__(self, store, doc_id):
        self._store = store
        self._id = doc_id

    def get(self):
        return FakeDoc(self._store.get(self._id))

    def set(self, data, merge=False):
        if merge and self._id in self._store:
            self._store[self._id] = {**self._store[self._id], **data}
        else:
            self._store[self._id] = dict(data)


class FakeQuery:
    def __init__(self, docs):
        self._docs = docs

    def where(self, field, op, value):
        assert op == "=="
        return FakeQuery([d for d in self._docs if d.get(field) == value])

    def order_by(self, field, direction=None):
        reverse = direction == "DESCENDING"
        return FakeQuery(sorted(self._docs, key=lambda d: d[field], reverse=reverse))

    def stream(self):
        return [FakeDoc(d) for d in self._docs]


class FakeCollection(FakeQuery):
    def __init__(self, store):
        self._store = store

    @property
    def _docs(self):
        return list(self._store.values())

    def document(self, doc_id):
        return FakeDocRef(self._store, doc_id)


class FakeFirestore:
    def __init__(self):
        self.collections = {}

    def collection(self, name):
        return FakeCollection(self.collections.setdefault(name, {}))

    def add(self, collection, doc_id, data):
        self.collections.setdefault(collection, {})[doc_id] = data
