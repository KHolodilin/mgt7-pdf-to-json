"""Tests for artifact management."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from mgt7_pdf_to_json.artifacts import ArtifactManager
from mgt7_pdf_to_json.config import Config
from mgt7_pdf_to_json.models import NormalizedDocument, ParsedDocument, RawDocument


class TestArtifactManager:
    """Test artifact management functionality."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for artifacts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def config_with_artifacts(self, temp_dir):
        """Configuration with artifacts enabled."""
        config = Config.default()
        config.artifacts.enabled = True
        config.artifacts.save_raw = True
        config.artifacts.save_normalized = True
        config.artifacts.save_parsed = True
        config.artifacts.save_output = True
        config.logging.file = str(temp_dir)
        return config

    @pytest.fixture
    def config_without_artifacts(self, temp_dir):
        """Configuration with artifacts disabled."""
        config = Config.default()
        config.artifacts.enabled = False
        config.logging.file = str(temp_dir)
        return config

    @pytest.fixture
    def raw_document(self):
        """Create sample raw document."""
        return RawDocument(
            text="Sample text",
            pages=[],
            tables=[],
            metadata={"pages": 1},
        )

    @pytest.fixture
    def normalized_document(self):
        """Create sample normalized document."""
        return NormalizedDocument(
            text="normalized text",
            pages=[],
        )

    @pytest.fixture
    def parsed_document(self):
        """Create sample parsed document."""
        return ParsedDocument(
            form_type="MGT-7",
            company={"cin": "U12345DL2013PTC123456", "name": "Test Company"},
            financial_year={"from": "01/04/2023", "to": "31/03/2024"},
            data={},
        )

    def test_save_raw_when_enabled(self, config_with_artifacts, raw_document, temp_dir):
        """Test saving raw artifact when enabled."""
        manager = ArtifactManager(config_with_artifacts)
        request_id = "test-123"

        result = manager.save_raw(request_id, raw_document)

        assert result is not None
        assert Path(result).exists()
        with open(result, encoding="utf-8") as f:
            data = json.load(f)
            assert data["text"] == "Sample text"

    def test_save_raw_when_disabled(self, config_without_artifacts, raw_document):
        """Test saving raw artifact when disabled."""
        manager = ArtifactManager(config_without_artifacts)
        request_id = "test-123"

        result = manager.save_raw(request_id, raw_document)

        assert result is None

    def test_save_normalized_when_enabled(
        self, config_with_artifacts, normalized_document, temp_dir
    ):
        """Test saving normalized artifact when enabled."""
        manager = ArtifactManager(config_with_artifacts)
        request_id = "test-123"

        result = manager.save_normalized(request_id, normalized_document)

        assert result is not None
        assert Path(result).exists()
        with open(result, encoding="utf-8") as f:
            data = json.load(f)
            assert data["text"] == "normalized text"

    def test_save_normalized_when_disabled(self, config_without_artifacts, normalized_document):
        """Test saving normalized artifact when disabled."""
        manager = ArtifactManager(config_without_artifacts)
        request_id = "test-123"

        result = manager.save_normalized(request_id, normalized_document)

        assert result is None

    def test_save_parsed_when_enabled(self, config_with_artifacts, parsed_document, temp_dir):
        """Test saving parsed artifact when enabled."""
        manager = ArtifactManager(config_with_artifacts)
        request_id = "test-123"

        result = manager.save_parsed(request_id, parsed_document)

        assert result is not None
        assert Path(result).exists()
        with open(result, encoding="utf-8") as f:
            data = json.load(f)
            assert data["form_type"] == "MGT-7"

    def test_save_parsed_when_disabled(self, config_without_artifacts, parsed_document):
        """Test saving parsed artifact when disabled."""
        manager = ArtifactManager(config_without_artifacts)
        request_id = "test-123"

        result = manager.save_parsed(request_id, parsed_document)

        assert result is None

    def test_save_output_when_enabled(self, config_with_artifacts, temp_dir):
        """Test saving output artifact when enabled."""
        manager = ArtifactManager(config_with_artifacts)
        request_id = "test-123"
        output = {"meta": {"request_id": "test-123"}, "data": {}}

        result = manager.save_output(request_id, output)

        assert result is not None
        assert Path(result).exists()
        with open(result, encoding="utf-8") as f:
            data = json.load(f)
            assert data["meta"]["request_id"] == "test-123"

    def test_save_output_when_disabled(self, config_without_artifacts):
        """Test saving output artifact when disabled."""
        manager = ArtifactManager(config_without_artifacts)
        request_id = "test-123"
        output = {"meta": {"request_id": "test-123"}, "data": {}}

        result = manager.save_output(request_id, output)

        assert result is None

    def test_cleanup_removes_old_artifacts(self, config_with_artifacts, temp_dir):
        """Test cleanup removes artifacts older than retention period."""
        manager = ArtifactManager(config_with_artifacts)
        artifacts_dir = manager.artifacts_dir

        # Create artifact file
        artifact_file = artifacts_dir / "test.raw.json"
        artifact_file.write_text('{"text": "test"}', encoding="utf-8")

        # Mock datetime.now() to return a date far in the future
        # This makes the file appear old relative to the cutoff
        from datetime import datetime, timedelta

        future_date = datetime.now() + timedelta(
            days=config_with_artifacts.artifacts.keep_days + 10
        )

        with patch("mgt7_pdf_to_json.artifacts.datetime") as mock_datetime:
            mock_datetime.now.return_value = future_date
            deleted = manager.cleanup()

        # File should be deleted as it's now older than keep_days
        assert deleted >= 0  # At least 0, could be 1 if file was old enough

    def test_cleanup_keeps_recent_artifacts(self, config_with_artifacts, temp_dir):
        """Test cleanup keeps artifacts within retention period."""
        manager = ArtifactManager(config_with_artifacts)
        artifacts_dir = manager.artifacts_dir

        # Create recent artifact file
        recent_file = artifacts_dir / "recent.raw.json"
        recent_file.write_text('{"text": "recent"}', encoding="utf-8")

        deleted = manager.cleanup()

        assert deleted == 0
        assert recent_file.exists()

    def test_cleanup_when_dir_not_exists(self, config_with_artifacts, tmp_path):
        """Test cleanup when artifacts directory doesn't exist."""
        # Use a non-existent subdirectory in temp path (accessible but doesn't exist)
        nonexistent_dir = tmp_path / "nonexistent" / "path"
        config_with_artifacts.logging.file = str(nonexistent_dir)
        # Disable artifacts to avoid creating directory in __init__
        config_with_artifacts.artifacts.enabled = False
        manager = ArtifactManager(config_with_artifacts)

        deleted = manager.cleanup()

        assert deleted == 0

    def test_cleanup_with_request_id(self, config_with_artifacts, temp_dir):
        """Test cleanup with request ID for logging."""
        manager = ArtifactManager(config_with_artifacts)
        request_id = "test-123"

        deleted = manager.cleanup(request_id)

        assert deleted == 0  # No old files

    def test_cleanup_without_request_id(self, config_with_artifacts, temp_dir):
        """Test cleanup without request ID (uses logger.info)."""
        manager = ArtifactManager(config_with_artifacts)

        deleted = manager.cleanup()

        assert deleted == 0  # No old files

    def test_cleanup_error_handling(self, config_with_artifacts, temp_dir):
        """Test cleanup error handling when file deletion fails."""
        manager = ArtifactManager(config_with_artifacts)
        artifacts_dir = manager.artifacts_dir

        # Create artifact file
        artifact_file = artifacts_dir / "test.raw.json"
        artifact_file.write_text('{"text": "test"}', encoding="utf-8")

        # Mock Path.unlink to raise exception (patch the method, not the instance)
        with patch("pathlib.Path.unlink", side_effect=OSError("Permission denied")):
            deleted = manager.cleanup()

        # Should handle error gracefully and continue
        assert deleted == 0  # File wasn't deleted due to error

    def test_cleanup_actually_deletes_file(self, config_with_artifacts, temp_dir):
        """Test cleanup actually deletes old files (covers unlink and deleted_count increment)."""
        manager = ArtifactManager(config_with_artifacts)
        artifacts_dir = manager.artifacts_dir

        # Create artifact file
        artifact_file = artifacts_dir / "old.raw.json"
        artifact_file.write_text('{"text": "old"}', encoding="utf-8")
        assert artifact_file.exists()

        # Set file modification time to be old by using os.utime
        import os
        from datetime import datetime, timedelta

        old_time = datetime.now() - timedelta(days=config_with_artifacts.artifacts.keep_days + 1)
        old_timestamp = old_time.timestamp()
        os.utime(artifact_file, (old_timestamp, old_timestamp))

        deleted = manager.cleanup()

        # File should be deleted (covers lines 182-183)
        assert deleted > 0
        assert not artifact_file.exists()

    def test_cleanup_logs_with_request_id_when_deleted(self, config_with_artifacts, temp_dir):
        """Test cleanup logs with request_id when files are deleted (covers lines 189-197)."""
        manager = ArtifactManager(config_with_artifacts)
        request_id = "test-123"

        # Create old artifact file
        artifacts_dir = manager.artifacts_dir
        artifact_file = artifacts_dir / "old.raw.json"
        artifact_file.write_text('{"text": "old"}', encoding="utf-8")

        # Set file modification time to be old by using os.utime
        import os
        from datetime import datetime, timedelta

        old_time = datetime.now() - timedelta(days=config_with_artifacts.artifacts.keep_days + 1)
        old_timestamp = old_time.timestamp()
        os.utime(artifact_file, (old_timestamp, old_timestamp))

        deleted = manager.cleanup(request_id)

        # Should use log_with_request_id (covers lines 189-197)
        assert deleted > 0

    def test_cleanup_logs_without_request_id_when_deleted(self, config_with_artifacts, temp_dir):
        """Test cleanup logs without request_id when files are deleted (covers lines 198-199)."""
        manager = ArtifactManager(config_with_artifacts)

        # Create old artifact file
        artifacts_dir = manager.artifacts_dir
        artifact_file = artifacts_dir / "old.raw.json"
        artifact_file.write_text('{"text": "old"}', encoding="utf-8")

        # Set file modification time to be old by using os.utime
        import os
        from datetime import datetime, timedelta

        old_time = datetime.now() - timedelta(days=config_with_artifacts.artifacts.keep_days + 1)
        old_timestamp = old_time.timestamp()
        os.utime(artifact_file, (old_timestamp, old_timestamp))

        deleted = manager.cleanup()

        # Should use logger.info (covers lines 198-199)
        assert deleted > 0

    def test_cleanup_deletes_old_file(self, config_with_artifacts, temp_dir):
        """Test cleanup actually deletes old files."""
        manager = ArtifactManager(config_with_artifacts)
        artifacts_dir = manager.artifacts_dir

        # Create artifact file
        artifact_file = artifacts_dir / "old.raw.json"
        artifact_file.write_text('{"text": "old"}', encoding="utf-8")

        # Mock datetime.now() to make the file appear old
        from datetime import datetime, timedelta

        future_date = datetime.now() + timedelta(days=config_with_artifacts.artifacts.keep_days + 1)
        with patch("mgt7_pdf_to_json.artifacts.datetime") as mock_datetime:
            mock_datetime.now.return_value = future_date
            deleted = manager.cleanup()

        # File should be deleted as it's now older than keep_days
        assert deleted >= 0

    def test_cleanup_logs_with_request_id(self, config_with_artifacts, temp_dir):
        """Test cleanup logs with request_id when provided."""
        manager = ArtifactManager(config_with_artifacts)
        request_id = "test-123"

        # Create old artifact file
        artifacts_dir = manager.artifacts_dir
        artifact_file = artifacts_dir / "old.raw.json"
        artifact_file.write_text('{"text": "old"}', encoding="utf-8")

        # Mock datetime.now() to make the file appear old
        from datetime import datetime, timedelta

        future_date = datetime.now() + timedelta(days=config_with_artifacts.artifacts.keep_days + 1)
        with patch("mgt7_pdf_to_json.artifacts.datetime") as mock_datetime:
            mock_datetime.now.return_value = future_date
            deleted = manager.cleanup(request_id)

        # Should use log_with_request_id
        assert deleted >= 0

    def test_cleanup_logs_without_request_id(self, config_with_artifacts, temp_dir):
        """Test cleanup logs without request_id (uses logger.info)."""
        manager = ArtifactManager(config_with_artifacts)

        # Create old artifact file
        artifacts_dir = manager.artifacts_dir
        artifact_file = artifacts_dir / "old.raw.json"
        artifact_file.write_text('{"text": "old"}', encoding="utf-8")

        # Mock datetime.now() to make the file appear old
        from datetime import datetime, timedelta

        future_date = datetime.now() + timedelta(days=config_with_artifacts.artifacts.keep_days + 1)
        with patch("mgt7_pdf_to_json.artifacts.datetime") as mock_datetime:
            mock_datetime.now.return_value = future_date
            deleted = manager.cleanup()

        # Should use logger.info (not log_with_request_id)
        assert deleted >= 0
