import random
import time
import bcrypt

DEMO = True
TAX = 0.13

PICKUPS = {
    "item1": [[0, 0, 0], [0, 0, 0]],
    "item2": [[0, 0, 0], [0, 0, 0]],
    "item3": [[0, 0, 0], [0, 0, 0]],
    "item4": [[0, 0, 0], [0, 0, 0]],
    "item5": [[0, 0, 0], [0, 0, 0]],
    "item6": [[0, 0, 0], [0, 0, 0]],
}
ABOVE_BIN = [0, 0, 0]
IN_BIN = [0, 0, 0]
CLOSE_DEGREES = 0

if DEMO:
    USERS = "demo_users.csv"
    ORDERS = "demo_orders.csv"
else:
    USERS = "users.csv"
    ORDERS = "orders.csv"


def readRows(fileName, mode="r"):
    rows = []
    with open(fileName, mode) as dataFile:
        dataFile.seek(0)
        for line in dataFile:
            if line.strip() != "":
                rows.append(line.strip().split(","))
    return rows


def readCatalogue():
    if DEMO:
        return [["widget", 4.00], ["gear", 6.00], ["block", 2.50]]
    catalogue = []
    for row in readRows("products.csv"):
        if row[1].strip().lower() != "price":
            catalogue.append([row[0].strip(), float(row[1])])
    return catalogue


def askYesNo(question):
    answer = input(question + " (y/n): ").strip().lower()
    while answer != "y" and answer != "n":
        answer = input("Enter y or n: ").strip().lower()
    return answer == "y"


def validPassword(password):
    hasUpper = False
    hasLower = False
    hasDigit = False
    hasSymbol = False
    for char in password:
        if char.isupper():
            hasUpper = True
        elif char.islower():
            hasLower = True
        elif char.isdigit():
            hasDigit = True
        elif char in "!.@#$%^&*()_[]":
            hasSymbol = True
    return len(password) >= 6 and hasUpper and hasLower and hasDigit and hasSymbol


def signUp():
    existingIds = []
    for row in readRows(USERS, "a+"):
        existingIds.append(row[0])

    userId = input("Choose a user ID: ").strip()
    while userId == "" or "," in userId or userId in existingIds:
        userId = input("That ID can't be used, pick another: ").strip()

    password = input("Choose a password: ")
    while not validPassword(password):
        print("Password needs 6+ characters, an uppercase, a lowercase, a digit")
        print("and one of !.@#$%^&*()_[]")
        password = input("Choose a password: ")

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    with open(USERS, "a") as usersFile:
        usersFile.write(userId + "," + hashed.decode("utf-8") + "\n")
    print("Account created.")


def authenticate():
    if not askYesNo("Do you have an account?"):
        signUp()

    accounts = readRows(USERS, "a+")
    while True:
        userId = input("User ID: ").strip()
        password = input("Password: ").encode("utf-8")
        for row in accounts:
            if row[0] == userId and bcrypt.checkpw(password, row[1].encode("utf-8")):
                print("Signed in as", userId)
                return userId
        print("Wrong user ID or password.")


def readScan():
    if DEMO:
        return input("Enter products: ")
    method = input("Scan (s) or type (m) the order: ").strip().lower()
    while method != "s" and method != "m":
        method = input("Enter s or m: ").strip().lower()
    if method == "m":
        return input("Enter products: ")
    return scan_barcode()


def lookupProducts(products):
    catalogue = readCatalogue()

    if "," in products:
        entries = products.split(",")
    else:
        entries = products.split()

    matches = []
    for entry in entries:
        name = entry.strip().lower()
        if name == "":
            continue
        found = False
        for item in catalogue:
            if item[0].lower() == name:
                matches.append([item[0], item[1]])
                found = True
                break
        if not found:
            print(entry.strip(), "is not in the catalogue, skipping")
    return matches


