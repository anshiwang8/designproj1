from pathlib import Path
import json
import win32com.client
import pythoncom
from win32com.client import dynamic

ROOT = Path(__file__).resolve().parents[1]
app = dynamic.Dispatch(pythoncom.GetActiveObject('Inventor.Application').QueryInterface(pythoncom.IID_IDispatch))
app.SilentOperation = True

def xyz(p): return [round(p.X*10,6),round(p.Y*10,6),round(p.Z*10,6)]

def inspect(doc):
    doc=win32com.client.CastTo(doc,'PartDocument' if doc.DocumentType==12290 else 'AssemblyDocument')
    cd=doc.ComponentDefinition
    out={'file':doc.FullFileName,'type':doc.DocumentType}
    if doc.DocumentType==12290:
        out['bounds']=[xyz(cd.RangeBox.MinPoint),xyz(cd.RangeBox.MaxPoint)]
        out['features']=[{'name':f.Name,'type':f.Type,'health':f.HealthStatus} for f in cd.Features]
        out['parameters']=[{'name':p.Name,'expression':p.Expression,'value':p.Value} for p in cd.Parameters]
        out['sketches']=[]
        for s in cd.Sketches:
            sk={'name':s.Name,'entities':s.SketchEntities.Count}
            sk['lines']=[{'start':xyz(l.StartSketchPoint.Geometry3d),'end':xyz(l.EndSketchPoint.Geometry3d)} for l in s.SketchLines if l.StartSketchPoint and l.EndSketchPoint]
            out['sketches'].append(sk)
    else:
        out['parameters']=[{'name':p.Name,'expression':p.Expression,'value':p.Value} for p in cd.Parameters]
        out['occurrences']=[]
        for o in cd.Occurrences:
            out['occurrences'].append({'name':o.Name,'file':o.Definition.Document.FullFileName,'matrix':[o.Transformation.Cell(i,j) for i in range(1,5) for j in range(1,5)],'grounded':o.Grounded})
        out['constraints']=[]
        for c in cd.Constraints:
            d={'name':c.Name,'type':c.Type,'health':c.HealthStatus}
            for key in ['Offset','Angle','Ratio']:
                try:
                    v=getattr(c,key);d[key]=v.Expression if hasattr(v,'Expression') else v
                except Exception:pass
            for key in ['OccurrenceOne','OccurrenceTwo']:
                try:d[key]=getattr(c,key).Name
                except Exception:pass
            out['constraints'].append(d)
    return out

result=[]
try:
    for p in [*ROOT.glob('*.ipt'),ROOT/'Final QArm Gripper.iam']:
        print('Inspecting',p.name,flush=True)
        doc=app.Documents.Open(str(p),False)
        result.append(inspect(doc))
    (ROOT/'native_revision'/'before.json').write_text(json.dumps(result,indent=2))
finally:
    app.SilentOperation=False
