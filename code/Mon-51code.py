# ENG 1P13 | Mon-51 | Warehouse orders
# Run from the folder containing this file. For a laptop scan, try: widget,gear,widget
import random
import time
import bcrypt  # The project gives us the two password-hashing commands.

DEMO = True
CALIBRATE = False  # True: capture measured positions in main(), then exit.
TAX_PERCENT = 13  # Assumption: the brief asks for tax without giving a rate.

# Lab setup: use the course template's setup lines here to create arm and
# scan_barcode. Put products.csv in the working folder, then set DEMO to False.
# CALIBRATION (also see README.md):
# 1. Add the supplied lab setup above this section; set DEMO = False.
# 2. Put the official products.csv beside this file. Set CALIBRATE = True.
# 3. Run the file from this folder. Use the lab's controls to position the
#    arm at each requested waypoint, stop, then press Enter to read XYZ.
#    This mode reads positions only; it does not move the arm for you.
# 4. Copy the printed PICKUPS, ABOVE_BIN and IN_BIN assignments here.
# 5. From a known open gripper, measure a suitable signed MOTOR-SHAFT
#    rotation to grip the items. Set CLOSE_DEGREES below to that value.
#    arm.home() does NOT reset the gripper. Restore the known open state
#    before every run. Opening during packing reverses CLOSE_DEGREES.
# 6. Set CALIBRATE = False. Test the measured paths in the lab before orders.
#    Recalibrate after moving the tray, bin, arm base or changing the gripper.
# Keep the documented joint ranges: base +/-170, shoulder +/-85,
# elbow -95 to +75, wrist +/-160 degrees. Gripper travel is design-specific.
# Never substitute example coordinates for measurements in metres.
# PICKUPS uses a lowercase product name as its key. Its value is a list:
# [position above the item, position at the item]. Each position is [x, y, z].
PICKUPS = {}
ABOVE_BIN = []
IN_BIN = []
CLOSE_DEGREES = 0  # Measured motor rotation from open to closed. Start open.

if DEMO:
    USERS = "demo_users.csv"
    ORDERS = "demo_orders.csv"
else:
    USERS = "users.csv"
    ORDERS = "orders.csv"


def read_rows(filename, mode="r"):
    # For users and orders, "a+" creates an empty file on the first run.
    # seek(0) starts reading at the first line. Each line becomes a list.
    rows = []
    with open(filename, mode, encoding="utf-8-sig") as data_file:
        data_file.seek(0)
        for line in data_file:
            if line.strip() != "":
                rows.append(line.strip().split(","))
    return rows


def ask_yes_no(question):
    answer = input(question + " (y/n): ").strip().lower()
    while answer not in ["y", "yes", "n", "no"]:
        answer = input("Please enter y or n: ").strip().lower()
    return answer in ["y", "yes"]


def valid_password(password):
    upper = False
    lower = False
    digit = False
    symbol = False
    for character in password:
        if character.isupper():
            upper = True
        elif character.islower():
            lower = True
        elif character.isdigit():
            digit = True
        elif character in "!.@#$%^&*()_[]":
            symbol = True
    # bcrypt accepts at most 72 bytes.
    return (len(password) >= 6 and len(password.encode("utf-8")) <= 72
            and upper and lower and digit and symbol)


def sign_up():
    existing_ids = []
    for row in read_rows(USERS, "a+"):
        existing_ids.append(row[0])

    userid = input("Choose a user ID: ").strip()
    while userid == "" or "," in userid or userid in existing_ids:
        userid = input("Choose an unused, nonempty ID without a comma: ").strip()

    print("Use a practice password. It will be visible while you type.")
    password = input("Choose a password: ")
    while not valid_password(password):
        print("Use 6 or more characters with uppercase, lowercase, a digit")
        print("and one of !.@#$%^&*()_[]. Maximum length: 72 UTF-8 bytes.")
        password = input("Choose a password: ")

    # From the project brief: save a bcrypt hash in place of the password.
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    with open(USERS, "a", encoding="utf-8") as users_file:
        users_file.write(userid + "," + password_hash.decode("utf-8") + "\n")
    print("Account created. You can now sign in.")


def authenticate():
    if not ask_yes_no("Do you have an account?"):
        sign_up()

    accounts = read_rows(USERS, "a+")
    while True:
        userid = input("User ID: ").strip()
        password = input("Practice password (visible): ").encode("utf-8")
        for row in accounts:
            if userid == row[0] and len(password) <= 72:
                if bcrypt.checkpw(password, row[1].encode("utf-8")):
                    print("Signed in as", userid)
                    return userid
        print("User ID or password did not match. Try again.")