def canPack(product_list):
    if len(product_list) == 0:
        print("No valid products in this order.")
        return False
    if DEMO:
        return True
    if len(ABOVE_BIN) != 3 or len(IN_BIN) != 3 or CLOSE_DEGREES == 0:
        print("Bin positions or gripper angle not set.")
        return False
    for item in product_list:
        if item[0].lower() not in PICKUPS:
            print("No pickup position for", item[0])
            return False
    return True


def moveTo(position):
    arm.set_arm_position(position)
    time.sleep(2)


def packProducts(product_list):
    validNames = []
    for item in readCatalogue():
        validNames.append(item[0].lower())

    i = 0
    while i < len(product_list):
        if product_list[i][0].lower() not in validNames:
            print(product_list[i][0], "is not in the catalogue, skipping")
            del product_list[i]
        else:
            i += 1

    if not canPack(product_list):
        product_list.clear()
        return

    packed = []
    i = 0
    while i < len(product_list):
        name = product_list[i][0]
        if DEMO:
            print("Packing", name)
        else:
            if name.lower() in packed:
                if not askYesNo("Refill " + name + " slot. Ready?"):
                    del product_list[i:]
                    return
            aboveItem = PICKUPS[name.lower()][0]
            atItem = PICKUPS[name.lower()][1]
            moveTo(aboveItem)
            moveTo(atItem)
            arm.rotate_gripper(CLOSE_DEGREES)
            time.sleep(2)
            moveTo(aboveItem)
            moveTo(ABOVE_BIN)
            moveTo(IN_BIN)
            arm.rotate_gripper(-CLOSE_DEGREES)
            time.sleep(2)
            moveTo(ABOVE_BIN)
            print("Packed", name)
        packed.append(name.lower())
        i += 1


def completeOrder(userId, product_list):
    if len(product_list) == 0:
        return

    subtotal = 0
    names = []
    print("\nMON-51 RECEIPT -", userId)
    print("-" * 36)
    for item in product_list:
        subtotal += item[1]
        names.append(item[0])
        print("{:<22} ${:>10.2f}".format(item[0], item[1]))

    discountPercent = random.randint(5, 50)
    discount = round(subtotal * discountPercent / 100, 2)
    tax = round((subtotal - discount) * TAX, 2)
    total = round(subtotal - discount + tax, 2)

    print("-" * 36)
    print("{:<22} ${:>10.2f}".format("Subtotal", subtotal))
    print("{:<22} ${:>10.2f}".format("Discount " + str(discountPercent) + "%", -discount))
    print("{:<22} ${:>10.2f}".format("Tax", tax))
    print("{:<22} ${:>10.2f}".format("Total", total))

    with open(ORDERS, "a") as ordersFile:
        ordersFile.write(userId + "," + "{:.2f}".format(total) + "," + ",".join(names) + "\n")

    orderCount = 0
    for row in readRows(ORDERS):
        if row[0] == userId:
            orderCount += 1
    print("Orders placed so far:", orderCount)


def customerSummary(userId):
    orderCount = 0
    totalSpent = 0
    quantities = {}
    for row in readRows(ORDERS, "a+"):
        if row[0] == userId:
            orderCount += 1
            totalSpent += float(row[1])
            for name in row[2:]:
                if name in quantities:
                    quantities[name] += 1
                else:
                    quantities[name] = 1

    print("\nMON-51 SUMMARY -", userId)
    print("Orders:", orderCount)
    print("Total spent: ${:.2f}".format(totalSpent))
    print("-" * 36)
    print("{:<22} {:>12}".format("Product", "Quantity"))
    for name in quantities:
        print("{:<22} {:>12}".format(name, quantities[name]))


def main():
    print("Welcome to the Mon-51 warehouse.")
    userId = authenticate()
    anotherOrder = True
    while anotherOrder:
        product_list = lookupProducts(readScan())
        packProducts(product_list)
        completeOrder(userId, product_list)
        anotherOrder = askYesNo("Place another order?")
    customerSummary(userId)
    if not DEMO:
        arm.end_arm_connection()


main()
