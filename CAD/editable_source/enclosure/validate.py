"""Repeatable geometric validation. This is not a physical fit/thermal test."""
import itertools,json,math,struct,time
from pathlib import Path
import numpy as np
import cadquery as cq
from .common import *
from .components import knob_local
from .fasteners import fasteners

EPS=0.005 # mm^3 intersection threshold, numerical contacts below this ignored

def bbox_overlap(a,b):
    a=a.BoundingBox();b=b.BoundingBox()
    return all(min(getattr(a,k+'max'),getattr(b,k+'max'))-max(getattr(a,k+'min'),getattr(b,k+'min'))>1e-6 for k in 'xyz')

def overlap(a,b):
    if not bbox_overlap(a,b):return 0.0
    return a.intersect(b).Volume()

def mesh_check(path):
    data=Path(path).read_bytes();n=struct.unpack_from('<I',data,80)[0]
    if len(data)!=84+50*n:raise ValueError('Expected binary STL: '+str(path))
    dt=np.dtype([('normal','<f4',(3,)),('v','<f4',(3,3)),('attr','<u2')])
    tris=np.frombuffer(data,dtype=dt,offset=84,count=n)['v'].astype(np.float64)
    verts,ids=np.unique(np.round(tris.reshape(-1,3),5),axis=0,return_inverse=True)
    faces=ids.reshape(-1,3)
    edges=np.concatenate((faces[:,[0,1]],faces[:,[1,2]],faces[:,[2,0]]))
    sorted_edges=np.sort(edges,axis=1)
    _,ei,ec=np.unique(sorted_edges,axis=0,return_inverse=True,return_counts=True)
    orientation=np.bincount(ei,weights=np.where(edges[:,0]<edges[:,1],1,-1))
    area=np.linalg.norm(np.cross(tris[:,1]-tris[:,0],tris[:,2]-tris[:,0]),axis=1)/2
    volume=float(np.einsum('ij,ij->i',tris[:,0],np.cross(tris[:,1],tris[:,2])).sum()/6)
    dims=verts.max(axis=0)-verts.min(axis=0)
    return {'triangles':int(n),'welded_vertices':len(verts),'boundary_edges':int(np.sum(ec==1)),
            'nonmanifold_edges':int(np.sum(ec>2)),'inconsistent_edge_winding':int(np.count_nonzero(orientation)),
            'degenerate_triangles':int(np.sum(area<1e-9)),'signed_volume_mm3':round(volume,4),
            'bounds_mm':[round(float(x),3) for x in dims],
            'watertight':bool(np.all(ec==2) and np.all(orientation==0) and np.all(area>1e-9) and volume>0)}

