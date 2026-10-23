import math
import cadquery as cq

def normalize_parameters(p):
    """A numeric height controls the high rear edge; null uses front_height."""
    e=p['enclosure']
    if e.get('height') is not None:
        e['front_height']=e['height']-e['panel_run']*math.tan(math.radians(e['front_angle_deg']))
    if e['front_height']<10:raise ValueError('Front height is too small; increase enclosure.height')
    return p

def box(w,d,h,x=0,y=0,z=0):
    return cq.Workplane('XY').box(w,d,h,centered=(False,False,False)).translate((x,y,z)).val()

def cylinder(r,h,x=0,y=0,z=0):
    return cq.Workplane('XY').circle(r).extrude(h).translate((x,y,z)).val()

def rounded_box(w,d,h,r,x=0,y=0,z=0):
    s=cq.Workplane('XY').box(w,d,h,centered=(False,False,False))
    if r: s=s.edges('|Z').fillet(r)
    return s.translate((x,y,z)).val()

def union(shapes):
    shapes=list(shapes)
    if not shapes: raise ValueError('empty union')
    return shapes[0].fuse(*shapes[1:]).clean() if len(shapes)>1 else shapes[0]

def cut_many(s,tools):
    tools=list(tools)
    return s.cut(*tools).clean() if tools else s

def compound(shapes): return cq.Compound.makeCompound(list(shapes))

def geometry(p):
    e=p['enclosure']; a=math.radians(e['front_angle_deg'])
    h=e['front_height']+e['panel_run']*math.tan(a)
    return a,h,h-e['cover_thickness']

def panel_transform(s,p):
    return s.rotate((0,0,0),(1,0,0),p['enclosure']['front_angle_deg']).translate((0,0,p['enclosure']['front_height']))

def panel_point(x,t,n,p):
    a,_,_=geometry(p)
    return (x,t*math.cos(a)-n*math.sin(a),p['enclosure']['front_height']+t*math.sin(a)+n*math.cos(a))

def panel_box(w,d,h,x,t,n,p): return panel_transform(box(w,d,h,x,t,n),p)

def panel_cylinder(r,h,x,t,n,p): return panel_transform(cylinder(r,h,x,t,n),p)

def yz_prism(points,width,x=0):
    return cq.Workplane('YZ').polyline(points).close().extrude(width).translate((x,0,0)).val()

def hex_nut_cut(x,y,z,p,entry=1):
    f=p['fasteners']; af=f['m3_nut_af']; hh=f['m3_nut_height']
    r=af/math.sqrt(3)
    pts=[(x+r*math.cos(i*math.pi/3),y+r*math.sin(i*math.pi/3)) for i in range(6)]
    hx=cq.Workplane('XY').polyline(pts).close().extrude(hh).translate((0,0,z)).val()
    channel=box(8,af,hh,x if entry>0 else x-8,y-af/2,z)
    return hx.fuse(channel)

def countersink(x,y,z,p,up=False):
    f=p['fasteners']; r=f['m3_clearance']/2; R=f['m3_head_diameter']/2
    if up: return cq.Solid.makeCone(r,R,R-r,cq.Vector(x,y,z-(R-r)),cq.Vector(0,0,1))
    return cq.Solid.makeCone(R,r,R-r,cq.Vector(x,y,z),cq.Vector(0,0,1))

def vertical_slot(length,width,height,x,y,z,angle=0):
    return cq.Workplane('XY').center(x,y).slot2D(length,width,angle).extrude(height).translate((0,0,z)).val()

def rear_opening(x,z,w,h,p,chamfer=3.0):
    # Roof chamfers limit unsupported horizontal bridges on the upright rear wall.
    d=p['enclosure']['depth']; c=min(chamfer,h/4,w/4)
    pts=[(x,z),(x+w,z),(x+w,z+h-c),(x+w-c,z+h),(x+c,z+h),(x,z+h-c)]
    return cq.Workplane('XZ').polyline(pts).close().extrude(12,both=True).translate((0,d,0)).val()

def print_orientation(s,kind,p):
    if kind=='front_panel' or kind.startswith('joystick_spacer'):
        s=s.translate((0,0,-p['enclosure']['front_height'])).rotate((0,0,0),(1,0,0),-p['enclosure']['front_angle_deg'])
        s=s.rotate((0,0,0),(1,0,0),180)
    elif kind in ('top_cover','tb_clamp_left','tb_clamp_right'):
        s=s.rotate((0,0,0),(1,0,0),180)
    b=s.BoundingBox()
    return s.translate((-b.xmin,-b.ymin,-b.zmin))
