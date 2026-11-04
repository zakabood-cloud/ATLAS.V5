"""Quiesced complete backups and verified restore-to-new-destination only."""
import hashlib
import os
import tempfile
import zipfile
from pathlib import Path
from .archive import checked_members, manifest_index, safe_name, MAX_FILE_BYTES, MAX_TOTAL_BYTES
from .io import AtlasError, file_hash, canonical, now, parse_json


def backup(project_dir,archive,quiesced=False):
    source=Path(project_dir).resolve(); archive=Path(archive).absolute()
    if quiesced is not True: raise AtlasError("Quiesce project writers and external jobs before backup")
    if not source.is_dir() or not (source/"state.sqlite3").is_file(): raise AtlasError("Not an ATLAS project")
    if archive.is_symlink() or archive.exists(): raise AtlasError("Will not overwrite a backup or symlink")
    if archive.resolve().is_relative_to(source): raise AtlasError("Backup destination must be outside project")
    entries=[]; total=0
    for path in sorted(source.rglob("*")):
        if path.is_symlink(): raise AtlasError("Symlink in project backup")
        if not path.is_file(): continue
        size=path.stat().st_size; total+=size
        if size>MAX_FILE_BYTES or total>MAX_TOTAL_BYTES: raise AtlasError("Project exceeds bounded backup size")
        entries.append({"path":safe_name(path.relative_to(source).as_posix()),"size":size,"sha256":file_hash(path)})
    manifest_index(entries)
    receipt={"schema_version":1,"created_at":now(),"files":entries,
             "limitation":"Operator attests quiescence; no guarantee against a malicious same-user writer."}
    archive.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".atlas-backup-",dir=archive.parent) as temp:
        candidate=Path(temp)/"backup.zip"
        with zipfile.ZipFile(candidate,"x",zipfile.ZIP_DEFLATED) as output:
            output.writestr("MANIFEST.json",canonical(receipt))
            for row in entries:
                data=(source/row["path"]).read_bytes()
                if len(data)!=row["size"] or hashlib.sha256(data).hexdigest()!=row["sha256"]:
                    raise AtlasError("Project changed during backup; quiesce all writers")
                output.writestr("PROJECT/"+row["path"],data)
        if archive.exists(): raise AtlasError("Backup destination appeared during creation")
        os.rename(candidate,archive)
    return {"archive":str(archive),"sha256":file_hash(archive),"files":len(entries)}


def restore(archive,new_project_dir):
    target=Path(new_project_dir).absolute()
    if target.exists() or target.is_symlink(): raise AtlasError("Restore requires a nonexistent destination")
    with zipfile.ZipFile(archive) as source:
        infos=checked_members(source)
        names={item.filename for item in infos}
        if "MANIFEST.json" not in names: raise AtlasError("Missing project manifest")
        receipt=parse_json(source.read("MANIFEST.json").decode("utf-8"))
        if not isinstance(receipt,dict) or receipt.get("schema_version")!=1: raise AtlasError("Unknown project archive schema")
        expected=manifest_index(receipt.get("files"))
        if "state.sqlite3" not in expected: raise AtlasError("Project archive lacks state database")
        if names!={"MANIFEST.json"}|{"PROJECT/"+name for name in expected}:
            raise AtlasError("Backup manifest and contents differ")
        target.parent.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=".atlas-restore-",dir=target.parent) as temp:
            stage=Path(temp)/"project"; stage.mkdir()
            for name,row in expected.items():
                info=source.getinfo("PROJECT/"+name)
                if info.file_size!=row["size"]: raise AtlasError("Backup size mismatch")
                data=source.read(info)
                if len(data)!=row["size"] or hashlib.sha256(data).hexdigest()!=row["sha256"]:
                    raise AtlasError("Backup hash mismatch")
                path=stage/name; path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(data)
            if target.exists() or target.is_symlink(): raise AtlasError("Restore destination appeared during verification")
            os.rename(stage,target)
    return {"restored_path":str(target),"files":len(expected),
            "warning":"Verified byte-for-byte copy, not authenticated source truth. Revalidate project state and external access before continuing."}
