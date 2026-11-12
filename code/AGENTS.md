# Accepted project feedback for future code edits

## Mandatory product list contract

- Use the parameter name `product_list` for the list passed to `pack_products` and `complete_order`.
- It must be a two-dimensional Python list. Every inner list contains exactly a product name and a numeric price, in that order: `[[name, price], ...]`.
- Preserve this structure between product lookup, packing and invoicing. Repeated valid names represent multiple requested units.

## Invalid scanned items

- A supplied barcode contains an incorrect or inapplicable item, such as Labubu.
- Build a reference list of valid names from the official products.csv catalogue. Validate membership rather than hardcoding a check for Labubu. Sample names are for demo mode only.
- lookup_products must warn about and skip missing catalogue entries, while keeping the valid items from the same scan.
- During packing, check each entry against the reference list before commanding the arm. Warn and skip an invalid product. Do not attempt a pickup or charge for it.
- Keep the invoice consistent with the validated packing list. The revised flowchart removes invalid entries from the shared product_list in place, retaining the required None return from pack_products. If all entries are removed, complete_order must avoid recording an empty order.
- When removing an entry while iterating by index, retain the current index so the next shifted entry is checked. Increment the index after handling a valid entry.
- Catalogue membership and pickup-coordinate availability are different checks. A missing coordinate is a lab setup issue, not proof that a catalogue product does not exist.

## Current implementation status

The Python file now implements the per-entry catalogue check and shared-list removal. It also accepts the supplied space-separated barcodes, offers manual entry in lab mode, and captures calibration positions inside the existing main function. Preserve these behaviors and test mixed valid/invalid scans, Labubu, adjacent invalid entries, all-invalid scans, repeated valid products, and calibration without commanded movement. README.md documents the current setup; the existing flowchart PDF predates the added calibration and manual-entry branches.

## Course constraints

Use the user's introductory course topics: variables, conditionals, loops, strings, lists, functions, dictionaries, and basic file operations. The project supplies bcrypt password examples and Q-Arm methods. Use measured lab coordinates and the supplied catalogue when available.
