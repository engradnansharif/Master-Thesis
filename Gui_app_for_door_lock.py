
import os
import cv2
import tkinter as tk
from tkinter import ttk
import tkinter.font as font
import adafruit_fingerprint
import serial
from picamera import PiCamera
from picamera.array import PiRGBArray
from time import sleep
import subprocess
import adafruit_fingerprint
from imutils import paths
from Automatic_door_lock import *
import signal

uart = serial.Serial("/dev/ttyS0", baudrate=57600, timeout=1)
finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

# For raspberry pi
dataset_path = "/home/thdcham/door_systems/dataset"

model = Automatic_door_lock(dataset_path)

class PhotoCaptureApp:
    counter = 0

    def __init__(self, root):
        self.root = root
        self.root.title("Photo Capture App")
        self.root.geometry("480x600")
        self.model = model
        

        # Define font after root window is created
        self.labelFont = font.Font(size=20)
        self.buttonFont = font.Font(size=30)
        
        self.root.columnconfigure(0, weight = 1)
        self.root.columnconfigure(1, weight = 1)
        self.root.rowconfigure(0, weight = 1)
        self.root.rowconfigure(1, weight = 1)
        self.root.rowconfigure(2, weight = 1)

        self.name_label = ttk.Label(root, text="User Name")
        self.name_label['font'] = self.labelFont
        self.name_entry = ttk.Entry(root)
        self.name_label.grid(row=4, column=1, padx=10, pady=10, sticky="ew")
        self.name_entry.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.password_label = ttk.Label(root, text="Password")
        self.password_label['font'] = self.labelFont
        self.password_entry = ttk.Entry(root, show = "*")  # Show asterisks for password input
        self.password_label.grid(row=6, column=1, padx=10, pady=10, sticky="ew")
        self.password_entry.grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky="ew")


        #self.name_entry.bind("<FocusIn>", lambda event: root.after(100, self.keyboard_process))
        self.keyboard_process = subprocess.Popen(["matchbox-keyboard"])
        sleep(1)
        # Use xdotool to move the Matchbox Keyboard window to the bottom of the screen
        subprocess.run(["xdotool", "search", "--onlyvisible", "--class", "matchbox-keyboard", "windowmove", "0", "800"])

        self.submit_button = tk.Button(root, text="Submit Name", command=self.submit, height=3, width=20, bg='#0052cc', fg='#ffffff')
        self.submit_button['font'] = self.buttonFont
        self.submit_button.grid(row=8, column=0, columnspan=2, pady= self.calculate_vertical_padding())

        # Initialize PiCamera with specified resolution and framerate
        self.camera = PiCamera()
        self.camera.resolution = (1024, 608)  # Set resolution to Full HD
        self.camera.brightness = 50  # Set brightness (0-100)
        self.camera.framerate = 20

        # Initialize PiRGBArray for raw capture
        self.raw_capture = PiRGBArray(self.camera)
        self.raw_capture.truncate(0)
        self.raw_capture = PiRGBArray(self.camera, size=(1024, 608))
        self.img_counter = 0
        self.face_detector = dlib.get_frontal_face_detector()

    def calculate_vertical_padding(self):
        button_hight = 110
        window_hight = self.root.winfo_reqheight()
        padding = window_hight - button_hight
        return max(0,padding)


    def check_password(self, password):
        initial_password = "thdcham"
        return password == initial_password

    def submit(self):
        #subprocess.Popen(["onboard"])
        #subprocess.Popen(["matchbox-keyboard"])
        #keyboard_process = subprocess.Popen(["matchbox-keyboard"])

        entered_password = self.password_entry.get()  # Get the entered password
        if self.check_password(entered_password):  # Check if the password is correct
            print("Password is correct!")
            # Proceed with other actions if the password is correct
            self.keyboard_process.terminate()
            self.open_new_window()
        else:
            print("Password is incorrect.")
            self.keyboard_process.terminate()
            root.destroy()

    def open_new_window(self):
        new_window = tk.Toplevel(self.root)
        new_window.title("Additional Actions")
        new_window.geometry("480x800")  # Set the size of the second window
        
        # Capture photo buttons in the new window
        capture_photo_button = tk.Button(new_window, text="Capture Photo", command=self.capture_photo)
        capture_photo_button.pack(pady=10)

        # Fingerprint capture button
        enter_fingerprint_button = tk.Button(new_window, text="Enter Finger Print", command=self.enroll)
        enter_fingerprint_button.pack(pady=10)

        # Model traning button
        train_model_button = tk.Button(new_window, text="Train Model", command= lambda: [self.trainModel(),root.destroy()])
        train_model_button.pack(pady=10)

        # Create a text box to display the output
        self.output_text_box = tk.Text(new_window, height=10, width=45, font=("Helvetica", 12))
        self.output_text_box.pack(pady=10)

        # Create a "Done" button to close all windows
        #done_button = tk.Button(new_window, text="Done", command=root.destroy)
        #done_button.pack(pady=10)
        
        self.output_text_box.delete(1.0, tk.END)  # Clear the current text in the text box
        self.output_text_box.insert(tk.END, "Password is correct! Please Capture Photo. :)")


    def capture_photo(self):
        name = self.name_entry.get()
        if name:
            # This line creates the folder path
            folder_path = f"/home/thdcham/door_systems/dataset/{name}"

            # This code creates the folder if it doesn't exist
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                print(f"Folder '{name}' created successfully.")
            else:
                print(f"Folder '{name}' already exists.") 

            # Attempt to open the camera device
            try:
                # Initializing a loop to capture and display images
                while True:
                    # Capture image
                    self.camera.capture(self.raw_capture, format='bgr')
                    image = self.raw_capture.array
                    self.raw_capture.truncate(0)

                    # Detect faces in the captured image
                    faces = self.face_detector(image, 0)

                    # Process detected faces
                    for i, face in enumerate(faces):
                        # Get bounding box coordinates
                        x, y, w, h = face.left(), face.top(), face.width(), face.height()

                        # Draw bounding box around the face on the image
                        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)

                    # Save the image
                    img_name = f"dataset/{name}/image_{self.img_counter}.jpg"
                    cv2.imwrite(img_name, image)
                    
                    # Display the captured image with bounding boxes
                    resized_frame = cv2.resize(image, (500, 350))
                    cv2.imshow("Captured Image", resized_frame)

                    # This line waits for a key press (adjust the delay as needed)
                    key = cv2.waitKey(1000)

                    # If a key is pressed or 'self.img_counter' exceeds a certain limit, break out of the loop
                    if key != -1 or self.img_counter >= 6:
                        print("Photo Capture Done. Please Provide Fingerprint.")
                        # Insert text into an output text box (assuming 'self.output_text_box' is defined)
                        self.output_text_box.delete(1.0, tk.END)
                        self.output_text_box.insert(tk.END, "Photo Capture Done. Please Provide Fingerprint.")
                        break

                    # Output information
                    self.img_counter += 1

                # This line closes the OpenCV window after exiting the loop
                cv2.destroyAllWindows()

            except Exception as e:
                print(f"Error: {e}")
                cv2.destroyAllWindows()
                self.output_text_box.delete(1.0, tk.END)  # Clear the current text in the text box
                self.output_text_box.insert(tk.END, "Photo Capture Failed. Try Again...")
                self.camera.close()

            finally:
                cv2.destroyAllWindows()
                # Release the camera resources
                if hasattr(self, 'camera'):
                    self.camera.close()
        
    def enroll_finger(self, location):
        """Take a 2 finger images and template it, then store in 'location'"""
        for fingerimg in range(1, 3):
            if fingerimg == 1:
                print("Place finger on sensor...", end="")
                self.output_text_box.delete(1.0, tk.END)
                self.output_text_box.insert(tk.END, "Place finger on sensor...")
            else:
                print("Place same finger again...", end="")
                self.output_text_box.delete(1.0, tk.END)
                self.output_text_box.insert(tk.END, "Place same finger again...")

            while True:
                i = finger.get_image()
                if i == adafruit_fingerprint.OK:
                    print("Image taken")
                    self.output_text_box.delete(1.0, tk.END)
                    self.output_text_box.insert(tk.END, "Image taken")
                    break
                if i == adafruit_fingerprint.NOFINGER:
                    print(".", end="")
                elif i == adafruit_fingerprint.IMAGEFAIL:
                    print("Imaging error")
                    self.output_text_box.delete(1.0, tk.END)
                    self.output_text_box.insert(tk.END, "Imaging error")
                    return False
                else:
                    print("Other error")
                    return False

            print("Templating...", end="")
            i = finger.image_2_tz(fingerimg)
            if i == adafruit_fingerprint.OK:
                print("Templated")
            else:
                if i == adafruit_fingerprint.IMAGEMESS:
                    print("Image too messy")
                elif i == adafruit_fingerprint.FEATUREFAIL:
                    print("Could not identify features")
                elif i == adafruit_fingerprint.INVALIDIMAGE:
                    print("Image invalid")
                else:
                    print("Other error")
                return False

            if fingerimg == 1:
                print("Remove finger")
                self.output_text_box.delete(1.0, tk.END)
                self.output_text_box.insert(tk.END, "Remove finger")
                sleep(1)
                while i != adafruit_fingerprint.NOFINGER:
                    i = finger.get_image()

        print("Creating model...", end="")
        i = finger.create_model()
        if i == adafruit_fingerprint.OK:
            print("Created")
            self.output_text_box.delete(1.0, tk.END)
            self.output_text_box.insert(tk.END, "Created")
        else:
            if i == adafruit_fingerprint.ENROLLMISMATCH:
                print("Prints did not match")
                self.output_text_box.delete(1.0, tk.END)
                self.output_text_box.insert(tk.END, "Prints did not match")
            else:
                print("Other error")
            return False

        print("Storing model #%d..." % location, end="")
        i = finger.store_model(location)
        if i == adafruit_fingerprint.OK:
            print("Stored")
            self.output_text_box.delete(1.0, tk.END)
            self.output_text_box.insert(tk.END, "Stored")
        else:
            if i == adafruit_fingerprint.BADLOCATION:
                print("Bad storage location")
            elif i == adafruit_fingerprint.FLASHERR:
                print("Flash storage error")
            else:
                print("Other error")
            return False

        return True

    def get_num(self, max_number):
        """Use input() to get a valid number from 0 to the maximum size
        of the library. Retry till success!"""
        i = -1
        while (i > max_number - 1) or (i < 0):
            try:
                #i = int(input("Enter ID # from 0-{}: ".format(max_number - 1)))
                i = int(((max_number + finger.template_count)-max_number) + 1)
                print(i)
            except ValueError:
                pass
        return i

    def enroll(self):
        while True:
            print("----------------")
            if finger.read_templates() != adafruit_fingerprint.OK:
                raise RuntimeError("Failed to read templates")
            print("Fingerprint templates: ", finger.templates)
            if finger.count_templates() != adafruit_fingerprint.OK:
                raise RuntimeError("Failed to read templates")
            print("Number of templates found: ", finger.template_count)
            if finger.read_sysparam() != adafruit_fingerprint.OK:
                raise RuntimeError("Failed to get system parameters")
            print("Size of template library: ", finger.library_size)

            result = self.enroll_finger(self.get_num(finger.library_size))
            if result == True:
                self.output_text_box.delete(1.0, tk.END)  # Clear the current text in the text box
                self.output_text_box.insert(tk.END, "Fingerprint Capture Done.")
                break
            else:
                self.output_text_box.delete(1.0, tk.END)  # Clear the current text in the text box
                self.output_text_box.insert(tk.END, "Fingerprint Capture Failed. Try Again...")
                break
        #self.output_text_box.delete(1.0, tk.END)  # Clear the current text in the text box
        #self.output_text_box.insert(tk.END, "FINGERPRINT Capture Done. PRESS 'Train Model'. Don't close the GUI. It will be close Automatically...")
    
    def trainModel(self):
        self.output_text_box.delete(1.0, tk.END)  # Clear the current text in the text box
        self.output_text_box.insert(tk.END, "Dont't close the App. It will be close Automatically... :)")
        
        self.model.train_Model()        

if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoCaptureApp(root)
    root.mainloop()

