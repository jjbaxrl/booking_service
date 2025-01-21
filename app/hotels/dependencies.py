import json
from app.exceptions import IncorrectServicesFormat


def convert_services_to_list(value) -> list:
    if isinstance(value, str):
        try:
            value = value.replace("'", '"')
            json_value = json.loads(value)
            if not isinstance(json_value, list):
                raise IncorrectServicesFormat
            return json_value
        except (json.JSONDecodeError, ValueError):
            raise IncorrectServicesFormat
    elif isinstance(value, list):
        return value
    else:
        raise IncorrectServicesFormat
