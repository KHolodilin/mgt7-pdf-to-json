"""Configuration management."""

from pathlib import Path
from typing import Optional, Union

import yaml
from pydantic import BaseModel, Field


class LoggingConfig(BaseModel):
    """Logging configuration."""

    level: str = "INFO"
    format: str = "console"  # console or json
    format_file: str = "json"
    file: str = "logs"
    date_format: str = "%d-%m-%Y"


class ArtifactsConfig(BaseModel):
    """Artifacts configuration."""

    enabled: bool = False
    dir: str = "artifacts"
    save_raw: bool = True
    save_normalized: bool = True
    save_parsed: bool = True
    save_output: bool = False
    keep_days: int = 7


class PipelineConfig(BaseModel):
    """Pipeline configuration."""

    mapper: str = "default"  # default, minimal, db


class ValidationConfig(BaseModel):
    """Validation configuration."""

    strict: bool = False
    required_fields: list[str] = Field(
        default_factory=lambda: [
            "meta.form_type",
            "meta.financial_year.from",
            "meta.financial_year.to",
            "company.cin",
            "company.name",
        ]
    )


class Config(BaseModel):
    """Main configuration."""

    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    artifacts: ArtifactsConfig = Field(default_factory=ArtifactsConfig)
    pipeline: PipelineConfig = Field(default_factory=PipelineConfig)
    validation: ValidationConfig = Field(default_factory=ValidationConfig)

    @classmethod
    def from_yaml(cls, path: Union[Path, str]) -> "Config":
        """Load configuration from YAML file."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        return cls(**data)

    @classmethod
    def default(cls) -> "Config":
        """Create default configuration."""
        return cls()

    @classmethod
    def from_file_or_default(cls, path: Optional[Union[Path, str]] = None) -> "Config":
        """Load config from file if exists, otherwise use default."""
        if path:
            path = Path(path)
            if path.exists():
                return cls.from_yaml(path)

        # Try default config.yml in current directory
        default_path = Path("config.yml")
        if default_path.exists():
            return cls.from_yaml(default_path)

        return cls.default()
