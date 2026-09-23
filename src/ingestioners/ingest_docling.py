"""Read pdf / docx / txt with Docling, chunk structurally, store in ChromaDB.

pip install docling chromadb

CLI:  python document_ingestor.py path/to/file.pdf
"""
from __future__ import annotations

import hashlib
import logging
from io import BytesIO
from pathlib import Path
from typing import Any, Iterable

import chromadb
from docling.chunking import HierarchicalChunker, HybridChunker
from docling.datamodel.base_models import DocumentStream, InputFormat
from docling.document_converter import DocumentConverter

from configuration.entities import DocumentIngestorConfig

log = logging.getLogger(__name__)

SUPPORTED_EXTS = {".pdf", ".docx", ".txt", ".md"}


class DocumentIngestor:
    def __init__(
        self,
        ingestor_config: DocumentIngestorConfig | None = None,
        embedding_function: Any | None = None,  # None -> Chroma default (MiniLM)
    ):
        ingestor_config = ingestor_config or DocumentIngestorConfig()

        self.converter = DocumentConverter(
            allowed_formats=[InputFormat.PDF, InputFormat.DOCX, InputFormat.MD]
        )
        self.chunker = (
            HybridChunker()
            if ingestor_config.ingestor_chunker == "HybridChunker"
            else HierarchicalChunker()
        )
        self.batch_size = ingestor_config.ingestor_batch_size

        self.client = chromadb.PersistentClient(path=ingestor_config.ingestor_persist_dir)
        kwargs = {"embedding_function": embedding_function} if embedding_function else {}
        self.collection = self.client.get_or_create_collection(
            name=ingestor_config.ingestor_collection_name,
            metadata={"hnsw:space": "cosine"},
            **kwargs,
        )

    # ---------- reading ----------
    def _convert(self, path: Path):
        if path.suffix.lower() == ".txt":
            # Docling has no native .txt input; feed it as markdown.
            stream = DocumentStream(
                name=f"{path.stem}.md", stream=BytesIO(path.read_bytes())
            )
            return self.converter.convert(stream).document
        return self.converter.convert(path).document

    # ---------- chunking ----------
    def _chunk(self, doc) -> Iterable[tuple[str, dict]]:
        for chunk in self.chunker.chunk(dl_doc=doc):
            # contextualize() prepends headings -> better embeddings
            text = self.chunker.contextualize(chunk=chunk).strip()
            if not text:
                continue
            meta: dict[str, Any] = {
                "headings": " > ".join(chunk.meta.headings or []),
            }
            pages = sorted(
                {p.page_no for item in chunk.meta.doc_items for p in item.prov}
            )
            if pages:  # docx/txt have no page provenance
                meta["page_start"], meta["page_end"] = pages[0], pages[-1]
            yield text, meta

    # ---------- ingestion ----------
    @staticmethod
    def _file_hash(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def ingest_file(self, path: str | Path, skip_unchanged: bool = True) -> int:
        """Read the file at `path`, chunk it, and store the chunks in Chroma.

        Returns the number of chunks stored (0 if the file was unchanged).
        """
        # path = Path(path).expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError(path)
        if path.suffix.lower() not in SUPPORTED_EXTS:
            raise ValueError(f"Unsupported file type: {path.suffix}")

        file_hash = self._file_hash(path)
        source = str(path)

        if skip_unchanged and self.collection.get(
            where={"$and": [{"source": source}, {"file_hash": file_hash}]},
            limit=1,
        )["ids"]:
            log.info("Skipping unchanged file: %s", path.name)
            return 0

        # Convert first: if parsing fails, existing chunks stay untouched.
        doc = self._convert(path)

        source_id = hashlib.sha256(source.encode()).hexdigest()[:16]
        ids, docs, metas = [], [], []
        for i, (text, meta) in enumerate(self._chunk(doc)):
            ids.append(f"{source_id}-{i}")
            docs.append(text)
            metas.append(
                {
                    **meta,
                    "source": source,
                    "filename": path.name,
                    "file_type": path.suffix.lower().lstrip("."),
                    "file_hash": file_hash,
                    "chunk_index": i,
                }
            )

        # File changed (or new): drop stale chunks for this source, then write
        self.collection.delete(where={"source": source})
        for s in range(0, len(ids), self.batch_size):
            e = s + self.batch_size
            self.collection.upsert(
                ids=ids[s:e], documents=docs[s:e], metadatas=metas[s:e]
            )
        log.info("Ingested %s -> %d chunks", path.name, len(ids))
        return len(ids)

    def ingest_dir(self, directory: str | Path, recursive: bool = True) -> dict[str, int]:
        pattern = "**/*" if recursive else "*"
        results = {}
        for p in sorted(Path(directory).glob(pattern)):
            if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS:
                try:
                    results[p.name] = self.ingest_file(p)
                except Exception:
                    log.exception("Failed to ingest %s", p)
                    results[p.name] = -1
        return results

    # ---------- maintenance ----------
    def delete_file(self, path: str | Path) -> None:
        self.collection.delete(where={"source": str(Path(path).resolve())})


if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Ingest a single file into Chroma")
    parser.add_argument("path", help="Path to a pdf / docx / txt / md file")
    args = parser.parse_args()

    n = DocumentIngestor().ingest_file(args.path)
    print(f"{n} chunks stored")