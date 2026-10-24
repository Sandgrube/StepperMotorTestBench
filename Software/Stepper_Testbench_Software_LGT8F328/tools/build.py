#!/usr/bin/env python3
"""Build a named LGT8F328 board/clock profile with a normal arduino-cli installation."""
from pathlib import Path
import argparse,subprocess,shutil,json
root=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser()
ap.add_argument('--cli',default='arduino-cli')
ap.add_argument('--config-file')
ap.add_argument('--single-file',action='store_true')
profiles=json.loads((root/'board_profiles.json').read_text())
ap.add_argument('--profile',choices=profiles,default='p16')
args=ap.parse_args()
cmd=[args.cli]
if args.config_file:cmd+=['--config-file',str(Path(args.config_file).resolve())]
sketch=root/('single_file/Stepper_Testbench_LGT8F328' if args.single_file else 'Stepper_Testbench_LGT8F328')
destination=root/'build'/args.profile/('single_file' if args.single_file else 'modular')
subprocess.run(cmd+['compile','--fqbn',profiles[args.profile]['fqbn'],'--warnings','all','--build-path',str(destination),str(sketch)],check=True)
release=root/'firmware'/args.profile;release.mkdir(parents=True,exist_ok=True)
if not args.single_file:
    for ext in ('.hex','.elf'):
        shutil.copy2(destination/('Stepper_Testbench_LGT8F328.ino'+ext),release/('Stepper_Testbench_LGT8F328'+ext))

