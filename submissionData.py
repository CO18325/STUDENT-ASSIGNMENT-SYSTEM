from tkinter import *
import shutil
from functools import partial
from tkinter import messagebox
import sys
import sqlite3
import os
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def get_download_path():
    """Returns the default downloads path for linux or windows"""
    if os.name == 'nt':
        import winreg
        sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
        downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
            location = winreg.QueryValueEx(key, downloads_guid)[0]
        return location
    else:
        return os.path.join(os.path.expanduser('~'), 'downloads')







def closs_btn_event():
    pass

def send_submission(main_screen, workpad_screen, Textdata, assignment_id, st):
    print(Textdata,assignment_id)


    conn = sqlite3.connect('db.sqlite')
    curr = conn.cursor()

    curr.execute("SELECT * FROM assignments WHERE assignment_id=?",(assignment_id,))

    row = curr.fetchone()

    if row[3] == 0:
        print("ASSIGNMENT IS CLOSED BY THE TEACHER")
        # SHOW A MESSAGE BOX
        # win.destroy
        messagebox.showinfo("FAILURE MESSGAE","TEACHER HAS CLOSED THE ASSIGNMENT",parent=workpad_screen)


    else:
        assignment_name = row[1]
        # TRY TO SAVE IN A PDF FORMAT
        resData = Textdata
        save_path = get_download_path()
        filename = str(st.roll_no)+ "_" + assignment_name + ".txt"
        filename = os.path.join(save_path, filename)   
        fhand = open(filename,"w")
        fhand.write(resData)
        fhand.close()
        assignment_col_name = "ASSIGNMENTID_"+str(assignment_id)
        table_name = "sem_" + str(st.semester) + "_branch_" + str(st.branch) + "_record" 
        qry = "UPDATE {}  SET {}='S' WHERE roll_no={}".format(table_name,assignment_col_name,st.roll_no)
        curr.execute(qry)
        conn.commit()
        teacher_id = row[4]
        curr.execute("SELECT * FROM teachers WHERE teacher_id=?",(teacher_id,))
        teachrow = curr.fetchone()
        teacher_email = teachrow[3]
        teacher_name = teachrow[1]
        print(teacher_email)
        send_response(teacher_email,teacher_name,assignment_name,st,filename)
        messagebox.showinfo("SUCCESS MESSGAE","ASSIGNMENT SUBMITTED SUCCESSFULLY",parent=workpad_screen)

    
      
    workpad_screen.destroy()
    main_screen.update()
    main_screen.wm_deiconify()


 

def send_response(teacher_email, teacher_name, assignment_name, st,filename):
    
    subject = "SUBMISSION OF {} FOR {}".format(st.roll_no,assignment_name)
    # NEED TO FORM A HTML BODY
    if st.branch == 1:
        branch_name = 'CSE'
    elif st.branch ==2:
        branch_name = 'ECE'
    elif st.branch == 3:
        branch_name = 'MECH'
    elif st.branch == 4:
        branch_name = 'CIVIL'
    body = '''
        Greetings {},
            Please find the attached response of {}
            of Branch {} and Semester {}
            for the assignment {}
    '''.format(teacher_name,st.roll_no, branch_name, st.semester, assignment_name)
    sender_email = "capinnovations3000@gmail.com"
    receiver_email = teacher_email
    # FIND SOME METHOD TO SAFEGAURD PASSWORD 
    password = 'peggycarter'

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email  # Recommended for mass emails

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    # filename = "document.pdf"  # In same directory as script

    # Open PDF file in binary mode
    with open(filename, "rb") as attachment:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    # Encode file in ASCII characters to send by email    
    encoders.encode_base64(part)

    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )

    # Add attachment to message and convert message to string
    message.attach(part)
    text = message.as_string()

    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)    



