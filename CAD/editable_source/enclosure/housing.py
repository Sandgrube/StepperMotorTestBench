import math
import cadquery as cq
from .common import *

def make_chassis(p):
    e=p['enclosure']; f=p['fasteners']; a,H,seat=geometry(p)
    W,D=e['width'],e['depth']; floor=e['floor']; wall=e['wall']; run=e['panel_run']
    # Open wedge tub. The flat floor is the print-bed surface.
    profile=[(0,0),(D,0),(D,seat),(run+0.2,seat),
             (run, e['front_height']+run*math.tan(a)-(e['panel_thickness']+e['cover_clearance'])/math.cos(a)),
             (0,e['front_height']-(e['panel_thickness']+e['cover_clearance'])/math.cos(a))]
    outer=rounded_box(W,D,H+5,e['corner_radius'])
    s=outer.intersect(yz_prism(profile,W))
    cavity=rounded_box(W-2*wall,D-2*wall,H+10,max(1,e['corner_radius']-wall),wall,wall,floor)
    s=s.cut(cavity)
    additions=[]; holes=[]
    # Independent, three-screw Uno support. Fourth hole has a small locating pin.
    u=p['uno']; ux=u['origin_x']; uy=u['rear_board_edge_y']; z=u['pcb_bottom_z']
    for i,(uu,vv) in enumerate(u['holes']):
        x,y=ux+vv,uy-uu
        additions.append(cylinder(3.1,z-floor,x,y,floor))
        additions.append(cq.Solid.makeCone(4.5,3.1,2,cq.Vector(x,y,floor),cq.Vector(0,0,1)))
        if i==u['omit_screw_index']:
            additions.append(cylinder(1.25,0.95,x,y,z))
        else: holes.append(cylinder(f['m25_pilot']/2,z-0.9,x,y,0.9))
    # Four narrow TB6600 feet leave a 7 mm flow space below the metal fin tips.
    t=p['tb6600']
    for x in (t['x']+10,t['x']+t['length']-10):
        for y in (t['y']+8,t['y']+t['body_depth']-8):
            additions.append(rounded_box(8,8,t['bottom_z']-floor,1,x-4,y-4,floor))
    for x,y in t['clamp_foot_screws']:
        additions.append(cylinder(4.5,3,x,y,floor))
        holes.append(cylinder(f['m3_pilot']/2,5.1,x,y,0.9))
    # Plain 40 x 60 perfboard is retained by edges; its corner holes are irrelevant.
    q=p['a4988']; x=q['carrier_x']; y=q['carrier_y']; w=q['carrier_width']; d=q['carrier_depth']
    for xx in (x+4,x+w-4):
        for yy in (y+4,y+d-4): additions.append(cylinder(3,q['pcb_bottom_z']-floor,xx,yy,floor))
    for xx in (x+4,x+w-4):
        additions.append(box(7,2,10.0,xx-3.5,y-2,floor))
        # A half-millimetre overhang catches the bare board edge, not a component.
        additions.append(box(7,2.6,1.2,xx-3.5,y-2,11.8))
    for xx,yy in q['clip_centers']:
        additions.append(cylinder(3.8,8.8-floor,xx,yy,floor))
        holes.append(cylinder(f['m3_pilot']/2,7.9,xx,yy,0.9))
    # Captive nuts for a lid that removes without disturbing the front controls.
    for x,y in e['lid_screws']:
        additions.append(rounded_box(10,10,seat-floor,1,x-5,y-5,floor))
        holes.extend([cylinder(f['m3_clearance']/2,15,x,y,seat-14),
                      hex_nut_cut(x,y,seat-8.35,p,1 if x<W/2 else -1)])
    # Cable tie anchors. A short bridge is the only roof in each anchor.
    for x,y in ((45,77),(77,77),(111,77),(148,77),(185,77),(93,99)):
        additions.append(rounded_box(9,7,4,0.8,x-4.5,y-3.5,floor))
        holes.append(box(3.4,10,1.8,x-1.7,y-5,floor+0.9))
    s=union([s,*additions]); s=cut_many(s,holes)
    cuts=[]
    for x,y in e['panel_feet']:
        cuts.extend([cylinder(f['m3_clearance']/2,5,x,y,-1),countersink(x,y,0,p)])
    ac=p['access']
    for tag in ('usb','dc','tb_rear','a_rear'):
        cuts.append(rear_opening(ac[tag+'_x'],ac[tag+'_z'],ac[tag+'_width'],ac[tag+'_height'],p,2.0 if tag=='usb' else 3.0))
    # Two paired tie holes per rear cable bay, below the pass-through.
    for xx,zz in ((146,27),(185,27),(87,11),(103,11)):
        for dx in (-3,3): cuts.append(box(2.7,wall+4,2.2,xx+dx-1.35,D-wall-2,zz-1.1))
    v=p['vents']
    for y in v['side_y']:
        z0,z1=v['side_bottom_z'],v['side_top_z']; sw=v['slot_width']
        pts=[(y-sw/2,z0),(y+sw/2,z0),(y+sw/2,z1-sw/2),(y,z1),(y-sw/2,z1-sw/2)]
        cuts.append(yz_prism(pts,wall+2,W-wall-1))
    for xx in (149,157,165,173,181,189,197):
        cuts.append(vertical_slot(30,3.2,floor+2,xx,123,-1,90))
    for xx in (83,91,99,107):
        cuts.append(vertical_slot(22,3.2,floor+2,xx,137,-1,90))
    # Flat underside: adhesive feet need no unsupported recess roofs.
    return cut_many(s,cuts).clean()

