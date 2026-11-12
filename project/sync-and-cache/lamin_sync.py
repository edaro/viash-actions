# /// script
# requires-python = ">=3.10"
# dependencies = ["lamindb==2.12.2"]
# ///
"""Resolve and sync LaminDB test resources for `project/sync-and-cache`.

Test resources are specified in the `info.test_resources` of a Viash project
config (`_viash.yaml`):

    info:
      test_resources:
        - path: lamin://<owner>/<instance>/collection/<uid>
          dest: resources_test
          strip_prefix: resources_test/  # optional, collections only
        - path: lamin://<owner>/<instance>/artifact/<uid>
          dest: resources_test/common/pancreas/dataset.anndata.zarr

A 20-character uid pins an exact version, a 16-character stem uid resolves to
the latest version.

Usage:

    # resolve uids and hashes, write a manifest
    uv run --script lamin_sync.py resolve --resources test_resources.json --manifest manifest.json

    # download whatever is missing or out of date, remove stray files
    uv run --script lamin_sync.py sync --manifest manifest.json [--cache-hit]

`test_resources.json` is `info.test_resources` as a JSON list, with `type`
filled in. Paths are relative to the working directory.

Public instances are read anonymously. For private instances, set the
`LAMIN_API_KEY` environment variable.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path, PurePosixPath

URI_PATTERN = re.compile(
    r"^lamin://(?P<owner>[^/]+)/(?P<name>[^/]+)/(?P<registry>artifact|collection)/(?P<uid>[A-Za-z0-9]+)/?$"
)
UID_LENGTH = 20
STEM_UID_LENGTH = 16


class LaminSyncError(Exception):
    pass


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def setup_environment() -> None:
    """Must be called before importing lamindb."""
    # GitHub Actions passes an empty string for secrets that are not set
    if os.environ.get("LAMIN_API_KEY", None) == "":
        del os.environ["LAMIN_API_KEY"]
    # never move files out of the user's own lamindb cache
    if not os.environ.get("LAMIN_CACHE_DIR"):
        os.environ["LAMIN_CACHE_DIR"] = tempfile.mkdtemp(prefix="lamin_sync_cache_")


# --- helpers for paths ------------------------------------------------------


def is_within(path: PurePosixPath, parent: PurePosixPath) -> bool:
    """Whether `path` is `parent` or lies inside it."""
    return path == parent or parent in path.parents


def normalise_dest(dest: str) -> PurePosixPath:
    path = PurePosixPath(os.path.normpath(dest))
    if str(path) in ("", ".") or path.is_absolute() or ".." in path.parts:
        raise LaminSyncError(f"Invalid dest '{dest}': must be a relative path inside the project.")
    return path


def member_target(key: str | None, uid: str, strip_prefix: str, dest: PurePosixPath) -> PurePosixPath:
    """Destination of a collection member, validated to stay inside `dest`."""
    if key is None:
        raise LaminSyncError(f"Collection member '{uid}' has no key, so it cannot be placed in '{dest}'.")
    if not key.startswith(strip_prefix):
        raise LaminSyncError(f"Key '{key}' of collection member '{uid}' does not start with strip_prefix '{strip_prefix}'.")
    relative = PurePosixPath(key[len(strip_prefix):])
    if (
        str(relative) in ("", ".")
        or relative.is_absolute()
        or any(part in ("", ".", "..") for part in relative.parts)
    ):
        raise LaminSyncError(f"Key '{key}' of collection member '{uid}' does not result in a valid relative path.")
    return dest / relative


def check_no_overlap(targets: dict[PurePosixPath, str], what: str) -> None:
    """Fail if two targets are equal or one contains the other."""
    ordered = sorted(targets)
    for i, a in enumerate(ordered):
        for b in ordered[i + 1:]:
            if is_within(b, a):
                raise LaminSyncError(f"{what}: '{targets[a]}' and '{targets[b]}' map to overlapping paths '{a}' and '{b}'.")


# --- resolve ----------------------------------------------------------------


def get_record(registry, uid: str, uri: str):
    if len(uid) == UID_LENGTH:
        records = list(registry.filter(uid=uid))
    elif len(uid) == STEM_UID_LENGTH:
        records = list(registry.filter(uid__startswith=uid, is_latest=True))
    else:
        raise LaminSyncError(f"Invalid uid in '{uri}': expected {UID_LENGTH} characters (exact version) or {STEM_UID_LENGTH} characters (latest version).")
    if len(records) != 1:
        raise LaminSyncError(f"Expected one record for '{uri}', found {len(records)}.")
    return records[0]


def artifact_item(artifact, target: PurePosixPath) -> dict:
    return {
        "uid": artifact.uid,
        "hash": artifact.hash,
        "size": artifact.size,
        "n_files": artifact.n_files,
        "is_dir": artifact.n_files is not None,
        "key": artifact.key,
        "target": str(target),
    }


def resolve(resources: list[dict]) -> dict:
    import lamindb as ln

    lamin_resources = [(i, r) for i, r in enumerate(resources) if r.get("type") == "lamin"]
    all_dests = {i: normalise_dest(r["dest"]) for i, r in enumerate(resources)}

    dbs = {}
    out = []
    for index, resource in lamin_resources:
        uri = resource["path"]
        match = URI_PATTERN.match(uri)
        if not match:
            raise LaminSyncError(f"Invalid Lamin URI '{uri}'. Expected 'lamin://<owner>/<instance>/artifact/<uid>' or 'lamin://<owner>/<instance>/collection/<uid>'.")
        instance = f"{match['owner']}/{match['name']}"
        kind = match["registry"]
        dest = all_dests[index]
        strip_prefix = resource.get("strip_prefix") or ""
        if strip_prefix and kind != "collection":
            raise LaminSyncError(f"'strip_prefix' is only supported for collections, not for '{uri}'.")

        # resources nested inside a Lamin dest must be collection members' neighbours,
        # and a Lamin dest must not be inside an s3/gs dest, which syncs with --delete
        for other_index, other_dest in all_dests.items():
            if other_index == index:
                continue
            other = resources[other_index]
            if is_within(other_dest, dest) and kind == "artifact":
                raise LaminSyncError(f"The dest of '{other['path']}' lies inside the dest of artifact '{uri}'.")
            if is_within(dest, other_dest) and other.get("type") != "lamin":
                raise LaminSyncError(f"The dest of '{uri}' lies inside the dest of '{other['path']}', which would delete it on every sync.")

        if instance not in dbs:
            log(f"Connecting to instance '{instance}'")
            dbs[instance] = ln.DB(instance)
        db = dbs[instance]

        if kind == "artifact":
            artifact = get_record(db.Artifact, match["uid"], uri)
            log(f"Resolved '{uri}' to artifact '{artifact.uid}'")
            record = artifact
            items = [artifact_item(artifact, dest)]
        else:
            collection = get_record(db.Collection, match["uid"], uri)
            members = list(collection.ordered_artifacts.all())
            log(f"Resolved '{uri}' to collection '{collection.uid}' with {len(members)} artifacts")
            record = collection
            items = [
                artifact_item(member, member_target(member.key, member.uid, strip_prefix, dest))
                for member in members
            ]
            targets = {PurePosixPath(item["target"]): item["uid"] for item in items}
            check_no_overlap(targets, f"Collection '{uri}'")
            for other_index, other_dest in all_dests.items():
                if other_index == index:
                    continue
                for target, uid in targets.items():
                    if is_within(target, other_dest) or is_within(other_dest, target):
                        raise LaminSyncError(f"Collection member '{uid}' of '{uri}' overlaps with the dest of '{resources[other_index]['path']}'.")

        # the cache key changes exactly when the resolved content changes
        key_lines = [f"{kind}\t{uri}\t{record.uid}\t{record.hash}"]
        if kind == "collection":
            key_lines += [f"member\t{item['target']}\t{item['uid']}\t{item['hash']}" for item in items]

        out.append({
            "index": index,
            "path": uri,
            "dest": str(dest),
            "instance": instance,
            "kind": kind,
            "uid": record.uid,
            "hash": record.hash,
            "strip_prefix": strip_prefix,
            "protected": [
                str(other_dest)
                for other_index, other_dest in all_dests.items()
                if other_index != index and is_within(other_dest, dest)
            ],
            "items": items,
            "key_lines": sorted(key_lines),
        })
    return {"resources": out}


# --- sync -------------------------------------------------------------------


def remove(path: Path) -> None:
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    elif path.exists() or path.is_symlink():
        path.unlink()


def is_up_to_date(path: Path, item: dict) -> bool:
    """Compare local content with the artifact's hash."""
    from lamindb_setup.core.hashing import hash_dir, hash_file

    if item["hash"] is None:
        return False
    if item["is_dir"]:
        if not path.is_dir() or path.is_symlink():
            return False
        files = [p for p in path.rglob("*") if p.is_file()]
        if len(files) != item["n_files"] or sum(p.stat().st_size for p in files) != item["size"]:
            return False
        _, local_hash, _, _ = hash_dir(path)
    else:
        if not path.is_file() or path.is_symlink() or path.stat().st_size != item["size"]:
            return False
        _, local_hash, _ = hash_file(path)
    return local_hash == item["hash"]


