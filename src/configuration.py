import json
from typing import Dict


class Configuration:
    """
    Configures the different services needed
    """

    def __init__(self, config_path: str):
        self.config_path = config_path
        self.parameters = self._read_parameters()

    def _read_parameters(self) -> Dict:
        """
        reads parameters from config
        """
        parameters = json.load(open(self.config_path, "r"))
        return parameters
