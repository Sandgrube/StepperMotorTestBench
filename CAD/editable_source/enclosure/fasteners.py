"""Nominal unthreaded fasteners. Thread/pilot intersections are intentional."""
import math
import cadquery as cq
from .common import *
from .components import Item

def fasteners(p):
    out=[];e=p['enclosure'];_,H,seat=geometry(p);metal=(.37,.39,.41)
    def add(name,shape,kind):out.append(Item(name,shape,metal,kind))
    def cs(name,x,y,top,length,up=False):
        if not up:
            head=cq.Solid.makeCone(1.5,3.0,1.5,cq.Vector(x,y,top-1.5),cq.Vector(0,0,1));shaft=cylinder(1.5,length-1.5,x,y,top-length)
        else:
            head=cq.Solid.makeCone(3.0,1.5,1.5,cq.Vector(x,y,top),cq.Vector(0,0,1));shaft=cylinder(1.5,length-1.5,x,y,top+1.5)
        add(name+'_head',head,'FASTENER_HEAD');add(name+'_shaft',shaft,'FASTENER_SHAFT')
    def nut(name,x,y,z):
        R=5.5/math.sqrt(3);pts=[(x+R*math.cos(i*math.pi/3),y+R*math.sin(i*math.pi/3)) for i in range(6)]
        s=cq.Workplane('XY').polyline(pts).close().extrude(2.4).translate((0,0,z)).val()
        add(name,s.cut(cylinder(1.25,4,x,y,z-1)),'NUT')
    for i,(x,y) in enumerate(e['panel_feet']):
        cs(f'M3x12_panel_{i}',x,y,0,12,True);nut(f'M3_nut_panel_{i}',x,y,7.75)
    for i,(x,y) in enumerate(e['lid_screws']):
        cs(f'M3x12_lid_{i}',x,y,H,12);nut(f'M3_nut_lid_{i}',x,y,seat-8.20)
    for i,(x,y) in enumerate(p['tb6600']['clamp_foot_screws']):cs(f'M3x8_TB_clamp_{i}',x,y,9,8)
    u=p['uno']
    for i,(uu,vv) in enumerate(u['holes']):
        if i==u['omit_screw_index']:continue
        x,y=u['origin_x']+vv,u['rear_board_edge_y']-uu;z=u['pcb_bottom_z']+u['pcb_thickness']
        add(f'M25x8_UNO_{i}_head',cylinder(2.25,2.5,x,y,z),'FASTENER_HEAD');add(f'M25x8_UNO_{i}_shaft',cylinder(1.25,8,x,y,z-8),'FASTENER_SHAFT')
    for label,q,m,headr,headh in [('LCD',p['lcd'],2.5,2.25,2.5),('JOYSTICK',p['joystick'],3,2.75,3)]:
        for i,(dx,dt) in enumerate(q['hole_offsets']):
            x,t=q['center_x']+dx,q['center_t']+dt;n=q['pcb_front_n']-q['pcb_thickness']-.5
            add(f'{label}_screw_{i}_head',panel_cylinder(headr,headh,x,t,n-headh,p),'FASTENER_HEAD')
            add(f'{label}_screw_{i}_shaft',panel_cylinder(m/2,8 if label=='LCD' else 10,x,t,n,p),'FASTENER_SHAFT')
            ring=cylinder(2.5 if label=='LCD' else 3,.5,x,t,n).cut(cylinder(m/2+.15,1,x,t,n-.1))
            add(f'{label}_washer_{i}',panel_transform(ring,p),'WASHER')
    for i,(x,y) in enumerate(p['a4988']['clip_centers']):
        z=13.7
        add(f'M3x10_carrier_{i}_head',cylinder(2.75,3,x,y,z),'FASTENER_HEAD');add(f'M3x10_carrier_{i}_shaft',cylinder(1.5,10,x,y,z-10),'FASTENER_SHAFT')
        add(f'carrier_washer_{i}',cylinder(3,.5,x,y,13.2).cut(cylinder(1.65,1,x,y,13)),'WASHER')
    return out
