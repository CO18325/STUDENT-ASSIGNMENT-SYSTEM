from tkinter import *
# import myFunctions as mf
import numpy as np
import cv2
import os
import sqlite3
import sys
import shutil
from functools import partial
from tkinter import messagebox
import plagarism as plag
import sqlite3
from tkscrolledframe import ScrolledFrame




class Table: 
      
    def __init__(self,teach_screen, root,lst,total_rows,total_columns, t): 
          
        # code for creating table 
          
        for i in range(total_rows): 
            self.e = Entry(root, width=18, fg='blue', 
                            font=('Arial',16,'bold')) 
                
            self.e.grid(row=i, column=0) 
            self.e.insert(END, lst[i]['assignment_name']) 


            self.e = Entry(root, width=18, fg='blue', 
                            font=('Arial',16,'bold')) 
                
            self.e.grid(row=i, column=1) 
            self.e.insert(END, lst[i]['subject'])

    
            self.e = Entry(root, width=18, fg='blue', 
                    font=('Arial',16,'bold')) 
                
            self.e.grid(row=i, column=2) 
            self.e.insert(END, str(lst[i]['time_alloted'])+" MINS")

            # NEED TO PASS THE ASSIGNMENT ID TO THE WORK SPACE EVOKING FUNCTION FUNCTION
            self.e = Button(root, text ="VIEW", 
                command=partial(t.view_assignment, lst[i]), 
                width=18, height=1, fg='GREEN', font=('Arial',14,'bold')) 
                
            self.e.grid(row=i, column=3) 



