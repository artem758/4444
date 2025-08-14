class AssociativeMemory:
    def __init__(self):
        # простое key-value хранилище
        self._store = {}

    def set(self, key, value):
        """Сохраняет значение по ключу."""
        self._store[key] = value

    def get(self, key, default=None):
        """Возвращает значение по ключу, если оно есть."""
        return self._store.get(key, default)

    def clear(self):
        """Очищает всё хранилище."""
        self._store.clear()

    def search(self, query: str):
        """
        Ищет ключи или значения, содержащие подстроку query (без регистра).
        Возвращает список подходящих ключей.
        """
        q = (query or "").lower()
        return [
            k for k, v in self._store.items()
            if q in str(k).lower() or q in str(v).lower()
        ]
