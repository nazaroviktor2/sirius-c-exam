from typing import Any, Dict

URLS: Dict[str, Any] = {
    "auth": {
        "login": "/api/v1/auth/login",
        "info": "/api/v1/auth/info",
        "register": "/api/v1/auth/register",
    },
    "crud": {
        "form": {
            "create": "form/create",
            "read": "form/info",
            "update": "task/update/"
        },
        "search_params": {
            "create": "search/search_params/create",
            "read": "search/search_params/info/",
            "update": "search/search_params/update/",
        },
        "statistics": {
            "create": "statistics/create",
            "read": "statistics/info",
            "update": "statistics/update",
        },
        "image": {
            "create": "image/upload",
            "read": "image/info/",
        }
    },
}
