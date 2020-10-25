from tkinter import *
import myFunctions as mf
import numpy as np
import cv2
import os
import sqlite3
import sys
import shutil
from functools import partial
from tkinter import messagebox
import workPad as nt
import atexit
import teacher_portal as tp

# def get_student_data(roll_no):
#     conn = sqlite3.connect(db.sqlite)
#     curr = conn.cursor()
#     curr.execute("SELECT * FROM students WHERE roll_no=?",(roll_no,))
#     studData = curr.fetchone()
#     return studData

def on_closing_toplevel(win, main_screen):
    main_screen.update()
    main_screen.wm_deiconify()
    win.destroy()


def register_user(main_screen, win, passInput, emailInput):

    password = passInput.get()
    email = emailInput.get()

    if password == "" or email == "":
        messagebox.showerror("INVALID INPUT", "INPUT CREDENTIALS EMPTY!", parent=win )
        return

        
    dir_id, branch = mf.save_teacher_data(password, email)

    if dir_id == -2:
        messagebox.showerror("INVALID INPUT", "ALREADY REGISTERED", parent=win )
        return
    
    if dir_id == -1:
        messagebox.showerror("INVALID INPUT", "CREDENTIALS ARE NOT CORRECT", parent=win )
        return

    print(dir_id)
    
    dir_name = mf.create_dir(dir_id)

    mf.display_video(dir_name, frameLimit = 100)
    
    # mf.update_db(dir_id)
    messagebox.showinfo("Notification", "SUCCESSFUL REGISTRAION!!", parent=win)
    win.destroy()

    # FROM HERE THE STUDENT PORTAL'S CODE WILL BE IMPLEMENTED

    tp.teach_portal(main_screen,dir_id,branch)




def registration(main_screen):

    regWin = Toplevel()
    regWin.geometry("500x600") 
    regWin.title("ADVANCED ASSIGNMENT SYSTEM: USER REGISTRATION")
    
    main_screen.withdraw()
    regWin.protocol("WM_DELETE_WINDOW",partial(on_closing_toplevel, regWin, main_screen))

    Label(regWin, relief=RAISED, text='REGISTRATION PORTAL', bg="steelblue", width="500", height="3", font=("Calibri", 18)).pack() 
    Label(regWin, text="\n").pack()

    Label(regWin, relief=GROOVE, text='ENTER YOUR CREDENTIALS:', width="40", height="2", font=("Calibri", 15)).pack() 
    Label(regWin, text="\n").pack()
    
    credentialFrame = Frame(regWin, relief=GROOVE, borderwidth=2)
    credentialFrame.pack()

    emailLabel = Label(credentialFrame, text="Email     ", font=("Calibri", 18))
    emailLabel.grid(row = 0,column = 2, padx=20, pady=20)
    
    emailInput = Entry(credentialFrame, bd =5,  font=("Calibri", 18))
    emailInput.grid(row = 0,column = 4, padx=20, pady=20)

    passLabel = Label(credentialFrame, text="Password     ",  font=("Calibri", 18))
    passLabel.grid(row = 2,column = 2, padx=20, pady=20)
    
    passInput = Entry(credentialFrame, bd =5,  font=("Calibri", 18))
    passInput.grid(row = 2,column = 4, padx=20, pady=20)

    Label(regWin, text="\n").pack()

    Button(regWin, text="Register", bg="steelblue", width="30", height="1",font=("Calibri", 18), 
            command=partial(register_user, main_screen, regWin, passInput, emailInput)).pack()

    
    


def login_user(main_screen, win, emailInput, passInput):
    password = passInput.get()
    email = emailInput.get()    

    if password == "" or email == "":
        messagebox.showerror("INVALID INPUT", "INPUT CREDENTIALS EMPTY!", parent=win )
        return
    
    dir_id, branch = mf.get_teacher_id(email, password)

    if dir_id == -1:
        errorBox = messagebox.askquestion("USER INVALID", '''
            USER NOT FOUND \n
            PLEASE REGISTER IF YOU HAVE NOT REGISTERED \n
            ELSE CONTACT MANAGEMENT \n
            UNSUCCESSFUL LOGIN!!! \n
            DO YOU WANT TO RETRY?

        ''', parent=win)
        # print("USER NOT FOUND")
        # print("PLEASE REGISTER IF YOU HAVE NOT REGISTERED")
        # print("ELSE CONTACT MANAGEMENT")
        #sys.exit("UNSUCCESSFUL login!!!")
        if errorBox == "yes":
            return
        else:
            on_closing_toplevel(win, main_screen)

    # THIS IS LOADED AFTER THE FACE RECOGNITION IS DONE :(  
    # text = Text(win)
    # text.insert(INSERT, "LOADING FACE RECOGNITION... PLEASE WAIT!!")
    # text.pack()


    print("USER FOUND SUCCESSFULLY!!")
    print("NOW, ITS TIME FOR FACE VERIFICATION")
   
    parent_dir = "DATA/USERS"
    dir_name = "USER_" + str(dir_id)
    #FUNCTION TO CONSTRUCT A PATH 
    path = os.path.join(parent_dir,dir_name)
    print(path)
    
    print("Preparing Test Data...")

    faces, labels = mf.prepare_training_data(dir_id, path)
    print("Data prepared")
     
    

    #print total faces and labels
    #print("Total faces: ", len(faces))
    #print("Total labels: ", len(labels))
    #print(labels)

    print("TIME TO TEST THE USER WEBCAM IMAGE")


    faceTestStatus = mf.test_face(faces, labels)

    if (faceTestStatus == 1):    
        messagebox.showinfo("SUCCESS","CONGRAX!! NOW YOU CAN ACCESS ASSIGNMENTS", parent=win)
    elif faceTestStatus == -1:
        messagebox.showerror("INVALID PERSON", "NOT ENOUGH BLINKS RECOGIZED!!", parent=win)
        return 
    else:
        messagebox.showerror("INVALID PERSON", "FACE UNRECOGNIZED", parent=win)
        return

    win.destroy()
    # FROM HERE THE STUDENT PORTAL CODE WILL BE IMPLEMENTED
    
    tp.teach_portal(main_screen,dir_id,branch)




