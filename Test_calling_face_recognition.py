from Automatic_door_lock import *
from time import sleep, time
import RPi.GPIO as GPIO
from imutils import paths
import adafruit_fingerprint
import os


if __name__ == "__main__":
    uart = serial.Serial("/dev/ttyS0", baudrate=57600, timeout=1)
    finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)
    
    # For raspberry pi
    dataset_path = list(paths.list_images("/home/thdcham/door_systems/dataset"))
    
    model = Automatic_door_lock(dataset_path)

    try:
        while True: #This will keep the motion detector running
            if model.pir_sensor() == 1:
                os.system("xscreensaver-command -deactivate")
                print("Motion Detected!")
                
                # A flag to if fingerprint will activate or not
                fingerprint_detected = False
                if model.face_Recognition()== True:
                
                #Setting timer for face recognition and fingerprint sensing
                    start_time = time()
                
            
                    #while True:
                        
                        #if model.face_Recognition()== True:
                    """Get a finger print image, template it, and see if it matches!"""
                    if model.fingerprint_sensor()== True:
                        
                        
                        fingerprint_detected = True
                        #Motor control
                        #model.motor_forward()
                        model.motor_backward()
                        sleep(12)
                        model.motor_stop()
                        sleep(5)
                        #model.motor_backward()
                        model.motor_forward()
                        sleep(12)
                        model.motor_stop()
                        #os.system("xscreensaver-command -activate")
                        #break
                        
                    sleep(1)
                os.system("xscreensaver-command -activate")
                #break
                    #if model.fingerprint_sensor()== False:
                        #finger.set_led(0)
                        #break
                #os.system("xscreensaver-command -activate")
                        

    except KeyboardInterrupt:
        GPIO.cleanup()
        print("GPIO Good to go")

