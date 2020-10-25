from tkinter import *
import shutil
from functools import partial
from tkinter import messagebox
import sys
import sqlite3
import submissionData as sa
import  multiprocessing as mp
import time
import speech_recognition as sr
TextArea = "fsd"


class studentWorkspace(Frame):
    def __init__(self,main_screen,  master,set_time,assignment_id, st , time_allocated, *args, **kwargs):
        Frame.__init__(self, master, *args, **kwargs)
        # self.parentWin = student_screen
        self.assignment_id = assignment_id
        self.st = st
        self.time_allocated = time_allocated
        self.master = master
        self.time = set_time
        self.hours = 0
        self.mins = 0
        self.secs = 0
        self.build_interface()
        self.running = True
        self.timer()
        self.main_screen = main_screen
        self.waitScrTxt = '''
            PLEASE WAIT!! 
            UNTIL YOUR ASSIGNMENT GETS SUBMITTED
            DON'T CLOSE THIS WINDOW
            THIS WINDOW WILL AUTOMATICALLY DESTROY!! 
            YOUR ASSIGNMENT WILL BE DOWNLOADED SHORTLY
            IT WILL BE STORED IN THE DOWNLOADS FOLDER
        '''

    def build_interface(self):
        """The interface function."""
        self.clock = Label(self, text="00:00:00", font=("Courier", 20), width=10)
        self.clock.grid(row=1, column=1, stick="S")

        self.time_label = Label(self, text="hour min sec", font=("Courier", 10), width=15)
        self.time_label.grid(row=2, column=1, sticky="N")

    def calculate(self):
        """Calculates the time"""
        self.hours = self.time // 3600
        self.mins = (self.time // 60) % 60
        self.secs = self.time % 60
        return "{:02d}:{:02d}:{:02d}".format(self.hours, self.mins, self.secs)


    def timer(self):
        """Calculates the time to be displayed"""
        if self.running:
            if self.time <= 0:
                self.clock.configure(text="Time's up!")
                self.submit()
            else:
                self.clock.configure(text=self.calculate())
                self.time -= 1
                self.after(1000, self.timer)


    def extract_assignment_data(self):
        conn = sqlite3.connect('db.sqlite')
        curr = conn.cursor()

        curr.execute("SELECT * FROM assignments WHERE assignment_id=?",(self.assignment_id,))
        row = curr.fetchone()

        self.assignment_data = row[2]
        self.teacher_id = row[4]


    def save_in_db(self):
        conn = sqlite3.connect('db.sqlite')
        curr = conn.cursor()    

        mystr = self.Textdata.replace("\n","%10")
        mystr = mystr.replace(" ","%20")
        
        assignment_col_name = "ASSIGNMENTID_"+str(self.assignment_id)+"_DATA"
        table_name = "sem_" + str(self.st.semester) + "_branch_" + str(self.st.branch) + "_record" 
        qry = "UPDATE {} SET {}='{}' WHERE roll_no={}".format(table_name, assignment_col_name, mystr, self.st.roll_no)
        print(qry)
        # curr.execute("UPDATE ? SET ?=? WHERE roll_no=?",(table_name, assignment_col_name, self.Textdata, self.st.roll_no))
        curr.execute(qry)
        conn.commit()
        
        Label(self.master, relief=RAISED, text=self.waitScrTxt, bg="steelblue", width="500", height="12", font=("Calibri", 18)).pack()
        

    def send_for_submission(self):
        time.sleep(1)
        sa.send_submission(self.main_screen,self.master,self.Textdata,self.assignment_id, self.st)

    def submit(self):
        global TextArea
        self.Textdata = (TextArea.get('1.0', END))
        print(self.Textdata)
        # TextArea.forget()
        for widget in self.master.winfo_children():
            widget.destroy()

        # p1 = mp.Process(target=self.show_wait_msg)
        # p2 = mp.Process(target=self.send_for_submission)

        # p1.start()
        # p2.start()
        # self.show_wait_msg()
        self.save_in_db()
        self.send_for_submission()
        
        

def speechRecognizer():
    r = sr.Recognizer()
    response = "kdsjfk"
    mic = sr.Microphone()
    global TextArea
    totResponse =  ""
    while True:
        with mic as source:
            print("Start Speaking....")
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source, timeout=3)
        try:
            response = r.recognize_google(audio)
            TextArea.insert(INSERT, response + ".\n")
            TextArea.pack(expand=YES, fill=BOTH)
        except sr.RequestError:
            # API was unreachable or unresponsive
            # response["success"] = False
            response = "API unavailable, Please Check your Internet Connection!!"
        except sr.UnknownValueError:
            # speech was unintelligible
            response = "Unable to recognize speech"


        print(response)   

        if response == "quit" or response == "stop":
            break
        totResponse = totResponse + response + ".\n"
        
    print(totResponse)


def closs_btn_event():
    pass



def initiate_test(main_screen, student_screen, assignment_id, st, time_allocated):
    
    student_screen.destroy()
    print(assignment_id, st.roll_no, st.branch, st.semester, time_allocated)
    
    # sw.initialize_gui()
    
    win = Toplevel()
    win.title("ADVANCED ASSIGNMENT SYSTEM: WORKSPACE")
    win.geometry("600x600")
    win.overrideredirect(True)
    win.protocol("WM_DELETE_WINDOW",closs_btn_event)

    Label(win, relief=RAISED, text='USER WORKSPACE', bg="steelblue", width="500", height="2", font=("Calibri", 18)).pack() 

    sw = studentWorkspace(main_screen, win,time_allocated * 60,assignment_id, st , time_allocated)

    menu = Menu(win)
    win.config(menu=menu)
    timmer = sw.pack(side="top")

    sw.extract_assignment_data()

    global TextArea 
    TextArea = Text(win)
    TextArea.insert(INSERT, sw.assignment_data)
    ScrollBar = Scrollbar(win)
    ScrollBar.config(command=TextArea.yview)
    TextArea.config(yscrollcommand=ScrollBar.set)
    ScrollBar.pack(side=RIGHT, fill=Y)
    TextArea.pack(expand=YES, fill=BOTH)

    Button(win, text="SPEECH TEXT", bg="steelblue", width="30", height="1",font=("Calibri", 18),command=speechRecognizer).pack()
    Button(win, text="SUBMIT", bg="steelblue", width="30", height="1",font=("Calibri", 18),command=sw.submit).pack()