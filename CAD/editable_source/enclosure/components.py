"""Simplified solid reference models, NOT supplier-certified component CAD.

Only interfaces stated as sourced in dimensions.md have manufacturer provenance.
Parts are deliberately solid envelopes in areas where exact moulded details are
unavailable. No external/downloaded polygon models are needed to regenerate.
"""
import math
from dataclasses import dataclass
import cadquery as cq
from .common import *

@dataclass
class Item:
    name: str
    shape: object
    color: tuple
    group: str

def make_uno(p):
    q=p['uno']; z=q['pcb_bottom_z']; th=q['pcb_thickness']
    pcb=cq.Workplane('XY').polyline(q['outline']).close().extrude(th).val()
    pcb=cut_many(pcb,[cylinder(1.6,th+2,x,y,-1) for x,y in q['holes']])
    def tr(s):return s.rotate((0,0,0),(0,0,1),-90).translate((q['origin_x'],q['rear_board_edge_y'],z))
    out=[Item('UNO_PCB',tr(pcb),(0.02,0.40,0.44),'UNO')]
    for k in ('usb','dc'):
        a=q[k]; s=box(a['u_max']-a['u_min'],a['v_max']-a['v_min'],a['height'],a['u_min'],a['v_min'],th)
        out.append(Item('UNO_'+k.upper(),tr(s),(.64,.67,.68) if k=='usb' else (.10,.11,.12),'UNO'))
    headers=[(36.83,2.54,8),(57.15,2.54,6),(54.61,50.8,8),(30.226,50.8,10)]
    for i,(x,y,n) in enumerate(headers):
        out.append(Item('UNO_header_'+str(i),tr(box(n*2.54,2.54,8.5,x-n*2.54/2,y-1.27,th)),(.11,.12,.13),'UNO'))
    out.append(Item('UNO_DIP_envelope',tr(box(35,8,5,29,14,th)),(.13,.14,.15),'UNO'))
    return out

def make_lcd(p):
    q=p['lcd']; x,t=q['center_x'],q['center_t']; n=q['pcb_front_n']; th=q['pcb_thickness']
    pcb=box(q['pcb_width'],q['pcb_depth'],th,x-q['pcb_width']/2,t-q['pcb_depth']/2,n-th)
    pcb=cut_many(pcb,[cylinder(q['hole_diameter']/2,th+2,x+dx,t+dt,n-th-1) for dx,dt in q['hole_offsets']])
    out=[Item('LCD_PCB',panel_transform(pcb,p),(.10,.37,.22),'LCD')]
    bezel=box(q['bezel_width'],q['bezel_depth'],q['bezel_face_n']-n,x-q['bezel_width']/2,t-q['bezel_depth']/2,n)
    out.append(Item('LCD_bezel',panel_transform(bezel,p),(.13,.14,.15),'LCD'))
    out.append(Item('LCD_glass',panel_box(q['view_width'],q['view_depth'],.15,x-q['view_width']/2,t-q['view_depth']/2,q['bezel_face_n']+.03,p),(.14,.34,.36),'LCD'))
    b=q['backpack_bottom_n']
    out.append(Item('LCD_I2C_backpack_envelope',panel_box(q['backpack_width'],q['backpack_depth'],12.0,x-21,t-9.5,b,p),(.13,.22,.19),'LCD'))
    out.append(Item('LCD_I2C_plug_keepout',panel_box(12,9,8,x+16,t-4.5,b-8,p),(.27,.28,.29),'LCD'))
    return out

def knob_local(p,angle=0,azimuth=0,press=0):
    q=p['joystick']; dx,dt=q['shaft_offset']; x,t=q['center_x']+dx,q['center_t']+dt
    s=cq.Workplane('XZ').polyline(q['knob_profile']).close().revolve(360,(0,0),(0,1)).val()
    s=union([s,cylinder(3,12,0,0,q['pivot_n'])])
    s=s.translate((x,t,0))
    az=math.radians(azimuth); pivot=(x,t,q['pivot_n'])
    s=s.rotate(pivot,(x+math.cos(az),t+math.sin(az),q['pivot_n']),angle)
    return s.translate((0,0,-press))

def make_joystick(p):
    q=p['joystick']; x,t=q['center_x'],q['center_t']; n=q['pcb_front_n']; th=q['pcb_thickness']
    pcb=box(q['pcb_width'],q['pcb_depth'],th,x-q['pcb_width']/2,t-q['pcb_depth']/2,n-th)
    pcb=cut_many(pcb,[cylinder(q['hole_diameter']/2,th+2,x+dx,t+dt,n-th-1) for dx,dt in q['hole_offsets']])
    mech=panel_box(q['mechanism_width'],q['mechanism_depth'],q['mechanism_height'],x-q['mechanism_width']/2,t-q['mechanism_depth']/2,n,p)
    return [Item('JOYSTICK_PCB',panel_transform(pcb,p),(.06,.28,.46),'JOYSTICK'),
            Item('JOYSTICK_gimbal_envelope',mech,(.53,.54,.52),'JOYSTICK'),
            Item('JOYSTICK_knob_and_stem',panel_transform(knob_local(p),p),(.10,.11,.12),'JOYSTICK'),
            Item('JOYSTICK_5pin_plug_keepout',panel_box(15,8,7,x-7.5,t-25,n,p),(.20,.21,.22),'JOYSTICK')]

