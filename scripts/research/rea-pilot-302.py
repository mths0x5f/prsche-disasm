"""Isolated read-only REA CLI pilot; every command gets an immutable receipt."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import time

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'local/tools/rea-pilot-302'
PILOT=SOURCE/'.pilot'
OUT=ROOT/'local/experiments/v2-rea-pilot-302'
NODE=PILOT/'node/node-v26.12.0-win-x64/node.exe'
NPM=PILOT/'node/node-v26.12.0-win-x64/node_modules/npm/bin/npm-cli.js'
PACKAGE=PILOT/'package'
TARBALL=PILOT/'downloads/rea-agents-6.7.0.tgz'
TARGET=OUT/'Porsche.exe'
ORIGINAL=ROOT/'local/game/Porsche.exe'
ORIGINAL_SHA='ddd748fdbe6d2030e31f9257a4e01852749460b6b58560a6b4a8559d3799ff39'

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def relative(path):
    value=Path(path).resolve()
    return value.relative_to(ROOT).as_posix() if value.is_relative_to(ROOT) else str(value)
def save(path,value):Path(path).write_text(json.dumps(value,indent=2)+'\n',encoding='utf8',newline='\n')

def environment():
    env=os.environ.copy()
    env['PATH']=str(NODE.parent)+os.pathsep+env.get('PATH','')
    env.update(NPM_CONFIG_CACHE=str(PILOT/'npm-cache'),NPM_CONFIG_PREFIX=str(PILOT/'npm-prefix'),
               NPM_CONFIG_USERCONFIG=str(PILOT/'npmrc'),NPM_CONFIG_UPDATE_NOTIFIER='false',
               NPM_CONFIG_OFFLINE='false',
               GHIDRA_INSTALL_DIR=str(ROOT/'local/tools/ghidra_12.1.3_PUBLIC'),
               JAVA_HOME=str(ROOT/'local/tools/jdk-25.0.4.1+1'),
               REA_ANALYSIS_PROVIDER='ghidra',REA_GHIDRA_STARTUP_TIMEOUT_MS='1200000',
               REA_GHIDRA_DISABLED_ANALYZERS='WindowsResourceReference',
               TEMP=str(PILOT/'tmp'),TMP=str(PILOT/'tmp'))
    return env

def command(phase):
    cli=[str(NODE),str(PACKAGE/'scripts/rea.mjs')]
    target=str(TARGET)
    return {
        'pack':([str(NODE),str(NPM),'pack','rea-agents@6.7.0','--pack-destination',str(PILOT/'downloads')],SOURCE,300),
        'install':([str(NODE),str(NPM),'ci','--omit=dev','--ignore-scripts','--no-audit','--no-fund'],PACKAGE,900),
        'help':(cli+['--help'],PACKAGE,120),
        'doctor':(cli+['doctor','--json'],PACKAGE,120),
        'providers':(cli+['providers','--json'],PACKAGE,120),
        'function':(cli+['function',target,'0x00476170','--provider','ghidra','--json'],PACKAGE,1500),
        'xrefs':(cli+['xrefs',target,'0x00476170','--provider','ghidra','--json'],PACKAGE,1500),
        'instructions':(cli+['instructions',target,'0x00476170','--provider','ghidra','--json'],PACKAGE,1500),
    }[phase]

def extract():
    if PACKAGE.exists():raise FileExistsError('Package directory already exists')
    if not TARBALL.exists():raise FileNotFoundError(TARBALL)
    PACKAGE.mkdir(parents=True)
    with tarfile.open(TARBALL,'r:gz') as archive:
        for member in archive.getmembers():
            parts=Path(member.name).parts
            if not parts or parts[0]!='package' or '..' in parts or member.issym() or member.islnk():
                raise ValueError('Unsafe npm tarball member')
            target=PILOT.joinpath(*parts).resolve()
            if not target.is_relative_to(PACKAGE.resolve()):raise ValueError('Tarball escapes package directory')
            if member.isdir():target.mkdir(parents=True,exist_ok=True)
            elif member.isfile():
                target.parent.mkdir(parents=True,exist_ok=True)
                with archive.extractfile(member) as src,target.open('xb') as dst:shutil.copyfileobj(src,dst)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--phase',choices=('pack','extract','verify-package','copy-target','install','help','doctor','providers','function','xrefs','instructions'),required=True)
    parser.add_argument('--attempt',required=True);args=parser.parse_args()
    if not args.attempt.isdigit() or len(args.attempt)!=3:raise ValueError('Three-digit attempt required')
    attempt=OUT/(args.phase+'-'+args.attempt)
    if attempt.exists():raise FileExistsError('Immutable attempt already exists')
    attempt.mkdir(parents=True)
    (PILOT/'tmp').mkdir(parents=True,exist_ok=True)
    (PILOT/'npmrc').touch(exist_ok=True)
    start=time.perf_counter()
    if args.phase=='extract':
        spec=dict(operation='tarfile extract matching published package',tarball=relative(TARBALL),source_tarball_sha256=digest(TARBALL))
        try:extract();code=0;message='extracted'
        except Exception as exc:code=1;message=type(exc).__name__+': '+str(exc)
        output=(message+'\n').encode()
    elif args.phase=='verify-package':
        spec=dict(operation='compare extracted package with every tarball file',tarball=relative(TARBALL))
        try:
            with tarfile.open(TARBALL,'r:gz') as archive:
                members=[item for item in archive.getmembers() if item.isfile()]
                for item in members:
                    actual=PILOT.joinpath(*Path(item.name).parts)
                    if not actual.is_file() or hashlib.sha256(actual.read_bytes()).digest()!=hashlib.sha256(archive.extractfile(item).read()).digest():
                        raise ValueError('Package extraction differs: '+item.name)
            package=json.loads((PACKAGE/'package.json').read_bytes())
            if package['name']!='rea-agents' or package['version']!='6.7.0':raise ValueError('Package identity drift')
            if not (PACKAGE/'native/windows/build/rea-windows-x64.node').is_file():raise ValueError('Matching native addon absent')
            code=0;output=('verified '+str(len(members))+' files\n').encode()
        except Exception as exc:code=1;output=(type(exc).__name__+': '+str(exc)+'\n').encode()
    elif args.phase=='copy-target':
        spec=dict(operation='copy original into isolated experiment',source=relative(ORIGINAL))
        try:
            if TARGET.exists():raise FileExistsError('Target copy already exists')
            if digest(ORIGINAL)!=ORIGINAL_SHA:raise ValueError('Original target SHA drift')
            shutil.copyfile(ORIGINAL,TARGET)
            if digest(TARGET)!=ORIGINAL_SHA:raise ValueError('Copied target SHA mismatch')
            code=0;output=b'copied original SHA-verified target\n'
        except Exception as exc:code=1;output=(type(exc).__name__+': '+str(exc)+'\n').encode()
    else:
        if args.phase=='install':
            source_lock=SOURCE/'package-lock.json'
            package_lock=PACKAGE/'package-lock.json'
            source_data=json.loads(source_lock.read_bytes())
            package_data=json.loads((PACKAGE/'package.json').read_bytes())
            if source_data['packages']['']['version']!=package_data['version'] or source_data['packages']['']['dependencies']!=package_data['dependencies']:
                raise ValueError('Source lock does not match published package')
            if package_lock.exists():
                if digest(package_lock)!=digest(source_lock):raise ValueError('Existing package lock drift')
            else:shutil.copyfile(source_lock,package_lock)
        argv,cwd,timeout=command(args.phase)
        spec=dict(command=argv,cwd=relative(cwd),timeout_seconds=timeout,
                  package_lock_sha256=digest(PACKAGE/'package-lock.json') if args.phase=='install' else None)
        try:
            proc=subprocess.run(argv,cwd=cwd,env=environment(),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=timeout)
            code=proc.returncode;output=proc.stdout
        except Exception as exc:
            code=999;output=(type(exc).__name__+': '+str(exc)+'\n').encode()
    log=attempt/'output.log';log.write_bytes(output)
    receipt=dict(schema=1,phase=args.phase,attempt=args.attempt,**spec,
                 exit_code=code,seconds=time.perf_counter()-start,log=relative(log),log_sha256=digest(log),
                 source_commit=subprocess.check_output(['git','-C',str(SOURCE),'rev-parse','HEAD'],text=True).strip(),
                 node_sha256=digest(NODE) if NODE.exists() else None,
                 tarball_sha256=digest(TARBALL) if TARBALL.exists() else None,
                 target_sha256=digest(TARGET) if TARGET.exists() else None)
    save(attempt/'receipt.json',receipt)
    print(json.dumps(dict(phase=args.phase,attempt=args.attempt,exit_code=code,seconds=round(receipt['seconds'],3),
                          output_preview=output[:800].decode(errors='replace'))))
    if code:raise SystemExit(code if 0<code<256 else 1)

if __name__=='__main__':main()
