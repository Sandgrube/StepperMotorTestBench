#!/usr/bin/env python3
"""Produce the independently compilable one-file distribution from modular sources."""
from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]
source=root/'Stepper_Testbench_LGT8F328'
order=['Config.h','Core.h','Control.h','Ui.h','App.h','Core.cpp','Control.cpp','Ui.cpp','App.cpp','Stepper_Testbench_LGT8F328.ino']
out=['/* Stepper Testbench 2.1.0 — generated single-file edition.\n'
     '   LGT8F328P/D at 16/32 MHz; lgt8fx 2.0.7 + hd44780 1.3.2.\n'
     '   Edit electrical options in the Config.h section below.\n'
     '   Modular editable sources, tests and wiring manual are in the complete ZIP.\n'
     '   Regenerate this file: python tools/make_single_file.py\n*/\n#include <Arduino.h>\n']
for name in order:
    text=(source/name).read_text()
    text=re.sub(r'^#pragma once\s*\n','',text,flags=re.M)
    text=re.sub(r'^#include "[^"\n]+"\s*\n','',text,flags=re.M)
    out.append('\n// ===== '+name+' =====\n'+text)
dest=root/'single_file/Stepper_Testbench_LGT8F328/Stepper_Testbench_LGT8F328.ino'
dest.parent.mkdir(parents=True,exist_ok=True)
dest.write_text(''.join(out))
print(dest)

