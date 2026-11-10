from pathlib import Path
import math,json,struct,hashlib
import pythoncom,win32com.client as w
from win32com.client import dynamic
ROOT=Path(__file__).resolve().parents[1]
a=dynamic.Dispatch(pythoncom.GetActiveObject('Inventor.Application').QueryInterface(pythoncom.IID_IDispatch))
tg=a.TransientGeometry
def doc(n,asm=False):return w.CastTo(a.Documents.Open(str(ROOT/n),False),'AssemblyDocument' if asm else 'PartDocument')
def xyz(p):return [p.X*10,p.Y*10,p.Z*10]
def transform(p,m):
    q=tg.CreatePoint(*p);q.TransformBy(m);return xyz(q)
def health(d):
    cd=d.ComponentDefinition
    return {'solid_count':cd.SurfaceBodies.Count,'is_solid':cd.SurfaceBodies.Item(1).IsSolid,'features':[{'name':f.Name,'health':f.HealthStatus} for f in cd.Features], 'bounds_mm':[xyz(cd.RangeBox.MinPoint),xyz(cd.RangeBox.MaxPoint)]}
report={'revision_date':'2026-11-10','parts':[],'poses':[]}
a.SilentOperation=True
try:
    for p in ROOT.glob('*.ipt'):
        d=doc(p.name);data=health(d);data['file']=p.name;report['parts'].append(data)
    d=doc('Final QArm Gripper.iam',True);cd=d.ComponentDefinition
    print('USER PARAMS',[(p.Name,p.Expression) for p in cd.Parameters.UserParameters],flush=True)
    jaw=cd.Parameters.Item('JawOpening');saved=jaw.Expression
    oc=a.TransientObjects.CreateObjectCollection()
    for o in cd.Occurrences:oc.Add(o)
    for gap in [15,20,30,40,50,60,70,75]:
        jaw.Expression=f'{gap} mm';ok=d.Update2(False)
        pose={'command_mm':gap,'updated':ok,'unhealthy_constraints':[(c.Name,c.HealthStatus) for c in cd.Constraints if c.HealthStatus!=11778]}
        pads=[cd.Occurrences.ItemByName(s+' foam contact pad') for s in ['Left','Right']]
        left=transform((1.4,.3,.2),pads[0].Transformation);right=transform((1.4,.3,.2),pads[1].Transformation)
        pose['measured_gap_mm']=right[0]-left[0]
        pose['tip_angles_deg']=[]
        for pad in pads:
            p0=transform((0,0,0),pad.Transformation);p1=transform((2.8,0,0),pad.Transformation)
            v=[y-x for x,y in zip(p0,p1)];pose['tip_angles_deg'].append(math.degrees(math.atan2(v[2],math.hypot(v[0],v[1]))))
        results=cd.AnalyzeInterference(oc)
        pose['interferences']=[]
        for it in results:
            pose['interferences'].append({'one':it.OccurrenceOne.Name,'two':it.OccurrenceTwo.Name,'volume_mm3':it.Volume*1000})
        report['poses'].append(pose)
        (ROOT/'native_revision'/'validation-progress.json').write_text(json.dumps(report,indent=2))
        gripper_hits=[hit for hit in pose['interferences'] if any(s in (hit['one']+' '+hit['two']).lower() for s in ['finger','follower','gear','pivot','frame bolt','plate'])]
        print('POSE',gap,'gap',pose['measured_gap_mm'],'angles',pose['tip_angles_deg'],'gripper collisions',gripper_hits,flush=True)
    jaw.Expression=saved;d.Update2(False);d.Save()
    report['constraints']=cd.Constraints.Count;report['occurrences']=cd.Occurrences.Count
    report['external_references']=[r.FullFileName for r in d.AllReferencedDocuments if not Path(r.FullFileName).is_relative_to(ROOT)]
    cam=a.TransientObjects.CreateCamera();cam.SceneObject=cd
    cam.Eye=tg.CreatePoint(24,28,20);cam.Target=tg.CreatePoint(1.3,2,1.5);cam.UpVector=tg.CreateUnitVector(0,0,1);cam.Fit()
    cam.SaveAsBitmap(str(ROOT/'native_revision'/'Assembly revised.png'),1600,1200,a.TransientObjects.CreateColor(245,246,248),a.TransientObjects.CreateColor(245,246,248))
    (ROOT/'native_revision'/'validation.json').write_text(json.dumps(report,indent=2))
finally:a.SilentOperation=False
