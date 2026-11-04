"""Shared bounded ZIP validation for backups, baselines and release packages."""
from pathlib import Path, PurePosixPath
import re
import stat
from .io import AtlasError

MAX_FILE_BYTES=100_000_000
MAX_TOTAL_BYTES=500_000_000
MAX_MEMBERS=50_000


def safe_name(name):
    if not isinstance(name,str) or not name or "\\" in name or ":" in name or "\x00" in name:
        raise AtlasError("Unsafe archive path")
    path=PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts or not path.parts or path.as_posix()!=name:
        raise AtlasError("Archive path must be normalized and relative")
    return name


def checked_members(archive):
    infos=archive.infolist()
    if len(infos)>MAX_MEMBERS: raise AtlasError("Too many archive members")
    seen=set(); portable=set(); files=set(); total=0
    for info in infos:
        name=safe_name(info.filename[:-1] if info.is_dir() else info.filename)
        if name in seen or name.casefold() in portable: raise AtlasError("Duplicate or nonportable archive path")
        seen.add(name); portable.add(name.casefold())
        kind=stat.S_IFMT(info.external_attr>>16)
        if kind not in (0,stat.S_IFREG,stat.S_IFDIR) or info.flag_bits&1:
            raise AtlasError("Special, symlink or encrypted archive member")
        if info.file_size<0 or info.file_size>MAX_FILE_BYTES: raise AtlasError("Archive member exceeds size limit")
        total+=info.file_size
        if total>MAX_TOTAL_BYTES: raise AtlasError("Archive expanded size exceeds limit")
        if not info.is_dir(): files.add(name)
    portable_files={name.casefold() for name in files}
    for name in seen:
        if any(parent.as_posix().casefold() in portable_files for parent in PurePosixPath(name).parents if parent.parts):
            raise AtlasError("Archive file/directory conflict")
    return infos


def manifest_index(rows,size_key="size"):
    if not isinstance(rows,list) or len(rows)>MAX_MEMBERS: raise AtlasError("Invalid manifest file list")
    result={}; portable=set(); total=0
    for row in rows:
        if not isinstance(row,dict): raise AtlasError("Invalid manifest row")
        name=safe_name(row.get("path"))
        size=row.get(size_key)
        if name.casefold() in portable or type(size) is not int or not 0<=size<=MAX_FILE_BYTES:
            raise AtlasError("Duplicate manifest path or invalid size")
        portable.add(name.casefold())
        if not isinstance(row.get("sha256"),str) or not re.fullmatch(r"[a-f0-9]{64}",row["sha256"]):
            raise AtlasError("Invalid manifest SHA256")
        total+=size
        if total>MAX_TOTAL_BYTES: raise AtlasError("Manifest expanded size exceeds limit")
        result[name]=row
    for name in result:
        if any(parent.as_posix().casefold() in portable for parent in PurePosixPath(name).parents if parent.parts):
            raise AtlasError("Manifest file/directory conflict")
    return result


def extract_checked(archive,destination):
    """Extract only to a fresh caller-owned scratch directory, after checking all names."""
    destination=Path(destination)
    if destination.exists(): raise AtlasError("Extraction destination must be new")
    infos=checked_members(archive)
    destination.mkdir(parents=True)
    for info in infos:
        path=destination/info.filename
        if info.is_dir():
            path.mkdir(parents=True,exist_ok=True)
        else:
            path.parent.mkdir(parents=True,exist_ok=True)
            with archive.open(info) as source, path.open("xb") as output:
                remaining=info.file_size
                while remaining:
                    chunk=source.read(min(1024*1024,remaining))
                    if not chunk: raise AtlasError("Truncated archive member")
                    output.write(chunk); remaining-=len(chunk)
                if source.read(1): raise AtlasError("Archive member size mismatch")
