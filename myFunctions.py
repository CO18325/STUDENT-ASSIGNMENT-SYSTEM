
#IMPORTANT PACKAGES


from scipy.spatial import distance as dist
from imutils.video import FileVideoStream
from imutils.video import VideoStream
from imutils import face_utils
import argparse
import imutils
import time
import dlib
import numpy as np
import cv2
import os
import sqlite3
import sys
import shutil

###########################################################################

# INITIATING IMPRTANT BLINK COUNT FUNCTION PRE REQUESTIES

def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])

    C = dist.euclidean(eye[0], eye[3])

    ear = (A + B) / (2.0 * C)

    return ear


EYE_AR_THRESH = 0.27 #args['threshold']
EYE_AR_CONSEC_FRAMES = 2 #args['frames']

COUNTER = 0
TOTAL = 0

# print("[INFO] loading facial landmark predictor...")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]


######################################################################################


# FACE RECOGNIZER

face_recognizer = cv2.face.LBPHFaceRecognizer_create()

#######################################################################################

# DATABASE INTERACTIONS: 


# THESE TWO FUNCTION IS TO STORE THE USER DATA INTO THE DATABASE
# AND RETRIEVE THE ROW_ID FOR THE USER DATA
# THIS ID WILL BE USED TO CREATE THE USER_IMAGE_DIR 


def save_data(password, email):

    # ESTABLISHING CONNECT WITH THE SQLITE DB
    conn = sqlite3.connect('db.sqlite')
    # CURSOR IS SIMILAR TO A FILE HANDLER
    cur = conn.cursor()

    cur.execute("SELECT * FROM students WHERE email = ?",(email,))
    row = cur.fetchone()

    if row is not None:
        # print("CHECK THE PREVIOUS REGISTERATION STATUS",row)
        if row[6] == 1:
            return -2,-2,-2


    cur.execute("UPDATE students SET password=?, registeration=1 WHERE email=?",(password,email))
    conn.commit()
    # print("DB UPDATED")

    cur.execute("SELECT * FROM students WHERE email=?",(email,))
    row = cur.fetchone()
    print(row)
    if row is None:
        print("UNSUCCESFUL DATABASE UPDAION")
        return (-1,-1,-1)
    else:
        print("DATABASE UPDATION SUCCESSFUL!!")
        return (row[0], row[3], row[5])
    cur.close()



def save_teacher_data(password,email):

    conn = sqlite3.connect('db.sqlite')
    # CURSOR IS SIMILAR TO A FILE HANDLER
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM teachers WHERE email = ?",(email,))
    row = cur.fetchone()
    if row is None:
        print("UNSUCCESFUL DATABASE UPDAION")
        return (-1,-1)
    else:
        # print("CHECK THE PREVIOUS REGISTERATION STATUS",row)
        if row[5] == 1:
            return -2,-2


    cur.execute("UPDATE teachers SET password=?, registeration=1 WHERE email=?",(password,email))
    conn.commit()
    # print("DB UPDATED")

    cur.execute("SELECT * FROM teachers WHERE email=?",(email,))
    row = cur.fetchone()
    cur.close() 
    print(row)
    if row is None:
        print("UNSUCCESFUL DATABASE UPDAION")
        return (-1,-1)
    else:
        print("DATABASE UPDATION SUCCESSFUL!!")
        return (row[0], row[2])
       

#####################################################################################################

# FUNCTION TO CREATE A DIRECTORY AT A SPECIFIC PATH

def create_dir(dir_id):
    
    # CREATING THE DIR NAME FOR THE DIR WHICH WILL STORE USER IMAGES
    dir_name = "USER_" + str(dir_id)
    # PARENT DIRECTORY WHERE ALL THE USER DIRs WILL BE STORED
    parent_dir = "DATA/USERS"

    #FUNCTION TO CONSTRUCT A PATH 
    path = os.path.join(parent_dir,dir_name)
    print(path)
    # FUNCTION TO CREATE A DIR OF THE GIVEN PATH
    os.mkdir(path)
    # CONSIDER ALL THE FAIL CONDITIONS AND ADD TRY EXCEPT BLOCKS

    return dir_name


#################################################################################################

# FACE DETECTION AND IMAGE SAVING FUNCTIONS


