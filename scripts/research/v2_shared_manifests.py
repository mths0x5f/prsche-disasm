"""Immutable shared pin sets, with legacy readers and per-run deltas."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import re

from v2_proof_cache import ProofCache

DIRECTORY = 'research/v2/proof-manifests/sha256'
MODES = {'raw', 'crlf-to-lf'}


def _sha(value):
    if not isinstance(value, str) or not re.fullmatch(r'[0-9a-f]{64}', value):
        raise ValueError('Expected a lowercase SHA256')
    return value


def _relative(value):
    if not isinstance(value, str) or not value or '\\' in value or ':' in value:
        raise ValueError('Manifest paths must be canonical repository-relative paths')
    p = PurePosixPath(value)
    if p.is_absolute() or '..' in p.parts or p.as_posix() != value or value == '.':
        raise ValueError('Invalid repository-relative path')
    return value


def _pins(value, strict):
    if not isinstance(value, dict):
        raise ValueError('Pins must be an object')
    result = {}
    for path, digest in value.items():
        if not isinstance(path, str) or not path:
            raise ValueError('Pin path is empty')
        if strict:
            _relative(path)
        result[path] = _sha(digest)
    return result


def _scope(value):
    if value not in ('input', 'source'):
        raise ValueError('Expected input or source scope')
    return value


def _mode(value):
    if not isinstance(value, str) or value not in MODES:
        raise ValueError('Unknown hash mode')
    return value


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key')
        result[key] = value
    return result


def write_manifest(root, pins, hash_mode):
    """Create once; the filename is the hash of the exact UTF-8/LF bytes."""
    document = dict(schema=1, kind='recovery-pin-manifest', hash_mode=_mode(hash_mode),
                    files=_pins(pins, strict=True))
    data = (json.dumps(document, sort_keys=True, ensure_ascii=False, indent=2) + '\n').encode('utf8')
    digest = hashlib.sha256(data).hexdigest()
    name = DIRECTORY + '/' + digest + '.json'
    path = (Path(root) / name).resolve()
    if not path.is_relative_to(Path(root).resolve()):
        raise ValueError('Manifest store escapes the repository')
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open('xb') as stream:
            stream.write(data)
    except FileExistsError:
        if path.read_bytes() != data:
            raise ValueError('Existing immutable manifest is corrupt')
    return dict(path=name, sha256=digest)


class ManifestReader:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.cache = ProofCache()
        self._raw = {}
        self._manifests = {}

    def _repo_path(self, name):
        path = (self.root / _relative(name)).resolve()
        if not path.is_relative_to(self.root):
            raise ValueError('Manifest reference escapes the repository')
        return path

    def _digest(self, path, mode):
        data = self.cache.data(path)  # Checks the mutation stamp even on reuse.
        if mode == 'crlf-to-lf':
            return self.cache.digest(path)
        path = Path(path).resolve()
        if path not in self._raw:
            self._raw[path] = hashlib.sha256(data).hexdigest()
        return self._raw[path]

    def manifest(self, reference):
        if not isinstance(reference, dict) or set(reference) != {'path', 'sha256'}:
            raise ValueError('Invalid manifest reference')
        expected = _sha(reference['sha256'])
        path = self._repo_path(reference['path'])
        if PurePosixPath(reference['path']).parent.as_posix() != DIRECTORY or path.name != expected + '.json':
            raise ValueError('Manifest reference must name its content hash')
        if self._digest(path, 'raw') != expected:
            raise ValueError('Manifest content SHA mismatch')
        if path not in self._manifests:
            value = json.loads(self.cache.data(path).decode('utf8'), object_pairs_hook=_unique)
            if not isinstance(value, dict) or set(value) != {'schema', 'kind', 'hash_mode', 'files'} or type(value['schema']) is not int or value['schema'] != 1 or value['kind'] != 'recovery-pin-manifest':
                raise ValueError('Unsupported manifest schema')
            self._manifests[path] = _mode(value['hash_mode']), _pins(value['files'], strict=True)
        mode, pins = self._manifests[path]
        return mode, dict(pins)

    def resolve(self, document, scope='input', legacy_hash_mode='raw', expected_hash_mode=None):
        scope = _scope(scope)
        inline, reference, delta, removed = (scope + x for x in ('_sha256', '_manifest', '_delta', '_removed'))
        if reference not in document:
            if delta in document or removed in document:
                raise ValueError('Delta without a base manifest')
            mode, pins = _mode(legacy_hash_mode), _pins(document[inline], strict=False)
        else:
            if inline in document:
                raise ValueError('Ambiguous inline and manifest pin sets')
            mode, pins = self.manifest(document[reference])
            deletes = document.get(removed, [])
            if not isinstance(deletes, list):
                raise ValueError('Invalid removed-path list')
            for path in deletes:
                _relative(path)
            if len(set(deletes)) != len(deletes):
                raise ValueError('Duplicate removal')
            updates = _pins(document.get(delta, {}), strict=True)
            for path in deletes:
                _relative(path)
                if path not in pins or path in updates:
                    raise ValueError('Missing or contradictory removal')
                del pins[path]
            pins.update(updates)
        if expected_hash_mode is not None and mode != _mode(expected_hash_mode):
            raise ValueError('Hash mode mismatch')
        return mode, pins

    def verify(self, document, scope='input', legacy_hash_mode='raw', expected_hash_mode=None):
        mode, pins = self.resolve(document, scope, legacy_hash_mode, expected_hash_mode)
        for name, expected in pins.items():
            p = Path(name)
            path = p if p.is_absolute() else self.root / p
            if self._digest(path, mode) != expected:
                raise ValueError('Input SHA mismatch: ' + name)
        self.cache.check_stable()
        return mode, pins

    @property
    def counts(self):
        return dict(**self.cache.counts, manifest_documents=len(self._manifests), raw_sha256=len(self._raw))


def externalize(root, document, scope='input', hash_mode='raw', base_reference=None):
    """Make a new document; never mutate an existing proof or its base manifest."""
    scope = _scope(scope)
    inline = scope + '_sha256'
    if any(scope + key in document for key in ('_manifest', '_delta', '_removed')):
        raise ValueError('Document already contains manifest metadata')
    current = _pins(document[inline], strict=True)
    if base_reference is None:
        base_reference = write_manifest(root, current, hash_mode)
        base = current
    else:
        mode, base = ManifestReader(root).manifest(base_reference)
        if mode != _mode(hash_mode):
            raise ValueError('Base hash mode mismatch')
    result = {key: value for key, value in document.items() if key != inline}
    result[scope + '_manifest'] = dict(base_reference)
    delta = {key: value for key, value in current.items() if base.get(key) != value}
    removed = sorted(set(base) - set(current))
    if delta:
        result[scope + '_delta'] = delta
    if removed:
        result[scope + '_removed'] = removed
    return result