class teacher:
    
    def __init__(self,teach_screen, teacher_id=1):
        self.teacher_id = teacher_id
        self.teach_screen = teach_screen

    def get_assignments(self):
        conn = sqlite3.connect('db.sqlite')
        conn.row_factory = sqlite3.Row
        curr=conn.cursor()
        
        self.lst = []

        curr.execute("SELECT * FROM assignments WHERE teacher_id=?",(self.teacher_id,))
        self.lst = curr.fetchall()


        curr.close()

        # LIST OF ASSIGNMENTS AVAILABLE FOR THE CURRENT STUDENTS
        for item in self.lst:
            print(dict(item))

        return self.lst

    def change_state(self,assignment_id,state_to_be_assigned,viewWin):
        viewWin.destroy()
        print(assignment_id,"   ",state_to_be_assigned)
        conn = sqlite3.connect('db.sqlite')
        conn.row_factory = sqlite3.Row
        curr=conn.cursor()

        curr.execute("UPDATE assignments SET current_state=? WHERE assignment_id=?",(state_to_be_assigned,assignment_id))   
        conn.commit()

        curr.execute("SELECT * FROM assignments WHERE assignment_id=?",(assignment_id,))
        cred = curr.fetchone()
        
        print(dict(cred))


        self.view_assignment(dict(cred))


    def generate_plagarism(self,cred,win):
        messagebox.showinfo("PLAGARISM REPORT",
        "PLAGARISM REPORT WILL BE DOWNLOADED IN THE DOWNLOADS FOLDER", parent=win)
        plag.generate_plag_rep(cred['branch'],cred['semester'],cred['assignment_id'],cred['assignment_name'])


    def on_closing_toplevel(self,win):
        self.teach_screen.update()
        self.teach_screen.wm_deiconify()
        win.destroy()


    def view_assignment(self,cred):
        teach_screen = self.teach_screen
        viewWin = Toplevel()
        viewWin.geometry("500x600") 
        viewWin.title("ADVANCED ASSIGNMENT SYSTEM: VIEW ASSIGNMENT")
        
        teach_screen.withdraw()
        viewWin.protocol("WM_DELETE_WINDOW",partial(self.on_closing_toplevel, viewWin))

        Label(viewWin, relief=RAISED, text='ASSIGNMENT', bg="steelblue", width="500", height="3", font=("Calibri", 18)).pack() 
        Label(viewWin, text="\n").pack()

        Label(viewWin, relief=GROOVE, text='ASSIGNMENT DETAILS:', width="40", height="2", font=("Calibri", 15)).pack() 
        Label(viewWin, text="\n").pack()
        
        credentialFrame = Frame(viewWin, relief=GROOVE, borderwidth=2)
        credentialFrame.pack()

        nameLabel = Label(credentialFrame, text="Assignment Name", font=("Calibri", 14))
        nameLabel.grid(row = 0,column = 2, padx=10, pady=10)
        
        name = Label(credentialFrame, text=cred['assignment_name'], font=("Calibri", 14))
        name.grid(row = 0,column = 4, padx=10, pady=10)

        subjectLabel = Label(credentialFrame, text="Subject",  font=("Calibri", 14))
        subjectLabel.grid(row = 1,column = 2, padx=10, pady=10)
        
        subject = Label(credentialFrame, text=cred['subject'],  font=("Calibri", 14))
        subject.grid(row = 1,column = 4, padx=10, pady=10)

        timeLabel = Label(credentialFrame, text="TIME", font=("Calibri", 14))
        timeLabel.grid(row = 2,column = 2, padx=10, pady=10)
        
        time = Label(credentialFrame, text=cred['time_alloted'],  font=("Calibri", 14))
        time.grid(row = 2,column = 4, padx=10, pady=10)

        statusLabel = Label(credentialFrame, text="STATUS",  font=("Calibri", 14))
        statusLabel.grid(row = 3,column = 2, padx=10, pady=10)
        
        status = Label(credentialFrame, text=cred['current_state'],  font=("Calibri", 14))
        status.grid(row = 3,column = 4, padx=10, pady=10)

        dataLabel = Label(credentialFrame, text="DATA",  font=("Calibri", 14))
        dataLabel.grid(row = 4,column = 2, padx=10, pady=10)
        
        data = Label(credentialFrame, text=cred['assignmnet_data'],  font=("Calibri", 14))
        data.grid(row = 4,column = 4, padx=10, pady=10)

        Label(viewWin, text="\n").pack()
        if cred['current_state'] == 1:
            Button(viewWin, text="DISABLE", bg="steelblue", width="30", height="1",font=("Calibri", 18), 
            command=partial(self.change_state,cred['assignment_id'],0,viewWin)).pack()
        else:
            Button(viewWin, text="ENABLE", bg="steelblue", width="30", height="1",font=("Calibri", 18),
            command=partial(self.change_state,cred['assignment_id'],1,viewWin)).pack() 


        Button(viewWin, text="GENERATE PLAGARISM REPORT", bg="steelblue", width="30", height="1",font=("Calibri", 18), 
        command=partial(self.generate_plagarism,cred,viewWin)).pack()   


    def save_assignment(self,name,subject,dur,sem,branch,data,status):
        
        assignment_cred = {}
        assignment_cred['name'] = name.get()
        assignment_cred['subject'] = subject.get()
        assignment_cred['branch'] = branch.get()
        assignment_cred['dur'] = dur.get()
        assignment_cred['status'] = status.get()
        assignment_cred['semester'] = sem.get()
        assignment_cred['data'] = (data.get('1.0', END))

        print(assignment_cred)

        conn = sqlite3.connect("db.sqlite")
        cur = conn.cursor()
        qry = "INSERT INTO assignments VALUES(NULL,{},{},{},{},{},{},{},{}) ".format(assignment_cred[name],
        assignment_cred['data'],assignment_cred['status'],self.teacher_id,assignment_cred['subject'],assignment_cred['dur'],
        assignment_cred['branch'],assignment_cred['semester'])

        cur.execute(qry)
        conn.commit()




    def generate_assignment(self):
        teach_screen = self.teach_screen
        Win = Toplevel()
        Win.geometry("700x650") 
        Win.title("ADVANCED ASSIGNMENT SYSTEM: VIEW ASSIGNMENT")
        
        teach_screen.withdraw()
        Win.protocol("WM_DELETE_WINDOW",partial(self.on_closing_toplevel,Win))

        Label(Win, relief=RAISED, text='ASSIGNMENT', bg="steelblue", width="500", height="3", font=("Calibri", 18)).pack() 
        Label(Win, text="\n").pack()

        Label(Win, relief=GROOVE, text='ASSIGNMENT DETAILS:', width="40", height="2", font=("Calibri", 15)).pack() 
        Label(Win, text="\n").pack()
                

        # Create a ScrolledFrame widget
        sf = ScrolledFrame(Win)
        sf.pack(side="top", expand=1, fill="both")

        # Bind the arrow keys and scroll wheel
        sf.bind_arrow_keys(Win)
        sf.bind_scroll_wheel(Win)

        # credentialFrame = Frame(Win, relief=GROOVE, borderwidth=2)
        # credentialFrame.pack()
        credentialFrame = sf.display_widget(Frame)

        nameLabel = Label(credentialFrame, text="Assignment Name", font=("Calibri", 14))
        nameLabel.grid(row = 0,column = 2, padx=10, pady=10)
        
        name = Entry(credentialFrame, bd =5,  font=("Calibri", 18))
        name.grid(row = 0,column = 4, padx=10, pady=10)

        subjectLabel = Label(credentialFrame, text="Subject",  font=("Calibri", 14))
        subjectLabel.grid(row = 1,column = 2, padx=10, pady=10)
        
        subject = Entry(credentialFrame, bd =5,  font=("Calibri", 18))
        subject.grid(row = 1,column = 4, padx=10, pady=10)

        durationLabel = Label(credentialFrame, text="DURATION",  font=("Calibri", 14))
        durationLabel.grid(row = 2,column = 2, padx=10, pady=10)
        
        dur = Entry(credentialFrame, bd =5,  font=("Calibri", 18))
        dur.grid(row = 2,column = 4, padx=10, pady=10)

        statusLabel = Label(credentialFrame, text="STATUS(1/0)",  font=("Calibri", 14))
        statusLabel.grid(row = 3,column = 2, padx=10, pady=10)
        
        status = Entry(credentialFrame, bd =5,  font=("Calibri", 18))
        status.grid(row = 3,column = 4, padx=10, pady=10)

        branchLabel = Label(credentialFrame, text="BRANCH", font=("Calibri", 14))
        branchLabel.grid(row = 4,column = 2, padx=10, pady=10)
        
        branch = Entry(credentialFrame, bd =5,  font=("Calibri", 18))
        branch.grid(row = 4,column = 4, padx=10, pady=10)

        semLabel = Label(credentialFrame, text="SEMESTER",  font=("Calibri", 14))
        semLabel.grid(row = 5,column = 2, padx=10, pady=10)
        
        sem = Entry(credentialFrame, bd =5,  font=("Calibri", 18))
        sem.grid(row = 5,column = 4, padx=10, pady=10)

        dataLabel = Label(credentialFrame, text="DATA",  font=("Calibri", 14))
        dataLabel.grid(row = 6,column = 2, padx=10, pady=10)
        
        data = Text(credentialFrame, height=20, width=80)
        data.grid(row = 6,column = 4, padx=10, pady=10)        

        Button(credentialFrame, text="GENERATE ASSIGNMENT", bg="steelblue", width="30", height="1",font=("Calibri", 18),
        command=partial(self.save_assignment,name,subject,dur,sem,branch,data,status)).grid(row = 7,column = 4, padx=10, pady=10)      









