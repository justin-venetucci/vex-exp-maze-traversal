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
import math

# Begin project code

turn_deg = 88

def main():

    # using proportional control here

    desired_distance = 5.5
    distance_bound = 2 # for whether we hit or lost wall
    base_speed = 10.0
    #correction_before_slow = 1.5
    
    # proportional gain for P-control
    k_p = 2.375

    # opt saw nothing, so drive
    if not opt.is_near_object():
        
        # While we are following a wall
        print("-- initiating new wall follow loop --")
        while True:
            # Control polling rate
            wait(0.1, SECONDS)
            drivetrain.drive(FORWARD)
            drivetrain.set_drive_velocity(base_speed, PERCENT)

            current_distance = dist.object_distance(INCHES)
            print(current_distance)
            

            # FOUND FRONT WALL
            if opt.is_near_object():
                print("-- obj in front, breaking wall follow loop --")
                left_drive_smart.set_velocity(base_speed, PERCENT)
                right_drive_smart.set_velocity(base_speed, PERCENT)
                drivetrain.stop()
                turn("RIGHT")
                #drivetrain.drive(FORWARD)
                #break

            # LOST SIDE WALL
            elif current_distance > desired_distance + distance_bound:
                print("-- lost wall, breaking wall follow loop --")
                left_drive_smart.set_velocity(base_speed, PERCENT)
                right_drive_smart.set_velocity(base_speed, PERCENT)
                drivetrain.stop()
                error = current_distance - desired_distance
                turn("LEFT")
                #turn(k_p * error)
                break
                #k_p = 5

            # HIT SIDE WALL
            elif current_distance < desired_distance - distance_bound:
                print("-- hit wall, breaking wall follow loop --")
                left_drive_smart.set_velocity(base_speed, PERCENT)
                right_drive_smart.set_velocity(base_speed, PERCENT)
                drivetrain.stop()
                break
            else:
                print("else")
            # calculate the error (aka deviation from the desired distance)
            error = current_distance - desired_distance

            # use P-control to adjust motor speeds
            correction = k_p * error
            #if error > 1 or error < -1:
            #    correction = error**2 * error/abs(error)

            # Set motor velocities based on the correction
            #left_velocity = base_speed - correction
            left_velocity = base_speed
            right_velocity = base_speed + correction

            #if correction is getting out of control, zero-point turn
            #if(correction > correction_before_slow):
            #    left_velocity = -1.5*correction  # hard coded idk
            #    right_velocity = 1.5*correction
            #    print("-- OUT OF CONTROL, SLOWING --")


            # new correction
            #if(dist.object_distance(INCHES) < 4.5):
            #    drivetrain.drive_for(REVERSE, 1, INCHES)
            #    drivetrain.turn_for(RIGHT, 15, DEGREES)


            # Set motor velocities
            left_drive_smart.set_velocity(left_velocity, PERCENT)
            right_drive_smart.set_velocity(right_velocity, PERCENT)

            print("Error:", error, "Correction:", correction)
            print("L:", left_velocity, "R:", right_velocity)


# ------------------------------------------

def calc_turn_correction():
    cardinal = round((drivetrain.heading(DEGREES))/90)*90
    if(cardinal <= 0):
        cardinal = 360 + cardinal
    elif(cardinal >= 360):
        cardinal = cardinal - 360
    #cardinal = drivetrain.heading(DEGREES) % 90
    print("Cardinal: ", cardinal)
    return cardinal

# ------------------------------------------

def turn(direction):
    print("-- left turn function called --")
    cardinal = calc_turn_correction()
    drivetrain.turn_to_heading(cardinal)
    
    # spin dist sensor forward and take measurement
    serv.spin_to_position(0, DEGREES,wait=True)
    clearance = min(dist.object_distance(INCHES) - 2.5, 7.5)
    print("Clearance: ", clearance)
    
    drivetrain.drive_for(FORWARD, clearance, INCHES)
    if(direction == "LEFT"):
        drivetrain.turn_for(LEFT, turn_deg, DEGREES)
    elif(direction == "RIGHT"):
        drivetrain.turn_for(RIGHT, turn_deg, DEGREES)
    else:
        print("invalid turn direction provided: ", direction)
    
    # reset distance sensor
    serv.spin_to_position(90, DEGREES)
    
    #left_drive_smart.set_velocity(10, PERCENT)
    #right_drive_smart.set_velocity(10.5, PERCENT)
    
    # keep driving until we find wall on left again
    while(dist.object_distance(INCHES) > 6.5):
        drivetrain.drive(FORWARD)
    main()

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
        brain.screen.print("BOT TOO FAR")
        brain.screen.next_row()
        brain.screen.print("FROM LEFT WALL")
        serv.spin_to_position(0,DEGREES,wait=True) # straight again for re-calibrate
        wait(100000, SECONDS)
    elif(dist.object_distance(INCHES) <= 4.5):
        brain.screen.print("BOT TOO CLOSE")
        brain.screen.next_row()
        brain.screen.print("TO LEFT WALL")
        serv.spin_to_position(0,DEGREES,wait=True) # straight again for re-calibrate
        wait(100000, SECONDS)
    else:
        return

# ------------------------------------------

# Start code
calibrate_serv()
check_initial_pos()

main()

#while(True):
#    main()