def view_identified_faces(img, gray_img, faces, frameCount, dir_name, img_count = 10):

    if faces == ():
        print("NO FACE FOUND IN THE IMAGE")
    else:
        # PATH WHERE THE IMAGE WILL BE STORED 
        # GETTING DIR_NAME FROM THE create_dir FUNCTION
        path = 'DATA/USERS/{}'.format(dir_name)
        
        # GETTING INFO ABOUT THE DATA IN THE DIRECTORY
        path, dirs, files = next(os.walk(path))

        # ACQUIRING THE NUMBER OF FILES IN THE DIR 
        file_count = len(files)
        
        #print(file_count)

        # CONDITION TO STORE AN IMAGE IN THE DIR
        # ONLY 15 IMAGES TO BE STORED IN THE DIR
        # STORING IMAGES AFTER EVERY 5 ms 
        # TO GET DIFFERENT EXPRESSIONS AND FACE FEATURE VIEW
        # MIGHT HELP IN TRAINING OUR MODEL
        if file_count<img_count  and frameCount%3 == 0:
            cv2.imwrite(os.path.join(path , '{}.jpg'.format(str(frameCount))), img)


           
    # SHOWING A GREEN RECTANGLE AROUND ALL THE FACES
    for (x,y,w,h) in faces:
        # FUNCTION DEFINATION:
        # cv2.rectangle(image, start_point, end_point, color, thickness)
        cv2.rectangle(img, (x+5,y+5),(x+w+5,y+h+5), (0,255,0), 3)

        break;

    rects = detector(gray_img, 0)
    global COUNTER
    global TOTAL
    for rect in rects:    
        shape = predictor(gray_img, rect)
        shape = face_utils.shape_to_np(shape)

        leftEye = shape[lStart:lEnd]
        rightEye = shape[rStart:rEnd]
        leftEAR = eye_aspect_ratio(leftEye)
        rightEAR = eye_aspect_ratio(rightEye)


        ear = (leftEAR + rightEAR) / 2.0

        leftEyeHull = cv2.convexHull(leftEye)
        rightEyeHull = cv2.convexHull(rightEye)
        cv2.drawContours(img, [leftEyeHull], -1, (255, 255, 0), 1)
        cv2.drawContours(img, [rightEyeHull], -1, (255, 255, 0), 1)

        if ear < EYE_AR_THRESH:
            COUNTER += 1
        else:
            if COUNTER >= EYE_AR_CONSEC_FRAMES:
                TOTAL += 1
            
            COUNTER = 0

        cv2.putText(img, "Blinks: {}".format(TOTAL), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(img, "EAR: {:.2f}".format(ear), (300, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        break    
    
    return img




# THIS IS A FUNCTION TO DETECT FACES
# WE USE A RESCALED IMAGE FOR BETTER OUTPUT AS PREVIOUS IMAGE WAS WAY TOO LARGE
# Haar Cascade Classifiers are basically a machine learning based approach where 
# a cascade function is trained from a lot of images both positive and negative. 
# Based on the training it is then used to detect the objects in the other images.
# So how this works is they are huge individual .xml files with a lot of feature sets 
# and each xml corresponds to a very specific type of use case.

def detect_face(img,frameCount, dir_name, img_count = 10):
    
    # LOADS THE CASSCADE XML FILE
    # THUS WE FORM AN OBJECT LOADED WITH haarcascade_frontalface_default.xml 
    # I.E. IT WILL CONTAIN THE FACE FEATURES
    face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

    # For the purposes of image recognition, we need to convert this BGR channel to gray channel. 
    # The reason for this is gray channel is easy to process 
    # and is computationally less intensive as it contains only 1-channel of black-white.
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    


    faces = face_cascade.detectMultiScale(gray_img, scaleFactor=1.05, minNeighbors=5)

    # NOW TO SHOW RECTANGLES AROUND FACES
    img = view_identified_faces(img, gray_img, faces, frameCount, dir_name, img_count)
    return img




def display_video(dir_name, frameLimit=1000, img_count = 10):

    global TOTAL
    TOTAL = 0
    global COUNTER 
    COUNTER = 0



    video = cv2.VideoCapture(0)
    
    frameCount = 0

    # THIS LOOP WILL ITERATE THROUGH ALL THE FRAMES
    while True:

        frameCount += 1


        check, frame = video.read()
        
        
        img = detect_face(frame,frameCount, dir_name, img_count)
        cv2.imshow("DETECTING FEATURES...",img)
        
        # THIS WILL GENERATE NEW FRAME EVERY 1 MILLISECOND
        key = cv2.waitKey(1)

        # LOOP WILL BREAK WHEN WE PRESS Q
        # if key == ord('q') or key == ord('Q'):
        #     break
        if frameCount == frameLimit:
            break;

    print('NUMBER OF FRAMES = {}'.format(frameCount))
    
    # TO OPEN/RELEASE THE CAMERA
    video.release()

    cv2.destroyAllWindows() 

    print("\n\n TOTAL NO. OF BLINKS = {}".format(TOTAL))



####################################################################################################################
####################################################################################################################

# FUNCTIONS TO RETRIEVE USER ID'S FROM DB


def get_user_id(email, password):

    # ESTABLISHING CONNECT WITH THE SQLITE DB
    conn = sqlite3.connect('db.sqlite')
    # CURSOR IS SIMILAR TO A FILE HANDLER
    cur = conn.cursor()

    cur.execute("SELECT * FROM students WHERE email=? AND password=?",(email,password))
    row = cur.fetchone()
    cur.close()
    if row is None:
        print("NO SUCH RECORD FOUND")
        return -1,-1,-1
    else:
        print("STUDENT DATA FOUND IN THE DATABASE!!")
        return row[0], row[3], row[5]
    

def get_teacher_id(email, password):
    
    # ESTABLISHING CONNECT WITH THE SQLITE DB
    conn = sqlite3.connect('db.sqlite')
    # CURSOR IS SIMILAR TO A FILE HANDLER
    cur = conn.cursor()

    cur.execute("SELECT * FROM teachers WHERE email=? AND password=?",(email,password))
    row = cur.fetchone()
    cur.close()
    if row is None:
        print("NO SUCH RECORD FOUND")
        return -1,-1
    else:
        print("STUDENT DATA FOUND IN THE DATABASE!!")
        return row[0], row[2]
    

#################################################################################################

# FUNCTIONS TO TEST THE FACIAL DATA


def get_face_data(img):
    
    face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


    faces = face_cascade.detectMultiScale(gray_img, scaleFactor=1.05, minNeighbors=5)

    if (len(faces) == 0):
        return None,None

    x,y,w,h = faces[0]

    return gray_img[y:y+w, x:x+h], faces[0]




def prepare_training_data(user_id, path):

    training_img_names = os.listdir(path)

    faces = []
    labels = []

    for training_img in training_img_names:

        # TO IGNORE .DS FILES
        if training_img.startswith("."):
            continue

        training_img_path = path + "/" + training_img

        img = cv2.imread(training_img_path)

        #cv2.imshow("Training Image..", img)
        #cv2.waitKey(200)

        face,rect = get_face_data(img)

        if face is not None:

            faces.append(face)
            labels.append(user_id)
        
        #cv2.destroyAllWindows()
        #cv2.waitKey(1)
        #cv2.destroyAllWindows()

    return faces, labels



#function to draw rectangle on image 
#according to given (x, y) coordinates and 
#given width and height
def draw_rectangle(img, rect):
    (x, y, w, h) = rect
    cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)



#function to draw text on give image starting from
#passed (x, y) coordinates. 
def draw_text(img, text, x, y):
    cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0), 2)