def make_tb(p):
    q=p['tb6600']; x,y,z=q['x'],q['y'],q['bottom_z']; fh=q['fin_height']
    fins=[]; xx=x
    while xx<=x+q['length']-q['fin_width']+1e-6:
        fins.append(box(q['fin_width'],q['body_depth'],fh,xx,y,z));xx+=q['fin_pitch']
    metal=union([box(q['length'],q['body_depth'],2,x,y,z+fh),*fins])
    out=[Item('TB6600_heatsink_reference',metal,(.18,.20,.22),'TB6600'),
         Item('TB6600_housing_envelope',box(q['length'],q['body_depth'],q['height']-fh-2,x,y,z+fh+2),(.22,.23,.25),'TB6600')]
    # Two blocks of six, 5.08 pitch. Pitch/position must be measured on the real unit.
    width=q['terminal_pitch']*6; ty=y+q['body_depth']; top=z+q['height']+q['terminal_top_offset']
    for k,tx in enumerate((x+q['terminal_x_margin'],x+q['terminal_x_margin']+width+5)):
        s=box(width,q['terminal_depth'],14,tx,ty,top-14)
        for i in range(6):s=s.cut(cylinder(1.5,3,tx+(i+.5)*q['terminal_pitch'],y+q['terminal_screw_y_offset'],top-2))
        out.append(Item('TB6600_terminal_'+str(k),s,(.15,.39,.25),'TB6600'))
    for i,xx in enumerate(q['clamp_x']):
        out.append(Item(f'TB6600_compressed_foam_pad_{i}',box(8,20,q['clamp_clearance'],xx-4,y+17,z+q['height']),(.16,.17,.18),'TB6600'))
    return out

def make_a4988(p):
    q=p['a4988']; x,y=q['carrier_x'],q['carrier_y']; z=q['pcb_bottom_z']; th=q['pcb_thickness']; top=z+th
    out=[Item('A4988_perfboard_40x60',box(q['carrier_width'],q['carrier_depth'],th,x,y,z),(.51,.35,.18),'A4988')]
    cx,cy=q['module_center_x'],q['module_center_y']; sh=q['socket_height']
    for xx in (cx-q['row_pitch']/2,cx+q['row_pitch']/2):
        out.append(Item('A4988_socket_'+str(xx),box(2.54,20.32,sh,xx-1.27,cy-10.16,top),(.12,.13,.14),'A4988'))
    mz=top+sh
    out.append(Item('A4988_driver_PCB',box(q['module_width'],q['module_depth'],q['module_thickness'],cx-q['module_width']/2,cy-q['module_depth']/2,mz),(.44,.10,.13),'A4988'))
    sinkz=mz+q['module_thickness']+1
    out.append(Item('A4988_heatsink_envelope',box(q['heatsink_width'],q['heatsink_depth'],q['heatsink_height'],cx-5,cy-2,sinkz),(.60,.61,.62),'A4988'))
    out.append(Item('A4988_pot_reference',cylinder(2.2,2,q['pot_x'],q['pot_y'],mz+q['module_thickness']),(.22,.33,.50),'A4988'))
    out.append(Item('A4988_VMOT_capacitor_envelope',cylinder(q['capacitor_diameter']/2,q['capacitor_height'],q['capacitor_x'],q['capacitor_y'],top),(.21,.23,.25),'A4988'))
    term=box(q['terminal_width'],q['terminal_depth'],q['terminal_height'],q['terminal_x'],q['terminal_y'],top)
    for i in range(6):term=term.cut(cylinder(1.4,3,q['terminal_x']+(i+.5)*5.08,q['terminal_y']+4,top+q['terminal_height']-2))
    out.append(Item('A4988_6way_terminal_reference',term,(.15,.39,.25),'A4988'))
    return out

def all_components(p):
    e=p['enclosure']
    feet=[Item(f'adhesive_foot_{i}',cylinder(e['rubber_foot_diameter']/2,e['rubber_foot_height'],x,y,-e['rubber_foot_height']),(.10,.11,.12),'FEET') for i,(x,y) in enumerate(e['rubber_feet'])]
    return make_uno(p)+make_lcd(p)+make_joystick(p)+make_tb(p)+make_a4988(p)+feet