def make_front_panel(p):
    e=p['enclosure']; f=p['fasteners']; a,H,seat=geometry(p)
    W=e['width']; run=e['panel_run']; th=e['panel_thickness']
    # Vertical front/rear seams, outer face precisely at the selected angle.
    slab=yz_prism([(0,e['front_height']-th/math.cos(a)),(run,H-th/math.cos(a)),(run,H),(0,e['front_height'])],W)
    slab=slab.intersect(rounded_box(W,run,H+2,e['corner_radius']))
    addons=[]; cuts=[]
    for x,y in e['panel_feet']:
        top=e['front_height']+y*math.tan(a)-th/math.cos(a)+0.35
        addons.append(rounded_box(10,10,top-e['floor'],1,x-5,y-5,e['floor']))
        cuts.extend([cylinder(f['m3_clearance']/2,11,x,y,e['floor']-0.05),
                     hex_nut_cut(x,y,7.6,p,1 if x<W/2 else -1)])
    l=p['lcd']; x,t=l['center_x'],l['center_t']; n=l['pcb_front_n']
    for dx,dt in l['hole_offsets']:
        addons.append(panel_cylinder(2.5,-th-n+0.25,x+dx,t+dt,n,p))
        cuts.append(panel_cylinder(f['m25_pilot']/2,9.0,x+dx,t+dt,n-0.05,p))
    # PCB lies behind the bezel pocket. Only the LCD viewing aperture is visible.
    cuts.extend([
        panel_box(l['window_width'],l['window_depth'],10,x-l['window_width']/2,t-l['window_depth']/2,-5,p),
        panel_box(l['bezel_pocket_width'],l['bezel_pocket_depth'],8.9,x-l['bezel_pocket_width']/2,t-l['bezel_pocket_depth']/2,-9.6,p)])
    j=p['joystick']; x,t=j['center_x'],j['center_t']; n=j['pcb_front_n']+j['mount_spacer']
    for dx,dt in j['hole_offsets']:
        addons.append(panel_cylinder(3.0,-th-n+0.2,x+dx,t+dt,n,p))
        cuts.append(panel_cylinder(f['m3_pilot']/2,-n-.60,x+dx,t+dt,n-0.05,p))
    dx,dt=j['shaft_offset']
    cuts.append(panel_cylinder(j['opening_diameter']/2,12,x+dx,t+dt,-6,p))
    # Recessing the knob means these four supports need a short outward gusset.
    for dx,dt in j['hole_offsets']:
        xx=x+dx; tt=t+dt
        direction=1 if dt>0 else -1
        addons.append(panel_box(3,5,7,xx-1.5,tt if direction>0 else tt-5,-10,p))
    return cut_many(union([slab,*addons]),cuts).clean()

def make_cover(p):
    e=p['enclosure']; a,H,seat=geometry(p); v=p['vents']; f=p['fasteners']
    W,D=e['width'],e['depth']; sy=e['panel_run']+e['cover_clearance']
    s=rounded_box(W,D-sy,e['cover_thickness'],e['corner_radius'],0,sy,seat)
    addons=[]; cuts=[]
    # Integral ribs print upwards with the outside face on the bed.
    for yy in (sy+5,145): addons.append(box(W-14,2.4,5,7,yy,seat-5))
    for xx in (68,120): addons.append(box(2.4,D-sy-16,4,xx,sy+8,seat-4))
    for yy in (98,151):
        addons.append(box(1.4,12,3,e['wall']+e['cover_clearance'],yy,seat-3))
        addons.append(box(1.4,12,3,W-e['wall']-e['cover_clearance']-1.4,yy,seat-3))
    s=union([s,*addons])
    for x,y in e['lid_screws']:
        cuts.extend([cylinder(f['m3_clearance']/2,10,x,y,seat-3),countersink(x,y,H,p,True)])
    for xx in v['tb_cover_x']:
        cuts.append(vertical_slot(v['slot_length'],v['slot_width'],12,xx,v['tb_cover_y'],seat-6,90))
    for xx in v['a_cover_x']:
        cuts.append(vertical_slot(v['slot_length'],v['slot_width'],12,xx,v['a_cover_y'],seat-6,90))
    ac=p['access']
    for tag in ('tb_tool','a_tool'):
        cuts.append(rounded_box(ac[tag+'_width'],ac[tag+'_depth'],15,1.0,ac[tag+'_x'],ac[tag+'_y'],seat-8))
    q=p['a4988']
    cuts.append(cylinder(ac['pot_access_diameter']/2,15,q['pot_x'],q['pot_y'],seat-8))
    return cut_many(s,cuts).clean()

