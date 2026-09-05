"""Compile original public rule lists; publish only a fully verified batch."""
import gzip
import hashlib
import ipaddress
import json
from pathlib import Path
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import yaml

ROOT = Path(__file__).resolve().parents[1]
VERSION = 'v1.19.30'
ARCHIVE_SHA256 = 'db214c7a2517e63c150d123178d16d102e03a241ccdae4e5e07ffbe9cf56c6f9'
BINARY_URL = f'https://github.com/MetaCubeX/mihomo/releases/download/{VERSION}/mihomo-linux-amd64-compatible-{VERSION}.gz'

def download(url):
    with requests.Session() as session:
        retry=Retry(total=3,backoff_factor=2,status_forcelist=[429,500,502,503,504])
        session.mount('https://',HTTPAdapter(max_retries=retry))
        response=session.get(url,timeout=(15,90))
        response.raise_for_status()
        return response.content

def covered(value, entries):
    if value in entries:return True
    name=value[2:] if value.startswith('+.') else value
    parts=name.split('.')
    return any('+.'+'.'.join(parts[i:]) in entries for i in range(len(parts)))

def verify(original, decoded, behavior):
    if behavior=='domain':
        original={v.lower() for v in original};decoded={v.lower() for v in decoded}
        if any(not covered(v,decoded) for v in original) or any(not covered(v,original) for v in decoded):
            raise ValueError('Domain coverage changed')
    elif behavior=='ipcidr':
        def canon(values):
            networks=[ipaddress.ip_network(v) for v in values]
            return {str(n) for version in (4,6) for n in ipaddress.collapse_addresses(n for n in networks if n.version==version)}
        if canon(original)!=canon(decoded):raise ValueError('IP coverage changed')
    else:raise ValueError('Unsupported behavior')

def main():
    work=ROOT/'.work';work.mkdir(exist_ok=True)
    binary=work/'mihomo'
    archive=download(BINARY_URL)
    if hashlib.sha256(archive).hexdigest()!=ARCHIVE_SHA256:raise ValueError('Converter checksum mismatch')
    binary.write_bytes(gzip.decompress(archive));binary.chmod(0o755)
    subprocess.run([str(binary),'-v'],check=True)
    sources=json.loads((ROOT/'sources.json').read_text())
    def convert(item):
        name,provider=item
        if not name or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-' for c in name):raise ValueError('Invalid name')
        raw=download(provider['url']);payload=yaml.safe_load(raw)['payload']
        if not isinstance(payload,list) or not payload:raise ValueError('Empty source')
        src=work/(name+'.yaml');mrs=work/(name+'.mrs');decoded=work/(name+'.decoded.txt')
        src.write_bytes(raw)
        for fmt,input_path,output_path in [('yaml',src,mrs),('mrs',mrs,decoded)]:
            result=subprocess.run([str(binary),'convert-ruleset',provider['behavior'],fmt,str(input_path),str(output_path)],capture_output=True,text=True,timeout=120)
            if result.returncode:raise RuntimeError(name+' conversion failed: '+result.stderr)
        verify(payload,decoded.read_text().splitlines(),provider['behavior'])
        body=mrs.read_bytes()
        if not body:raise ValueError('Empty MRS')
        print(name,len(payload),len(raw),'->',len(body),'coverage verified',flush=True)
        return name,{'behavior':provider['behavior'],'source_url':provider['url'],'source_sha256':hashlib.sha256(raw).hexdigest(),'source_rules':len(payload),'source_bytes':len(raw),'mrs_bytes':len(body),'sha256':hashlib.sha256(body).hexdigest()}
    with ThreadPoolExecutor(max_workers=4) as pool:
        providers=dict(pool.map(convert,sources.items()))
    dist=ROOT/'dist';dist.mkdir(exist_ok=True)
    for name in providers:shutil.copyfile(work/(name+'.mrs'),dist/(name+'.mrs'))
    # Stable metadata: no timestamp-only commits. Git commit date records publication.
    manifest={'converter':{'version':VERSION,'archive_sha256':ARCHIVE_SHA256},'providers':providers}
    (dist/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
    (dist/'SHA256SUMS').write_text(''.join(f"{providers[n]['sha256']}  {n}.mrs\n" for n in sorted(providers)))
    for name in ['README.md','LICENSE']:shutil.copyfile(ROOT/name,dist/name)

if __name__=='__main__':main()
