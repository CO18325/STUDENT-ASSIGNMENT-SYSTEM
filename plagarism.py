import sys
import sqlite3
import os
import nltk
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords


# GET THE REQUIRED DOWNLOAD PATH

def get_download_path():

    if os.name == 'nt':
        import winreg
        sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
        downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
            location = winreg.QueryValueEx(key, downloads_guid)[0]
        return location
    else:
        return os.path.join(os.path.expanduser('~'), 'downloads')

# PLAGARISM CLASS

class Plagarism:
    def __init__(self,branch,semester,assignment_id,assignment_name):
        self.branch = branch
        self.assignment_id = assignment_id
        self.semester = semester
        self.assignment_name = assignment_name


    # LOAD ASSIGNMENTS 
    def load_assignments(self):
        conn = sqlite3.connect('db.sqlite')
        curr = conn.cursor()

        assignment_data_col_name = "ASSIGNMENTID_"+str(self.assignment_id)+"_DATA"
        assignment_sub_col_name = "ASSIGNMENTID_"+str(self.assignment_id)
        table_name = "sem_" + str(self.semester) + "_branch_" + str(self.branch) + "_record" 

        qry = "SELECT roll_no,{} FROM {} WHERE {}='S'".format(assignment_data_col_name,table_name,assignment_sub_col_name)
        curr.execute(qry)

        self.records = curr.fetchall()
        # print(records)

        # for record in self.records:
        #     print(record[0],":--\n",record[1],"\n")

    def change_data_form(self, mystr):
        mystr = mystr.replace("%10","\n")
        mystr = mystr.replace("%20"," ") 
        return mystr   
    
    
    def plag_formula(self,orig , plag):
        
        orig = self.change_data_form(orig)
        plag = self.change_data_form(plag)

        tokens_o=word_tokenize(orig)
        tokens_p=word_tokenize(plag)

        #lowerCase
        tokens_o = [token.lower() for token in tokens_o]
        tokens_p = [token.lower() for token in tokens_p]

        #stop word removal
        #punctuation removal
        stop_words=set(stopwords.words('english'))
        punctuations=['"','.','(',')',',','?',';',':',"''",'``']
        filtered_tokens_o = [w for w in tokens_o if not w in stop_words and not w in punctuations]
        filtered_tokens_p = [w for w in tokens_p if not w in stop_words and not w in punctuations]



        #Trigram Similiarity measures
        trigrams_o=[]
        for i in range(len(tokens_o)-2):
            t=(tokens_o[i],tokens_o[i+1],tokens_o[i+2])
            trigrams_o.append(t)

        s=0
        trigrams_p=[]
        for i in range(len(tokens_p)-2):
            t=(tokens_p[i],tokens_p[i+1],tokens_p[i+2])
            trigrams_p.append(t)
            if t in trigrams_o:
                s+=1
                
        #jaccord coefficient = (S(o)^S(p))/(S(o) U S(p))
        J=s/(len(trigrams_o)+len(trigrams_p)) 
    #     print(J)

        #containment measure
        C=s/len(trigrams_p)
        return C            

    def find_plag(self):
        self.plag_record = []
        self.tot_subissions = len(self.records)
        for i in range(self.tot_subissions - 1):
            for j in range(i+1,self.tot_subissions):
                C = self.plag_formula(self.records[i][1], self.records[j][1])
                if C > 0.5:
                    rec = (self.records[i][0],self.records[j][0],C)
                    self.plag_record.append(rec)   

        print(self.plag_record)

        self.output_str = '''\n\n\t\t\t PLAGARISM REPORT \n
        ASSIGNMENT NAME - {}
        BRANCH - {}
        SEMESTER - {}
        TOTAL SUBMISSIONS - {}\n\n\n
        -------PLAGARISM DATA-------\n\n'''.format(self.assignment_name,self.branch,self.semester,self.tot_subissions)


        for item in self.plag_record:
            temp = "\t{} AND {}  -----  {}% \n".format(item[0],item[1],item[2]*100)
            self.output_str += temp
        
        print(self.output_str)
        
        save_path = get_download_path()

        filename = "PLAGARISM_REPORT"+ "_" + self.assignment_name + ".txt"
        filename = os.path.join(save_path, filename)   
        fhand = open(filename,"w")
        fhand.write(self.output_str)
        fhand.close()



def generate_plag_rep(branch,semester,assignment_id,assignment_name):

    P = Plagarism(branch,semester,assignment_id,assignment_name)

    P.load_assignments()
    P.find_plag()

