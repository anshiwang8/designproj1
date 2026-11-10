from pathlib import Path
import json,csv,hashlib,shutil
ROOT=Path(__file__).resolve().parents[1]
BACK=ROOT.parent/'finalparts-backup-2026-11-10'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
changes={
 'LowerFollowerLink.ipt':'Thickness reduced from 4 to 3.5 mm; 45 mm pivot spacing and 4.3 mm bearing holes retained.',
 'LowerPivotSpacer.ipt':'Length reduced from 5.5 to 4.5 mm; bearing bore retained.',
 'UpperPivotSpacer.ipt':'Length reduced from 3.5 to 2 mm; bearing bore retained.',
 'P1-02 Design Study Structural Pillar.ipt':'Length reduced from 14 to 11 mm; M3 clearance bore retained.',
 'P4-04 Upper axle-support plate.ipt':'Thickness reduced from 3 to 2 mm; clearance and mounting-tool access holes retained.',
 'P4-05 Foam contact pad.ipt':'Foam dimensions now 28 x 6 x 2 mm; pad occurrences follow bent carriers.',
 **{f'Update 1.2 {s} Finger and Pad Carrier.ipt':'Thickness reduced from 8 to 6 mm; tip and integrated carrier bent upward 45 degrees beyond the pivot holes; flat-to-45-degree underside reinforcement added for printing.' for s in ['Left','Right']},
 **{f'Update 1.2 Uppercrankline and {s} Driven Gears.ipt':'Overall thickness reduced from 9.5 to 8 mm by trimming the crank face. Gear teeth, bearing bores, 45 mm pivot spacing, and 25.5 mm cap envelope retained; remaining exposed-face bevel is 1 mm.' for s in ['Left','Right']},
 'P1-01_Lower_Mounting_Frame.ipt':'Unchanged from the November 3 finalparts package; retain its M3 clearance holes and captive nut pockets.',
 'P2-01 Input pinion 18 teeth.ipt':'Unchanged from the November 3 finalparts package; retain D-bore and M3 tapping pilot.',
}
entries=json.loads((BACK/'parts-manifest.json').read_text())
entries=[e for e in entries if not e['file'].startswith('Hardware/')]
for e in entries:
    name=e['file'];e['changes']=changes[name];e['previous_package_sha256']=sha(BACK/name);e['final_sha256']=sha(ROOT/name)
    e['changed_since_2026_11_03']=e['previous_package_sha256']!=e['final_sha256']
    e['changed']=e['source_sha256']!=e['final_sha256']
    if 'Uppercrankline' in name:e['print_orientation']='Flat trimmed crank face down; native Z=8 on bed'
    if name=='P4-05 Foam contact pad.ipt':e['print_orientation']='Cut 28 x 6 x 2 mm soft foam'
for name,length,qty in [('Pivot sleeve 4OD 3.2ID x11.ipt',11,4),('Pivot sleeve 4OD 3.2ID x10.5.ipt',10.5,4),('M3x16 socket screw.ipt',16,7)]:
    e={'file':'Hardware/'+name,'changed':True,'changes':f'Metal hardware; {length} mm length.','quantity':qty,'print_orientation':'Do not print','category':'Metal hardware','source_sha256':None,'final_sha256':sha(ROOT/'Hardware'/name)}
    entries.append(e)
(ROOT/'parts-manifest.json').write_text(json.dumps(entries,indent=2))
with (ROOT/'PRINT AND REUSE.csv').open('w',newline='',encoding='utf-8-sig') as f:
    writer=csv.writer(f);writer.writerow(['File','Quantity','Action relative to Nov 3 package','Print orientation','Change'])
    for e in entries:
        action='Metal hardware' if e['category']=='Metal hardware' else 'Cut foam; do not rigid-print' if 'foam' in e['file'].lower() else 'REPRINT - revised' if e['changed_since_2026_11_03'] else 'REUSE - unchanged since Nov 3'
        writer.writerow([e['file'],e['quantity'],action,e['print_orientation'],e['changes']])
hardware=[
 ['M3 x 16 socket-head screw',7,'Frame/pillar joints; replaces the former 20 mm frame screws'],
 ['M3 x 20 socket-head screw',4,'Finger pivots'],
 ['M3 x 10 countersunk screw',4,'Platform mounting; unchanged'],
 ['M3 x 4 grub/set screw',1,'Pinion hub; tap pilot M3 x 0.5'],
 ['M3 hex nut; 5.5 mm AF x 2.4 mm',11,'7 captive frame nuts + 4 platform nuts'],
 ['M3 nyloc nut; approx 4 mm high',4,'Finger pivots'],
 ['M3 flat washer; 7 OD / 3.2 ID / 0.5 thick',12,'8 finger pivot washers + 4 platform washers'],
 ['Metal sleeve; 4 OD / 3.2 ID x 11 mm',4,'Fixed gear/follower axes; cut square and deburr'],
 ['Metal sleeve; 4 OD / 3.2 ID x 10.5 mm',4,'Finger/link pivots; cut square and deburr'],
 ['Soft foam; 28 x 6 x 2 mm',2,'Bond to the bent integrated carriers'],
]
with (ROOT/'HARDWARE.csv').open('w',newline='',encoding='utf-8-sig') as f:
    wr=csv.writer(f);wr.writerow(['Item','Quantity','Use']);wr.writerows(hardware)
