#!/usr/bin/env python3
"""Offline previews from the actual OpenCascade geometry, no generated imagery.

Matplotlib's triangle painter is for illustrations, not interference testing.
The separate OCCT boolean validator owns all engineering checks.
"""
import json,math,sys,argparse
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import findfont
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from PIL import Image,ImageDraw,ImageFont
from generate import build
from enclosure.common import panel_transform,normalize_parameters
from enclosure.components import all_components
from enclosure.fasteners import fasteners
import cadquery as cq

ROOT=Path(__file__).resolve().parents[2]
PALETTE=(.25,.27,.30)

def tris(shape):
    v,f=shape.tessellate(.35,.18)
    v=np.array([[p.x,p.y,p.z] for p in v]);f=np.asarray(f,dtype=int)
    return v[f]

def render(items,path,elev=29,azim=-58,size=(12,8),limits=None,zoom=1.08):
    # Orthographic CPU z-buffer: unlike a triangle painter it handles large
    # perforated coplanar CAD faces without showing hidden internal triangles.
    width,height=int(size[0]*150),int(size[1]*150)
    az,el=np.radians([azim,elev])
    right=np.array([-np.sin(az),np.cos(az),0])
    up=np.array([-np.sin(el)*np.cos(az),-np.sin(el)*np.sin(az),np.cos(el)])
    near=np.array([np.cos(el)*np.cos(az),np.cos(el)*np.sin(az),np.sin(el)])
    light=np.array([-.4,-.65,1.0]);light/=np.linalg.norm(light)
    allts=[];colors=[]
    for shape,color in items:
        t=tris(shape);norm=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0])
        norm/=np.maximum(np.linalg.norm(norm,axis=1,keepdims=True),1e-12)
        shade=.70+.30*np.clip(norm@light,0,1)
        allts.append(t);colors.append(np.clip(np.asarray(color)[None,:]*shade[:,None]*255,0,255).astype(np.uint8))
    t=np.concatenate(allts);colors=np.concatenate(colors)
    xy=np.stack((t@right,t@up),axis=-1);zz=t@near
    lo=xy.reshape(-1,2).min(axis=0);hi=xy.reshape(-1,2).max(axis=0)
    scale=min(width/(hi[0]-lo[0]),height/(hi[1]-lo[1]))*.89
    center=(lo+hi)/2
    xy=(xy-center)*scale
    xy[:,:,0]+=width/2;xy[:,:,1]=height/2-xy[:,:,1]
    buf=np.full((height,width),-1e12,dtype=np.float32)
    canvas=np.full((height,width,3),[243,244,245],dtype=np.uint8)
    for pts,z,col in zip(xy,zz,colors):
        x0=max(0,int(np.floor(pts[:,0].min())));x1=min(width-1,int(np.ceil(pts[:,0].max())))
        y0=max(0,int(np.floor(pts[:,1].min())));y1=min(height-1,int(np.ceil(pts[:,1].max())))
        if x0>x1 or y0>y1:continue
        a,b,c=pts;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(den)<1e-5:continue
        xx=np.arange(x0,x1+1,dtype=float)[None,:]+.5;yy=np.arange(y0,y1+1,dtype=float)[:,None]+.5
        u=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den
        v=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den
        w=1-u-v
        depth=u*z[0]+v*z[1]+w*z[2]
        dest=buf[y0:y1+1,x0:x1+1]
        mask=(u>=-1e-7)&(v>=-1e-7)&(w>=-1e-7)&(depth>dest)
        dest[mask]=depth[mask]
        canvas[y0:y1+1,x0:x1+1][mask]=col
    Image.fromarray(canvas).save(path)

def screen_text(p):
    q=p['lcd']; out=[]
    for text,dy in [('TB6600   1/8',3.5),('LOCK   0 RPM',-3.5)]:
        s=cq.Workplane('XY').text(text,4.1,.04,font='DejaVu Sans Mono',fontPath=findfont('DejaVu Sans Mono'),halign='center',valign='center').val()
        s=s.translate((q['center_x'],q['center_t']+dy,q['bezel_face_n']+.20))
        out.append((panel_transform(s,p),(.75,.85,.77)))
    return out

