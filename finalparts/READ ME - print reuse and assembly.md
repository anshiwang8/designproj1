# Final QArm gripper — manufacturing and assembly pack

Open **Final QArm Gripper.iam** in Inventor. All of its references are within this folder. The saved padded jaw opening is 75 mm, allowing approach to a nominal 70 mm object. This assembly uses the small gripper motor output shaft.

## Reuse these printed parts

These files are byte-for-byte identical to the corresponding files in the parent project folder. Do not reprint them if your existing prints match these exact versions and are sound.

| Unchanged file | Quantity in assembly |
|---|---:|
| `LowerFollowerLink.ipt` | 2 |
| `LowerPivotSpacer.ipt` | 2 |
| `UpperPivotSpacer.ipt` | 4 |
| `P1-02 Design Study Structural Pillar.ipt` | 3 |
| `Update 1.2 Left Finger and Pad Carrier.ipt` | 1 |
| `Update 1.2 Right Finger and Pad Carrier.ipt` | 1 |

`P4-05 Foam contact pad.ipt` is also unchanged (two pads); cut soft foam, not rigid plastic. The original supplied platform files in `ReferencePlatform` are unchanged and are reference hardware, not parts to print. The `1.2 LowerPivotSpacer.ipt` variant is **not** used here; this assembly uses the unchanged `LowerPivotSpacer.ipt` listed above.

## Print these revised parts

| Revised file | Quantity | Change |
|---|---:|---|
| `Update 1.2 Uppercrankline and Left Driven Gears.ipt` | 1 | Cap reduced from 28 to 25.5 mm to prevent collision; 1.25 mm 45 degree tooth transition; exposed face 2.5 mm chamfer |
| `Update 1.2 Uppercrankline and Right Driven Gears.ipt` | 1 | Cap reduced from 28 to 25.5 mm to prevent collision; 1.25 mm 45 degree tooth transition; exposed face 2.5 mm chamfer |
| `P1-01_Lower_Mounting_Frame.ipt` | 1 | Four blind axle pockets replaced with M3 clearance through holes and captive M3 nuts. Original platform mount coordinates retained verified against supplied platform; maximum centre error 0.000030 mm. |
| `P4-04 Upper axle-support plate.ipt` | 1 | Blind axle pockets replaced with M3 clearance through holes; four 6.6 mm tool-access holes over platform mounting screws. |
| `P2-01 Input pinion 18 teeth.ipt` | 1 | M2 radial pilot replaced by 2.5 mm M3 tapping pilot at Z=2 mm. Tap M3 x 0.5 after printing. 45 degree teardrop roof in print orientation. |

There are **11 unique printed part designs, 18 printed pieces total**. Only the five designs above require replacement of existing prints. `Print STLs` contains one STL per design, in millimetres, already oriented with its intended bed face at Z=0. Use the quantities in `PRINT AND REUSE.csv`; the STL files contain one piece each.

The two crank/gear caps are 25.5 mm diameter because 28 mm caps collide at the 26 mm shaft spacing. Each has a 2.5 mm exposed-face chamfer and a 1.25 mm, 45° gear-rim transition. The remaining full tooth face is 3.75 mm. Print crank-face down. Print the lower frame with its nut pockets upward, pinion with its full gear face down, and the other parts on the flat faces specified in the CSV. Do not auto-orient the supplied STLs onto a different face.

## M3 fasteners and rotating joints

All new gripper screw connections use M3 hardware. Clearance holes are 3.4 mm, not 3.0 mm. The pinion has a 2.5 mm pilot that must be tapped **M3 x 0.5**; its teardrop roof is oriented for support-free printing. It opens into the motor bore, rather than crossing the opposite hub wall. The 3.3 mm D-shaped motor bore is unchanged.

The 4.3 mm holes in the moving links and spacers are **bearing bores** for 4 mm OD metal sleeves. M3 bolts pass through the sleeves' 3.2 mm bores. This retains the existing printed parts and lets the bolts clamp the metal sleeves instead of clamping the links. The former solid `MetalAxle.ipt` rods are not used. Do not print the sleeves, screws, nuts, or motor reference parts. Full added hardware quantities are in `HARDWARE.csv`; factory platform hardware is additional and stays in place.

