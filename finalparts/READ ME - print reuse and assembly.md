# Final QArm gripper — native Inventor revision, November 10, 2026

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
