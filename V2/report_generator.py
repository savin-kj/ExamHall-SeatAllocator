import json
from fpdf import FPDF, HTMLMixin
import sqlite3 as sq
import itertools

print("Starting Generation")


print("Loading Files")

# importing json data files (inputs)
with open('Halls.json', 'r') as JSON:
    Halls = json.load(JSON)

D_Halls = Halls["D"] # drawing halls
B_Halls = Halls["B"] # bench halls

with open('Subjects.json', 'r') as JSON:
    Subjects = json.load(JSON)

MetaInfo = Subjects.pop("meta") # Meta info global for each generation

print("Generating intermediary DB")

# setting up sqlite DB for processed or sorted data storage ( allocated seats )
conn = sq.connect("report.db")
conn.execute("DROP TABLE IF EXISTS REPORT;")
conn.execute('''CREATE TABLE REPORT
         (ID         CHAR(15)         PRIMARY KEY     NOT NULL,
         CLASS       CHAR(10)                         NOT NULL,
         ROLL        INT                              NOT NULL,
         HALL        TEXT                             NOT NULL,
         SEAT_NO     INT                              NOT NULL,
         SUBJECT     CHAR(50)                         NOT NULL);''')


allocation_done = False
Student_allocated_count=0

Subjects_list = [] # List of subjects
Students_total=0

for i in Subjects:
    Subjects_list.append([len(Subjects[i]),i] + Subjects[i]) # No of students , Sub Name , roll nos ...
    Students_total+=len(Subjects[i])

Subjects_list = sorted(Subjects_list, key = lambda x: x[0],reverse=True) # Sorting by number of students

even_row_subject_list = []
odd_row_subject_list = []

if len(D_Halls) != 0 :

    for i in range(len(Subjects_list)):
        if i%2==0: #even
            even_row_subject_list.append(Subjects_list[i])
        else: #odd
            odd_row_subject_list.append(Subjects_list[i])

    Halls_list = [] # List of halls

    for i in D_Halls:
        #print(i)
        Halls_list.append([D_Halls[i][0],i,D_Halls[i][1]]) # Hall Capacity , Hall name , Hall col size

    Halls_list = sorted(Halls_list, key = lambda x: x[0],reverse=True) # Sorting by capacity 

    Halls_sorted_list = []

    for i in Halls_list:
        if allocation_done == True:
                break
        else:
            Hall_name = i[1]
            Hall_capacity = i[0]
            Hall_cols = i[2]

            a = int(Hall_capacity/Hall_cols)
            b = int(Hall_capacity%Hall_cols)

            Hall_structure = [ [] for x in range(Hall_cols)]

            
            for i in Hall_structure:
                if b>0:
                    k=1
                else:
                    k=0

                i.extend([  [] for x in range(a+k) ])
                b-=1

            counter = 1
            for i in Hall_structure:
                for j in i:
                    j.append(counter)
                    counter+=1

            for i in range(len(Hall_structure)):
                if allocation_done == True:
                    break
                else:
                    for j in range(len(Hall_structure[i])):
                        if i%2 == 0: #even row
                            if len(even_row_subject_list) == 0:
                                pass
                            elif len(Hall_structure[i][j])<3:
                                Hall_structure[i][j].extend([even_row_subject_list[0].pop(2),even_row_subject_list[0][1]])
                                temp_expression = Hall_structure[i][j][1].split("-")
                                conn.execute(f"INSERT INTO REPORT VALUES('{Hall_structure[i][j][1]}','{temp_expression[0]}','{temp_expression[1]}','{Hall_name}','{Hall_structure[i][j][0]}','{Hall_structure[i][j][2]}')")
                                conn.commit()
                                Student_allocated_count+=1
                                even_row_subject_list[0][0]-=1
                                if even_row_subject_list[0][0]==0:
                                    even_row_subject_list.pop(0)

                        else: #odd row
                            if len(odd_row_subject_list) == 0:
                                pass
                            elif len(Hall_structure[i][j])<3:
                                Hall_structure[i][j].extend([odd_row_subject_list[0].pop(2),odd_row_subject_list[0][1]])
                                temp_expression = Hall_structure[i][j][1].split("-")
                                conn.execute(f"INSERT INTO REPORT VALUES('{Hall_structure[i][j][1]}','{temp_expression[0]}','{temp_expression[1]}','{Hall_name}','{Hall_structure[i][j][0]}','{Hall_structure[i][j][2]}')")
                                conn.commit()
                                Student_allocated_count+=1
                                odd_row_subject_list[0][0]-=1
                                if odd_row_subject_list[0][0]==0:
                                    odd_row_subject_list.pop(0)

                        if (len(even_row_subject_list)==0) and (len(odd_row_subject_list)>1):
                            Subjects_list = sorted(odd_row_subject_list, key = lambda x: x[0],reverse=True) # Sorting by number of students

                            even_row_subject_list = []
                            odd_row_subject_list = []

                            for i in range(len(Subjects_list)):
                                if i%2==0: #even
                                    even_row_subject_list.append(Subjects_list[i])
                                else: #odd
                                    odd_row_subject_list.append(Subjects_list[i])

                        if (len(odd_row_subject_list)==0) and (len(even_row_subject_list)>1):
                            Subjects_list = sorted(even_row_subject_list, key = lambda x: x[0],reverse=True) # Sorting by number of students

                            even_row_subject_list = []
                            odd_row_subject_list = []

                            for i in range(len(Subjects_list)):
                                if i%2==0: #even
                                    even_row_subject_list.append(Subjects_list[i])
                                else: #odd
                                    odd_row_subject_list.append(Subjects_list[i])

                        if (len(even_row_subject_list)==0) and (len(odd_row_subject_list)==0):
                            allocation_done = True
                            break

        Halls_sorted_list.append(Hall_structure)

