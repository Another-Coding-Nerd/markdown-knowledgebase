"""Shared setup: config loading, embedding model, chroma collection."""

import yaml
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_config(config_path=None):
    path = Path(config_path) if config_path else PROJECT_ROOT / "config.yaml"
    with open(path) as f:
        cfg = yaml.safe_load(f)

    cfg["_project_root"] = PROJECT_ROOT
    cfg["kb_root"] = (PROJECT_ROOT / cfg["kb_root"]).resolve()
    cfg["index_dir"] = (PROJECT_ROOT / cfg["index_dir"]).resolve()
    return cfg


def get_embedding_model(cfg):
    from fastembed import TextEmbedding
    return TextEmbedding(model_name=cfg["embedding_model"])


def get_collection(cfg, client=None):
    import chromadb
    if client is None:
        client = chromadb.PersistentClient(path=str(cfg["index_dir"]))
    return client.get_or_create_collection(
        name="kb_chunks",
        metadata={"hnsw:space": "cosine"},
    )