def make_tb_clamp(p,right=False):
    q=p['tb6600']; x=q['clamp_x'][1 if right else 0]; y=q['y']; f=p['fasteners']
    cap_bottom=q['bottom_z']+q['height']+q['clamp_clearance']; cap_top=cap_bottom+3.6
    y0=y-5.6; y1=y+q['overall_depth']+0.6
    # U bridge printed upside down. It does not use the module's mounting holes.
    parts=[box(8,y1+4-y0,3.6,x-4,y0,cap_bottom),
           box(8,4,cap_bottom-6,x-4,y0,6),box(8,4,cap_bottom-6,x-4,y1,6)]
    fx=x-18 if right else x-4
    mounts=q['clamp_foot_screws'][2:4] if right else q['clamp_foot_screws'][0:2]
    for (sx,sy),dd in zip(mounts,(10.4,9.7)):
        parts.append(rounded_box(22,dd,3,1,fx,sy-5.5,6))
    s=union(parts)
    cuts=[]
    for sx,sy in mounts:
        cuts.append(vertical_slot(8,3.6,6,sx,sy,5,0))
        sink=(cq.Workplane('XY').workplane(offset=7.6).center(sx,sy).slot2D(8,3.6)
              .workplane(offset=1.4).slot2D(10.8,6.4).loft(combine=True).val())
        cuts.append(sink)
    return cut_many(s,cuts)

def make_carrier_clip(p,index=0):
    x,y=p['a4988']['clip_centers'][index]
    # Underside step bears on its post; cantilever stays 0.2 above the perfboard.
    s=union([box(8,5,4.4,x-4,y-2.5,8.8),box(3.5,5.2,1.4,x-1.75,y-5.2,11.8)])
    return s.cut(cylinder(p['fasteners']['m3_clearance']/2,8,x,y,7))

def make_foot(p):
    return cylinder(p['enclosure']['rubber_foot_diameter']/2,4)

def make_joystick_spacer(p,index=0):
    j=p['joystick'];dx,dt=j['hole_offsets'][index];x,t=j['center_x']+dx,j['center_t']+dt
    s=cylinder(3,j['mount_spacer'],x,t,j['pcb_front_n'])
    return panel_transform(s.cut(cylinder(1.7,j['mount_spacer']+2,x,t,j['pcb_front_n']-1)),p)

def make_tests(p):
    l=p['lcd']; j=p['joystick']; f=p['fasteners']
    # Full-size flat coupons: cheap checks, not miniature decorative samples.
    lcd=rounded_box(90,46,2,2)
    lcd=lcd.cut(box(l['window_width'],l['window_depth'],4,45-l['window_width']/2,23-l['window_depth']/2,-1))
    for dx,dt in l['hole_offsets']:
        lcd=lcd.cut(cylinder(f['m25_clearance']/2,4,45+dx,23+dt,-1))
    joy=rounded_box(48,54,3,2,0,0,-3)
    for dx,dt in j['hole_offsets']:
        xx,tt=24+dx,27+dt
        end=j['pcb_front_n']+j['mount_spacer']
        joy=joy.fuse(cylinder(3,-3-end+.2,xx,tt,end))
        joy=joy.fuse(box(3,5,7,xx-1.5,tt if dt>0 else tt-5,-10))
    joy=joy.cut(cylinder(j['opening_diameter']/2,12,24,27,-6))
    for dx,dt in j['hole_offsets']:
        end=j['pcb_front_n']+j['mount_spacer']
        joy=joy.cut(cylinder(f['m3_pilot']/2,-end-.60,24+dx,27+dt,end-.05))
    joy=print_orientation(joy,'top_cover',p)
    nut=rounded_box(50,24,10,2)
    for xx,af in ((10,5.7),(25,5.9),(40,6.1)):
        pp={**p,'fasteners':{**f,'m3_nut_af':af}}
        pocket=hex_nut_cut(xx,12,3,pp,1).rotate((xx,12,0),(xx,12,1),90)
        pocket=pocket.fuse(box(af,14,pp['fasteners']['m3_nut_height'],xx-af/2,12,3))
        nut=nut.cut(pocket).cut(cylinder(1.7,12,xx,12,-1))
    ports=box(68,3,26)
    for key,xx in (('usb',5),('dc',38)):
        ac=p['access']; w,h=ac[key+'_width'],ac[key+'_height']; c=2 if key=='usb' else 3
        pts=[(xx,3),(xx+w,3),(xx+w,3+h-c),(xx+w-c,3+h),(xx+c,3+h),(xx,3+h-c)]
        ports=ports.cut(cq.Workplane('XZ').polyline(pts).close().extrude(10,both=True).val())
    pilot=rounded_box(58,18,10,2)
    for xx,dd in ((8,2.45),(22,2.55),(36,2.65),(50,2.75)):
        pilot=pilot.cut(cylinder(dd/2,9,xx,9,2))
    return {'lcd_fit_coupon':lcd,'joystick_pattern_coupon':joy,'m3_nut_coupon':nut,'rear_ports_coupon':ports,'m3_pilot_coupon':pilot}