def login(main_screen):
    logWin = Toplevel()
    logWin.geometry("500x600") 
    logWin.title("ADVANCED ASSIGNMENT SYSTEM: USER LOGIN")
    
    main_screen.withdraw()
    logWin.protocol("WM_DELETE_WINDOW",partial(on_closing_toplevel, logWin, main_screen))
    
    Label(logWin, relief=RAISED, text='LOGIN PORTAL', bg="steelblue", width="500", height="3", font=("Calibri", 18)).pack() 
    Label(logWin, text="\n").pack()

    Label(logWin, relief=GROOVE, text='ENTER LOGIN CREDENTIALS:', width="40", height="2", font=("Calibri", 15)).pack() 
    Label(logWin, text="\n").pack()
    
    credentialFrame = Frame(logWin, relief=GROOVE, borderwidth=2)
    credentialFrame.pack()

    emailLabel = Label(credentialFrame, text="Email     ", font=("Calibri", 18))
    emailLabel.grid(row = 0,column = 2, padx=20, pady=20)
    
    emailInput = Entry(credentialFrame, bd =5,  font=("Calibri", 18))
    emailInput.grid(row = 0,column = 4, padx=20, pady=20)

    passLabel = Label(credentialFrame, text="Password     ",  font=("Calibri", 18))
    passLabel.grid(row = 2,column = 2, padx=20, pady=20)
    
    passInput = Entry(credentialFrame, bd =5,  font=("Calibri", 18))
    passInput.grid(row = 2,column = 4, padx=20, pady=20)

    Label(logWin, text="\n").pack()
    


    Button(logWin, text="LOGIN", bg="steelblue", width="30", height="1",font=("Calibri", 18), 
            command=partial(login_user, main_screen, logWin, emailInput, passInput)).pack()

    # # logWin.wm_protocol("WM_DELETE_WINDOW", on_closing(logWin, main_screen))
    # atexit.register(on_closing(logWin, main_screen))



    

def on_closing_main(win):
    if messagebox.askyesno("Exit", "Do you want to quit the application?", parent=win):
        win.destroy()    


def main():
    main_screen = Tk()  

    main_screen.geometry("900x600") # set the configuration of GUI window 
    main_screen.title("ADVANCED ASSIGNMENT SYSTEM: A PRODUCT BY CAP_INNOVATIONS") # set the title of GUI window
    
    main_screen.protocol("WM_DELETE_WINDOW",partial(on_closing_main, main_screen))
    
    Label(relief=RAISED, text='''ADVANCED ASSIGNMENT SYSTEM - TEACHER'S SECTION
        -- A CAPINNOVATIONS PRODUCT''', bg="steelblue", width="500", height="3", font=("Calibri", 18)).pack() 
    Label(text="").pack() 


    InfoArea = Label(relief=GROOVE, justify=LEFT, text='''
                    \t\t--PROJECT DESCRIPTION--
WORKING:
    In today’s world online teaching is a fast growing industry. And along with it 
    students have numerous ways to do their Homework / Assignments / Quizzes /Tests 
    etc using illicit means. To tackle this problem I have designed a solution of 
    advanced assignment submission portal. Time based live assignments/tests would 
    be conducted at this portal. It will allow students to login through face and 
    blink recognition to ensure real-time liveliness detection approach against 
    photograph spoofing.It will have the feature of converting speech to text in 
    the live assignments. It will also generate plagarism reports for teachers. 

BUILT BY:
    INDERPREET SINGH (inderpreet221099@gmail.com)
    LinkedIn: https://www.linkedin.com/in/inderpreet-singh-a32816169
    ''', bg="white", width="80", height="17", font=("Calibri", 13))
    InfoArea.pack()


    frame = Frame(main_screen, relief=GROOVE, borderwidth=2)
    frame.pack(fill=BOTH, expand=True)

    Button(frame, text="Register", bg="steelblue", width="20", height="1",font=("Calibri", 18), command=partial(registration, main_screen)).pack(side=RIGHT, padx=20, pady=20)
    Button(frame, text="Login", bg="steelblue", width="20", height="1",font=("Calibri", 18), command=partial(login, main_screen)).pack(side=LEFT, padx=20, pady=20) 


    main_screen.mainloop() 



main()