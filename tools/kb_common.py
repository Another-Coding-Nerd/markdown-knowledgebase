"""Shared setup: config loading, embedding model, chroma collection."""

import fnmatch
import os
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


def iter_kb_files(cfg):
    """Return sorted list of Paths for all indexed .md files, per config filters."""
    kb_root = cfg["kb_root"]
    patterns = cfg.get("file_patterns") or ["**/*.md"]
    skip_patterns = cfg.get("skip_files") or cfg.get("exclude_patterns") or []
    follow_syms = bool(cfg.get("follow_symlinks", False))

    seen, found = set(), []
    for dirpath, _, filenames in os.walk(kb_root, followlinks=follow_syms):
        dp = Path(dirpath)
        for name in filenames:
            if not name.endswith(".md"):
                continue
            p = dp / name
            if p in seen:
                continue
            rel = str(p.relative_to(kb_root))
            if not any(p.match(pat) for pat in patterns):
                continue
            if any(fnmatch.fnmatch(name, sp) or fnmatch.fnmatch(rel, sp)
                   for sp in skip_patterns):
                continue
            seen.add(p)
            found.append(p)
    return sorted(found)


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
