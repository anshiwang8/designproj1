"""Native Inventor revision. All geometric dimensions use cm internally."""
from pathlib import Path
import json,math
import pythoncom,win32com.client as w
from win32com.client import dynamic
ROOT=Path(__file__).resolve().parents[1]
a=dynamic.Dispatch(pythoncom.GetActiveObject('Inventor.Application').QueryInterface(pythoncom.IID_IDispatch))
tg=a.TransientGeometry

def doc(name,assembly=False):
    return w.CastTo(a.Documents.Open(str(ROOT/name),False),'AssemblyDocument' if assembly else 'PartDocument')

def trim(d,axis,limit,name):
    cd=d.ComponentDefinition
    if any(f.Name==name for f in cd.Features):return
    plane_index={'X':1,'Y':2,'Z':3}[axis]
    wp=cd.WorkPlanes.AddByPlaneAndOffset(cd.WorkPlanes.Item(plane_index),f'{limit} mm')
    wp.Name=name+' plane';wp.Visible=False
    f=cd.Features.SplitFeatures.TrimSolid(wp,cd.SurfaceBodies.Item(1),False);f.Name=name

def validate(d):
    assert d.Update2(False),d.DisplayName
    cd=d.ComponentDefinition
    assert cd.SurfaceBodies.Count==1 and cd.SurfaceBodies.Item(1).IsSolid,d.DisplayName
    assert all(f.HealthStatus in (11778,11780) for f in cd.Features),[(f.Name,f.HealthStatus) for f in cd.Features]

def modify(name,fn):
    d=doc(name);tr=a.TransactionManager.StartTransaction(d,'Screw reach and angled fingers revision')
    try:
        fn(d);validate(d);tr.End();d.Save();print('SAVED',name,flush=True)
    except:tr.Abort();raise
    return d

def params(d,values):
    for k,v in values.items():d.ComponentDefinition.Parameters.Item(k).Expression=v

def bend_finger(d):
    cd=d.ComponentDefinition
    trim(d,'Z',6,'Finger thickness reduced to 6 mm')
    if not any(f.Name=='Upward 45 degree finger tip and carrier' for f in cd.Features):
        sk=cd.Sketches.Add(cd.WorkPlanes.Item('Finger thickness reduced to 6 mm plane'))
        sk.Name='Tip bend after both pivot holes'
        ln=sk.SketchLines.AddByTwoPoints(sk.ModelToSketchSpace(tg.CreatePoint(-2,3.1,.6)),sk.ModelToSketchSpace(tg.CreatePoint(2,3.1,.6)))
        f=cd.Features.BendPartFeatures.Add(ln,83458,'1 mm','45 deg',20993,True,cd.SurfaceBodies.Item(1),True)
        f.Name='Upward 45 degree finger tip and carrier';sk.Visible=False
    params(d,{'FingerThickness':'6 mm'})
    # Fill the shallow underside of the bend with a flat-to-45-degree web.
    # This retains the bend and avoids a small unsupported curved underside.
    if not any(f.Name=='Support-free 45 degree bend underside' for f in cd.Features):
        x=-1.3 if 'Right' in d.DisplayName else .1
        end_y=3.1+.7*math.sqrt(.5);end_z=.7*(1-math.sqrt(.5));flat_end=end_y-end_z
        wp=cd.WorkPlanes.AddByPlaneAndOffset(cd.WorkPlanes.Item(1),x);wp.Visible=False
        sk=cd.Sketches.Add(wp);sk.Name='Flat bed and 45 degree bend reinforcement'
        pts=[(3.1,0),(flat_end,0),(end_y,end_z)]
        sp=[sk.ModelToSketchSpace(tg.CreatePoint(x,y,z)) for y,z in pts]
        points=[sk.SketchPoints.Add(p,False) for p in sp]
        for i in range(len(sp)):sk.SketchLines.AddByTwoPoints(points[i],points[(i+1)%len(sp)])
        f=cd.Features.ExtrudeFeatures.AddByDistanceExtent(sk.Profiles.AddForSolid(),'12 mm',20993,20481)
        f.Name='Support-free 45 degree bend underside';sk.Visible=False
    # Map the rigid carrier portion from its original position to its bent pose.
    pt=max((v.Point for v in cd.SurfaceBodies.Item(1).Vertices),key=lambda p:p.Z)
    c=math.sqrt(.5);ty=pt.Y-c*6.4+c*.6;tz=pt.Z-c*6.4-c*.6
    return ty,tz

def cst(c):
    return w.CastTo(c,{100666368:'FlushConstraint',100665856:'MateConstraint',100665088:'AngleConstraint',100666624:'MotionConstraint'}[c.Type])

def plane_proxy(occ,plane):return occ.CreateGeometryProxy(plane)

def attach_pad(assembly,side,ty,tz):
    cd=assembly.ComponentDefinition
    finger=cd.Occurrences.ItemByName(side+' finger');pad=cd.Occurrences.ItemByName(side+' foam contact pad')
    fcd=w.CastTo(finger.Definition,'PartComponentDefinition');pcd=w.CastTo(pad.Definition,'PartComponentDefinition')
    # Foam local x follows the carrier, local y spans its thickness.
    c=math.sqrt(.5);left=side=='Left';sx=1 if left else -1
    origin=tg.CreatePoint(sx*1.5,c*3.4-c*(0 if left else .6)+ty,c*3.4+c*(0 if left else .6)+tz)
    axes=[tg.CreateUnitVector(0,c,c),tg.CreateUnitVector(0,-sx*c,sx*c),tg.CreateUnitVector(sx,0,0)]
    for k in range(cd.Constraints.Count,0,-1):
        con=cd.Constraints.Item(k)
        if con.Name.startswith(side+' foam contact pad - datum'):con.Delete()
    # Three coincident datum planes define pad position and orientation.
    for i,(ix,iy) in enumerate([(1,2),(2,0),(0,1)],1):
        name='Bent carrier foam datum '+str(i)
        try:wp=fcd.WorkPlanes.Item(name)
        except:
            wp=fcd.WorkPlanes.AddFixed(origin,axes[ix],axes[iy]);wp.Name=name;wp.Visible=False
        co=cd.Constraints.AddFlushConstraint(plane_proxy(finger,wp),plane_proxy(pad,pcd.WorkPlanes.Item(i)),0)
        co.Name=side+' foam contact pad - datum '+str(i)
    fcd.Document.Save()

