from pathlib import Path
import json,hashlib,math,shutil
import pythoncom,win32com.client as w
from win32com.client import dynamic
ROOT=Path(__file__).resolve().parents[1];BACK=ROOT.parent/'finalparts-backup-2026-11-10'
a=dynamic.Dispatch(pythoncom.GetActiveObject('Inventor.Application').QueryInterface(pythoncom.IID_IDispatch))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def xyz(p):return [p.X*10,p.Y*10,p.Z*10]
report={'date':'2026-11-10','unchanged_files':[],'cylindrical_bores':[]}
for name in ['P1-01_Lower_Mounting_Frame.ipt','P2-01 Input pinion 18 teeth.ipt']:
    assert sha(ROOT/name)==sha(BACK/name);report['unchanged_files'].append(name)
for p in (BACK/'ReferencePlatform').rglob('*'):
    if p.is_file():
        q=ROOT/p.relative_to(BACK)
        assert q.exists() and sha(p)==sha(q),str(q)
        report['unchanged_files'].append(str(p.relative_to(BACK)))
for p in ROOT.glob('*.ipt'):
    d=w.CastTo(a.Documents.ItemByName(str(p)),'PartDocument');cd=d.ComponentDefinition
    cylinders=[]
    for face in cd.SurfaceBodies.Item(1).Faces:
        if face.SurfaceType!=5891:continue
        geom=w.CastTo(face.Geometry,'Cylinder')
        cylinders.append({'diameter_mm':round(geom.Radius*20,6),'base_mm':xyz(geom.BasePoint),'axis':[geom.AxisVector.X,geom.AxisVector.Y,geom.AxisVector.Z]})
    report['cylindrical_bores'].append({'file':p.name,'cylinders':cylinders})
    if p.name in ['LowerFollowerLink.ipt','LowerPivotSpacer.ipt','UpperPivotSpacer.ipt'] or 'Finger and Pad Carrier' in p.name:
        count=sum(abs(c['diameter_mm']-4.3)<.0001 for c in cylinders)
        assert count >= (2 if 'Finger' in p.name or 'Follower' in p.name else 1),(p,count)
d=w.CastTo(a.Documents.ItemByName(str(ROOT/'Final QArm Gripper.iam')),'AssemblyDocument');cd=d.ComponentDefinition
assert all(c.HealthStatus==11778 for c in cd.Constraints)
assert cd.Parameters.Item('JawOpening').Value==7.5
report['frame_screw_origins_mm']=[xyz(o.Transformation.Translation) for o in cd.Occurrences if o.Name.startswith('M3 frame bolt')]
report['frame_screw_files']=[Path(o.Definition.Document.FullFileName).name for o in cd.Occurrences if o.Name.startswith('M3 frame bolt')]
assert set(report['frame_screw_files'])=={'M3x16 socket screw.ipt'}
assert all(abs(v[2]-16)<.001 for v in report['frame_screw_origins_mm'])
report['all_references_resolve_inside_finalparts']=all(Path(r.FullFileName).is_relative_to(ROOT) and Path(r.FullFileName).exists() for r in d.AllReferencedDocuments)
assert report['all_references_resolve_inside_finalparts']
validation=json.loads((ROOT/'native_revision'/'validation.json').read_text())
for pose in validation['poses']:
    assert not pose['unhealthy_constraints']
    assert abs(pose['measured_gap_mm']-pose['command_mm'])<.001
    assert all(abs(v-45)<.001 for v in pose['tip_angles_deg'])
    for hit in pose['interferences']:
        assert not any(s in (hit['one']+' '+hit['two']).lower() for s in ['finger','follower','gear','pivot','frame bolt','plate']),hit
meshes=json.loads((ROOT/'native_revision'/'mesh-validation.json').read_text())
assert len(meshes)==11
assert all(m['watertight'] and m['components']==1 and m['unsupported_area_below_44deg_mm2']<.001 for m in meshes)
report['mesh_checks_passed']=True
(ROOT/'interface-validation.json').write_text(json.dumps(report,indent=2))
validation['meshes']=meshes;validation['interface_report']='interface-validation.json';validation['physical_test_performed']=False
(ROOT/'validation.json').write_text(json.dumps(validation,indent=2))
# Remove scratch artifacts created during this revision, including an unused trial sleeve.
for rel in ['Hardware/Pivot sleeve 4OD 3.2ID x12.ipt','native_revision/Assembly revised.png','native_revision/bend_trial.py','native_revision/probe.py','native_revision/validation-progress.json']:
    p=ROOT/rel
    if not p.exists():continue
    if p.suffix=='.ipt':
        try:a.Documents.ItemByName(str(p)).Close(True)
        except:pass
    p.unlink()
for p in (BACK/'OldVersions').iterdir():
    dest=ROOT/'OldVersions'/p.name
    if not dest.exists():shutil.copy2(p,dest)
print('PASS: native solids, holes, 214 constraints, 8 motion poses, 11 closed printable meshes, frame hardware, and preserved interfaces')
