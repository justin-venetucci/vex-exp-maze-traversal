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
limit_switch_a = Limit(brain.three_wire_port.a)


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
# \tProject:      VEXcode Project
#\tAuthor:       VEX
#\tCreated:
#\tDescription:  VEXcode EXP Python Project
# 
# ------------------------------------------

# Library imports
from vex import *
import math

# Begin project code

turn_deg = 88

def main():

    # using proportional control here

    desired_distance = 5.0
    distance_bound = 1.0 # for whether we hit or lost wall
    base_speed = 20.0
    max_speed = 25.0
    #correction_before_slow = 1.5
    
    # proportional gain for P-control
    k_p = 3.5

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
            # print(current_distance)
            

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
            elif dist.object_distance(INCHES) > desired_distance + distance_bound + 2:
                print("CUR DIST" + str(dist.object_distance(INCHES)))
                #if current_distance <  desired_distance + distance_bound + 0.1:
                #    print(current_distance)
                #    print(desired_distance + distance_bound + 0.1)
                #    returnToWall()
                #
                if False:
                    print()
                else:
                    print("-- lost wall, breaking wall follow loop --")
                    left_drive_smart.set_velocity(base_speed, PERCENT)
                    right_drive_smart.set_velocity(base_speed, PERCENT)
                    drivetrain.stop()
                    error = current_distance - desired_distance
                    turn("LEFT")
                    while(dist.object_distance(INCHES) > 8):
                        if(opt.is_near_object()):
                            drivetrain.turn_for(RIGHT, 90, DEGREES)
                        else:
                            drivetrain.drive(FORWARD)
                            if(limit_switch_a.pressing()):
                                print("-- LIMIT SWITCH HIT WALL --")
                                drivetrain.drive_for(REVERSE, 2,INCHES)
                                drivetrain.turn_for(RIGHT, 2, DEGREES)
                            
                                
                                
                            

            # HIT SIDE WALL
            elif current_distance < desired_distance - distance_bound:
                print("-- hit wall, breaking wall follow loop --")
                left_drive_smart.set_velocity(base_speed, PERCENT)
                right_drive_smart.set_velocity(base_speed, PERCENT)
                drivetrain.stop()
                drivetrain.drive_for(REVERSE, 3, INCHES, wait=True)
                
            # else:
                # print("else")
            
            # calculate the error (aka deviation from the desired distance)
            error = current_distance - desired_distance

            # use P-control to adjust motor speeds
            correction = k_p * error

            # Set motor velocities based on the correction
            left_velocity = base_speed
            right_velocity = min(base_speed + correction, max_speed)

            # Set motor velocities
            left_drive_smart.set_velocity(left_velocity, PERCENT)
            right_drive_smart.set_velocity(right_velocity, PERCENT)

            # print("Error:", error, "Correction:", correction)
            # print("L:", left_velocity, "R:", right_velocity)


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
    serv.spin_to_position(90, DEGREES, wait=True)
    
    #left_drive_smart.set_velocity(10, PERCENT)
    #right_drive_smart.set_velocity(10.5, PERCENT)
    
    # keep driving until we find wall on left again
    #while(dist.object_distance(INCHES) > 6.5):
    #    drivetrain.drive(FORWARD)
    return
    #main()

# ------------------------------------------

def returnToWall():
    print("-- Attempting to return to wall --")
    drivetrain.turn_for(LEFT, 90, DEGREES)

# ------------------------------------------
def reverseAndCorrect():
    drivetrain.drive_for(REVERSE, 2,INCHES)
    turn("RIGHT")
    drivetrain.drive_for(FORWARD, 2,INCHES)
    turn("LEFT")


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

    if(dist.object_distance(INCHES) >= 5):
        brain.screen.print("BOT TOO FAR")
        brain.screen.next_row()
        brain.screen.print("FROM LEFT WALL")
        serv.spin_to_position(0,DEGREES,wait=True) # straight again for re-calibrate
        wait(100000, SECONDS)
    elif(dist.object_distance(INCHES) <= 4):
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
