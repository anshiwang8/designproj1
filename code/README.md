# Mon-51 warehouse ordering

Run `python Mon-51code.py` from this folder. The program keeps the existing
functions and the required `product_list` format: `[[name, price], ...]`.
It uses introductory Python topics and the supplied Q-Arm methods.

## Laptop practice

Leave `DEMO = True` and `CALIBRATE = False`. Create a practice account and type
`widget gear widget` or `widget,gear,widget`. Demo mode uses only sample names
and prices, simulates packing, and writes `demo_users.csv` and `demo_orders.csv`.
The lab barcode names are not added to this sample catalogue as invented stock.

## Connect the scanner and arm

Use the course's Q-Arm Python template on the lab computer to supply the
connection/setup lines defining `arm` and `scan_barcode` in the marked setup
section. Put the official `products.csv` in this folder and set `DEMO = False`.
The supplied template and official catalogue are not included in this repository;
the program cannot run physical orders until those lab inputs are supplied.
Catalogue rows must contain a product name then its numeric price, with an
optional `name,price` heading. Use the official names and prices without guessing.

For each order, choose `s` to call the supplied `scan_barcode()` or `m` to type
names. Both routes use the same lookup, packing, and invoicing pipeline.

All six Code 128 barcodes in the supplied photo were decoded. They contain:

```text
Sponge
Sponge Bottle
Sponge Bottle Rook
Sponge Bottle Rook WitchHat
Sponge Bottle D12 Bowl
Sponge Bottle Labubu Bowl
```

Some contain trailing whitespace/newlines. `lookup_products` accepts these
space-separated names and comma-separated manual orders, ignoring surrounding
whitespace and letter case. For multiple catalogue names containing spaces,
separate the names with commas. A single complete catalogue name is also accepted.
Use `WitchHat` as encoded, unless the official catalogue has a different spelling;
there are no guessed aliases.

## Calibrate in the code

1. With the supplied lab connection set up and `DEMO = False`, set
   `CALIBRATE = True` near the top of `Mon-51code.py` and run the program.
2. Enter the official catalogue names whose tray positions you want to measure.
   Calibration runs inside the existing `main()` and exits without login,
   packing, or writing an order.
3. Use the lab controls to move the open gripper to each requested waypoint.
   Stop the arm, then press Enter. The code calls `arm.get_arm_position()` and
   records XYZ in metres. It does not command calibration movements. Capture
   the position above each item, its pickup position, the position above the
   shipping bin, and the release position in the bin.
4. Copy the printed `PICKUPS`, `ABOVE_BIN`, and `IN_BIN` assignments into the
   marked setup section, replacing the empty values. Capture all items you
   intend to use; each calibration output replaces the whole pickup dictionary.
5. Measure the signed **motor-shaft** rotation from the known open gripper to a
   suitable grip using the course controls. Enter it as `CLOSE_DEGREES` in that
   section. Positive or negative rotation may close your particular mechanism.
   Opening uses its negative. Account for your gearing and mechanical travel;
   no unmeasured closing angle is provided. The present program uses one tested
   closing angle for all items.
6. Restore the gripper to that same known open state and set `CALIBRATE = False`.
   Check the complete paths with lab supervision before running physical orders.

The interface guide specifies relative joint rotations with these ranges:
base ±170°, shoulder ±85°, elbow −95° to +75°, wrist ±160°. End-effector motor
travel depends on the gripper design. `arm.home()` resets the arm joints but
**does not reset the gripper**. The code keeps two-second pauses between packing
commands. Recorded XYZ values and height checks do not establish that a path
is collision-free or within joint limits; verify the actual paths in the lab.
Recalibrate after changing the gripper or moving the arm base, tray, or bin.

## Unavailable items and packing

`lookup_products` warns `Unavailable product; skipping: ...` for names absent
from the official catalogue and keeps valid items from the same barcode.
`pack_products` independently builds a valid-name reference from that catalogue,
checks every entry, and removes invalid entries from the same `product_list`
in place. Adjacent invalid entries are all checked. The function returns `None`.
Only the remaining packed entries reach the invoice; an empty list creates no
order record. Labubu has no special hardcoded rule: catalogue membership decides.

A valid product without measured pickup positions is a **calibration issue**.
Missing positions, unset bin positions, an unset closing angle, or approach
positions that are not higher than contact positions stop the entire order
before any movement or invoice.

Each name has one pickup slot. Repeated names request multiple units. In lab
mode, the program asks you to refill that slot before picking another unit of
the same product within an order. Answering no cancels the remaining units and
invoices only those already packed. Refill all used slots between orders, and
start each run with stocked slots. The arm has no stock or grip sensor in this
program; catalogue availability does not detect a physically empty slot.

Lab accounts and orders use `users.csv` and `orders.csv`. The existing adjustable
13% tax assumption and discount behavior are preserved.
