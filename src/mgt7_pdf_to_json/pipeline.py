"""Main pipeline orchestrator."""

from __future__ import annotations

import json
import logging
import time
import uuid
from pathlib import Path
from typing import Any

from mgt7_pdf_to_json.artifacts import ArtifactManager
from mgt7_pdf_to_json.config import Config
from mgt7_pdf_to_json.extractor import PdfPlumberExtractor
from mgt7_pdf_to_json.logging_ import LoggerFactory, log_with_request_id
from mgt7_pdf_to_json.mappers import get_mapper
from mgt7_pdf_to_json.normalizer import DocumentNormalizer
from mgt7_pdf_to_json.parser import DocumentParser
from mgt7_pdf_to_json.validator import Validator

logger = LoggerFactory.get_logger("pipeline")


class Pipeline:
    """Main pipeline for PDF to JSON conversion.

    Orchestrates the complete conversion process from PDF to JSON,
    including extraction, normalization, parsing, mapping, and validation.

    Example:
        >>> from mgt7_pdf_to_json.config import Config
        >>> config = Config.default()
        >>> pipeline = Pipeline(config)
        >>> result = pipeline.process("example.pdf", "output.json")
        >>> "meta" in result
        True
    """

    def __init__(self, config: Config):
        """
        Initialize pipeline with configuration.

        Args:
            config: Configuration object
        """
        self.config = config
        self.extractor = PdfPlumberExtractor()
        self.normalizer = DocumentNormalizer()
        self.parser = DocumentParser()
        self.validator = Validator(config)
        self.artifact_manager = ArtifactManager(config)

        # Setup logging
        LoggerFactory.setup_logging(config)

    def process(self, pdf_path: str, output_path: str | None = None) -> dict[str, Any]:
        """
        Process PDF file and convert to JSON.

        Args:
            pdf_path: Path to input PDF file
            output_path: Optional output JSON path. If not provided, uses <pdf_path>.json

        Returns:
            Dictionary with processing result
        """
        # Generate request_id for this run
        request_id = str(uuid.uuid4())
        pdf_name = Path(pdf_path).name

        # Set request_id in context for all components
        from mgt7_pdf_to_json.logging_ import set_request_id

        set_request_id(request_id)

        log_with_request_id(
            logger,
            logging.INFO,
            f"Starting processing: {pdf_name}",
            request_id,
            pdf_path=pdf_name,
            step="start",
        )

        start_time = time.time()

        try:
            # Step 1: Extract
            step_start = time.time()
            log_with_request_id(
                logger,
                logging.INFO,
                "Extracting PDF",
                request_id,
                pdf_path=pdf_name,
                step="extract",
            )

            raw_doc = self.extractor.extract(pdf_path)

            duration_ms = (time.time() - step_start) * 1000
            log_with_request_id(
                logger,
                logging.INFO,
                "Extraction completed",
                request_id,
                pdf_path=pdf_name,
                step="extract",
                duration_ms=duration_ms,
            )

            # Save raw artifact
            self.artifact_manager.save_raw(request_id, raw_doc)

            # Step 2: Normalize
            step_start = time.time()
            log_with_request_id(
                logger,
                logging.INFO,
                "Normalizing document",
                request_id,
                pdf_path=pdf_name,
                step="normalize",
            )

            normalized_doc = self.normalizer.normalize(raw_doc)

            duration_ms = (time.time() - step_start) * 1000
            log_with_request_id(
                logger,
                logging.INFO,
                "Normalization completed",
                request_id,
                pdf_path=pdf_name,
                step="normalize",
                duration_ms=duration_ms,
            )

            # Save normalized artifact
            self.artifact_manager.save_normalized(request_id, normalized_doc)

            # Step 3: Parse
            step_start = time.time()
            log_with_request_id(
                logger,
                logging.INFO,
                "Parsing document",
                request_id,
                pdf_path=pdf_name,
                step="parse",
            )

            parsed_doc = self.parser.parse(normalized_doc, raw_doc.tables)

            duration_ms = (time.time() - step_start) * 1000
            parsed_keys = len(parsed_doc.data.get("key_value_pairs", {}))
            logger.debug(f"Parsed {parsed_keys} key-value pairs, form_type={parsed_doc.form_type}")
            log_with_request_id(
                logger,
                logging.INFO,
                f"Parsing completed: form_type={parsed_doc.form_type}",
                request_id,
                pdf_path=pdf_name,
                step="parse",
                duration_ms=duration_ms,
            )

            # Save parsed artifact
            self.artifact_manager.save_parsed(request_id, parsed_doc)

            # Step 4: Map
            step_start = time.time()
            log_with_request_id(
                logger,
                logging.INFO,
                f"Mapping to {self.config.pipeline.mapper} schema",
                request_id,
                pdf_path=pdf_name,
                step="map",
            )

            mapper = get_mapper(self.config.pipeline.mapper)
            logger.debug(f"Using mapper: {self.config.pipeline.mapper}")
            output = mapper.map(parsed_doc, request_id, pdf_name)
            output_size = len(str(output))
            logger.debug(
                f"Output generated: {output_size} characters (approx {output_size / 1024:.2f} KB)"
            )

            duration_ms = (time.time() - step_start) * 1000
            log_with_request_id(
                logger,
                logging.INFO,
                "Mapping completed",
                request_id,
                pdf_path=pdf_name,
                step="map",
                duration_ms=duration_ms,
            )

            # Step 5: Validate
            step_start = time.time()
            log_with_request_id(
                logger,
                logging.INFO,
                "Validating output",
                request_id,
                pdf_path=pdf_name,
                step="validate",
            )

            warnings, errors = self.validator.validate(output, pdf_path)

            output["warnings"] = warnings
            output["errors"] = errors

            if warnings:
                logger.debug(
                    f"Validation warnings ({len(warnings)}): {[w.get('code', 'unknown') for w in warnings]}"
                )
            if errors:
                logger.debug(
                    f"Validation errors ({len(errors)}): {[e.get('code', 'unknown') for e in errors]}"
                )

            duration_ms = (time.time() - step_start) * 1000
            log_with_request_id(
                logger,
                logging.INFO,
                f"Validation completed: {len(warnings)} warnings, {len(errors)} errors",
                request_id,
                pdf_path=pdf_name,
                step="validate",
                duration_ms=duration_ms,
            )

            # Step 6: Write output
            if output_path:
                step_start = time.time()
                log_with_request_id(
                    logger,
                    logging.INFO,
                    f"Writing output to {output_path}",
                    request_id,
                    pdf_path=pdf_name,
                    step="write",
                )

                output_path_obj = Path(output_path)
                output_path_obj.parent.mkdir(parents=True, exist_ok=True)

                with open(output_path_obj, "w", encoding="utf-8") as f:
                    json.dump(output, f, indent=2, ensure_ascii=False)

                file_size = output_path_obj.stat().st_size
                logger.debug(
                    f"Output file written: {output_path} ({file_size} bytes, {file_size / 1024:.2f} KB)"
                )

                duration_ms = (time.time() - step_start) * 1000
                log_with_request_id(
                    logger,
                    logging.INFO,
                    f"Output written: {output_path}",
                    request_id,
                    pdf_path=pdf_name,
                    step="write",
                    duration_ms=duration_ms,
                    artifact_path=str(output_path),
                )

            # Save output artifact
            self.artifact_manager.save_output(request_id, output)

            # Cleanup old artifacts
            if self.config.artifacts.enabled:
                self.artifact_manager.cleanup(request_id)

            total_duration_ms = (time.time() - start_time) * 1000
            log_with_request_id(
                logger,
                logging.INFO,
                f"Processing completed successfully in {total_duration_ms:.2f}ms",
                request_id,
                pdf_path=pdf_name,
                step="complete",
                duration_ms=total_duration_ms,
            )

            return output

        except Exception as e:
            total_duration_ms = (time.time() - start_time) * 1000
            log_with_request_id(
                logger,
                logging.ERROR,
                f"Processing failed: {e}",
                request_id,
                pdf_path=pdf_name,
                step="error",
                duration_ms=total_duration_ms,
            )
            raise
