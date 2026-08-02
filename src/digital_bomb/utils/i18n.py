"""_summary_"""

import json
import os
import locale
from functools import lru_cache
from pathlib import Path

class I18n:
    """_summary_"""

    def __init__(self) -> None:
        """_summary_"""
        self.default_lang: str = "zh"
        sys_lang: str = locale.getdefaultlocale()[0]
        self.current_lang: list[str] = os.getenv("LANG", sys_lang or self.default_lang)[:2]

    @lru_cache(maxsize=None)
    def _load(self, lang: str) -> dict[str, str]:
        """_summary_

        :param lang: _description_
        :type lang: str
        :return: _description_
        :rtype: dict[str, str]
        """
        path: Path = Path(__file__).resolve().parent.parent.parent.parent / "locales" / f"{lang}.json"
        
        if path.exists():
            return json.loads(path.read_text(encoding='utf-8'))
                
        return {}

    def t(self, key: str, count: int | None = None, **kwargs: dict[str, str | int]) -> str:
        """_summary_

        :param key: _description_
        :type key: str
        :param count: _description_, defaults to None
        :type count: int | None, optional
        :return: _description_
        :rtype: str
        """

        if count is not None:
            kwargs["count"] = count

        data: dict[str, dict[str, str | dict[str, str]]] | str = self._load(self.current_lang) or self._load(self.default_lang)
        parts: list[str] = key.split(".")

        for part in parts:
        
            if isinstance(data, dict):
                data = data.get(part)
                
            else:
                return key
                
            if data is None:
                return key
            
        if (
        count is not None
        and isinstance(data, dict)
        and "one" in data
        and "other" in data
        ):
            plural_key: str = "one" if count == 1  else "other"
            data = data.get(plural_key, data.get("other", key))

        if isinstance(data, str):
            return data.format(**kwargs) if kwargs else data
        
        return data if data is not None else key

    def set_lang(self, lang: str) -> None:
        """_summary_

        :param lang: _description_
        :type lang: str
        """
        self.current_lang = lang

    def reload(self) -> None:
        """_summary_"""
        self._load.cache_clear()
        
_: I18n = I18n()