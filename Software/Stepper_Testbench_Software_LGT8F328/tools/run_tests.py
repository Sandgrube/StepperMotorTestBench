#!/usr/bin/env python3
"""Compile and exercise the same portable C++ core used on the Uno."""
from pathlib import Path
import os,subprocess,tempfile
root=Path(__file__).resolve().parents[1]
sketch=root/'Stepper_Testbench_LGT8F328'
with tempfile.TemporaryDirectory(prefix='stepper-tests-') as tmp:
    exe=Path(tmp)/'test_core'
    cmd=[os.environ.get('CXX','g++'),'-std=c++11','-O2','-Wall','-Wextra','-Werror','-pedantic',
         '-fsanitize=address,undefined','-fno-omit-frame-pointer','-I'+str(sketch),
         str(root/'tests/test_core.cpp'),str(sketch/'Core.cpp'),str(sketch/'Control.cpp'),str(sketch/'Ui.cpp'),'-o',str(exe)]
    subprocess.run(cmd,check=True)
    subprocess.run([str(exe)],check=True)