def svg_layout(p,path):
    e=p['enclosure'];W=e['width'];D=e['depth'];u=p['uno'];q=p['a4988'];t=p['tb6600'];l=p['lcd'];j=p['joystick']
    def r(x,y,w,h,fill,label):
        return f'<rect x="{x}" y="{D-y-h}" width="{w}" height="{h}" rx="2" fill="{fill}" stroke="#59636b" stroke-width="0.35"/><text x="{x+w/2}" y="{D-y-h/2}" text-anchor="middle" dominant-baseline="middle" font-size="3.5">{label}</text>'
    a=math.radians(e['front_angle_deg'])
    content=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1020" viewBox="-22 -23 {W+44} {D+44}">
    <style>text{{font-family:Arial,sans-serif;fill:#263238}} .dim{{stroke:#64717d;stroke-width:.35;fill:none}}</style>
    <rect x="0" y="0" width="{W}" height="{D}" rx="4" fill="#e6eaed" stroke="#25313a" stroke-width=".7"/>
    <path d="M0 {D-e['panel_run']} H{W}" stroke="#7c878f" stroke-dasharray="2 1" stroke-width=".4"/>
    <text x="115" y="{D-12}" text-anchor="middle" font-size="4">FRONT · 18° zur Tischfläche</text>
    <text x="115" y="-8" text-anchor="middle" font-size="4">RÜCKSEITE / KABEL</text>'''
    content+=r(u['origin_x'],u['rear_board_edge_y']-68.58,53.34,68.58,'#a6c5c5','UNO R3')
    content+=r(q['carrier_x'],q['carrier_y'],40,60,'#d9c9ad','A4988')
    content+=r(t['x'],t['y'],96,71,'#b5bbc1','TB6600')
    content+=r(l['center_x']-40,l['center_t']*math.cos(a)-18,80,36,'#c8d3d8','LCD · 80 × 36')
    jy=D-j['center_t']*math.cos(a)
    content+=f'<circle cx="{j["center_x"]}" cy="{jy}" r="{j["opening_diameter"]/2}" fill="#c5ccd2" stroke="#59636b" stroke-width=".35"/><text x="{j["center_x"]}" y="{jy+1}" text-anchor="middle" font-size="3.5">JOYSTICK</text>'
    content+=f'<path class="dim" d="M0 {D+5} V{D+12} M{W} {D+5} V{D+12} M0 {D+9} H{W}"/><text x="{W/2}" y="{D+16}" text-anchor="middle" font-size="4.5">{W:.0f} mm</text>'
    content+=f'<path class="dim" d="M-5 0 H-13 M-5 {D} H-13 M-10 0 V{D}"/><text transform="translate(-15 {D/2}) rotate(-90)" text-anchor="middle" font-size="4.5">{D:.0f} mm</text>'
    content+='<text x="230" y="204" text-anchor="end" font-size="3">Referenzkonturen; kein Bohrplan im Maßstab 1:1.</text></svg>'
    path.write_text(content)

def main():
    global ROOT
    ap=argparse.ArgumentParser();ap.add_argument('--params',type=Path,default=ROOT/'CAD/parameters/default.json');ap.add_argument('--output',type=Path,default=ROOT)
    args=ap.parse_args();ROOT=args.output.resolve()
    p=normalize_parameters(json.loads(args.params.read_text()));parts=build(p);comps=all_components(p)
    dst=ROOT/'PREVIEWS';dst.mkdir(exist_ok=True)
    default=[(s,PALETTE) for s in parts.values()]+[(o.shape,o.color) for o in [*comps,*fasteners(p)]]+screen_text(p)
    render(default,dst/'assembled.png')
    render(default,dst/'rear.png',elev=25,azim=60)
    internal=[(s,PALETTE) for n,s in parts.items() if n not in ('top_cover','front_panel') and not n.startswith('joystick_spacer')]+[(o.shape,o.color) for o in comps if o.group not in ('LCD','JOYSTICK')]
    render(internal,dst/'internal_layout.png',elev=61,azim=-65,size=(12,9),zoom=1.12)
    exploded=[]
    for n,s in parts.items():
        if n=='front_panel' or n.startswith('joystick_spacer'):delta=(0,-8,64)
        elif n=='top_cover':delta=(0,15,114)
        elif n.startswith('tb_clamp'):delta=(0,0,55)
        elif n.startswith('a4988_edge'):delta=(0,0,46)
        else:delta=(0,0,0)
        exploded.append((s.translate(delta),PALETTE))
    for o in comps:
        delta=(0,-8,64) if o.group in ('LCD','JOYSTICK') else ((0,0,-15) if o.group=='FEET' else (0,0,25))
        exploded.append((o.shape.translate(delta),o.color))
    render(exploded,dst/'exploded.png',elev=24,azim=-64,size=(12,12),zoom=1.02)
    render(default,dst/'front_ortho.png',elev=0,azim=-90,size=(12,4),zoom=1.04)
    render(default,dst/'rear_ortho.png',elev=0,azim=90,size=(12,4),zoom=1.04)
    im=Image.new('RGB',(1800,1320),'#f3f4f5');dr=ImageDraw.Draw(im)
    fp=findfont('DejaVu Sans')
    font=ImageFont.truetype(fp,27)
    for i,(fname,title) in enumerate((('front_ortho.png','FRONT — nur LCD und Joystick'),('rear_ortho.png','RÜCKSEITE — TB6600 / A4988 / USB / DC'))):
        pic=Image.open(dst/fname).convert('RGB');pic.thumbnail((1740,580));im.paste(pic,((1800-pic.width)//2,60+i*650));dr.text((60,24+i*650),title,font=font,fill='#263238')
    im.save(dst/'front_rear_views.png')
    svg_layout(p,dst/'layout_dimensions.svg')
    print('Previews generated from exact delivered CAD shapes.',flush=True)

if __name__=='__main__':main()