def validate(p,parts,components,tests,root):
    report={'revision':p['revision'],'cadquery_version':cq.__version__,'units':'mm','intersection_threshold_mm3':EPS,
            'status':'PASS for reference geometry; physical interfaces unverified', 'failures':[],
            'solids':{},'collisions':[],'minimum_clearances_mm':{},'meshes':{},'step_roundtrip':{},'access_checks':[],
            'scope_limits':['No real hardware measurements supplied. Reference envelopes and documented assumptions only.',
                            'No physical print, assembly, strength, pull, electrical, thermal or slicer test performed.',
                            'No arbitrary cable shapes or exact vendor mouldings were simulated.',
                            'Intentional component-internal envelope overlaps are excluded from cross-component checks.']}
    def fail(s):report['failures'].append(s)
    # Source B-reps, individual STL export, STEP readback.
    for name,s in parts.items():
        b=s.BoundingBox();report['solids'][name]={'valid':s.isValid(),'solid_count':len(s.Solids()),'volume_cm3':round(s.Volume()/1000,3),'assembly_bounds_mm':[round(b.xlen,3),round(b.ylen,3),round(b.zlen,3)]}
        mesh=mesh_check(root/'PRINT'/f'{name}.stl'); report['meshes'][name]=mesh
        if not mesh['watertight']:fail(name+' mesh is not watertight')
        if max(mesh['bounds_mm'])>256:fail(name+' exceeds the 256 mm build envelope')
        st=cq.importers.importStep(str(root/'CAD/printed_parts'/f'{name}.step')).val()
        rel=abs(st.Volume()-s.Volume())/s.Volume()
        report['step_roundtrip'][name]={'valid':st.isValid(),'volume_relative_error':rel,'solid_count':len(st.Solids())}
        if rel>1e-6 or not st.isValid():fail(name+' STEP round trip failed')
        # Mesh volume independently approximates the original B-rep.
        meshrel=abs(mesh['signed_volume_mm3']-s.Volume())/s.Volume()
        mesh['volume_relative_error_vs_brep']=meshrel
        if meshrel>.005:fail(name+' STL volume differs by more than 0.5%')
    for name in tests:
        mesh=mesh_check(root/'PRINT/tolerance_tests'/f'{name}.stl');report['meshes'][name]=mesh
        if not mesh['watertight']:fail(name+' tolerance mesh failed')
    foot=mesh_check(root/'PRINT/optional_parts/tpu_foot_print_4.stl');report['meshes']['optional_tpu_foot']=foot
    if not foot['watertight']:fail('Optional TPU foot mesh failed')
    # Exact OCCT boolean common volumes, broad-phase pruning only skips disjoint boxes.
    nprint=0; ncomp=0; ncross=0
    for (na,a),(nb,b) in itertools.combinations(parts.items(),2):
        nprint+=1;v=overlap(a,b)
        if v>EPS:report['collisions'].append({'a':na,'b':nb,'intersection_mm3':round(v,6)})
    for name,s in parts.items():
        for c in components:
            ncomp+=1;v=overlap(s,c.shape)
            if v>EPS:report['collisions'].append({'a':name,'b':c.name,'intersection_mm3':round(v,6)})
    for a,b in itertools.combinations(components,2):
        if a.group==b.group:continue
        ncross+=1;v=overlap(a.shape,b.shape)
        if v>EPS:report['collisions'].append({'a':a.name,'b':b.name,'intersection_mm3':round(v,6)})
    report['collision_pairs_checked']={'printed_printed':nprint,'printed_component':ncomp,'component_cross_group':ncross}
    if report['collisions']:fail(f"{len(report['collisions'])} interference(s)")
    hw=fasteners(p);hw_hits=[]
    # Nominal shafts intentionally overlap plastic pilot bores and nut threads.
    # The physical head/washer/nut envelopes must fit without such an exception.
    for h in hw:
        if h.group=='FASTENER_SHAFT':continue
        for name,s in parts.items():
            vv=overlap(h.shape,s)
            if vv>EPS:hw_hits.append({'fastener':h.name,'part':name,'volume_mm3':round(vv,5)})
        for c in components:
            vv=overlap(h.shape,c.shape)
            if vv>EPS:hw_hits.append({'fastener':h.name,'part':c.name,'volume_mm3':round(vv,5)})
    report['nominal_fasteners']={'reference_solids':len(hw),'head_nut_washer_interferences':hw_hits,'threaded_shafts_excluded_from_pilot_intersections':True}
    if hw_hits:fail('Fastener envelope interference')
    groups={g:compound(c.shape for c in components if c.group==g) for g in set(c.group for c in components)}
    for ga,gb in itertools.combinations(sorted(groups),2):
        report['minimum_clearances_mm'][ga+' to '+gb]=round(groups[ga].distance(groups[gb]),4)
    # Front control sweep: 17 azimuths, 5 angles, pressed and unpressed.
    j=p['joystick']; worst=0.0; configurations=0; min_dist=1e9
    for az in range(0,360,22):
        for deg in (0,5,10,15,j['travel_deg']):
            for press in (0,j['press_travel']):
                s=panel_transform(knob_local(p,deg,az,press),p)
                v=overlap(s,parts['front_panel']);worst=max(worst,v);configurations+=1
                if v<=EPS:min_dist=min(min_dist,s.distance(parts['front_panel']))
    report['joystick_sweep']={'configurations':configurations,'max_tilt_deg':j['travel_deg'],'press_travel_mm':j['press_travel'],
                             'worst_intersection_mm3':worst,'minimum_model_gap_mm':round(min_dist,4)}
    if worst>EPS:fail('Joystick sweep intersects panel')
    # Simulate a vertical lid lift. Controls and drivers remain installed.
    paths=[]
    obstacles=[(n,s) for n,s in parts.items() if n!='top_cover']+[(c.name,c.shape) for c in components]
    for dz in (0.1,1,3,6,12,30,60):
        lid=parts['top_cover'].translate((0,0,dz));vv=0
        for n,s in obstacles:vv=max(vv,overlap(lid,s))
        paths.append({'lift_mm':dz,'max_intersection_mm3':round(vv,6)})
        if vv>EPS:fail('Lid removal obstructed at '+str(dz))
    report['lid_removal']=paths
    # Disconnected electronics can be removed without taking off the control panel.
    # Tools/screws and the stated retaining clips are removed before these paths.
    service={
      'UNO':([(0,0,1.1),(0,-4,1.1),(0,-8,1.1),(0,-8,6),(0,-8,35),(0,-8,80)],{'top_cover'}),
      'A4988':([(0,1,0),(0,1,1),(0,1,6),(0,1,35),(0,1,80)],{'top_cover','a4988_edge_clip_1','a4988_edge_clip_2'}),
      'TB6600':([(0,0,1),(0,0,6),(0,0,35),(0,0,80)],{'top_cover','tb_clamp_left','tb_clamp_right'})}
    service_results={}
    for group,(poses,removed) in service.items():
        result=[]
        for pose in poses:
            moving=groups[group].translate(pose);vv=0;hits=[]
            for name,s in parts.items():
                if name in removed:continue
                vol=overlap(moving,s);vv=max(vv,vol)
                if vol>EPS:hits.append(name)
            for g,s in groups.items():
                if g==group:continue
                vol=overlap(moving,s);vv=max(vv,vol)
                if vol>EPS:hits.append(g)
            result.append({'translation_mm':pose,'max_intersection_mm3':round(vv,6),'blocked_by':hits})
            if vv>EPS:fail(group+' removal path blocked at '+str(pose))
        service_results[group]=result
    report['component_removal_sampled_paths']=service_results
    # Known external plug and terminal screwdriver corridors.
    ac=p['access']; e=p['enclosure']; q=p['a4988']; t=p['tb6600']; _,H,seat=geometry(p)
    corridors=[('UNO_USB_metal_mating_envelope',box(13,18,12,46,169.5,11.3),{'UNO'}),
               ('UNO_DC_plug_12mm_envelope',cq.Solid.makeCylinder(6,25,cq.Vector(22,171,17),cq.Vector(0,1,0)),{'UNO'})]
    for i in range(6):
        corridors.append((f'A4988_terminal_tool_{i}',cylinder(1.5,65,q['terminal_x']+(i+.5)*5.08,q['terminal_y']+4,22),{'A4988'}))
    for k,tx in enumerate((t['x']+t['terminal_x_margin'],t['x']+t['terminal_x_margin']+6*t['terminal_pitch']+5)):
        for i in range(6):corridors.append((f'TB_terminal_tool_{k}_{i}',cylinder(1.5,45,tx+(i+.5)*5.08,t['y']+t['terminal_screw_y_offset'],46.1),{'TB6600'}))
    corridors.append(('A4988_pot_tool',cylinder(1.5,75,q['pot_x'],q['pot_y'],24),{'A4988'}))
    for i in range(6):
        xx=q['terminal_x']+(i+.5)*5.08
        corridors.append((f'A4988_wire_{i}',cq.Solid.makeCylinder(1.5,40,cq.Vector(xx,166,17),cq.Vector(0,1,0)),{'A4988'}))
        xx=t['x']+t['terminal_x_margin']+6*t['terminal_pitch']+5+(i+.5)*t['terminal_pitch']
        corridors.append((f'TB_power_motor_wire_{i}',cq.Solid.makeCylinder(1.5,40,cq.Vector(xx,165,38),cq.Vector(0,1,0)),{'TB6600'}))
    for name,s,ignore_groups in corridors:
        hits=[]
        for n,part in parts.items():
            vv=overlap(s,part)
            if vv>EPS:hits.append({'name':n,'volume_mm3':round(vv,5)})
        for c in components:
            if c.group in ignore_groups:continue
            vv=overlap(s,c.shape)
            if vv>EPS:hits.append({'name':c.name,'volume_mm3':round(vv,5)})
        report['access_checks'].append({'corridor':name,'blocked_by':hits})
        if hits:fail(name+' access is blocked')
    # Cross sections verify a narrow screwdriver path from an open service bay to PCB screws.
    for i,(u,v) in enumerate(p['uno']['holes']):
        if i==p['uno']['omit_screw_index']:continue
        xx=p['uno']['origin_x']+v;yy=p['uno']['rear_board_edge_y']-u
        shaft=cylinder(1.5,75,xx,yy,14.1);hits=[]
        for c in components:
            vv=overlap(shaft,c.shape)
            if vv>EPS:hits.append(c.name)
        for n,s in parts.items():
            if n=='top_cover':continue
            if overlap(shaft,s)>EPS:hits.append(n)
        report['access_checks'].append({'corridor':f'UNO_M2.5_screw_{i}_lid_off','blocked_by':hits})
        if hits:fail('UNO screw access '+str(i)+' blocked')
    for name,coords in [('TB_clamp',t['clamp_foot_screws']),('A4988_clip',q['clip_centers'])]:
        for i,(xx,yy) in enumerate(coords):
            shaft=cylinder(1.5,90,xx,yy,9.1 if name=='TB_clamp' else 16.8);hits=[]
            for n,s in parts.items():
                if n=='top_cover':continue
                if overlap(shaft,s)>EPS:hits.append(n)
            for c in components:
                if overlap(shaft,c.shape)>EPS:hits.append(c.name)
            report['access_checks'].append({'corridor':f'{name}_screw_{i}_lid_off','blocked_by':hits})
            if hits:fail(name+' screw access '+str(i)+' blocked')
    # Numeric free spaces, not a thermal rating.
    report['driver_clearances_mm']={'TB_top_to_lid':round(seat-(t['bottom_z']+t['height']),3),
        'TB_top_to_lid_rib':round(seat-5-(t['bottom_z']+t['height']),3),
        'TB_fin_tip_to_floor':t['bottom_z']-e['floor'],'A4988_sink_to_lid':round(seat-(q['pcb_bottom_z']+q['pcb_thickness']+q['socket_height']+q['module_thickness']+1+q['heatsink_height']),3)}
    # Main assembly STEP really imports, with the expected named objects' total volume.
    st=cq.importers.importStep(str(root/'CAD/main_assembly.step')).val()
    expected=sum(x.Volume() for x in parts.values())+sum(c.shape.Volume() for c in components)+sum(c.shape.Volume() for c in hw)
    rel=abs(st.Volume()-expected)/expected
    report['main_assembly_roundtrip']={'valid':st.isValid(),'solids':len(st.Solids()),'volume_relative_error':rel}
    if not st.isValid() or rel>1e-6:fail('Main assembly STEP failed import/volume check')
    if report['failures']:report['status']='FAIL: resolve listed geometry errors'
    print('Checked collisions:',report['collision_pairs_checked'],'failures:',report['failures'],flush=True)
    return report