Fixed-axis sleeves are 14 mm long between the frame and upper plate. Four M3 x 20 bolts pass down through the upper plate and sleeves into captive nuts in the lower frame. The three pillar joints use the same bolt and captive nut arrangement. The original pillar nut pockets have a different hex orientation; the assembly now matches both pocket orientations.

Each finger pivot uses a 13 mm sleeve and an M3 x 20 bolt. In the CAD frame's Z direction: bolt head below, 0.5 mm washer, link, finger, 0.5 mm washer, then M3 nyloc nut. The sleeve spans Z=9 to 22 mm, leaving axial running clearance around the 12 mm combined link/finger thickness. Tighten against the sleeve; confirm the link and finger still rotate freely. Sleeve ends must be square and deburred.

## Assembly order

1. Clean the printed holes and remove any first-layer bulge. Check a 4 mm sleeve turns/slides freely in the 4.3 mm bearing bores and M3 bolts pass through the 3.4 mm holes. Tap the pinion pilot M3 x 0.5 before fitting it to the motor.
2. Fit the seven captive M3 nuts into the lower frame. Mount the frame to the platform with four M3 x 10 countersunk screws, washers, and nuts. The mounting pattern is 49 x 49 mm at (-14,-21), (35,-21), (-14,28), (35,28) relative to the motor axis. The upper plate has four access holes over these fasteners.
3. Fit the three 14 mm pillars and four fixed-axis sleeves. Fit the lower follower spacers, integrated crank/gears, follower links, and four upper spacers in the positions shown in the assembly.
4. Fit the pinion to the motor D-shaft and secure its M3 set screw against the flat. Index both gears and cranks to the saved 75 mm pose before tightening. The supplied motor shaft is represented as a separate rotating component, aligned to the pinion D-bore.
5. Fit the fingers with the four 13 mm sleeve/bolt/washer/nyloc joints. Bond the foam pads to the integrated carriers.
6. Fit the upper support plate and seven M3 x 20 frame/pillar bolts. Turn the mechanism gently by hand before motor operation. The top plate must clamp the fixed sleeves and pillars while the gears and links remain free.
7. Set the motor/controller's travel to the checked 15–75 mm jaw-opening range. The CAD drive parameter is `JawOpening` in millimetres; it drives the crank angle and both gear ratios. Controller limits and force control are not supplied by an Inventor assembly, and there are no new physical end stops.

## Verification performed

- 73 top-level occurrences and 214 healthy native Inventor constraints; the lower frame is the fixed reference.
- Measured pad opening matches 15, 20, 30, 40, 50, 60, 70, and 75 mm to within 0.001 mm. Counter-rotation and the 26:18 input ratio were checked at each pose.
- No unintended interference involving the gripper at those eight poses. The simplified M3 set-screw envelope overlaps the untapped pilot as expected for thread engagement. Existing overlaps inside the supplied platform's connectors/case reference geometry are reported separately in `validation.json`.
- Every printed design is a single closed solid with healthy features. Faceted geometry has no downward-facing area below a 44° support-angle threshold away from the bed in the exported orientation. This is a CAD geometry check, not a slicer or printer trial.
- Nine clear rays per tested screw/bearing bore (centre plus eight near the wall) confirm the mounting/frame/plate/link/spacer bores run through. The supplied platform mounting centres match within 0.000030 mm.
- All assembly references resolve inside `finalparts`. Reuse files and all original platform files were checked by SHA-256.

The `End Effector Platform - rotating shaft reference.iam` and `N20 stationary motor reference.ipt` are assembly-only reference derivatives: they separate the original motor's output shaft for correct animation. They do not describe modifications to the real platform. The complete original `End Effector Platform.iam` remains alongside them unchanged.

**Physical fit, grip force, durability, and support-free print quality still require a real print and bench test.** Printer calibration, material, layer settings, foam compression, and motor torque have not been measured. The selected tolerances are designed clearances, not a guarantee of your printer's finished dimensions.
