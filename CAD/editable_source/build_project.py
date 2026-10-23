#!/usr/bin/env python3
"""Rebuild CAD, validation, preview images and the offline manual in sequence."""
import argparse,subprocess,sys
from pathlib import Path

def main():
    here=Path(__file__).resolve().parent;root=here.parents[1]
    ap=argparse.ArgumentParser();ap.add_argument('--params',type=Path,default=root/'CAD/parameters/default.json')
    args=ap.parse_args()
    for script in ('generate.py','render_previews.py','make_documents.py'):
        subprocess.run([sys.executable,str(here/script),'--params',str(args.params.resolve()),'--output',str(root)],check=True)
    print('Project regenerated; see DOCUMENTATION/assembly_guide.html')

if __name__=='__main__':main()
