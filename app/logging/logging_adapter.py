import json
import logging


class JsonAdapter(logging.LoggerAdapter):
    """Адаптер для преобразования логов в валидную JSON-строку."""

    def process(self, message, kwargs):
        new_message = json.dumps(message, ensure_ascii=False)[1:-1]
        return new_message, kwargs
