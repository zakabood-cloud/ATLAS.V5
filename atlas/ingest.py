"""Bounded text extraction with explicit source locators and omitted-content accounting."""
import csv
import hashlib
import io
import json
from html.parser import HTMLParser
from pathlib import Path
from .io import AtlasError, file_hash, parse_json

SUPPORTED={".txt",".md",".csv",".tsv",".json",".html",".htm",".pdf"}


class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__(); self.hidden=0; self.out=[]
    def handle_starttag(self,tag,attrs):
        if tag.lower() in {"script","style","noscript"}: self.hidden+=1
    def handle_endtag(self,tag):
        if tag.lower() in {"script","style","noscript"} and self.hidden: self.hidden-=1
    def handle_data(self,data):
        if not self.hidden and data.strip(): self.out.append(data)


def ingest(path,max_bytes=10_000_000,max_chars=200_000):
    path=Path(path)
    if path.is_symlink() or not path.is_file(): raise AtlasError("Input must be an existing regular nonsymlink file")
    if type(max_bytes) is not int or type(max_chars) is not int or not 1000<=max_bytes<=50_000_000 or not 1000<=max_chars<=1_000_000:
        raise AtlasError("Invalid ingestion bounds")
    if path.stat().st_size>max_bytes: raise AtlasError("Source file exceeds ingestion limit")
    suffix=path.suffix.lower()
    if suffix not in SUPPORTED: raise AtlasError("Unsupported format; use an approved specialist reader")
    warnings=[]; parts=[]; segments=[]; used=0; truncated=False; pages=None; pages_processed=0; empty_pages=[]
    def append(text,locator):
        nonlocal used,truncated
        remaining=max_chars-used
        if len(text)>remaining: truncated=True
        part=text[:remaining]
        if part:
            segments.append({"locator":locator,"start":used,"end":used+len(part)})
            parts.append(part); used+=len(part)
    if suffix==".pdf":
        try:
            from pypdf import PdfReader
        except ImportError as error:
            raise AtlasError("PDF extraction requires optional pypdf; graphics/scans still require visual inspection") from error
        reader=PdfReader(str(path),strict=True)
        if reader.is_encrypted: raise AtlasError("Encrypted PDFs are not supported")
        pages=len(reader.pages)
        if pages>500: raise AtlasError("PDF page count exceeds limit")
        for index,page in enumerate(reader.pages,1):
            if used>=max_chars:
                truncated=True
                break
            text=page.extract_text() or ""
            pages_processed+=1
            if not text.strip(): empty_pages.append(index)
            append(f"[[PDF page {index}]]\n{text}\n",f"PDF page {index}")
        warnings.append("Text extraction cannot verify charts, images, scans or layout; inspect relevant pages visually. Optional parsers are not a sandbox.")
    else:
        content=path.read_text(encoding="utf-8-sig",errors="strict")
        if suffix in {".html",".htm"}:
            parser=VisibleText(); parser.feed(content); parser.close()
            append("\n".join(parser.out),"HTML visible text")
            warnings.append("HTML extraction omits visual layout and JavaScript-rendered content")
        elif suffix==".json":
            append(json.dumps(parse_json(content),indent=2,ensure_ascii=False,allow_nan=False),"JSON document (formatted)")
        elif suffix in {".csv",".tsv"}:
            for index,row in enumerate(csv.reader(io.StringIO(content),delimiter="," if suffix==".csv" else "\t"),1):
                if index>100000: raise AtlasError("Too many tabular rows")
                if used>=max_chars:
                    truncated=True
                    break
                append(" | ".join(row)+"\n",f"table row {index}")
            warnings.append("Text view does not preserve cell types, quoting or formulas; use structured inputs for numerical analysis")
        else:
            append(content,f"source lines 1-{max(1,len(content.splitlines()))}")
    text="".join(parts)
    if not text.strip() or (pages and len(empty_pages)==pages_processed):
        warnings.append("No substantive text extracted; inspect empty or image-only content before using it as evidence")
    if truncated: warnings.append("Extraction is incomplete; omitted content must not be treated as reviewed")
    return {"path":str(path),"sha256":file_hash(path),"source_bytes":path.stat().st_size,"format":suffix,
            "pages":pages,"pages_processed":pages_processed,"empty_pages":empty_pages,
            "text":text,"text_sha256":hashlib.sha256(text.encode("utf-8")).hexdigest(),"segments":segments,
            "truncated":truncated,"warnings":warnings,"verification_level":"content_extraction_only_not_source_authenticity"}
