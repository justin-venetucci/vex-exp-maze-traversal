#region VEXcode Generated Robot Configuration
from vex import *
import urandom

# Brain should be defined by default
brain = Brain()

# Robot configuration code
brain_inertial = Inertial()
dist = Distance(Ports.PORT4)
opt = Optical(Ports.PORT3)
left_drive_smart = Motor(Ports.PORT1, True)
right_drive_smart = Motor(Ports.PORT5, False)
drivetrain = SmartDrive(left_drive_smart, right_drive_smart, brain_inertial, 219.44, 320, 40, MM, 1.6666666666666667)
serv = Motor(Ports.PORT2, False)
ptmr = Potentiometer(brain.three_wire_port.b)


# Wait for sensor(s) to fully initialize
wait(100, MSEC)

def calibrate_drivetrain():
    # Calibrate the Drivetrain Inertial
    sleep(200, MSEC)
    brain.screen.print("Calibrating")
    brain.screen.next_row()
    brain.screen.print("Inertial")
    brain_inertial.calibrate()
    while brain_inertial.is_calibrating():
        sleep(25, MSEC)
    brain.screen.clear_screen()
    brain.screen.set_cursor(1, 1)

#endregion VEXcode Generated Robot Configuration
# ------------------------------------------
# 
# 	Project:      VEXcode Project
#	Author:       VEX
#	Created:
#	Description:  VEXcode EXP Python Project
# 
# ------------------------------------------

# Library imports
from vex import *

# Begin project code

def main():

    # using proportional control here

    desired_distance = 5.0
    distance_bound = 1.5 # for whether we hit or lost wall
    base_speed = 10.0
    correction_before_slow = 1.5
    
    # proportional gain for P-control
    k_p = 2.0  # MINIMUM TWO

    # opt saw nothing, so drive
    if not opt.is_near_object():
        drivetrain.set_drive_velocity(base_speed, PERCENT)
        drivetrain.drive(FORWARD)

        # While we are following a wall
        print("-- initiating wall follow loop --")
        while True:
            # Control polling rate
            wait(0.1, SECONDS)
            current_distance = dist.object_distance(INCHES)
            print(current_distance)

            # break if opt sees an object in front
            if opt.is_near_object():
                print("-- obj in front, breaking wall follow loop --")
                left_drive_smart.set_velocity(base_speed, PERCENT)
                right_drive_smart.set_velocity(base_speed, PERCENT)
                drivetrain.stop()
                break

            # LOST WALL, reset motors and exit
            elif current_distance > desired_distance + distance_bound:
                print("-- lost wall, breaking wall follow loop --")
                left_drive_smart.set_velocity(base_speed, PERCENT)
                right_drive_smart.set_velocity(base_speed, PERCENT)
                drivetrain.stop()
                break

            elif current_distance < desired_distance - distance_bound:
                print("-- hit wall, breaking wall follow loop --")
                left_drive_smart.set_velocity(base_speed, PERCENT)
                right_drive_smart.set_velocity(base_speed, PERCENT)
                drivetrain.stop()
                break

            # calculate the error (aka deviation from the desired distance)
            error = current_distance - desired_distance

            # use P-control to adjust motor speeds
            correction = k_p * error

            # Set motor velocities based on the correction
            left_velocity = base_speed - correction
            right_velocity = base_speed + correction

            # Set motor velocities within a reasonable range
            #left_velocity = max(base_speed - correction_before_slow, min(left_velocity, base_speed + correction_before_slow))
            #right_velocity = max(base_speed - correction_before_slow, min(right_velocity, base_speed + correction_before_slow))

            # if correction is getting out of control, zero-point turn
            if(correction > correction_before_slow):
                left_velocity = -2*correction  # hard coded idk
                right_velocity = 2*correction
                print("-- OUT OF CONTROL, SLOWING --")

            # Set motor velocities
            left_drive_smart.set_velocity(left_velocity, PERCENT)
            right_drive_smart.set_velocity(right_velocity, PERCENT)

            print("Error:", error, "Correction:", correction)
            print("L:", left_velocity, "R:", right_velocity)


# ------------------------------------------

def calibrate_serv():
    straight = 115 # it is 115 in this file... no idea why
    for i in range(-10, 10, 1):
        serv.spin_to_position(i, DEGREES,wait=True)
        if(ptmr.angle(DEGREES) >= straight - 1 and ptmr.angle(DEGREES) <= straight + 1):
            serv.set_position(0,DEGREES) # we missed this last time so our calibration actually did not work
            return
    
    # print on error and wait indefinitely
    brain.screen.print("CALIBRATION")
    brain.screen.next_row()
    brain.screen.print("OF MOTOR FAILED")
    wait(100000, SECONDS)
    return

# ------------------------------------------

def check_initial_pos():

    # we want to be roughly 4 - 6.5 inches from wall
    # 3.5 is touching
    # 4.5 is 1 inch away (ideal lower bound for wall follow)
    # 5.5 is 2 inches away (ideal upper bound for wall follow)
    # 6.5 is 3 inches away (wall should be deemed lost here)

    # spin dist sensor to left
    serv.spin_to_position(90,DEGREES,wait=True) # left

    if(dist.object_distance(INCHES) >= 6.5):
        brain.screen.print("BOT NOT ALIGNED")
        brain.screen.next_row()
        brain.screen.print("WITH LEFT WALL")
        serv.spin_to_position(0,DEGREES,wait=True) # straight again for re-calibrate
        wait(100000, SECONDS)
    return


# Start code
calibrate_serv()
check_initial_pos()

main()

#while(True):
#    main()
