from pathlib import Path
import json,math,shutil
import numpy as np,trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import pythoncom,win32com.client as w
from win32com.client import dynamic
ROOT=Path(__file__).resolve().parents[1]
a=dynamic.Dispatch(pythoncom.GetActiveObject('Inventor.Application').QueryInterface(pythoncom.IID_IDispatch))
def doc(n,asm=False):return w.CastTo(a.Documents.Open(str(ROOT/n),False),'AssemblyDocument' if asm else 'PartDocument')
def mesh(body,tol=.0005):
    nv,nf,verts,normals,faces=body.CalculateFacets(tol)
    m=trimesh.Trimesh(vertices=np.array(verts).reshape(-1,3)*10,faces=np.array(faces).reshape(-1,3)-1,process=True)
    assert m.is_watertight,'Open mesh'
    return m
def matrix(m):
    ar=np.array([[m.Cell(i,j) for j in range(1,5)] for i in range(1,5)]);ar[:3,3]*=10;return ar

report=[];assembly_meshes=[]
a.SilentOperation=True
try:
    for stl in (ROOT/'Print STLs').glob('*.stl'):
        d=doc(stl.stem+'.ipt');m=mesh(d.ComponentDefinition.SurfaceBodies.Item(1))
        if stl.stem in ['LowerFollowerLink','LowerPivotSpacer','UpperPivotSpacer','P1-02 Design Study Structural Pillar']:
            # local Y (thickness axis) becomes print Z.
            mat=np.array([[1,0,0,0],[0,0,-1,0],[0,1,0,0],[0,0,0,1]],dtype=float)
            m.apply_transform(mat)
        elif 'Uppercrankline' in stl.stem or 'Input pinion' in stl.stem or stl.stem=='P1-01_Lower_Mounting_Frame':
            m.apply_transform(np.diag([1,-1,-1,1]))
        m.apply_translation([0,0,-m.bounds[0,2]])
        assert m.is_watertight and m.volume>0
        # Exclude the bed before checking downward-facing triangles.
        offbed=m.triangles.max(axis=1)[:,2]>.02
        unsupported=(m.face_normals[:,2]<-math.cos(math.radians(44))) & offbed
        area=float(m.area_faces[unsupported].sum())
        m.export(stl)
        reloaded=trimesh.load_mesh(stl)
        assert reloaded.is_watertight and len(reloaded.split())==1
        report.append({'file':stl.name,'watertight':bool(reloaded.is_watertight),'components':1,'triangles':len(m.faces),'bounds_mm':m.bounds.tolist(),'volume_mm3':m.volume,'unsupported_area_below_44deg_mm2':area})
        print('EXPORTED',stl.name,'unsupported',round(area,4),flush=True)
    d=doc('Final QArm Gripper.iam',True);cd=d.ComponentDefinition
    # Render the gripper directly from native solid facets without changing any UI view.
    for o in cd.Occurrences:
        if o.Name=='QArm supplied end effector platform':continue
        ocd=w.CastTo(o.Definition,'PartComponentDefinition')
        for b in ocd.SurfaceBodies:
            m=mesh(b,.001);m.apply_transform(matrix(o.Transformation))
            n=o.Name.lower()
            color='#364152' if 'foam' in n else '#b7c0cc' if any(s in n for s in ['bolt','nut','washer','sleeve','shaft','screw']) else '#c69638' if 'pinion' in n else '#50749b' if 'finger' in n else '#658578'
            assembly_meshes.append((o.Name,m,color))
    fig=plt.figure(figsize=(15,8),facecolor='#f5f6f8')
    allpoints=np.vstack([m.vertices for _,m,_ in assembly_meshes]);lo,hi=allpoints.min(0),allpoints.max(0);mid=(lo+hi)/2;span=max(hi-lo)*.55
    for k,(elev,azim,title) in enumerate([(25,-65,'Revised native assembly | 75 mm jaw opening'),(0,0,'Side view | finger tips and carriers rise 45°')],1):
        ax=fig.add_subplot(1,2,k,projection='3d',computed_zorder=True);ax.set_facecolor('#f5f6f8')
        for name,m,col in assembly_meshes:
            poly=Poly3DCollection(m.triangles,facecolors=col,edgecolors=col,linewidths=.05,antialiased=False,shade=True,lightsource=matplotlib.colors.LightSource(azdeg=130,altdeg=55))
            ax.add_collection3d(poly)
        ax.set_xlim(mid[0]-span,mid[0]+span);ax.set_ylim(mid[1]-span,mid[1]+span);ax.set_zlim(mid[2]-span,mid[2]+span)
        ax.set_box_aspect((1,1,1));ax.view_init(elev=elev,azim=azim);ax.set_axis_off()
        fig.text(.25 if k==1 else .75,.91,title,ha='center',fontsize=12,color='#1b2533')
    fig.text(.5,.06,'6 mm fingers · 3.5 mm follower links · 2 mm upper plate · 16 mm frame stack',ha='center',fontsize=12,color='#364152')
    fig.tight_layout(rect=(0,.06,1,1));fig.savefig(ROOT/'Assembly preview.png',dpi=150,facecolor=fig.get_facecolor());plt.close(fig)
    (ROOT/'native_revision'/'mesh-validation.json').write_text(json.dumps(report,indent=2))
    # Restore historical copies which Inventor automatically rotated out while saving.
    backup=ROOT.parent/'finalparts-backup-2026-11-10'
    for p in (backup/'OldVersions').iterdir():
        target=ROOT/'OldVersions'/p.name
        if not target.exists():shutil.copy2(p,target)
finally:a.SilentOperation=False
