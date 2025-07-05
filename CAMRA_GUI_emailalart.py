import tkinter as tk
from tkinter import filedialog, ttk, messagebox  # Import messagebox module
from keras.models import load_model
from PIL import Image, ImageTk, ImageOps
import numpy as np
   import cv2
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from playsound import playsound

# Load the model
model = load_model("keras_Model.h5", compile=False)

# Load the labels
class_names = [line.strip() for line in open("labels.txt", "r").readlines()]

def classify_image(image):
    global input_img_label, result_label, confidence_label
    
    # resizing the image to be at least 224x224 and then cropping from the center
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.LANCZOS)         # if face error replace  ANTIALIAS  to LANCZOS

    # Display the input image
    input_img = ImageTk.PhotoImage(image)
    input_img_label.config(image=input_img)
    input_img_label.image = input_img

    # turn the image into a numpy array
    image_array = np.asarray(image)

    # Normalize the image
    normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1

    # Load the image into the array
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    data[0] = normalized_image_array

    # Predicts the model
    prediction = model.predict(data)
    index = np.argmax(prediction)
    
    # Check if the index is within the range of class_names
    if index < len(class_names):
        class_name = class_names[index]
        confidence_score = prediction[0][index]
        
        # Update the result label with the predicted class name
        result_label.config(text=f"Predicted Class: {class_name}")
        
        # Check if the confidence score is greater than 0.98
        if confidence_score > 0.98:
            confidence_label.config(text=f"Confidence Score: {confidence_score:.4f}")
            confidence_label.pack()
            result_label.pack()  # Display the Predicted Class label
        else:
            confidence_label.pack_forget()  # Hide the Confidence Score label
            result_label.pack_forget()  # Hide the Predicted Class label
            
        # Check if the predicted class is  '
        if class_name.lower() == '2 forest fire':
            #messagebox.showinfo("Danger Alert", "This is a dangered!")
            playsound('alarm.wav')
            
            # Save the image
            cv2.imwrite("NewPicture.jpg", cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR))  # Convert image to BGR format before saving
            
            # Send email code here...
            fromaddr = "vikas105106@gmail.com"
            password = "qzhgjvvdlqgorzsx"
            toaddr = "keshavsin24@gmail.com"

            msg = MIMEMultipart()

            msg['From'] = fromaddr
            msg['To'] = toaddr
            msg['Subject'] = "Danger Alert "
            body = "An endangered bird has been detected. Please see the attached image for details."
            msg.attach(MIMEText(body, 'plain'))
            filename = "NewPicture.jpg"
            attachment = open(filename, "rb")
            p = MIMEBase('application', 'octet-stream')
            p.set_payload((attachment).read())
            encoders.encode_base64(p)
            p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
            msg.attach(p)
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(fromaddr, password)
            text = msg.as_string()
            server.send_message(msg)
            server.quit()
            
    else:
        result_label.config(text="Not Detected")
        confidence_label.pack_forget()  # Hide the Confidence Score label
        result_label.pack()  # Display the Predicted Class label

def select_image():
    file_path = filedialog.askopenfilename()
    if file_path:
        image = Image.open(file_path)
        classify_image(image)

def capture_from_webcam():
    cap = cv2.VideoCapture(0)                                        ################################# 0 for default cam.   1  for usb cam.
    if not cap.isOpened():
        messagebox.showerror("Error", "Unable to open webcam.")
        return
    
    while True:
        ret, frame = cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame)
            classify_image(image)
            
            # Update GUI
            root.update_idletasks()
            root.update()
            
            # Delay for smooth streaming (adjust as needed)
            root.after(50)
        else:
            messagebox.showerror("Error", "Unable to read frame from webcam.")
            break
            
    cap.release()

root = tk.Tk()
root.title("Real-Time Forest Fire Detection using Deep Learning")
root.geometry("900x650")

# Create a frame for the title
title_frame = tk.Frame(root, bg="#FF5733")  # Orange color
title_frame.pack(pady=20)

title_label = tk.Label(title_frame, text="Real-Time Forest Fire Detection", font=("Arial", 20, "bold"), bg="#FF5733", fg="white")
title_label.pack()

# Create a frame for input image
input_frame = tk.Frame(root, bg="#FFC300")  # Yellow color
input_frame.pack(pady=20)

input_label = tk.Label(input_frame, text="Input Image", font=("Arial", 16, "bold"), bg="#FFC300")
input_label.pack()

input_img_label = tk.Label(input_frame, bg="#FFC300")
input_img_label.pack()

# Create a frame for result
result_frame = tk.Frame(root, bg="#DAF7A6")  # Light green color
result_frame.pack(pady=20)

result_label = tk.Label(result_frame, text="", font=("Arial", 20), bg="#DAF7A6")
result_label.pack()

# Create a label for Confidence Score
confidence_label = tk.Label(root, text="", font=("Arial", 18), bg="#FF5733", fg="white")

# Create a button to select an image
select_button = tk.Button(root, text="Select Image", command=select_image, bg="#FF5733", fg="white", font=("Arial", 14))
select_button.pack(pady=10)

# Create a button to capture image from webcam
webcam_button = tk.Button(root, text="Start Live Stream", command=capture_from_webcam, bg="#FF5733", fg="white", font=("Arial", 14))
webcam_button.pack(pady=10)

# Run the Tkinter main loop
root.mainloop()