def predict(test_img):
    
    #make a copy of the image as we don't want to change original image
    img = test_img.copy()
    
    #detect face from the image
    face, rect = get_face_data(img)
    #print(face)
    successStatus = False
    
    #predict the image using our face recognizer 
    label, confidence_level = face_recognizer.predict(face)
    
    #print(label)
    
    #get name of respective label returned by face recognizer
    if confidence_level <= 45:
        label_text = str(label)
        successStatus = True
    
    # else:
    #     label_text = "FAKE USER!!" + str(confidence_level)
    
    # #draw a rectangle around face detected
    # draw_rectangle(img, rect)
    
    # #draw name of predicted person
    # draw_text(img, label_text, rect[0], rect[1]-5)
 
    return img, successStatus




def load_test_data(dir_name):

    parent_dir = "DATA/USERS"
    #FUNCTION TO CONSTRUCT A PATH 
    path = os.path.join(parent_dir,dir_name)
    print("PATH OF THE TEST IMAGES: ",path)
    images = os.listdir(path)
    
    successCount = 0
    print("TESTING DATA...")
    for img in images:
        if img.startswith("."):
            continue
        
        # PRINT THE NAME OF THE TEST IMAGE
        #print(img)
        
        # CONSTRUCTING THE PATH OF THE IMAGE
        img_path = os.path.join(path, img)
        #print(img_path)
        
        image = cv2.imread(img_path)
        image, succerStatus = predict(image)

        # cv2.imshow("User Test Image..",image)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        
        if succerStatus == True:
            successCount += 1

       
    print("NUMBER OF SUCCESSFUL TRUE DETECTIONS: ", successCount)
    # NOW OUR IMAGES ARE ARE READY FOR PREDICTION

    # DELETE THE USER TEMP DIRECTORY IMPORTANT
    try:
        shutil.rmtree(path)
    except OSError as e:
        print(e.strerror)
        sys.exit("LOGIN FAILED. CONTACT MANAGEMENT!!")

    print("TEMP DATA SUCCESSFULLY DELETED")
    if successCount > 3:
        print("USER VERIFIED!!!")
        return 1
    else:
        print("FAKE USER!!")
        return 0




def test_face(faces, labels):
    
    #train our face recognizer of our training faces
    face_recognizer.train(faces, np.array(labels))

    # THIS WILL STORE THE FRAMES OF THE PERSON AT THE TIME OF LOGIN
    # IN A TEMP FOLDER
    # NOTE: MAKE SURE THAT THE IMAGES ARE DELETED AFTER THE DETECTION IS DONE!!

    dir_name = create_dir("TEMP")
    display_video(dir_name, frameLimit = 50, img_count = 5)
    print(dir_name)
    # SO NOW WE HAVE DATA IMAGES TO TEST

    DetectionStatus = load_test_data(dir_name)

    print("\n\nNUMBER OF BLINKS: {}".format(TOTAL))

    if TOTAL < 2 :
        DetectionStatus = -1

    return DetectionStatus