def download(db, item: dict, target: Path) -> None:
    artifact = db.Artifact.get(item["uid"])
    cached = Path(artifact.cache(mute=True))
    remove(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    # move rather than copy, so files are not stored twice
    shutil.move(str(cached), str(target))


def clean_up(dest: Path, keep: list[Path]) -> None:
    """Remove files under `dest` that are not in or under one of the `keep` paths."""
    if not dest.is_dir():
        return

    def keep_path(path: Path) -> bool:
        return any(path == k or k in path.parents for k in keep)

    def needed_dir(path: Path) -> bool:
        return any(path in k.parents for k in keep)

    for path in sorted(dest.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if keep_path(path):
            continue
        if path.is_dir() and not path.is_symlink():
            if not needed_dir(path) and not any(path.iterdir()):
                log(f"Removing empty directory '{path}'")
                path.rmdir()
        else:
            log(f"Removing '{path}'")
            path.unlink()


def sync(manifest: dict, cache_hit: bool) -> None:
    import lamindb as ln

    dbs = {}
    for resource in manifest["resources"]:
        log(f"Syncing '{resource['path']}' to '{resource['dest']}'")
        for item in resource["items"]:
            target = Path(item["target"])
            label = f"'{item['key'] or item['uid']}' -> '{target}'"
            # on an exact cache hit, the cache key guarantees the content
            if cache_hit and target.exists():
                log(f"  {label}: restored from cache")
                continue
            if not cache_hit and is_up_to_date(target, item):
                log(f"  {label}: up to date")
                continue
            log(f"  {label}: downloading")
            if resource["instance"] not in dbs:
                dbs[resource["instance"]] = ln.DB(resource["instance"])
            download(dbs[resource["instance"]], item, target)

        if resource["kind"] == "collection":
            keep = [Path(item["target"]) for item in resource["items"]]
            keep += [Path(p) for p in resource["protected"]]
            clean_up(Path(resource["dest"]), keep)


# --- main -------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(dest="command", required=True)
    p_resolve = subparsers.add_parser("resolve", help="Resolve uids and hashes, write a manifest.")
    p_resolve.add_argument("--resources", required=True, type=Path, help="JSON list of test resources.")
    p_resolve.add_argument("--manifest", required=True, type=Path, help="Output manifest JSON.")
    p_sync = subparsers.add_parser("sync", help="Sync the resources in a manifest.")
    p_sync.add_argument("--manifest", required=True, type=Path, help="Manifest JSON written by 'resolve'.")
    p_sync.add_argument("--cache-hit", action="store_true", help="The destinations were restored from an exact cache hit.")
    args = parser.parse_args()

    setup_environment()
    try:
        if args.command == "resolve":
            resources = json.loads(args.resources.read_text())
            manifest = resolve(resources)
            args.manifest.write_text(json.dumps(manifest, indent=2))
        else:
            manifest = json.loads(args.manifest.read_text())
            sync(manifest, cache_hit=args.cache_hit)
    except LaminSyncError as e:
        log(f"Error: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