if ( (len(B_Halls) != 0) and (allocation_done==False) ):

    if (even_row_subject_list != [] and odd_row_subject_list != []):
        Subjects_list = even_row_subject_list + odd_row_subject_list
        Subjects_list = sorted(Subjects_list, key = lambda x: x[0],reverse=True) # Sorting by number of students

    even_row_subject_list = []
    odd_row_subject_list = []

    for i in range(len(Subjects_list)):
        if i%2==0: #even
            even_row_subject_list.append(Subjects_list[i])
        else: #odd
            odd_row_subject_list.append(Subjects_list[i])

    Halls_list = [] # List of halls 

    for i in B_Halls:
        Halls_list.append([B_Halls[i][0],i]) # Hall Capacity , Hall name

    Halls_list = sorted(Halls_list, key = lambda x: x[0],reverse=True) # Sorting by capacity 

    for i in Halls_list:
        if allocation_done == True:
                break
        else:
            Hall_name = i[1]
            Hall_capacity = i[0]*2

            for seat in range(1,Hall_capacity+1):
                if seat%2==0: #even
                    if len(even_row_subject_list) == 0:
                        pass
                    else:
                        x = even_row_subject_list[0].pop(2) #roll
                        temp_expression = x.split("-")
                        conn.execute(f"INSERT INTO REPORT VALUES('{x}','{temp_expression[0]}','{temp_expression[1]}','{Hall_name}','{seat}','{even_row_subject_list[0][1]}')")
                        conn.commit()
                        Student_allocated_count+=1
                        even_row_subject_list[0][0]-=1
                        if even_row_subject_list[0][0]==0:
                            even_row_subject_list.pop(0)
                else: #odd
                    if len(odd_row_subject_list) == 0:
                        pass
                    else:
                        x = odd_row_subject_list[0].pop(2) #roll
                        temp_expression = x.split("-")
                        conn.execute(f"INSERT INTO REPORT VALUES('{x}','{temp_expression[0]}','{temp_expression[1]}','{Hall_name}','{seat}','{odd_row_subject_list[0][1]}')")
                        conn.commit()
                        Student_allocated_count+=1
                        odd_row_subject_list[0][0]-=1
                        if odd_row_subject_list[0][0]==0:
                            odd_row_subject_list.pop(0)

                if (len(even_row_subject_list)==0) and (len(odd_row_subject_list)>1):
                    Subjects_list = sorted(odd_row_subject_list, key = lambda x: x[0],reverse=True) # Sorting by number of students

                    even_row_subject_list = []
                    odd_row_subject_list = []

                    for i in range(len(Subjects_list)):
                        if i%2==0: #even
                            even_row_subject_list.append(Subjects_list[i])
                        else: #odd
                            odd_row_subject_list.append(Subjects_list[i])

                if (len(odd_row_subject_list)==0) and (len(even_row_subject_list)>1):
                    Subjects_list = sorted(even_row_subject_list, key = lambda x: x[0],reverse=True) # Sorting by number of students

                    even_row_subject_list = []
                    odd_row_subject_list = []

                    for i in range(len(Subjects_list)):
                        if i%2==0: #even
                            even_row_subject_list.append(Subjects_list[i])
                        else: #odd
                            odd_row_subject_list.append(Subjects_list[i])

                if (len(even_row_subject_list)==0) and (len(odd_row_subject_list)==0):
                    allocation_done = True
                    break

