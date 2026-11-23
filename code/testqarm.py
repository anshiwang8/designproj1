#test file for calibrating the q arm
#fill in the coordinates below while testing, then copy them into Mon-51code.py
import time

#calibration values, all positions are [x, y, z]
HOME = [0, 0, 0]

#index 0-5 matches the order of products.csv (Sponge, Bottle, Rook, D12, Bowl, WitchHat)
#each object has (above location, at location)
PICKUPS = [
    [[0, 0, 0], [0, 0, 0]],  # 0
    [[0, 0, 0], [0, 0, 0]],  # 1
    [[0, 0, 0], [0, 0, 0]],  # 2
    [[0, 0, 0], [0, 0, 0]],  # 3
    [[0, 0, 0], [0, 0, 0]],  # 4
    [[0, 0, 0], [0, 0, 0]],  # 5
]

ABOVE_BIN = [0, 0, 0]
IN_BIN = [0, 0, 0]

#gripper angle to close on an object
CLOSE_DEGREES = 0

#how long to wait at each spot
MOVE_DELAY = 2
HOLD_DELAY = 3


def moveTo(position):
    arm.set_arm_position(position)
    time.sleep(MOVE_DELAY)


def testObject(index):
    if index < 0 or index >= len(PICKUPS):
        print("Object index must be 0 to", len(PICKUPS) - 1)
        return

    above = PICKUPS[index][0]
    at = PICKUPS[index][1]

    print("Moving to object", index)
    moveTo(above)
    moveTo(at)

    print("At object", index, "- holding for", HOLD_DELAY, "seconds")
    time.sleep(HOLD_DELAY)

    print("Going back")
    moveTo(above)
    moveTo(HOME)


def main():
    moveTo(HOME)
    choice = input("Object to test (0-5), or q to quit: ").strip().lower()
    while choice != "q":
        if choice.isdigit():
            testObject(int(choice))
        else:
            print("Enter a number 0-5 or q")
        choice = input("Object to test (0-5), or q to quit: ").strip().lower()
    arm.end_arm_connection()


main()
