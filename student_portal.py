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
import workPad as wp
import sqlite3

class Table: 
      
    def __init__(self, main_screen, stud_screen, root,lst,total_rows,total_columns, st): 
          
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
            self.e = Button(root, text ="START", 
                command=partial(wp.initiate_test, main_screen, stud_screen, lst[i]['assignment_id'],st,lst[i]['time_alloted'] ), 
                width=18, height=1, fg='GREEN', font=('Arial',14,'bold')) 
                
            self.e.grid(row=i, column=3) 



class student:
    
    def __init__(self, roll_no=18325, branch=1, semester=5):
        self.roll_no = roll_no
        self.branch = branch
        self.semester = semester


    def get_assignments(self):
        conn = sqlite3.connect('db.sqlite')
        conn.row_factory = sqlite3.Row
        curr=conn.cursor()
        
        self.final_lst = []

        curr.execute("SELECT * FROM assignments WHERE semester=? AND branch=? AND current_state=1",(self.semester, self.branch))
        assignments = curr.fetchall()

        table_name = "sem_" + str(self.semester) + "_branch_" + str(self.branch) + "_record"
        qry = "SELECT * FROM {} WHERE roll_no={} ".format(table_name, self.roll_no)
        curr.execute(qry)
        rows = curr.fetchall()
        

        
        for row in rows:
            print((dict(row)))
            print("\n")
            student_assignment_data = (dict(row))

        print("LIST OF ALL ACTIVE ASSIGNMENTS")    
        for assignment in assignments:
            print(dict(assignment))
            print("\n\n")
            assign_col = "ASSIGNMENTID_"+str(assignment['assignment_id'])
            if student_assignment_data[assign_col] == 'NS':
                # print(student_assignment_data[assign_col])
                self.final_lst.append(dict(assignment))
        
        curr.close()

        # LIST OF ASSIGNMENTS AVAILABLE FOR THE CURRENT STUDENTS
        for item in self.final_lst:
            print(item)

        return self.final_lst



def on_closing_main(win,main_screen):
    if messagebox.askyesno("Exit", "Do you want to quit the Portal", parent=win):
        win.destroy()
        main_screen.update()
        main_screen.wm_deiconify()


def stud_portal(main_screen,roll_no, branch=1, semester=5):

    st = student(roll_no,branch,semester)

    stud_screen = Toplevel()  

    stud_screen.geometry("950x600") # set the configuration of GUI window 
    stud_screen.title("ADVANCED ASSIGNMENT SYSTEM: A PRODUCT BY CAP_INNOVATIONS") # set the title of GUI window
    
    stud_screen.protocol("WM_DELETE_WINDOW",partial(on_closing_main, stud_screen,main_screen))
    
    Label(stud_screen,relief=RAISED, text='''ADVANCED ASSIGNMENT SYSTEM
        -- A CAPINNOVATIONS PRODUCT''', bg="steelblue", width="500", height="3", font=("Calibri", 18)).pack() 
    Label(text="").pack() 

    scrollbar = Scrollbar(stud_screen)
    scrollbar.pack(side=RIGHT, fill=Y)

    # NEED TO ADD A SCROLLBAR TO THE FRAME VVIP
    
    data_frame = Frame(stud_screen, relief=GROOVE, borderwidth=2,padx=20,pady=20)
    data_frame.pack(fill=BOTH, expand=True)

    lst = st.get_assignments()
    
    # lst = get_assignments(roll_no, branch, semester)
    # print(lst)
       
    # find total number of rows and 
    # columns in list 
    total_rows = len(lst)
    total_columns = 3 

    t = Table(main_screen,stud_screen, data_frame,lst,total_rows,total_columns, st) 

    # stud_screen.mainloop() 



# stud_portal()