if allocation_done == False:
    print()
    print("Hall capacity insufficient.")
    print("Number of students allocated: ",Student_allocated_count)
    print("Number of students left to allocate: ",Students_total-Student_allocated_count)
    input("\n Enter any key to exit ")

print("Generating PDF")


sessioninfo = MetaInfo["Session_Name"]
sessioninfo = sessioninfo.split()
Date = sessioninfo[0]
Session = sessioninfo[1]

#Functions
def ranges(i):
    for a, b in itertools.groupby(enumerate(i), lambda pair: pair[1] - pair[0]):
        b = list(b)
        yield b[0][1], b[-1][1]
def divide_chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

# fpdf Class definition
class PDF(FPDF, HTMLMixin):
    def footer(self):
        # Set position of the footer
        self.set_y(-15)
        
        text_w=self.get_string_width("Created by ProtoRes")+6
        self.set_x(((self.w - text_w) / 2)+14)

        self.set_font(font, '', 8)
        self.cell(self.get_string_width("Created by "), 10, "Created by ")

        self.set_font(font, 'B', 8)
        self.cell(self.get_string_width("ProtoRes"), 10, "ProtoRes")

        # Page number
        self.set_font('helvetica', '', 8)
        self.cell(0, 10, f'{self.page_no()}/{{nb}}', align='R')

# Creating pdf object for each pdf
pdf1 = PDF('P', 'mm', 'A4')
pdf2 = PDF('P', 'mm', 'A4')
pdf3 = PDF('P', 'mm', 'A4')

# adding fonts
try:
    pdf1.add_font('Poppins', '', 'Fonts/Poppins-Regular.ttf')
    pdf1.add_font('Poppins', 'B', 'Fonts/Poppins-Bold.ttf')
    pdf2.add_font('Poppins', '', 'Fonts/Poppins-Regular.ttf')
    pdf2.add_font('Poppins', 'B', 'Fonts/Poppins-Bold.ttf')
    pdf3.add_font('Poppins', '', 'Fonts/Poppins-Regular.ttf')
    pdf3.add_font('Poppins', 'B', 'Fonts/Poppins-Bold.ttf')
    font="Poppins"
except:
    print("Poppins font not found. Using Helvetica instead.")
    font="Helvetica"

# Notice Board PDF------------------------------------------------------------------------------------------------
# Code
cmd = """SELECT CLASS,HALL,ROLL
         FROM REPORT
         ORDER BY CLASS,HALL"""
cursor = conn.execute(cmd)
Q_list = cursor.fetchall()

PDF_list = [["Class", "Hall", "RollNo"]]
roll_list = []
class_name = Q_list[0][0]
hall_name = Q_list[0][1]

for i in Q_list:
    if class_name == i[0]:

        if hall_name == i[1]:
            roll_list.append(i[2])
        else:
            temp = "("+str(len(roll_list))+")"
            roll_list.append(temp)
            PDF_list.append([class_name, hall_name, roll_list])
            # print(roll_list)
            hall_name = i[1]
            roll_list = []
            roll_list.append(i[2])

    else:
        temp = "("+str(len(roll_list))+")"
        roll_list.append(temp)
        PDF_list.append([class_name, hall_name, roll_list])
        # print(roll_list)
        class_name = i[0]
        hall_name = i[1]
        roll_list = []
        roll_list.append(i[2])

    if Q_list[-1] == i:
        temp = "("+str(len(roll_list))+")"
        roll_list.append(temp)
        PDF_list.append([class_name, hall_name, roll_list])

pdf1.set_auto_page_break(auto = True, margin = 15) # Auto page break
pdf1.add_page()

pdf1.set_font(font, '', 27)
text="Marian Engineering College"
text_w=pdf1.get_string_width(text)+6
doc_w=pdf1.w
pdf1.set_x((doc_w - text_w) / 2)
pdf1.cell(text_w, 23, text,  new_x="LMARGIN", new_y="NEXT", align='C')

pdf1.set_font(font, '', 21)
text="Halls for Internal Examination"
text_w=pdf1.get_string_width(text)+6
pdf1.set_x((doc_w - text_w) / 2)
pdf1.cell(text_w, 7, text,  new_x="LMARGIN", new_y="NEXT", align='C')

