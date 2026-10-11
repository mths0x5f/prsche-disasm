"""Read each proof dependency once per audit, rejecting concurrent changes."""
import hashlib
import json
from pathlib import Path


class ProofCache:
    def __init__(self):
        self._files = {}
        self._json = {}
        self._digests = {}

    @staticmethod
    def _stamp(path):
        stat = path.stat()
        return stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns

    def _read(self, path):
        path = Path(path).resolve()
        if path not in self._files:
            before = self._stamp(path)
            data = path.read_bytes()
            if self._stamp(path) != before:
                raise RuntimeError(f'Dependency changed during audit: {path}')
            self._files[path] = before, data
        elif self._stamp(path) != self._files[path][0]:
            raise RuntimeError(f'Dependency changed during audit: {path}')
        return path, self._files[path][1]

    def digest(self, path):
        path, data = self._read(path)
        if path not in self._digests:
            self._digests[path] = hashlib.sha256(data.replace(b'\r\n', b'\n')).hexdigest()
        return self._digests[path]

    def document(self, path):
        path, data = self._read(path)
        if path not in self._json:
            self._json[path] = json.loads(data.decode('utf-8-sig'))
        return self._json[path]

    def check_stable(self):
        for path, (stamp, _) in self._files.items():
            if self._stamp(path) != stamp:
                raise RuntimeError(f'Dependency changed during audit: {path}')

    @property
    def counts(self):
        return {'unique_files': len(self._files), 'unique_sha256': len(self._digests),
                'unique_json': len(self._json)}
