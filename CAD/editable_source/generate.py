#!/usr/bin/env python3
"""Regenerate all B-rep CAD, print-oriented STL, and validation results.

Usage: python generate.py [--params ../parameters/default.json] [--output ../..]
The default output is the project root, independent of the current directory.
"""
import argparse,json,sys,time
from pathlib import Path
import cadquery as cq
from enclosure.common import compound,print_orientation,geometry,normalize_parameters
from enclosure.housing import make_chassis,make_cover,make_front_panel,make_tb_clamp,make_carrier_clip,make_tests,make_foot,make_joystick_spacer
from enclosure.components import all_components
from enclosure.fasteners import fasteners

def build(p):
    jobs=[('main_chassis',make_chassis),('front_panel',make_front_panel),('top_cover',make_cover),
          ('tb_clamp_left',lambda p:make_tb_clamp(p,False)),('tb_clamp_right',lambda p:make_tb_clamp(p,True)),
          ('a4988_edge_clip_1',lambda p:make_carrier_clip(p,0)),('a4988_edge_clip_2',lambda p:make_carrier_clip(p,1))]
    jobs.extend((f'joystick_spacer_{i+1}',lambda p,i=i:make_joystick_spacer(p,i)) for i in range(4))
    out={}
    for name,fn in jobs:
        t=time.time();s=fn(p)
        if not s.isValid():raise RuntimeError('Invalid B-rep: '+name)
        if len(s.Solids())!=1:raise RuntimeError(f'{name}: expected 1 solid, got {len(s.Solids())}')
        out[name]=s;print(f'{name}: {s.Volume()/1000:.2f} cm3, {time.time()-t:.1f}s',flush=True)
    return out

def export(p,parts,components,root):
    for folder in ('CAD/printed_parts','CAD/component_models','PRINT/optional_parts','PRINT/tolerance_tests','PREVIEWS','DOCUMENTATION'):(root/folder).mkdir(parents=True,exist_ok=True)
    assembly=cq.Assembly(name='Stepper_Testbench_Enclosure_R1')
    for name,s in parts.items():
        assembly.add(s,name=name,color=cq.Color(.22,.24,.26))
        cq.exporters.export(s,str(root/'CAD/printed_parts'/f'{name}.step'))
        ss=print_orientation(s,name,p)
        dest=root/'PRINT'/f'{name}.stl'
        cq.exporters.export(ss,str(dest),tolerance=.06,angularTolerance=.10)
    for obj in [*components,*fasteners(p)]: assembly.add(obj.shape,name=obj.name,color=cq.Color(*obj.color))
    assembly.export(str(root/'CAD/main_assembly.step'))
    cq.exporters.export(compound(parts.values()),str(root/'CAD/printed_parts_assembly.step'))
    for group in sorted(set(x.group for x in components)):
        cq.exporters.export(compound(x.shape for x in components if x.group==group),str(root/'CAD/component_models'/f'{group.lower()}_reference.step'))
    tests=make_tests(p)
    for name,s in tests.items():
        cq.exporters.export(s,str(root/'CAD/printed_parts'/f'{name}.step'))
        cq.exporters.export(s,str(root/'PRINT/tolerance_tests'/f'{name}.stl'),tolerance=.05,angularTolerance=.10)
    foot=make_foot(p)
    cq.exporters.export(foot,str(root/'PRINT/optional_parts/tpu_foot_print_4.stl'),tolerance=.05)
    return tests

def main():
    here=Path(__file__).resolve().parent
    ap=argparse.ArgumentParser();ap.add_argument('--params',type=Path,default=here.parent/'parameters/default.json');ap.add_argument('--output',type=Path,default=here.parent.parent);ap.add_argument('--skip-validation',action='store_true')
    args=ap.parse_args();root=args.output.resolve();p=normalize_parameters(json.loads(args.params.read_text()));parts=build(p);components=all_components(p)
    tests=export(p,parts,components,root)
    if not args.skip_validation:
        from enclosure.validate import validate
        report=validate(p,parts,components,tests,root)
        (root/'DOCUMENTATION/validation_results.json').write_text(json.dumps(report,indent=2))
        print('VALIDATION:',report['status'],flush=True)
        if report['failures']:sys.exit(2)
    print('CAD exports complete:',root,flush=True)

if __name__=='__main__':main()