text='''# Final QArm gripper — native Inventor revision, November 10, 2026

Open **Final QArm Gripper.iam**. The native parts and constrained assembly in this folder have been updated. The saved padded jaw opening is 75 mm. The finger tips and integrated pad carriers now rise 45 degrees relative to the linkage plane, compensating for a 45-degree downward arm pitch in the finger direction. The foam pads follow the bent carriers.

## Revised dimensions

| Part | Previous package | Current |
|---|---:|---:|
| Finger thickness at pivots | 8 mm | 6 mm |
| Follower link thickness | 4 mm | 3.5 mm |
| Lower pivot spacer length | 5.5 mm | 4.5 mm |
| Upper pivot spacer length | 3.5 mm | 2 mm |
| Structural pillar length | 14 mm | 11 mm |
| Upper support plate thickness | 3 mm | 2 mm |
| Integrated crank/gear overall thickness | 9.5 mm | 8 mm |
| Frame screw stack, base underside to upper plate top | 20 mm | 16 mm |
| Foam pad dimensions | 28 x 8 x 2 mm | 28 x 6 x 2 mm |

The lower mounting frame remains 3 mm thick to retain material around its 2.4 mm captive nut pockets. The input pinion is unchanged, preserving the motor D-bore, tooth engagement and set-screw pilot. Gear teeth and pivot centre spacing are unchanged. The bends begin beyond both finger pivots; a small underside web provides a flat-to-45-degree printable transition. These are native trim, bend, and extrusion features on the existing Inventor solids.

## Print and reuse

Relative to the **November 3 finalparts package**, reuse the lower mounting frame and input pinion. Reprint the other **nine printed designs, sixteen pieces**. There are still eleven unique printed designs and eighteen printed pieces in total. Cut two new soft foam pads. Quantities and orientations are in **PRINT AND REUSE.csv**; hardware is in **HARDWARE.csv**.

The eleven files in **Print STLs** were regenerated from the revised native solids, in millimetres, with one piece per STL and its intended bed face at Z=0. Print the fingers on their original flat proximal faces, with the bent tips rising from the bed. Print both crank/gears with the newly trimmed crank faces down (native Z=8 mm). Print the lower frame with its nut pockets upward. Keep the supplied orientations.

## Screws, sleeves and assembly

Use **seven M3 x 16 screws for the frame and pillars**. The frame stack is now 16 mm, and these screws engage the captive nuts without projecting into the platform. The former M3 x 20 frame screws extend into the platform in this thinner assembly. Four M3 x 20 screws remain at the finger pivots.

Use four **11 mm sleeves** on the fixed gear/follower axes, and four **10.5 mm sleeves** at the finger pivots. All sleeves remain 4 mm OD / 3.2 mm ID metal tube, square and deburred. Historical 13 and 14 mm sleeve models remain in Hardware for reference; the revised assembly references the new lengths.

The upper plate underside is at frame Z=14 mm, and its top is at Z=16 mm. Pillars and fixed sleeves run from Z=3 to 14 mm. Upper spacers run from Z=11.5 to 13.5 mm, retaining 0.5 mm clearance below the plate. The gears sit at Z=3.5 mm; their trimmed crank faces end at Z=11.5 mm. Follower links run from Z=8 to 11.5 mm, and finger pivot regions run from Z=12 to 18 mm.

Each finger sleeve runs from Z=8 to 18.5 mm. The lower washer is at Z=7.5–8 mm, the upper washer at Z=18.5–19 mm, and the nyloc nut starts at Z=19 mm. The sleeve provides 0.5 mm total axial running clearance around the 10 mm combined printed link/finger stack. Tighten against the sleeve and confirm free rotation.

Assembly order: fit the captive nuts and mount the lower frame to the supplied platform; fit the new pillars and fixed sleeves; install the pinion, gears, follower links and spacers; assemble the fingers with their sleeves, washers and locking nuts; bond the foam to the angled carriers; then fit the upper plate with the seven 16 mm screws. Tap the unchanged pinion pilot M3 x 0.5 before installation. Align the mechanism to the saved pose before tightening the set screw.

## Verification

The updated assembly has 73 top-level occurrences and 214 healthy constraints. At jaw commands of 15, 20, 30, 40, 50, 60, 70 and 75 mm, the measured foam-face gap matches the command within 0.001 mm, and both pad lengths remain at +45 degrees. No unintended gripper interference was found at those poses. The set-screw/pilot thread-engagement overlap and existing internal overlaps in the supplied platform reference are recorded separately in **validation.json**.

Every printed native design remains one solid with healthy features. Every exported STL is one closed connected mesh. The oriented meshes have no downward-facing area below a 44-degree support-angle threshold away from the bed; this is a geometry check, not a slicer or printer trial. All assembly references remain inside finalparts. The unchanged lower frame, pinion, and original platform files are checked against the backup by SHA-256.

Use Inventor parameter **JawOpening** for the checked 15–75 mm range. Controller travel limits, force control, physical fit, printed strength and print quality still require a bench test. The supplied platform and rotating motor reference remain reference hardware, not printed parts.

The complete pre-revision package is preserved in the sibling folder **finalparts-backup-2026-11-10**. Revision scripts, the original measurements, and detailed verification records are in **native_revision**. The earlier interface report is retained there as historical evidence; current results are in the top-level validation files.
'''
(ROOT/'READ ME - print reuse and assembly.md').write_text(text,encoding='utf-8')
shutil.copy2(BACK/'interface-validation.json',ROOT/'native_revision'/'pre-revision-interface-validation.json')
shutil.copy2(ROOT/'native_revision'/'validation.json',ROOT/'validation.json')
print('Updated manifest, CSVs, assembly notes, and validation report')