text_w=pdf1.get_string_width("Date: 12-04-2022         Session: FN")
pdf1.set_x(((doc_w - text_w) / 2)+10.5)

pdf1.set_font(font, '', 17)
pdf1.cell(pdf1.get_string_width("Date:"), 14, 'Date:', align='C')
pdf1.set_font(font, 'B', 17)
pdf1.cell(pdf1.get_string_width(Date), 14, Date)
pdf1.set_font(font, '', 17)
pdf1.cell(pdf1.get_string_width("         Session: "), 14, '         Session: ')
pdf1.set_font(font, 'B', 17)
pdf1.cell(pdf1.get_string_width(Session), 14, Session,  new_x="LMARGIN", new_y="NEXT")

#Create Table Header
pdf1.set_font(font, 'B', 12)
pdf1.cell(22.1, 10, "Class", align='C', border=True)
pdf1.cell(18.5, 10, "Hall", align='C', border=True)
pdf1.cell(0, 10, "Roll No.s", align='C', border=True, new_x="LMARGIN", new_y="NEXT")

# Create Table Body
prev_class=""
PDF_list.pop(0)
for i in PDF_list:
    temp="   "
    rows=1
    temp_count=1
    
    roll_list=[]
    roll_list.append(i[2])
    for j in roll_list[0]:
        if temp_count==20:  #to split rows
            temp+="\n   "
            rows+=1
            temp_count=1
        if j==roll_list[0][-1]:
            temp+=str(j)
        elif j==roll_list[0][-2]:
            temp+=(str(j)+"  ")
        else:
            temp+=(str(j)+", ")
        temp_count+=1

    curr_class=i[0]
    height=rows*12

    pdf1.set_font(font, 'B', 11)
    if prev_class==curr_class:
        pdf1.cell(22.1, height, '"', align='C', border=True)
    else:
        pdf1.cell(22.1, height, curr_class, align='C', border=True)
    prev_class=curr_class
    pdf1.set_font(font, '', 11)
    pdf1.cell(18.5, height, i[1], align='C', border=True, new_x="RIGHT")

    pdf1.multi_cell(0, height/rows, temp, new_x="LMARGIN", new_y="NEXT", border=True, align="L")

file_name="Halls "+Date+" "+Session+".pdf"
pdf1.output(file_name)


# Packaging List PDF------------------------------------------------------------------------------------------------
pdf2.set_auto_page_break(auto = True, margin = 15) # Auto page break
# code
cmd = """SELECT HALL,CLASS,SUBJECT,ROLL
         FROM REPORT
         ORDER BY HALL,CLASS, SUBJECT"""
cursor = conn.execute(cmd)
Q_list = cursor.fetchall()

cmd = """SELECT HALL,COUNT(ROLL)
         FROM REPORT
         GROUP BY HALL"""
cursor = conn.execute(cmd)
R_list = cursor.fetchall()

PDF_list = [["Class", "Subject", "RollNo", "No. of candidates"]]
roll_list = []
hall_name = Q_list[0][0]
class_name = Q_list[0][1]
subject_name = Q_list[0][2]