def on_closing_main(win,main_screen):
    if messagebox.askyesno("Exit", "Do you want to quit the Portal", parent=win):
        win.destroy()
        main_screen.update()
        main_screen.wm_deiconify()


def teach_portal(main_screen, teacher_id=1, branch=1):

    t = teacher(teacher_id)
    
    teach_screen = Toplevel()

    teach_screen.geometry("950x600") # set the configuration of GUI window 
    teach_screen.title("ADVANCED ASSIGNMENT SYSTEM: A PRODUCT BY CAP_INNOVATIONS") # set the title of GUI window
    
    teach_screen.protocol("WM_DELETE_WINDOW",partial(on_closing_main, teach_screen,main_screen))
    t = teacher(teach_screen,teacher_id)

    Label(teach_screen,relief=RAISED, text='''ADVANCED ASSIGNMENT SYSTEM
        -- A CAPINNOVATIONS PRODUCT''', bg="steelblue", width="500", height="2", font=("Calibri", 16)).pack() 

    Button(teach_screen, text="ADD NEW ASSIGNMENT", bg="white", width="30", height="1",font=("Calibri", 16), 
        command=partial(t.generate_assignment)).pack()     

    # scrollbar = Scrollbar(teach_screen)
    # scrollbar.pack(side=RIGHT, fill=Y)

    # NEED TO ADD A SCROLLBAR TO THE FRAME VVIP
    
    data_frame = Frame(teach_screen, relief=GROOVE, borderwidth=2,padx=20,pady=20)
    data_frame.pack(fill=BOTH, expand=True)

    

    lst = t.get_assignments()

    
    
    total_rows = len(lst)
    total_columns = 3 

    t = Table(teach_screen, data_frame,lst,total_rows,total_columns, t) 

    teach_screen.mainloop()
# teach_portal()