"""Artifact management and retention policy."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any

from mgt7_pdf_to_json.config import Config
from mgt7_pdf_to_json.logging_ import LoggerFactory, log_with_request_id

if TYPE_CHECKING:
    from mgt7_pdf_to_json.models import NormalizedDocument, ParsedDocument, RawDocument

logger = LoggerFactory.get_logger("artifacts")


class ArtifactManager:
    """Manage intermediate debug artifacts."""

    def __init__(self, config: Config):
        """
        Initialize artifact manager with configuration.

        Args:
            config: Configuration object
        """
        self.config = config
        self.artifacts_dir = Path(config.logging.file) / config.artifacts.dir
        if config.artifacts.enabled:
            self.artifacts_dir.mkdir(parents=True, exist_ok=True)

    def save_raw(self, request_id: str, raw_doc: RawDocument) -> str | None:
        """
        Save raw document artifact.

        Args:
            request_id: Request ID
            raw_doc: Raw document

        Returns:
            Artifact file path or None if disabled
        """
        if not self.config.artifacts.enabled or not self.config.artifacts.save_raw:
            return None

        artifact_path = self.artifacts_dir / f"{request_id}.raw.json"
        with open(artifact_path, "w", encoding="utf-8") as f:
            json.dump(raw_doc.model_dump(), f, indent=2, ensure_ascii=False)

        log_with_request_id(
            logger,
            logging.INFO,
            f"Saved raw artifact: {artifact_path}",
            request_id,
            artifact_path=str(artifact_path),
        )

        return str(artifact_path)

    def save_normalized(self, request_id: str, normalized_doc: NormalizedDocument) -> str | None:
        """
        Save normalized document artifact.

        Args:
            request_id: Request ID
            normalized_doc: Normalized document

        Returns:
            Artifact file path or None if disabled
        """
        if not self.config.artifacts.enabled or not self.config.artifacts.save_normalized:
            return None

        artifact_path = self.artifacts_dir / f"{request_id}.normalized.json"
        with open(artifact_path, "w", encoding="utf-8") as f:
            json.dump(normalized_doc.model_dump(), f, indent=2, ensure_ascii=False)

        log_with_request_id(
            logger,
            logging.INFO,
            f"Saved normalized artifact: {artifact_path}",
            request_id,
            artifact_path=str(artifact_path),
        )

        return str(artifact_path)

    def save_parsed(self, request_id: str, parsed_doc: ParsedDocument) -> str | None:
        """
        Save parsed document artifact.

        Args:
            request_id: Request ID
            parsed_doc: Parsed document

        Returns:
            Artifact file path or None if disabled
        """
        if not self.config.artifacts.enabled or not self.config.artifacts.save_parsed:
            return None

        artifact_path = self.artifacts_dir / f"{request_id}.parsed.json"
        with open(artifact_path, "w", encoding="utf-8") as f:
            json.dump(parsed_doc.model_dump(), f, indent=2, ensure_ascii=False)

        log_with_request_id(
            logger,
            logging.INFO,
            f"Saved parsed artifact: {artifact_path}",
            request_id,
            artifact_path=str(artifact_path),
        )

        return str(artifact_path)

    def save_output(self, request_id: str, output: dict[str, Any]) -> str | None:
        """
        Save output JSON artifact.

        Args:
            request_id: Request ID
            output: Output JSON dictionary

        Returns:
            Artifact file path or None if disabled
        """
        if not self.config.artifacts.enabled or not self.config.artifacts.save_output:
            return None

        artifact_path = self.artifacts_dir / f"{request_id}.output.json"
        with open(artifact_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        log_with_request_id(
            logger,
            logging.INFO,
            f"Saved output artifact: {artifact_path}",
            request_id,
            artifact_path=str(artifact_path),
        )

        return str(artifact_path)

    def cleanup(self, request_id: str | None = None) -> int:
        """
        Clean up old artifacts based on retention policy.

        Args:
            request_id: Optional request ID for logging

        Returns:
            Number of artifacts deleted
        """
        if not self.artifacts_dir.exists():
            return 0

        keep_days = self.config.artifacts.keep_days
        cutoff_date = datetime.now() - timedelta(days=keep_days)

        deleted_count = 0

        for artifact_file in self.artifacts_dir.glob("*.json"):
            try:
                # Get file modification time
                mtime = datetime.fromtimestamp(artifact_file.stat().st_mtime)

                if mtime < cutoff_date:
                    artifact_file.unlink()
                    deleted_count += 1

            except Exception as e:
                logger.warning(f"Error deleting artifact {artifact_file}: {e}")

        if deleted_count > 0:
            log_msg = f"Cleaned up {deleted_count} artifacts older than {keep_days} days"
            if request_id:
                log_with_request_id(
                    logger,
                    logging.INFO,
                    log_msg,
                    request_id,
                    step="artifacts_cleanup",
                )
            else:
                logger.info(log_msg)

        return deleted_count
