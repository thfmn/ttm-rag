"""
Orchestration resource scaffolding (Phase 2).

Lightweight, dependency-minimal helpers for configuring external resources
used by the ingestion & curation pipeline. These are import-guarded and
do not require Dagster unless explicitly requested by callers.

Resources covered (placeholders, productionize later):
- Database engine (Postgres via SQLAlchemy URL)
- Object storage client (optional; placeholder)
- KMS/Secrets config (env-based)
- Model gateway (adapter registry policy placeholder)
"""

from __future__ import annotations

from typing import Any, Dict, Optional
from dataclasses import dataclass
import os

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


@dataclass
class DatabaseConfig:
    url: str


def get_database_config() -> DatabaseConfig:
    """
    Return database configuration from environment or defaults to local SQLite.
    """
    url = os.getenv("DATABASE_URL", "sqlite:///thai_medicine.db")
    return DatabaseConfig(url=url)


def create_db_engine(cfg: Optional[DatabaseConfig] = None) -> Engine:
    """
    Create a SQLAlchemy engine from the provided config.
    """
    cfg = cfg or get_database_config()
    return create_engine(cfg.url)


@dataclass
class ObjectStoreConfig:
    provider: str  # e.g. "s3", "gcs", "local"
    bucket: str
    prefix: str = ""


def get_object_store_config() -> Optional[ObjectStoreConfig]:
    """
    Return object store config from env if present, otherwise None.
    """
    provider = os.getenv("OBJ_STORE_PROVIDER")
    bucket = os.getenv("OBJ_STORE_BUCKET")
    prefix = os.getenv("OBJ_STORE_PREFIX", "")
    if provider and bucket:
        return ObjectStoreConfig(provider=provider, bucket=bucket, prefix=prefix)
    return None


def create_object_store_client(cfg: ObjectStoreConfig) -> Any:
    """
    Placeholder object store client factory.
    For S3/GCS providers, integrate boto3/google-cloud-storage later.
    """
    # Deliberately return a simple dict for now to avoid new dependencies.
    return {"provider": cfg.provider, "bucket": cfg.bucket, "prefix": cfg.prefix}


@dataclass
class KMSConfig:
    provider: str  # "aws-kms", "gcp-kms", "vault", "env"
    key_id: str


def get_kms_config() -> Optional[KMSConfig]:
    provider = os.getenv("KMS_PROVIDER")
    key_id = os.getenv("KMS_KEY_ID")
    if provider and key_id:
        return KMSConfig(provider=provider, key_id=key_id)
    return None


@dataclass
class ModelGatewayPolicy:
    """
    Placeholder for a policy-based adapter selection.
    """
    default_model_id: str = "hf-typhoon-7b"


def get_model_gateway_policy() -> ModelGatewayPolicy:
    """
    Load model gateway policy from env or defaults.
    """
    default_model = os.getenv("DEFAULT_MODEL_ID", "hf-typhoon-7b")
    return ModelGatewayPolicy(default_model_id=default_model)


def get_dagster_resource_defs() -> Dict[str, Any]:
    """
    Optional: Build Dagster resource definitions if Dagster is available.
    Import-guarded to avoid adding a hard dependency.
    """
    try:
        from dagster import ResourceDefinition  # type: ignore
    except Exception as e:  # pragma: no cover
        raise ImportError(
            "Dagster is required to construct resource definitions.\n"
            "Install with:\n"
            "  uv pip install \"dagster>=1.7\" \"dagster-webserver>=1.7\""
        ) from e

    # Wrap factories into Dagster ResourceDefinition objects
    def _db_resource(_init_context):
        return create_db_engine()

    def _object_store_resource(_init_context):
        cfg = get_object_store_config()
        return create_object_store_client(cfg) if cfg else None

    def _kms_resource(_init_context):
        return get_kms_config()

    def _model_gateway_resource(_init_context):
        return get_model_gateway_policy()

    return {
        "db_engine": ResourceDefinition.hardcoded_resource(_db_resource(None)),  # simple eager construction
        "object_store": ResourceDefinition.hardcoded_resource(_object_store_resource(None)),
        "kms": ResourceDefinition.hardcoded_resource(_kms_resource(None)),
        "model_gateway_policy": ResourceDefinition.hardcoded_resource(_model_gateway_resource(None)),
    }
