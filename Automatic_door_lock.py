from imutils.video import VideoStream
from imutils import paths
import face_recognition
import imutils
import pickle
import cv2
import dlib
import os
import serial
import RPi.GPIO as GPIO
import time
import traceback
from time import sleep
import adafruit_fingerprint

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

class Automatic_door_lock:
    def __init__(self, dataset_path, encodings_path="/home/thdcham/door_systems/encodings.pickle"):
        self.dataset_path = dataset_path
        self.encodings_path = encodings_path
        self.recognized_name = None 

    def train_Model(self):
        # Load a face detection model from dlib (CNN-based model). This one for windows environment, please change according as your directory.
        # cnn_face_detector = dlib.cnn_face_detection_model_v1("C:/Users/adnan/Desktop/automatic_door_lock_code/Face_recognition_system/mmod_human_face_detector.dat")

        # Load a face detection model from dlib (CNN-based model). This one for raspberry pi.
        cnn_face_detector = dlib.cnn_face_detection_model_v1("/home/thdcham/door_systems/mmod_human_face_detector.dat")

        # Check if the dataset directory exists
        if os.path.exists(self.dataset_path):
            print("[INFO] Loading dataset images...")

            # Initialize lists to store encodings and corresponding names
            knownEncodings = []
            knownNames = []

            # Loop over the individual directories in the dataset
            for person_dir in os.listdir(self.dataset_path):
                person_path = os.path.join(self.dataset_path, person_dir)

                # Loop over the image files within each individual's directory
                for image_file in os.listdir(person_path):
                    image_path = os.path.join(person_path, image_file)

                    print("[INFO] Processing image: ", image_path)

                    # Extract the name from the individual directory
                    name = person_dir

                    image = cv2.imread(image_path)
                    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                    # Resize the image to a smaller size
                    rgb = imutils.resize(rgb, width=800)  # Adjust the width as needed

                    # Use dlib's CNN-based face detector
                    dlib_faces = cnn_face_detector(rgb, 1)

                    for face in dlib_faces:
                        x, y, w, h = face.rect.left(), face.rect.top(), face.rect.width(), face.rect.height()

                        # Crop and resize the face for better recognition
                        face_crop = rgb[y:y+h, x:x+w]
                        face_resized = cv2.resize(face_crop, (128, 128))

                        # Check if the resized face image is too small
                        if face_resized.shape[0] < 10 or face_resized.shape[1] < 10:
                            print("Skipping too small face")
                            continue

                        # Compute the facial encodings only if there's a detected face
                        encodings = face_recognition.face_encodings(face_resized)

                        if len(encodings) > 0:
                            encoding = encodings[0]
                            knownEncodings.append(encoding)
                            knownNames.append(name)  # Associate the name with the encoding

            # Serialize the facial encodings + names to disk
            print("[INFO] Serializing encodings...")
            data = {"encodings": knownEncodings, "names": knownNames}
            with open(self.encodings_path, "wb") as f:
                f.write(pickle.dumps(data))
                f.close()
        else:
            print(f"Dataset directory not found at {self.dataset_path}")


    def face_Recognition(self):
        # Load the known faces and embeddings from the encodings.pickle file
        data = pickle.loads(open(self.encodings_path, "rb").read())

        # Initialize the video stream and allow the camera sensor to warm up
        vs = VideoStream(usePiCamera=True).start()  # For Raspberry Pi camera
        time.sleep(3.0)

        try:
            #for _ in range(50):
                #frame = vs.read()
                #frame = imutils.resize(frame, width=500)
                #cv2.imshow("Facial Recognition is Running", frame)
                #cv2.waitKey(10)
            
            while True:
                frame = vs.read()
                frame = imutils.resize(frame, width=500)
                boxes = face_recognition.face_locations(frame)
                encodings = face_recognition.face_encodings(frame, boxes)

                names = []

                name = None  # Initialize name as None

                for encoding in encodings:
                    matches = face_recognition.compare_faces(data["encodings"], encoding)

                    if True in matches:
                        matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                        counts = {}

                        for i in matchedIdxs:
                            name = data["names"][i]
                            counts[name] = counts.get(name, 0) + 1

                        name = max(counts, key=counts.get)
                        self.recognized_name = name
                        print(f"{name}, your face is detected.")  # Print recognized name
                        return True

                    names.append(name)

                if name is None:  # No match found, use "Unknown"
                    print("Face is not recognized.")
                    return False

                cv2.imshow("Facial Recognition is Running", frame)
                key = cv2.waitKey(1) & 0xFF

                if key == ord("q"):
                    break
                #vs.stop()
                vs.release()
                cv2.destroyAllWindows()

        finally:
            
            cv2.destroyAllWindows()  # Close any OpenCV windows
            cv2.destroyAllWindows()
            cv2.VideoCapture(0).release()
            vs.stop()  # Release the video stream

        return False

    def fingerprint_sensor(self):
        """Get a finger print image, template it, and see if it matches!"""
        uart = serial.Serial("/dev/ttyS0", baudrate=57600, timeout=1)
        finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

        print("Waiting for fingerprint...")
        start_time = time.time()
        while finger.get_image() != adafruit_fingerprint.OK:
            if time.time() - start_time >= 4:
                #finger.set_led(mode=4)
                #break
                return False
            #pass
        print("Templating...")
        if finger.image_2_tz(1) != adafruit_fingerprint.OK:
            return False
        print("Searching...")
        if finger.finger_search() != adafruit_fingerprint.OK:
            return False
        print("Fingerprint Detected #", self.recognized_name, "with confidence", finger.confidence)
        return True

    def motor_forward(self):
        AIN1 = 17
        AIN2 = 23
        PWMA = 12

        GPIO.setup(AIN1, GPIO.OUT)
        GPIO.setup(AIN2, GPIO.OUT)
        GPIO.setup(PWMA, GPIO.OUT)

        # Set motor speed
        motor_speed = 300

        # Function to drive the motor forward
        GPIO.output(AIN1, GPIO.HIGH)
        GPIO.output(AIN2, GPIO.LOW)
        GPIO.output(PWMA, GPIO.HIGH)

    def motor_backward(self):
        AIN1 = 17
        AIN2 = 23
        PWMA = 12

        GPIO.setup(AIN1, GPIO.OUT)
        GPIO.setup(AIN2, GPIO.OUT)
        GPIO.setup(PWMA, GPIO.OUT)

        # Set motor speed
        motor_speed = 300

        # Function to drive the motor backward
        GPIO.output(AIN1, GPIO.LOW)
        GPIO.output(AIN2, GPIO.HIGH)
        GPIO.output(PWMA, GPIO.HIGH)

    def motor_stop(self):
        PWMA = 12

        GPIO.setup(PWMA, GPIO.OUT)

        # Function to stop the motor
        GPIO.output(PWMA, GPIO.LOW)

    def pir_sensor(self):
        motionPin = 18
        GPIO.setup(motionPin, GPIO.IN)
        #sleep(2)
        motion = GPIO.input(motionPin)
        print(motion)
        sleep(0.1)
        if motion==1:
            return 1

###################################################
#dataset_path = '/home/pi/OOP_test_code_for_automatic_door_lock/dataset'     
#model = Automatic_door_lock(dataset_path)
#model.train_Model()