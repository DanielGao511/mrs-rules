"""One normal Git commit publishes the complete verified set, without force pushes."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]

def main():
    repo=os.environ['GITHUB_REPOSITORY']
    with tempfile.TemporaryDirectory() as td:
        def git(*args,check=True):
            return subprocess.run(['git','-C',td,*args],check=check,capture_output=True,text=True)
        git('init','--quiet')
        git('remote','add','origin','https://github.com/'+repo+'.git')
        exists=git('ls-remote','--exit-code','--heads','origin','release',check=False)
        if exists.returncode==0:
            git('fetch','--depth=1','origin','release');git('checkout','-B','release','FETCH_HEAD')
        elif exists.returncode==2:git('checkout','--orphan','release')
        else:raise RuntimeError('Cannot inspect release branch: '+exists.stderr)
        for file in (ROOT/'dist').iterdir():
            if file.name not in {'README.md','LICENSE','manifest.json','SHA256SUMS'} and file.suffix!='.mrs':raise ValueError('Unexpected publication file')
            shutil.copyfile(file,Path(td)/file.name)
        git('add','--all')
        if git('diff','--cached','--quiet',check=False).returncode==0:
            print('Rules unchanged; no commit needed.');return
        git('config','user.name','github-actions[bot]')
        git('config','user.email','41898282+github-actions[bot]@users.noreply.github.com')
        git('commit','-m','Update verified MRS rules')
        git('push','origin','HEAD:release')
        print('Published verified MRS batch:',git('rev-parse','HEAD').stdout.strip())

if __name__=='__main__':main()