def read_scan():
    if DEMO:
        return input("Type product names separated by commas or spaces: ")
    method = input("Enter s to scan a barcode or m to type an order: ").strip().lower()
    while method not in ["s", "m"]:
        method = input("Please enter s or m: ").strip().lower()
    if method == "m":
        return input("Type product names separated by commas or spaces: ")
    return scan_barcode()  # Provided by the Q-Arm template.


def lookup_products(products):
    if DEMO:
        catalogue = [["widget", 4.00], ["gear", 6.00], ["block", 2.50]]
    else:
        catalogue = []
        for row in read_rows("products.csv"):
            if row[1].strip().lower() != "price":  # Skip the heading, if present.
                catalogue.append([row[0].strip(), float(row[1])])

    # The supplied barcodes contain SPACE-separated names and trailing newlines.
    # Commas also allow manual entry of catalogue names containing spaces.
    entries = products.split(",")
    if "," not in products:
        whole_name = False
        for item in catalogue:
            if products.strip().lower() == item[0].lower():
                whole_name = True
        if not whole_name:
            entries = products.split()

    matches = []
    for entry in entries:
        name = entry.strip().lower()
        if name != "":
            found = False
            for item in catalogue:
                if name == item[0].lower() and not found:
                    matches.append([item[0], item[1]])
                    found = True
            if not found:
                print("Unavailable product; skipping:", entry.strip())
    return matches


def can_pack(product_list):
    # Check the whole order before moving the arm or writing a receipt.
    if len(product_list) == 0:
        print("No matching products. No order recorded.")
        return False
    if not DEMO:
        if len(ABOVE_BIN) != 3 or len(IN_BIN) != 3 or CLOSE_DEGREES == 0:
            print("Set both bin positions and the closing angle first.")
            return False
        if ABOVE_BIN[2] <= IN_BIN[2]:
            print("Calibration needed: ABOVE_BIN must be higher than IN_BIN.")
            return False
        for item in product_list:
            name = item[0].lower()
            if name not in PICKUPS:
                print("Calibration needed: missing pickup positions for", item[0])
                return False
            points = PICKUPS[name]
            if len(points) != 2 or len(points[0]) != 3 or len(points[1]) != 3:
                print("Each product needs two measured XYZ positions:", item[0])
                return False
            if points[0][2] <= points[1][2]:
                print("Calibration needed: approach must be above pickup for", item[0])
                return False
    return True


def pack_products(product_list):
    # Recheck catalogue membership even if this function is called directly.
    # A position in PICKUPS does not establish that a product exists.
    valid_names = []
    if DEMO:
        valid_names = ["widget", "gear", "block"]
    else:
        for row in read_rows("products.csv"):
            if row[1].strip().lower() != "price":
                valid_names.append(row[0].strip().lower())

    index = 0
    while index < len(product_list):
        if product_list[index][0].strip().lower() not in valid_names:
            print("Unavailable product; skipping:", product_list[index][0])
            del product_list[index]  # Check the shifted entry at this index next.
        else:
            index += 1

    # No movement or invoicing when the remaining order lacks calibration.
    if not can_pack(product_list):
        product_list[:] = []
        return

    packed_names = []
    index = 0
    while index < len(product_list):
        item = product_list[index]
        name = item[0]
        if DEMO:
            print("Demo: simulated packing of", name)
        else:
            if name.lower() in packed_names:
                if not ask_yes_no("Refill the pickup slot for " + name + ". Ready?"):
                    # Keep only units already packed for the invoice.
                    del product_list[index:]
                    return
            above_item, at_item = PICKUPS[name.lower()]
            arm.set_arm_position(above_item)
            time.sleep(2)
            arm.set_arm_position(at_item)
            time.sleep(2)
            arm.rotate_gripper(CLOSE_DEGREES)
            time.sleep(2)
            arm.set_arm_position(above_item)
            time.sleep(2)
            arm.set_arm_position(ABOVE_BIN)
            time.sleep(2)
            arm.set_arm_position(IN_BIN)
            time.sleep(2)
            arm.rotate_gripper(-CLOSE_DEGREES)
            time.sleep(2)
            arm.set_arm_position(ABOVE_BIN)
            time.sleep(2)
            print("Packing sequence finished for", name)
        packed_names.append(name.lower())
        index += 1


