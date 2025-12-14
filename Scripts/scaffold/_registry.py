from typing import Callable
from typing import Final
from typing import Optional


class Registry[T]:
    """Реестр"""

    def __init__(self, item_provider: Callable[[str], Optional[T]]):
        """
        :param item_provider: Создаёт элемент по идентификатору
        """
        self._items: Final = dict[str, T]()
        self._item_provider: Final = item_provider

    def get(self, identifier: str) -> Optional[T]:
        """
        Получить значение из реестра
        :param identifier: идентификатора
        :return:
        """
        ret = self._items.get(identifier)

        if ret is not None:
            return ret

        ret = self._item_provider(identifier)

        if ret is not None:
            self._items[identifier] = ret

        return ret
