import configparser
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    jenkins_url: str = ""
    jenkins_login: str = ""
    jenkins_api_token: str = ""
    jenkins_hostname: str = ""
    jenkins_ssh_port: int = 22

    def has_http_creds(self) -> bool:
        return len(self.jenkins_url) > 0

    def has_ssh_creds(self) -> bool:
        return len(self.jenkins_hostname) > 0

    @staticmethod
    def load_file(file_path: Path) -> "Config":
        config = Config()
        parser = configparser.ConfigParser()

        parser.read(file_path)

        # HTTP configs
        config.jenkins_url = parser.get("http", "url", fallback=config.jenkins_url)
        config.jenkins_login = parser.get(
            "http", "login", fallback=config.jenkins_login
        )
        config.jenkins_api_token = parser.get(
            "http", "api_token", fallback=config.jenkins_api_token
        )

        # SSH configs
        config.jenkins_hostname = parser.get(
            "ssh", "hostname", fallback=config.jenkins_hostname
        )
        config.jenkins_ssh_port = parser.getint(
            "ssh", "port", fallback=config.jenkins_ssh_port
        )

        return config