def revise_assembly(d):
    cd=d.ComponentDefinition
    # Existing constraints use origin datums; adjust only Z stack dimensions.
    updates={
        'Upper axle-support plate - datum 3':'14 mm',
        **{f'Upper pivot spacer {i} - datum 2':'11.5 mm' for i in range(1,5)},
        **{f'M3 frame bolt {i} - datum 3':'16 mm' for i in range(1,8)},
        **{f'{side} follower height':'8 mm' for side in ['Left','Right']},
        **{f'{side} finger height':'12 mm' for side in ['Left','Right']},
    }
    for con in cd.Constraints:
        if con.Name in updates:
            cst(con).Offset.Expression=updates.pop(con.Name)
    assert not updates,updates
    # New sleeve lengths; preserve old hardware models for rollback/reference.
    for occ in cd.Occurrences:
        if occ.Name.startswith('Fixed pivot metal sleeve'):
            occ.Replace(str(ROOT/'Hardware'/'Pivot sleeve 4OD 3.2ID x11.ipt'),True)
        elif occ.Name.startswith('M3 frame bolt'):
            occ.Replace(str(ROOT/'Hardware'/'M3x16 socket screw.ipt'),False)
        elif 'finger pivot' in occ.Name and 'metal sleeve' in occ.Name:
            occ.Replace(str(ROOT/'Hardware'/'Pivot sleeve 4OD 3.2ID x10.5.ipt'),True)
    # Finger hardware is located relative to finger datum Z=0.
    # Finger bottom=12; sleeve spans 8..18.5 with 0.5 total axial play.
    for con in cd.Constraints:
        n=con.Name
        if 'finger pivot' not in n or not n.endswith('datum 3'):continue
        if 'metal sleeve' in n:val=-4
        elif 'upper washer' in n:val=6.5
        elif 'locking nut' in n:val=7
        else:val=-4.5
        cst(con).Offset.Expression=f'{val} mm'
    for side in ['Left','Right']:
        ty,tz=bend_offsets[side];attach_pad(d,side,ty,tz)
    assert d.Update2(False)
    bad=[(c.Name,c.HealthStatus) for c in cd.Constraints if c.HealthStatus!=11778]
    assert not bad,bad
    d.Save();print('SAVED ASSEMBLY',cd.Constraints.Count,flush=True)

def sleeve(old,new,length):
    p=ROOT/'Hardware'/new
    if not p.exists():doc('Hardware/'+old).SaveAs(str(p),True)
    d=doc('Hardware/'+new)
    trim(d,'Z',length,f'Sleeve length reduced to {length} mm')
    props=d.PropertySets.Item('Design Tracking Properties')
    props.Item('Part Number').Value=Path(new).stem
    props.Item('Description').Value=(f'M3 x {length} mm socket-head screw; metal hardware' if new.startswith('M3') else f'Metal pivot sleeve 4 mm OD, 3.2 mm ID, {length} mm long')
    validate(d);d.Save();print('SAVED',new,flush=True)

a.SilentOperation=True
bend_offsets={}
try:
    modify('LowerFollowerLink.ipt',lambda d:params(d,{'d10':'3.5 mm'}))
    modify('LowerPivotSpacer.ipt',lambda d:params(d,{'d1':'4.5 mm','d4':'4.5 mm'}))
    modify('UpperPivotSpacer.ipt',lambda d:params(d,{'d1':'2 mm'}))
    modify('P1-02 Design Study Structural Pillar.ipt',lambda d:params(d,{'d3':'11 mm'}))
    modify('P4-04 Upper axle-support plate.ipt',lambda d:trim(d,'Z',2,'Upper plate thickness reduced to 2 mm'))
    for side in ['Left','Right']:
        modify(f'Update 1.2 Uppercrankline and {side} Driven Gears.ipt',lambda d:trim(d,'Z',8,'Crank thickness reduced by 1.5 mm'))
        name=f'Update 1.2 {side} Finger and Pad Carrier.ipt'
        def work(d,side=side):bend_offsets[side]=bend_finger(d)
        modify(name,work)
    modify('P4-05 Foam contact pad.ipt',lambda d:trim(d,'Y',6,'Foam width reduced to 6 mm'))
    sleeve('Pivot sleeve 4OD 3.2ID x14.ipt','Pivot sleeve 4OD 3.2ID x11.ipt',11)
    sleeve('Pivot sleeve 4OD 3.2ID x13.ipt','Pivot sleeve 4OD 3.2ID x10.5.ipt',10.5)
    sleeve('M3x20 socket screw.ipt','M3x16 socket screw.ipt',16)
    revise_assembly(doc('Final QArm Gripper.iam',True))
    (ROOT/'native_revision'/'bend_offsets.json').write_text(json.dumps(bend_offsets,indent=2))
finally:a.SilentOperation=False