for i in Q_list:
    if hall_name == i[0]:
        if class_name == i[1]:

            if subject_name == i[2]:
                roll_list.append(i[3])

            else:
                roll_ = ranges(roll_list)
                no_of_candidates = len(roll_list)
                PDF_list.append([class_name, subject_name, str(list(roll_))[1:-1], no_of_candidates])
                subject_name = i[2]
                roll_list = []
                roll_list.append(i[3])

        else:
            roll_ = ranges(roll_list)
            no_of_candidates = len(roll_list)
            PDF_list.append([class_name, subject_name, str(list(roll_))[1:-1], no_of_candidates])
            class_name = i[1]
            subject_name = i[2]
            roll_list = []
            roll_list.append(i[3])

    else:
        # append , PDF Generate and empty pdf list
        roll_ = ranges(roll_list)
        no_of_candidates = len(roll_list)
        PDF_list.append([class_name, subject_name, str(list(roll_))[1:-1], no_of_candidates])

        pdf2.add_page()
        pdf2.set_font(font, '', 27)
        text="Marian Engineering College"
        text_w=pdf2.get_string_width(text)+6
        pdf2.w=pdf2.w
        pdf2.set_x((pdf2.w - text_w) / 2)
        pdf2.cell(text_w, 23, text,  new_x="LMARGIN", new_y="NEXT", align='C')

        pdf2.set_font(font, '', 20)
        text="Packing List for Internal Examination"
        text_w=pdf2.get_string_width(text)+6
        pdf2.set_x((pdf2.w - text_w) / 2)
        pdf2.cell(text_w, 10, text,  new_x="LMARGIN", new_y="NEXT", align='C')

        pdf2.set_y(45)
        pdf2.set_font(font, '', 18)
        pdf2.set_x(30)
        pdf2.write_html(f"<align=\"center\">Hall No: <b>{hall_name}</b>      Date: <b>{Date}</b>      Session: <b>{Session}<b/>")
        pdf2.cell(0, 15, "", new_x="LMARGIN", new_y="NEXT")

        #Create Table Header
        pdf2.set_font(font, 'B', 10)
        pdf2.set_y(60)
        class_w=pdf2.get_string_width("Class")+8
        pdf2.cell(class_w, 20, "Class", align='C', border=True)
        pdf2.cell(65, 20, "Subject", align='C', border=True)
        pdf2.cell(30, 20, "", align='C', border=True)
        pdf2.set_y(66.1)
        pdf2.set_x(class_w+65+14)
        pdf2.write_html("<b>Roll No.s of</b>")
        pdf2.set_y(71.1)
        pdf2.set_x(class_w+65+13.1)
        pdf2.write_html("<b>Candidates</b>")

        pdf2.set_y(60)
        pdf2.set_x(class_w+65+30+10)
        pdf2.cell(30, 20, "", align='C', border=True)
        pdf2.set_y(66.1)
        pdf2.set_x(class_w+65+14+35)
        pdf2.write_html("<b>No. of</b>")
        pdf2.set_y(71.1)
        pdf2.set_x(class_w+65+13.1+30)
        pdf2.write_html("<b>Candidates</b>")
        
        pdf2.set_y(60)
        pdf2.set_x(class_w+65+30+10+30)
        pdf2.cell(0, 20, "", align='C', border=True, new_x="LMARGIN", new_y="NEXT")
        pdf2.set_y(66.1)
        pdf2.set_x(class_w+65+14+35+34)
        pdf2.write_html("<b>Roll No.s of</b>")
        pdf2.set_y(71.1)
        pdf2.set_x(class_w+65+13.1+30+40)
        pdf2.write_html("<b>Absentees</b>")

        #Create Table Body
        y_pos=80
        pdf2.set_y(80)
        pdf2.set_x(10)
        prev_class=""
        PDF_list.pop(0)
        for k in PDF_list:
            sub_rows=1
            sub_flag=0
            if len(k[1])>30:
                sub_rows=2
                sub_flag=1

            roll_range_raw=k[2]
            temp1=""
            a=[]
            for m in roll_range_raw:
                if m.isdigit():
                    temp1+=m
                elif m==',':
                    temp1+=','
                elif m=='(':
                    temp1=""
                elif m==')':
                    a.append(temp1)
            roll_rows=len(a)
            roll_flag=0
            if roll_rows>1:
                roll_flag=1
            
            temp1=""
            for m in a:
                x=m.split(',')
                if x[0]==x[1]:
                    temp1+=x[0]+"\n"
                else:
                    temp1+=x[0]+"-"+x[1]+"\n"
            temp1=temp1[:-1]
            rows=max(sub_rows,roll_rows)
            height=10*rows
            pdf2.set_font(font, '', 10)

            curr_class=k[0]
            if prev_class==curr_class:
                pdf2.cell(class_w, height, '"', align='C', border=True) # Class
            else:
                pdf2.cell(class_w, height, curr_class, align='C', border=True) # Class
            prev_class=curr_class
            if sub_flag==0:
                pdf2.multi_cell(65, height, k[1], align='C', border=True) # Subject when subject is one line only
            elif sub_flag==1 and roll_flag==0:
                pdf2.multi_cell(65, 10, k[1], align='C', border=True) # Subject when subject is two line but roll no range is only one line
            elif sub_flag==1 and roll_flag==1:
                pdf2.multi_cell(65, (10*rows)/2, k[1], align='C', border=True) # Subject subject is 2 line and roll range is also multi line
            else:
                pdf2.multi_cell(65, 10, k[1], align='C', border=True) # Subject in other cases

            pdf2.set_y(y_pos)
            pdf2.set_x(pdf2.w-(pdf2.w-(18.061+65))+10)
            if sub_flag==1 and roll_flag==0:
                pdf2.multi_cell(30, height, temp1, align='C', border=True) # Roll no range when sub is 2 line and roll range is one line
            else:
                pdf2.multi_cell(30, 10, temp1, align='C', border=True) # Roll no range
            pdf2.set_y(y_pos)
            pdf2.set_x(class_w+65+30+10)

            pdf2.cell(30, height, str(k[3]), align='C', border=True) # No of candidates
            pdf2.cell(0, height, "", border=True, new_x="LMARGIN", new_y="NEXT") # Absentees blank column
            y_pos+=height
        
        pdf2.set_font(font, 'B', 10)
        pdf2.cell(class_w+65+30, 10, "Total:", border=True, align="C") # Total
        for l in R_list:
            if l[0]==hall_name:
                pdf2.cell(30, 10, str(l[1]), border=True, align="C") # Total count
        pdf2.cell(0, 10, "", border=True, new_x="LMARGIN", new_y="NEXT") # Final blank cell

        y_pos+=25
        pdf2.set_y(y_pos)
        pdf2.set_font(font, '', 15)
        pdf2.write_html("<U>Invigilators must</U>:")
        pdf2.write_html("<br><br>     1.  Ensure that all candidates have ID-Cards & are in proper uniform.")
        pdf2.write_html("<br><br>     2. Announce that mobile phones, smartwatches & other electronic")
        y_pos+=23
        pdf2.set_y(y_pos)
        pdf2.write_html("<br>         gadgets, pouches, bags, calculator-cover etc. are <B>NOT</B> allowed")
        y_pos+=8
        pdf2.set_y(y_pos)
        pdf2.write_html("<br>         inside.")
        
        PDF_list = [["Class", "Subject", "RollNo", "No. of candidates"]]

        hall_name = i[0]
        class_name = i[1]
        roll_list = []
        roll_list.append(i[3])

    if Q_list[-1] == i:
        roll_ = ranges(roll_list)
        no_of_candidates = len(roll_list)
        PDF_list.append([class_name, subject_name, str(list(roll_))[1:-1], no_of_candidates])
        
        pdf2.add_page()
        pdf2.set_font(font, '', 27)
        text="Marian Engineering College"
        text_w=pdf2.get_string_width(text)+6
        pdf2.w=pdf2.w
        pdf2.set_x((pdf2.w - text_w) / 2)
        pdf2.cell(text_w, 23, text,  new_x="LMARGIN", new_y="NEXT", align='C')

        pdf2.set_font(font, '', 20)
        text="Packing List for Internal Examination"
        text_w=pdf2.get_string_width(text)+6
        pdf2.set_x((pdf2.w - text_w) / 2)
        pdf2.cell(text_w, 10, text,  new_x="LMARGIN", new_y="NEXT", align='C')

        pdf2.set_y(45)
        pdf2.set_font(font, '', 18)
        pdf2.set_x(30)
        pdf2.write_html(f"<align=\"center\">Hall No: <b>{hall_name}</b>      Date: <b>{Date}</b>      Session: <b>{Session}<b/>")
        pdf2.cell(0, 15, "", new_x="LMARGIN", new_y="NEXT")

        #Create Table Header
        pdf2.set_font(font, 'B', 10)
        pdf2.set_y(60)
        class_w=pdf2.get_string_width("Class")+8
        pdf2.cell(class_w, 20, "Class", align='C', border=True)
        pdf2.cell(65, 20, "Subject", align='C', border=True)
        pdf2.cell(30, 20, "", align='C', border=True)
        pdf2.set_y(66.1)
        pdf2.set_x(class_w+65+14)
        pdf2.write_html("<b>Roll No.s of</b>")
        pdf2.set_y(71.1)
        pdf2.set_x(class_w+65+13.1)
        pdf2.write_html("<b>Candidates</b>")

        pdf2.set_y(60)
        pdf2.set_x(class_w+65+30+10)
        pdf2.cell(30, 20, "", align='C', border=True)
        pdf2.set_y(66.1)
        pdf2.set_x(class_w+65+14+35)
        pdf2.write_html("<b>No. of</b>")
        pdf2.set_y(71.1)
        pdf2.set_x(class_w+65+13.1+30)
        pdf2.write_html("<b>Candidates</b>")
        
        pdf2.set_y(60)
        pdf2.set_x(class_w+65+30+10+30)
        pdf2.cell(0, 20, "", align='C', border=True, new_x="LMARGIN", new_y="NEXT")
        pdf2.set_y(66.1)
        pdf2.set_x(class_w+65+14+35+34)
        pdf2.write_html("<b>Roll No.s of</b>")
        pdf2.set_y(71.1)
        pdf2.set_x(class_w+65+13.1+30+40)
        pdf2.write_html("<b>Absentees</b>")

        #Create Table Body
        y_pos=80
        pdf2.set_y(80)
        pdf2.set_x(10)
        prev_class=""
        PDF_list.pop(0)
        for k in PDF_list:
            sub_rows=1
            sub_flag=0
            if len(k[1])>30:
                sub_rows=2
                sub_flag=1

            roll_range_raw=k[2]
            temp1=""
            a=[]
            for m in roll_range_raw:
                if m.isdigit():
                    temp1+=m
                elif m==',':
                    temp1+=','
                elif m=='(':
                    temp1=""
                elif m==')':
                    a.append(temp1)
            roll_rows=len(a)
            roll_flag=0
            if roll_rows>1:
                roll_flag=1
            
            temp1=""
            for m in a:
                x=m.split(',')
                if x[0]==x[1]:
                    temp1+=x[0]+"\n"
                else:
                    temp1+=x[0]+"-"+x[1]+"\n"
            temp1=temp1[:-1]
            rows=max(sub_rows,roll_rows)
            height=10*rows
            pdf2.set_font(font, '', 10)

            curr_class=k[0]
            if prev_class==curr_class:
                pdf2.cell(class_w, height, '"', align='C', border=True) # Class
            else:
                pdf2.cell(class_w, height, curr_class, align='C', border=True) # Class
            prev_class=curr_class
            if sub_flag==0:
                pdf2.multi_cell(65, height, k[1], align='C', border=True) # Subject when subject is one line only
            elif sub_flag==1 and roll_flag==0:
                pdf2.multi_cell(65, 10, k[1], align='C', border=True) # Subject when subject is two line but roll no range is only one line
            elif sub_flag==1 and roll_flag==1:
                pdf2.multi_cell(65, (10*rows)/2, k[1], align='C', border=True) # Subject subject is 2 line and roll range is also multi line
            else:
                pdf2.multi_cell(65, 10, k[1], align='C', border=True) # Subject in other cases

            pdf2.set_y(y_pos)
            pdf2.set_x(pdf2.w-(pdf2.w-(18.061+65))+10)
            if sub_flag==1 and roll_flag==0:
                pdf2.multi_cell(30, height, temp1, align='C', border=True) # Roll no range when sub is 2 line and roll range is one line
            else:
                pdf2.multi_cell(30, 10, temp1, align='C', border=True) # Roll no range
            pdf2.set_y(y_pos)
            pdf2.set_x(class_w+65+30+10)

            pdf2.cell(30, height, str(k[3]), align='C', border=True) # No of candidates
            pdf2.cell(0, height, "", border=True, new_x="LMARGIN", new_y="NEXT") # Absentees blank column
            y_pos+=height
        
        pdf2.set_font(font, 'B', 10)
        pdf2.cell(class_w+65+30, 10, "Total:", border=True, align="C") # Total
        for l in R_list:
            if l[0]==hall_name:
                pdf2.cell(30, 10, str(l[1]), border=True, align="C") # Total count
        pdf2.cell(0, 10, "", border=True, new_x="LMARGIN", new_y="NEXT") # Final blank cell

        y_pos+=25
        pdf2.set_y(y_pos)
        pdf2.set_font(font, '', 15)
        pdf2.write_html("<U>Invigilators must</U>:")
        pdf2.write_html("<br><br>     1.  Ensure that all candidates have ID-Cards & are in proper uniform.")
        pdf2.write_html("<br><br>     2. Announce that mobile phones, smartwatches & other electronic")
        y_pos+=23
        pdf2.set_y(y_pos)
        pdf2.write_html("<br>         gadgets, pouches, bags, calculator-cover etc. are <B>NOT</B> allowed")
        y_pos+=8
        pdf2.set_y(y_pos)
        pdf2.write_html("<br>         inside.")

        PDF_list = []