def complete_order(userid, product_list):
    if len(product_list) == 0:
        print("No products to invoice.")
        return
    # Work in cents so prices can be added as whole numbers.
    subtotal = 0
    names = []
    print("\nMON-51 RECEIPT |", userid)
    print("-" * 36)
    for item in product_list:
        subtotal += round(item[1] * 100)
        names.append(item[0])
        print("{:<22} $ {:>10.2f}".format(item[0], item[1]))

    rate = random.randint(5, 50)
    # Adding 50 before integer division rounds half a cent up.
    discount = (subtotal * rate + 50) // 100
    after_discount = subtotal - discount
    tax = (after_discount * TAX_PERCENT + 50) // 100
    total = after_discount + tax

    print("-" * 36)
    print("{:<22} $ {:>10.2f}".format("Subtotal", subtotal / 100))
    print("{:<22} $ {:>10.2f}".format("Discount ({}%)".format(rate), -discount / 100))
    print("{:<22} $ {:>10.2f}".format("Tax ({}%)".format(TAX_PERCENT), tax / 100))
    print("{:<22} $ {:>10.2f}".format("Total", total / 100))

    with open(ORDERS, "a", encoding="utf-8") as orders_file:
        row = [userid, "{:.2f}".format(total / 100)] + names
        orders_file.write(",".join(row) + "\n")

    count = 0
    for row in read_rows(ORDERS):
        if row[0] == userid:
            count += 1
    print("Orders placed so far:", count)


def customer_summary(userid):
    order_count = 0
    spent_cents = 0
    quantities = {}
    for row in read_rows(ORDERS, "a+"):
        if row[0] == userid:
            order_count += 1
            spent_cents += round(float(row[1]) * 100)
            for name in row[2:]:
                if name not in quantities:
                    quantities[name] = 0
                quantities[name] += 1

    print("\nMON-51 CUSTOMER SUMMARY |", userid)
    print("Orders:", order_count)
    print("Total spent: ${:.2f}".format(spent_cents / 100))
    print("-" * 36)
    print("{:<22} {:>12}".format("Product", "Quantity"))
    for name in quantities:
        print("{:<22} {:>12}".format(name, quantities[name]))
    if order_count == 0:
        print("No orders yet.")


def main():
    print("Welcome to the Mon-51 warehouse.")
    if DEMO:
        print("Laptop practice mode. Sample products: widget, gear, block.")
    if CALIBRATE:
        if DEMO:
            print("Calibration needs the supplied lab setup and DEMO = False.")
            return
        print("Calibration reads positions only. Use the lab controls to move.")
        print("Keep the gripper open; stop at each waypoint before pressing Enter.")
        calibration_products = lookup_products(input("Catalogue items to calibrate: "))
        measured_pickups = {}
        for item in calibration_products:
            name = item[0].lower()
            if name not in measured_pickups:
                input("Position ABOVE " + item[0] + "; press Enter when stopped: ")
                point = arm.get_arm_position()
                above_item = [point[0], point[1], point[2]]
                input("Position AT pickup for " + item[0] + "; press Enter when stopped: ")
                point = arm.get_arm_position()
                at_item = [point[0], point[1], point[2]]
                measured_pickups[name] = [above_item, at_item]
        if len(measured_pickups) > 0:
            input("Position ABOVE the shipping bin; press Enter when stopped: ")
            point = arm.get_arm_position()
            above_bin = [point[0], point[1], point[2]]
            input("Position AT release in the bin; press Enter when stopped: ")
            point = arm.get_arm_position()
            in_bin = [point[0], point[1], point[2]]
            print("Copy these assignments into the lab setup section:")
            print("PICKUPS =", measured_pickups)
            print("ABOVE_BIN =", above_bin)
            print("IN_BIN =", in_bin)
            print("Also set the measured CLOSE_DEGREES, then CALIBRATE = False.")
        arm.end_arm_connection()
        return
    userid = authenticate()
    another_order = True
    while another_order:
        scan = read_scan()
        product_list = lookup_products(scan)
        # pack_products validates the whole list before its first movement.
        pack_products(product_list)
        complete_order(userid, product_list)
        if not DEMO:
            print("Before another order, refill every pickup slot used above.")
        another_order = ask_yes_no("Scan another order?")
    customer_summary(userid)
    if not DEMO:
        arm.end_arm_connection()


if __name__ == "__main__":
    main()

