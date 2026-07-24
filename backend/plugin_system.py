import json
from typing import Dict, Any, List, Callable

class PluginSystem:
    def __init__(self):
        self._plugins: Dict[str, Dict[str, Any]] = {}

    def register_plugin(self, id: str, name: str, description: str, handler: Callable[..., Any], default_config: Dict[str, Any] = None):
        self._plugins[id] = {
            "id": id,
            "name": name,
            "description": description,
            "handler": handler,
            "config": default_config or {},
            "enabled": True
        }

    def execute_plugin(self, id: str, *args, **kwargs) -> Any:
        plugin = self._plugins.get(id)
        if not plugin:
            raise ValueError(f"Plugin '{id}' is not registered.")
        if not plugin["enabled"]:
            raise ValueError(f"Plugin '{id}' is currently disabled.")
        return plugin["handler"](*args, **kwargs)

    def list_plugins(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": k,
                "name": v["name"],
                "description": v["description"],
                "enabled": v["enabled"],
                "config": v["config"]
            }
            for k, v in self._plugins.items()
        ]

    def set_enabled(self, id: str, enabled: bool):
        if id in self._plugins:
            self._plugins[id]["enabled"] = enabled

plugin_system = PluginSystem()

def weather_plugin_handler(location: str = "New York") -> str:
    return f"The weather in {location} is currently 72°F and sunny with an gentle breeze."

def stock_plugin_handler(symbol: str = "AAPL") -> Dict[str, Any]:
    return {"symbol": symbol, "price": 178.50, "change": "+1.25%"}

plugin_system.register_plugin("weather", "Weather Forecast", "Retrieve real-time global weather details", weather_plugin_handler, {"units": "imperial"})
plugin_system.register_plugin("stocks", "Stock Market Tracker", "Retrieve current prices of publicly listed stocks", stock_plugin_handler)