file_name="Packaging "+Date+" "+Session+".pdf"
pdf2.output(file_name)


# Seating List PDF------------------------------------------------------------------------------------------------
pdf3.set_auto_page_break(auto = True, margin = 15) # Set auto page break

cmd = """SELECT DISTINCT HALL , CLASS
         FROM REPORT
         ORDER BY HALL"""
cursor = conn.execute(cmd)
x = cursor.fetchall()
distinct_class = []
for i in x:
    distinct_class.append(list(i))

cmd = """SELECT HALL,SEAT_NO,ID
         FROM REPORT
         ORDER BY HALL,SEAT_NO"""
cursor = conn.execute(cmd)
x = cursor.fetchall()
query_list = []
for i in x:
    query_list.append(list(i))

hall_distinct_list = [[distinct_class[0][0]]]
hall = query_list[0][0]
hall_check_for_distinct = distinct_class[0][0]

for i in distinct_class:
    if hall_check_for_distinct == i[0]:
        if i[1] not in hall_distinct_list:
            hall_distinct_list[-1].append(i[1])
    else:
        if i[1] not in hall_distinct_list[-1]:
            hall_distinct_list[-1].append(i[1])
        hall_check_for_distinct = i[0]
        hall_distinct_list.append(i)

# print distinct
for i in hall_distinct_list:
    seat_List = [["Seat", "RollNo"]]
    hall = i[0]
    for j in query_list:
        if hall == j[0]:
            seat_List.append([j[1], j[2]])
    last_seat_no=seat_List[-1][0]
    for k in range(1, last_seat_no+1):
        if seat_List[k][0]!=k:
            seat_List.insert(k, [k, "-"])
    classes_list = i[1:]
    
    seat_List.pop(0)
    seat_List=divide_chunks(seat_List, ((int(len(seat_List)/4))+1))
    x=list(seat_List)

    # Headings
    pdf3.add_page()
    pdf3.set_font(font, '', 27)
    text="Marian Engineering College"
    text_w=pdf3.get_string_width(text)+6
    pdf3.w=pdf3.w
    pdf3.set_x((pdf3.w - text_w) / 2)
    pdf3.cell(text_w, 23, text,  new_x="LMARGIN", new_y="NEXT", align='C')
    pdf3.set_font(font, '', 20)
    text="Seating Arrangement for Internal Examination"
    text_w=pdf3.get_string_width(text)+6
    pdf3.set_x((pdf3.w - text_w) / 2)
    pdf3.cell(text_w, 10, text,  new_x="LMARGIN", new_y="NEXT", align='C')
    pdf3.set_y(45)
    pdf3.set_font(font, '', 18)
    pdf3.set_x(30)
    pdf3.write_html(f"<align=\"center\">Hall No: <b>{hall}</b>      Date: <b>{Date}</b>      Session: <b>{Session}<b/>")
    pdf3.cell(0, 15, "", new_x="LMARGIN", new_y="NEXT")

    # Class List Table
    col1_width=((pdf3.w-20)/(len(classes_list)+1))+15
    col_rest_width=(pdf3.w-20-col1_width)/len(classes_list)
    pdf3.set_font(font, '', 14)
    pdf3.cell(col1_width, 11, "Classes:", border=True, align="C")
    pdf3.set_font(font, 'B', 14)
    for k in classes_list:
        pdf3.cell(col_rest_width, 11, k, border=True, align="C")
    pdf3.set_y(76)

    # Seating Table
    # Header
    seat_w=((pdf3.w-20-15)/4)*0.4
    id_w=((pdf3.w-20-15)/4)*0.6

    # Body
    pdf3.set_font(font, '', 12)
    roll_rows=len(x[0])
    counter=x[-1][-1][0]
    for k in range(roll_rows):
        if k%19==0:
            if k!=0:
                pdf3.add_page()
            pdf3.set_font(font, 'B', 12)
            for n in range(4):
                pdf3.cell(seat_w, 10, "Seat", border=True, align="C")
                if n!=3:
                    pdf3.cell(id_w, 10, "Roll No.", border=True, align="C")
                    pdf3.cell(5, 10, "", border=False, align="C")
                else:
                    pdf3.cell(id_w, 10, "Roll No.", border=True, align="C", new_x="LMARGIN", new_y="NEXT")
        pdf3.set_font(font, '', 12)
        for l in range(4):
            try:
                pdf3.cell(seat_w, 10, str(x[l][k][0]), border=True, align="C")
                if l!=3:
                    pdf3.cell(id_w, 10, str(x[l][k][1]), border=True, align="C")
                    pdf3.cell(5, 10, "", border=False, align="C")
                else:
                    pdf3.cell(id_w, 10, str(x[l][k][1]), border=True, align="C", new_x="LMARGIN", new_y="NEXT")
            except:
                counter+=1
                pdf3.cell(seat_w, 10, str(counter), border=True, align="C")
                pdf3.cell(id_w, 10, "-", border=True, align="C", new_x="LMARGIN", new_y="NEXT")
file_name="Seating "+Date+" "+Session+".pdf"
pdf3.output(file_name)

print("Done")