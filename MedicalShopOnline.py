from tkinter import *
import re
import itertools
from functools import *
import mysql.connector
from fpdf import FPDF
from datetime import datetime 

#*****database connection 
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="",
)

print(mydb) 
mycursor = mydb.cursor()

mycursor.execute("create database if not exists mydatabase") #create database name mydatabase if already not exist
mydb.database ="mydatabase"    #select current database to access as mydatabase
#*******
#mycursor.execute("DROP TABLE customers")   # drops customers table at start
#mycursor.execute("DROP TABLE admins")
#mycursor.execute("DROP TABLE products")
#mycursor.execute("DROP TABLE VariableCount")
#****create tables for database if  tables not exist
mycursor.execute("CREATE TABLE if not exists customers (fname VARCHAR(50),lname VARCHAR(50),email VARCHAR(50),mobno VARCHAR(50),gender VARCHAR(10),dob VARCHAR(10),client VARCHAR(10),pass VARCHAR(30), address VARCHAR(255))")
mycursor.execute("CREATE TABLE if not exists admins (fname VARCHAR(50),lname VARCHAR(50),email VARCHAR(50),mobno VARCHAR(50),gender VARCHAR(10),dob VARCHAR(10),client VARCHAR(10),pass VARCHAR(30), address VARCHAR(255))")
mycursor.execute("CREATE TABLE if not exists products (itemid INT,iname VARCHAR(50),quantity INT,eachprice INT,mfgname VARCHAR(50),description VARCHAR(255),mfgdate VARCHAR(10),expdate VARCHAR(10),unit VARCHAR(10))")
mycursor.execute("CREATE TABLE if not exists OrdersTable (email VARCHAR(50),invoice_no VARCHAR(50),discount INT,address VARCHAR(255),mobno VARCHAR(10),cname VARCHAR(30),paymode VARCHAR(10))")
mycursor.execute("CREATE TABLE if not exists InvoiceTable (invoice_no VARCHAR(50),iname VARCHAR(50),quantity INT,eachprice INT)")
mycursor.execute("CREATE TABLE if not exists CardInfo (invoice_no VARCHAR(50),cardno VARCHAR(20))")
mycursor.execute("CREATE TABLE if not exists VariableCount (rowcount INT)")

#start count from 0 after droping table
#mycursor.execute("INSERT INTO VariableCount (rowcount) VALUES(0)")
#mydb.commit()

mycursor.execute("SELECT *FROM admins")
myresult = mycursor.fetchall()
print("From admins")
for x in myresult:
    print(x)

mycursor.execute("SELECT *FROM customers")
myresult = mycursor.fetchall()
print("From customers")
for x in myresult:
    print(x)


item_no=-1
items_dict = {}
#*******fetch data from database to items_dict
def fetch_data_from_db():
    global item_no,items_dict
    print("from products table")
    mycursor.execute("SELECT *FROM products")
    myresult = mycursor.fetchall()
    item_no=-1
    items_dict = {}
    for x in myresult:
        item_no +=1
        items_dict[item_no] = {}
        items_dict[item_no]['item_id'] =x[0]
        items_dict[item_no]['item_name']=x[1]
        items_dict[item_no]['quantity']=x[2]
        items_dict[item_no]['each_price']=x[3]
        items_dict[item_no]['mfg_name']=x[4]
        items_dict[item_no]['description']=x[5]
        
        print(items_dict)    
        print(x)
    print("Fetching from db to dict is completed successfully")
fetch_data_from_db()

#****current client info
current_email =""
current_name =""
current_lname =""
current_mob=""
current_pay_mode=""
#labels_destroyed=False
current_invoice_no=""
invoice_pt1="A51D289E1A679N"
current_add =""
row_id = 0


#******Discount code dictionary
disc_dict={}
disc_dict['MED50']=50
disc_dict['FREE20']=20
disc_dict['FREE10']=10

def test3():
    print(address.get("1.0","end-1c"))

def item_search():
    found=0
    print(search_text.get())
    if len(search_text.get())==0:
        add_item_to_store_from_dict()
        found=1
    else:
        for no in range(0,item_no+1):
            if no in items_dict:
                print("valid item index")
                if items_dict[no]['item_name'] == search_text.get():
                    print(items_dict[no])
                    print("found")
                    found=1
                    myframe.destroy()
                    create_center_items_list()
                    r=0
                    item_widget(items_dict[no]['item_id'],items_dict[no]['item_name'],items_dict[no]['description'],items_dict[no]['each_price'],items_dict[no]['mfg_name'])
                    break
            else:
                print("invalid store index")
    if found ==0:
        invoice_for_search_bar(search_text.get())
    return True

def create_search_bar():
    global search_frame,search_text
    search_frame = Frame(test1,relief=GROOVE, width=480,height=40,bg="red")
    search_frame.place(x=200,y=55)

    search_text = Entry(search_frame,width=40,font = ("Calibri",13))
    search_text.grid(row=0,column=0,sticky=W+E+N+S)
    Button(search_frame,text="Search",bg="DarkOliveGreen3", width=15, font = ("Calibri",13),command=item_search).grid(row=0, column=1,columnspan=1,sticky=W+E+S+N)

    


def user_logout():
    global Admin,current_login,cart_dict,cart_index
    if not Admin:
        myframe2.destroy()
        cart_option.destroy()
        del cart_dict
        cart_index=-1
    nav_frame.destroy()
    myframe.destroy()

    Admin=False
    current_login=False
    print(Admin)
    create_nav_menu()

    create_center_items_list()
    add_item_to_store_from_dict()    
#    create_cart()

    return True
def total_items_in_cart(): #this returns total items in cart
    total_items=0
    for i in range(0,cart_index+1):
        if i in cart_dict:
            total_items+=1
    print("Total items in cart is: "+str(total_items))
    if total_items ==0:
        return 0
    else:
        return total_items
def total_price_of_cart(): #this fn return total cost of cart
    cart_total=0
    for i in range(0,cart_index+1):
        if i in cart_dict:
            cart_total += cart_dict[i]['quantity']*cart_dict[i]['each_price']

    print("Total price of cart is: "+str(cart_total))
    if cart_total ==0:
        return 0
    else:
        return cart_total
    
def add_item_to_cart_from_dict():  #add cart item widget to cart widget from cart dictionary
    for i in range(0,cart_index+1):
        if i in cart_dict:
            cart_item_widget(cart_dict[i]['item_id'],cart_dict[i]['item_name'],cart_dict[i]['quantity'],cart_dict[i]['each_price'])

def delete_item_from_cart(item_id):
    for no in range(0,cart_index+1):
        if no in cart_dict:
            print("valid cart index")
            if cart_dict[no]['item_id'] == item_id:
                print(cart_dict[no])
                print("found")
                total_items_in_cart()
                print("Deleted item from cart at index: "+str(no))
                del cart_dict[no]
                total_items_in_cart()
                print(cart_dict)
                myframe2.destroy()
                create_cart()
                cart_r=0
                add_item_to_cart_from_dict()
                update_cart_values()
                break
        else:
            print("invalid cart index")
    return True

#**********center list fucntions**********
def total_items_in_store():
    total_items=0
    for i in range(0,item_no+1):
        if i in items_dict:
            total_items+=1
    print("Total items in store is: "+str(total_items))

def add_item_to_store_from_dict():
    myframe.destroy()
    create_center_items_list()
    for i in range(0,item_no+1):
        if i in items_dict:
            item_widget(items_dict[i]['item_id'],items_dict[i]['item_name'],items_dict[i]['description'],items_dict[i]['each_price'],items_dict[i]['mfg_name'])

def delete_item_from_store(item_id):
    global items_dict
    for no in range(0,item_no+1):
        if no in items_dict:
            print("valid item index")
            if items_dict[no]['item_id'] == item_id:
                print(items_dict[no])
                print("found")
                total_items_in_cart()
                print("Deleted item from store at index: "+str(no))

                iteminfo = items_dict[no]['item_id']
                sql = "DELETE FROM products WHERE itemid =%s "
                adr = (iteminfo,)
                print("item info for deleted item is : "+str(iteminfo))
                mycursor.execute(sql,adr)
                mydb.commit()
        
                del items_dict
                fetch_data_from_db()
                
                total_items_in_store()
                print(items_dict)
                myframe.destroy()
                create_center_items_list()
                r=0
                add_item_to_store_from_dict()
    return True
#************
def verify_login_db(ltype):
    global current_email,current_name,current_lname,current_mob,current_add
    print("login type : "+ltype)
    if ltype =="Admin":
        mycursor.execute("SELECT fname,lname,email,mobno,address,pass FROM admins")
        myresult = mycursor.fetchall()

        for x in myresult:
            if l_email.get() in x and l_pass.get() in x:
                current_email=x[2]
                current_name=x[0]
                current_lname=x[1]
                current_mob = x[3]
                current_add = x[4]
                return True

    elif ltype =="User":
        mycursor.execute("SELECT fname,lname,email,mobno,address,pass FROM customers")
        myresult = mycursor.fetchall()

        for x in myresult:
            if l_email.get() in x and l_pass.get() in x:
                current_email=x[2]
                current_name=x[0]
                current_lname=x[1]
                current_mob = x[3]
                current_add = x[4]
                return True
    else:
        return False

def login():
    global Admin,current_login,cart_dict
    print("email: "+str(l_email.get()))
    if len(l_email.get())!=0 and is_valid_email(l_email.get()):
        if len(l_pass.get())!=0 and is_valid_password(l_pass.get()):
            if verify_login_db(login_type):
                print("Login session started")
                print("Login Successful")
                print("current email is :"+current_email)
                print("current name is: "+current_name)

                #myframe2.destroy()
                nav_frame.destroy()
                myframe.destroy()

                if login_type =="Admin":
                    Admin =True
                    current_login=True
                else:
                    Admin=False
                    current_login=True
                    cart_dict={}
                    
                    create_cart()
                    create_cart_option()
                    add_item_to_cart_from_dict()

                create_nav_menu()
                create_center_items_list()
                add_item_to_store_from_dict()

            else: print("Login failed")
        else:
            print("Enter valid password")
    else:
        print("Enter valid email")

def update_cart_values():

    Label(cart_option,text=str("Total Items: "+str(total_items_in_cart())),bg="DarkOliveGreen3", width=29, font = ("Calibri",13)).grid(row=0, column=0,pady=5,columnspan=2,sticky=W+E)
    Label(cart_option,text=str("Cart Total: "+str(total_price_of_cart())),bg="DarkOliveGreen3", width=29, font = ("Calibri",13)).grid(row=1, column=0,columnspan=2,sticky=W+E)
    return True
#*************************************************************
PATTERN='^([456][0-9]{3})-?([0-9]{4})-?([0-9]{4})-?([0-9]{4})$'

def is_valid_card_number(sequence):

    match = re.match(PATTERN,sequence)

    if match == None:
        return False

#    for group in match.groups:
#        if group[0] * 4 == group:
#            return False
    return True
  
def enter_card_info_to_db():     # not just card , after payment to generate invoice
    global current_invoice_no,disc_dict,cart_dict,row_id,car_index

    mycursor.execute("SELECT *FROM VariableCount")
    myresult = mycursor.fetchone()
    sql ="UPDATE VariableCount SET rowcount = %s WHERE rowcount = %s"
    val=(myresult[0]+1,myresult[0])
    mycursor.execute(sql,val)
    mydb.commit()
    
    mycursor.execute("SELECT *FROM VariableCount")
    myresult = mycursor.fetchone()
    row_id=myresult[0]
    print(myresult[0])
    current_invoice_no=str(invoice_pt1+str(row_id))



    sql = "INSERT INTO CardInfo (invoice_no,cardno) VALUES(%s,%s)"
    val = (current_invoice_no,cd_e.get())
    mycursor.execute(sql,val)
    mydb.commit()

    if len(ds_e.get())!=0:   #check for promo code is entered or not if yes then get it's discount value from dict
        if ds_e.get() in disc_dict:
            discount_val =disc_dict[ds_e.get()]
    else:
        discount_val=0

    sql = "INSERT INTO OrdersTable (email,invoice_no,discount,address,mobno,cname,paymode,date) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)"
    val = (current_email,current_invoice_no,discount_val,current_add,current_mob,str(current_name+" "+current_lname),current_pay_mode,str(datetime.date(datetime.now())))
    mycursor.execute(sql,val)
    mydb.commit()


    for i in range(0,len(cart_dict)):
        if i in cart_dict:
            sql = "INSERT INTO InvoiceTable (invoice_no,iname,quantity,eachprice) VALUES(%s,%s,%s,%s)"
            val = (current_invoice_no,cart_dict[i]['item_name'],cart_dict[i]['quantity'],cart_dict[i]['each_price'])
            mycursor.execute(sql,val)
            mydb.commit()
    
    myframe2.destroy()
    cart_option.destroy()
    del cart_dict
    cart_dict={}
    create_cart()
    cart_index=-1
    create_cart_option()
        
    return True

def payment_validation():
    global current_pay_mode,current_invoice_no

    if current_pay_mode =="COD":
        print("Payment validation sucessfull")
        if enter_card_info_to_db():
            payment_window.destroy()
            invoice_for_search_bar(current_invoice_no)
            
            return True
    elif current_pay_mode =="CARD":
    
        if len(cd_e.get())==0:
            print("Enter card no")
        elif is_valid_card_number(cd_e.get()):
            print("valid card")
            if len(cv_e.get())!=0:
                print("valid cvv no")
                if len(val_e.get())!=0 and len(val_e.get()) == 10:
                    if validate_date(str(val_e.get())):
                        print("Payment validation sucessfull")
                        if enter_card_info_to_db():
                            payment_window.destroy()
                            invoice_for_search_bar(current_invoice_no)
                            return True
            else :
                print("Invalid cvv number")
                
        else:
            print("Invalid card")
            return False

def set_pay_mode(mode):
    global current_pay_mode                                                                     
    
    current_pay_mode=mode
    print(current_pay_mode)
    return True

def proceed_to_payment():    #-********payment window frame
    myframe.destroy()
    global payment_window,cdn,cvn,validd,cd_e,cv_e,val_e,pay_method,ds_e

    payment_window=Frame(test1,relief=GROOVE,width=370,height=480,bd=1)
    payment_window.place(x=250,y=100)

    pay_method = IntVar()
    cdn = StringVar()
    cvn = StringVar()
    validd = StringVar()
    
    Label(payment_window, text="Proceed To Pay", font=("Caliber",15)).grid(row =0,column=0,columnspan=4, sticky =W+E, padx=3)
    Label(payment_window, text="",font = ("Caliber",13)).grid(row =1,column=0)

    Label(payment_window, text="Select Payment Method", font=("Roboto",13)).grid(row =2,column=0,columnspan=4,sticky =W+E, padx=5 )  

    Label(payment_window,text="Mode", font=("Roboto",12)).grid(row=3, column=0,sticky=W)
    pay_e1 = Radiobutton(payment_window,text="COD", variable = pay_method,value = 1, font=("Roboto",12),command = partial(set_pay_mode,"COD"))
    pay_e1.grid(row=3, column=1,sticky=W)
    pay_e2 = Radiobutton(payment_window,text="Credit/Debit Card", variable = pay_method,value = 2, font=("Roboto",12),command = partial(set_pay_mode,"CARD"))
    pay_e2.grid(row=3, column=2,sticky=W)

    Label(payment_window,text="Promo Code", font=("Caliber",11)).grid(row=4, column=0,sticky=W)
    ds_e = Entry(payment_window,width=25, font=("Caliber",11))   
    ds_e.grid(row=4, column=1,columnspan =2,sticky=W)
    
    Label(payment_window, text="Enter below details if other then COD", font=("Roboto",11)).grid(row =5,column=0,columnspan=4,sticky =W+E, padx=5 )

    Label(payment_window,text="Card No", font=("Caliber",11)).grid(row=6, column=0,sticky=W)
    cd_e = Entry(payment_window,textvariable = cdn,width=25, font=("Caliber",11))   
    cd_e.grid(row=6, column=1,columnspan =2,sticky=W)
    
    Label(payment_window,text="Cvv", font=("Caliber",11)).grid(row=7, column=0,sticky=W)
    cv_e = Entry(payment_window,textvariable = cvn,width=25, font=("Caliber",11))
    cv_e.grid(row=7, column=1,columnspan =2,sticky=W)

    Label(payment_window,text="Valid upto", font=("Caliber",11)).grid(row=8, column=0,sticky=W)
    val_e = Entry(payment_window,textvariable = validd,width=25, font=("Caliber",11))
    val_e.grid(row=8, column=1,columnspan =2,sticky=W)
    Label(payment_window,text="", font=("Caliber",11)).grid(row=9, column=0)
    Button(payment_window, text="Pay",font = ("Caliber",13),width=20,command =payment_validation,bg="lime green").grid(row =12,column=0,columnspan=4,sticky =W+E,padx=10)


    return True
def create_cart_option(cart_total=0):
    global cart_option
    
    cart_option = Frame(test1,relief=GROOVE, width=273,height=150)
    cart_option.place(x=680,y=490)

    Label(cart_option,text=str("Total Items: "+str(total_items_in_cart())),bg="DarkOliveGreen3", width=29, font = ("Calibri",13)).grid(row=0, column=0,pady=5,columnspan=2,sticky=W+E)
    Label(cart_option,text=str("Cart Total: "+str(total_price_of_cart())),bg="DarkOliveGreen3", width=29, font = ("Calibri",13)).grid(row=1, column=0,columnspan=2,sticky=W+E)
    cart_pay_bt = Button(cart_option,text="Proceed to Buy", width=29, font = ("Calibri",13), command=proceed_to_payment).grid(row=2, column=0,columnspan=2)

def update_login_type(l_type="user"):
    global login_type
    print(l_type)
    login_type=l_type
    print(login_type)
def return_to_home_page():
    myframe.destroy()
    create_center_items_list()
    add_item_to_store_from_dict()
    
def create_nav_menu():
    global nav_frame
    global Admin,current_login
    
    print("(from nav menu creation)admin: "+str(Admin)+" userlogin: "+str(current_login))
    nav_frame = Frame(test1,relief=GROOVE, width=200,height=300,bg="orange")
    nav_frame.place(x=10,y=100)
    
    global l_email,l_pass
    
    Label(nav_frame,text="Menu",bg="gray", width=20, font = ("Calibri",13)).grid(row=0, column=0,columnspan=2)
    Button(nav_frame,text="Home", width=20, font = ("Calibri",13),bg="aquamarine", command=return_to_home_page).grid(row=1, column=0)
    
    if not current_login:
        Button(nav_frame,text="Signup", width=20, font = ("Calibri",13),bg="aquamarine", command=signup).grid(row=2, column=0)

        Label(nav_frame,text="Email",bg="orange").grid(row=7,column=0)
        l_email = Entry(nav_frame)
        l_email.grid(row=8,column=0)
        Label(nav_frame,text="Password",bg="orange").grid(row=9,column=0)
        l_pass = Entry(nav_frame)
        l_pass.grid(row=10,column=0)
        
        var1 = IntVar()  #user or admin
        login_type ="user"
        Radiobutton(nav_frame, text="User",variable=var1, value=1,bg="orange",command=partial(update_login_type,"User")).grid(row=11,column=0)
        Radiobutton(nav_frame, text="Admin",variable=var1, value=2,bg="orange",command=partial(update_login_type,"Admin")).grid(row=12,column=0)

        Button(nav_frame,text="Login", width=20, font = ("Calibri",13),bg="aquamarine", command=login).grid(row=13, column=0)

    else: 
        Button(nav_frame,text="logout", width=20, font = ("Calibri",13),bg="aquamarine", command=user_logout).grid(row=2, column=0)
        if not Admin:
            Button(nav_frame,text="Your Orders", width=20, font = ("Calibri",13),bg="aquamarine", command=orders).grid(row=3, column=0)
        
    if Admin and current_login:
        Button(nav_frame,text="Add item",width=20, font = ("Calibri",13),bg="aquamarine", command=add_item_window).grid(row=5, column=0)
        Button(nav_frame,text="Test", width=20, font = ("Calibri",13),bg="aquamarine", command="").grid(row=6, column=0)

def update_qty_in_cart(item_id,row_no,op_no):   # op_no is used for adding or subs if op_no is 0 then sub else if op_no is 1 then add
    for no in range(0,cart_index+1):
        if no in cart_dict:
            if cart_dict[no]['item_id'] == item_id:
                break
    if op_no ==1 and cart_dict[no]['quantity'] <5:
        cart_dict[no]['quantity'] +=1
    elif op_no ==0 and cart_dict[no]['quantity'] >1:
        cart_dict[no]['quantity'] -=1
    Label(frame2, text=str("Price Rs "+str(float(cart_dict[no]['each_price']))+"x"+str(cart_dict[no]['quantity'])+" = "+str(float(cart_dict[no]['each_price']*cart_dict[no]['quantity']))),font = ("Caliber",13)).grid(row =row_no,column=0,columnspan=2,sticky =W+E, padx=10)  
    update_cart_values()                
    
    
def cart_item_widget(item_id,iname,qty,ep):   #default cart item widget
    global cart_r
    global Admin,current_login
    print("qty from cart item widget: "+str(qty))
    
    Label(frame2, text=str(iname), font=("Caliber",15),bg="lemon chiffon").grid(row =cart_r,column=0,columnspan=2, sticky =W, padx=3)
    cart_r +=1
    Label(frame2, text=str("Price Rs "+str(float(ep))+"x"+str(qty)+" = "+str(float(ep*qty))),bg="lemon chiffon",font = ("Caliber",13)).grid(row =cart_r,column=0,columnspan=2,sticky =W+E, padx=10 )  
    cart_r +=1
    Button(frame2, text = "-", bg='gold2',width=10,command=partial(update_qty_in_cart,item_id,cart_r-1,0)).grid(row =cart_r,column=0,sticky =E)  
    Button(frame2, text = "+", bg='gold2',width=10,command=partial(update_qty_in_cart,item_id,cart_r-1,1)).grid(row =cart_r,column=1,sticky =W)
    cart_r +=1
            
    Button(frame2, text = "Remove Item", bg='red',width=25,command=partial(delete_item_from_cart,item_id)).grid(row =cart_r,column=0,columnspan = 2,sticky =W+E+S+N,padx=50,pady=8)  
    cart_r+=1
    Label(frame2,text="",bg="lemon chiffon").grid(row=cart_r,column=0)
    cart_r+=1

#work in progress........below
def admin_cart_item_widget(iname,qty,ep):   #when admin is login this widget shows more info for about each item
    global cart_r
    global Admin,current_login
    
    Label(frame2, text=str(iname), font=("Caliber",18)).grid(row =cart_r,column=0,columnspan=2, sticky =W, padx=3)
    cart_r +=1
    Label(frame2, text=str("Price Rs "+str(float(ep))+"x"+str(qty)+" = "+str(float(ep*qty))),font = ("Caliber",13)).grid(row =cart_r,column=0,columnspan=2,sticky =W, padx=10 )  
    cart_r +=1
    
    Button(frame2, text = "Remove Item", bg='red',command="").grid(row =cart_r,column=0,columnspan = 2,sticky =W+E+S+N,padx=50,pady=8)  
    cart_r+=1
    Label(frame2,text="").grid(row=cart_r,column=0)
    cart_r+=1

    
def item_widget(item_id,iname,des,ep,mfgn):   #default item widget, Pass iteminfo to add item to main widget
    global r

    global Admin,current_login

    Label(frame, text=str(iname), font=("Caliber",18),bg="gray80").grid(row =r,column=0,columnspan=2, sticky =W, padx=3)
    r +=1
    Label(frame, text=str("Manufactured by: "+str(mfgn)), font=("Roboto",11),bg="gray80").grid(row =r,column=0,sticky =W, padx=10 )  
    r +=1
    Label(frame, text=str("Price Rs"+str(float(ep))),font = ("Caliber",13),bg="gray80").grid(row =r,column=0,sticky =W, padx=10 )  
    r +=1
    print(len(des))
    len_str = len(des)/55
    print(len_str)
    if len_str > 1:
        len_str +=0.9
        len_str = int(len_str)
        x=[des[i:i+55] for i in range(0, len(des), 55)]
            
        for i in range(len_str):
            Label(frame, text = str(x[i]), font = ("Roboto",10),bg="gray80").grid(row =r,column=0,columnspan = 2,sticky =W, padx=10 ) 
            r+=1
        print("x"+str(x))
    else:
        Label(frame, text = str(des), font = ("Roboto",10),bg="gray80").grid(row=r,column=0,columnspan = 2,sticky =W, padx=10 )
        r+=1
    print(len_str)

    if current_login:
        if not Admin:
            Button(frame, text = "Add to Cart",state="normal", bg='spring green',command=partial(add_item_to_cart,iname,1,ep,mfgn)).grid(row =r,column=0,columnspan = 2,sticky =W+S+N+E,padx=50,pady=8)  
            r+=1
        else:
            Button(frame, text = "Delete Item", bg='firebrick1',command=partial(delete_item_from_store,item_id)).grid(row =r,column=0,columnspan = 2,sticky =W+S+N+E,padx=50,pady=8)  
            r+=1
    else:
        Button(frame, text = "Add to Cart",state="disabled", bg='spring green',command=partial(add_item_to_cart,iname,1,ep,mfgn)).grid(row =r,column=0,columnspan = 2,sticky =W+S+N+E,padx=50,pady=8)  
        r+=1
    Label(frame,text="",bg="gray80").grid(row=r,column=0)
    r+=1    
 
 
def myfunction(event):
    canvas.configure(scrollregion=canvas.bbox("all"),width=365,height=480)

def myfunction_cart(event):
    cart_canvas.configure(scrollregion=cart_canvas.bbox("all"),width=250,height=380)

def create_cart():
    global myframe2,frame2,cart_canvas

    myframe2=Frame(test1,relief=GROOVE,width=100,height=50,bd=1,bg="red")
    myframe2.place(x=680,y=100)

    cart_canvas=Canvas(myframe2,width=250,height=380,bg="lemon chiffon")
    frame2=Frame(cart_canvas,bg="lemon chiffon")
    myscrollbar_cart=Scrollbar(myframe2,orient="vertical",command=cart_canvas.yview)
    cart_canvas.configure(yscrollcommand=myscrollbar_cart.set)

    myscrollbar_cart.pack(side="right",fill="y")
    cart_canvas.pack(side="left")

    cart_canvas.create_window((0,0),window=frame2,anchor='nw')
    frame2.bind("<Configure>",myfunction_cart)    

def create_center_items_list():
    global frame,myframe,canvas,Admin,current_login

    myframe=Frame(test1,relief=GROOVE,width=100,height=100,bd=1,bg="blue")
    myframe.place(x=250,y=100)

    canvas=Canvas(myframe,bg="gray80")
    frame=Frame(canvas,bg="gray80")
    myscrollbar=Scrollbar(myframe,orient="vertical",command=canvas.yview)
    canvas.configure(yscrollcommand=myscrollbar.set)

    myscrollbar.pack(side="right",fill="y")
    canvas.pack(side="left")

    canvas.create_window((0,0),window=frame,anchor='nw')
    frame.bind("<Configure>",myfunction)

def orders():
    global current_email,current_name
    myframe.destroy()
    create_center_items_list()

    mycursor.execute("SELECT *FROM OrdersTable")
    myresult = mycursor.fetchall()
    for x in myresult:
        print(x)
        if current_email in x:
            invoice_no = x[1]
            disscount = x[2]
            add = x[3]
            mobile = x[4]
            name = x[5]
            pmode = x[6]
            date = x[7]
            invoice_widget(invoice_no,fetch_data_for_invoice(invoice_no),disscount,add,mobile,name,pmode,date)

def invoice_for_search_bar(invoice_search):
    global current_email,current_name
    myframe.destroy()
    create_center_items_list()

    mycursor.execute("SELECT *FROM OrdersTable")
    myresult = mycursor.fetchall()
    for x in myresult:
        print(x)
        if invoice_search in x:
            disscount = x[2]
            add = x[3]
            mobile = x[4]
            name = x[5]
            pmode = x[6]
            date = x[7]
            invoice_widget(invoice_search,fetch_data_for_invoice(invoice_search),disscount,add,mobile,name,pmode,date)
    

def fetch_data_for_invoice(invoice_no):
    mycursor.execute("SELECT *FROM InvoiceTable")
    myresult = mycursor.fetchall()
    
    items_list={}
    invoice_count=-1
    for x in myresult:
        print(x)
        if invoice_no in x:
            invoice_count +=1
            items_list[invoice_count]={}
            items_list[invoice_count]['iname'] = x[1]
            items_list[invoice_count]['qty'] = x[2]
            items_list[invoice_count]['ep'] = x[3]
    return items_list

#************generate invoice pdf******************************************************************
def invoice_pdf(invoice_no,customer_name,add,mob_no,discount,aft_dis_total,gst,g_total,date,paym,total,idict):
    def add_image():
        pdf.image('logo3.png', x=45, y=2, w=29)
        pdf.set_font("Arial", size=12)
        pdf.ln(85)  # move 85 down

    card_n=""
    if paym =="CARD":
        mycursor.execute("SELECT *FROM CardInfo")
        myresult = mycursor.fetchall()
        for x in myresult:
            if invoice_no in x:
                card_n = x[1]


     
    #str(datetime.date(datetime.now())))   for taking current date

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=30,style='B')
    pdf.set_text_color(96,96,96)
    pdf.cell(200, 10, txt="Re-Life Store", ln=1, align="C")
    pdf.set_font("Arial", size=12)
    pdf.set_text_color(0)

    pdf.cell(200, 10, txt="12, Dr Annie Besant Rd,Opp. Shiv Sagar Estate", ln=1, align="C")
    pdf.cell(200, 7, txt=" Worli, Mumbai,Maharashtra 400012", ln=1, align="C")
    pdf.cell(200, 7, txt="Contact: 9769254939", ln=1, align="C")

    pdf.set_line_width(1)
    pdf.set_draw_color(255, 0, 0)
    pdf.line(10, 45, 205, 45)

    pdf.set_font("Arial", size=24,style='B')
    pdf.set_text_color(0)
    pdf.cell(200, 15, txt="INVOICE", ln=1, align="C")

    pdf.set_font("Arial", size=14)
    pdf.cell(100, 15, txt=str(" Invoice #"+invoice_no), align="L")
    pdf.cell(100, 15, txt=str(" Date: "+date),ln=1, align="R")   #current date printing 

    pdf.set_font("Arial", size=18,style="B")
    pdf.set_text_color(0)
    pdf.cell(100, 10, txt="SHIP TO: ", align="L",ln=1)


    pdf.set_font("Arial", size=12)
    pdf.set_text_color(0)
    pdf.cell(100, 6, txt=customer_name, align="L",ln=1)
    pdf.cell(100, 6, txt=mob_no, align="L",ln=1)

    if paym=="CARD":
        pdf.cell(100, 6, txt="Paymode: CARD", align="L",ln=1)        
        pdf.cell(100, 6, txt=str("Card No: "+str(card_n)), align="L",ln=1)
    else:
        pdf.cell(100, 6, txt="Paymode: COD", align="L",ln=1)        


    len_str = len(add)/35
    print(len_str)
    if len_str > 1:
        len_str +=0.9
        len_str = int(len_str)
        a=[add[i:i+35] for i in range(0, len(add), 35)]
                
        for i in range(len_str):
            pdf.cell(100, 6, txt=str(a[i]), align="L",ln=1)

        print("x"+str(a))
    else:
        pdf.cell(100, 6, txt=add, align="L",ln=1)




    pdf.cell(100, 6, txt="", align="L",ln=1)

    pdf.set_line_width(0.5)
    pdf.set_draw_color(0)
    pdf.set_font("Arial", size=12)

    pdf.cell(125,7,txt="ITEM NAME", border=1,align="C")
    pdf.cell(35,7,txt="QTY", border=1,align="C")
    pdf.cell(35,7,txt="UNIT PRICE", border=1,align="C",ln=1)
    print(pdf.w)

    for i in range(0,len(idict)):
        if i in idict:
            pdf.cell(125,7,txt=idict[i]['iname'], border=1,align="L")
            pdf.cell(35,7,txt=str(idict[i]['qty']), border=1,align="C")
            pdf.cell(35,7,txt=str(idict[i]['ep']), border=1,align="C",ln=1)
        
    pdf.cell(125,7,txt="Total", border=1,align="C")
    pdf.cell(70,7,txt=str(total), border=1,align="C",ln=1)

    pdf.cell(125,7,txt="Discount", border=1,align="C")
    pdf.cell(70,7,txt=str(str(discount)+"%"), border=1,align="C",ln=1)

    pdf.cell(125,7,txt="After Discount", border=1,align="C")
    pdf.cell(70,7,txt=str(aft_dis_total), border=1,align="C",ln=1)


    pdf.cell(125,7,txt="GST", border=1,align="C")
    pdf.cell(70,7,txt=str(str(gst)+"%"), border=1,align="C",ln=1)

    pdf.cell(125,7,txt="Grand Total", border=1,align="C")
    pdf.cell(70,7,txt=str(g_total), border=1,align="C",ln=1)

    pdf.cell(100, 10, txt="", align="L",ln=1)
    pdf.cell(100, 10, txt="", align="L",ln=1)
    pdf.cell(100, 10, txt="", align="L",ln=1)
    pdf.cell(100, 10, txt="", align="L",ln=1)

    pdf.cell(200, 6, txt="Thank you for Shopping with Us!", align="C",ln=1)
    add_image()


    pdf.output("simple_demo.pdf")

#************


def invoice_widget(invoice_no,items_list,disc,add,mobile,name,pmode,date):   #default item widget, Pass iteminfo to add item to main widget

    global r
    card_number=""
    if pmode =="CARD":
        mycursor.execute("SELECT *FROM CardInfo")
        myresult = mycursor.fetchall()
        for x in myresult:
            if invoice_no in x:
                card_number = x[1]

    
    total_bill=0
    Label(frame, text="Invoice No:", font=("Caliber",14),bg="gray80").grid(row =r,column=0,columnspan=1, sticky =W)
    Label(frame, text=str(" "+str(invoice_no)), font=("Roboto",14),bg="gray80").grid(row =r,column=1,columnspan=3,sticky =W)  
    r +=1

    Label(frame, text="Name",font = ("Caliber",13),bg="gray80").grid(row =r,column=0,sticky =W)
    Label(frame, text=name,font = ("Caliber",13),bg="gray80").grid(row =r,column=1,columnspan=2,sticky =W)
    r +=1
    
    Label(frame, text="Address",font = ("Caliber",13),bg="gray80").grid(row =r,column=0,sticky =W)

#***********
    len_str = len(add)/27
    print(len_str)
    if len_str > 1:
        len_str +=0.9
        len_str = int(len_str)
        a=[add[i:i+27] for i in range(0, len(add), 27)]
            
        for i in range(len_str):
            Label(frame, text=str(a[i]),font = ("Caliber",11),bg="gray80").grid(row =r,column=1,columnspan=2,sticky =W)
            r+=1
        print("x"+str(a))
    else:
        Label(frame, text=add,font = ("Caliber",11),bg="gray80").grid(row =r,column=1,columnspan=2,sticky =W)
        r+=1
#****
    Label(frame, text="Mob No",font = ("Caliber",13),bg="gray80").grid(row =r,column=0,sticky =W)
    Label(frame, text=mobile,font = ("Caliber",13),bg="gray80").grid(row =r,column=1,columnspan=2,sticky =W)
    r +=1

    Label(frame, text="",font = ("Caliber",11),bg="gray80").grid(row =r,column=0)
    r +=1

        
    Label(frame, text="Item name",font = ("Caliber",13),bg="gray80").grid(row =r,column=0,sticky =W)
    Label(frame, text="Qty",font = ("Caliber",13),bg="gray80").grid(row =r,column=1,sticky =W,padx=5 )
    Label(frame, text="Price",font = ("Caliber",13),bg="gray80").grid(row =r,column=2,sticky =W )
    r +=1
    for i in range(0,len(items_list)):
        if i in items_list:
            if len(items_list[i]['iname'])>22:
                temp=items_list[i]['iname']
                temp_item_name=temp[0:22]+"..."
                
            else:
                temp_item_name=items_list[i]['iname']
                
            total_bill +=int(items_list[i]['qty'])*int(items_list[i]['ep'])
            Label(frame, text=str(temp_item_name),font = ("Caliber",10),bg="gray80").grid(row =r,column=0,sticky =W)
            Label(frame, text=str(items_list[i]['qty']),font = ("Caliber",10),bg="gray80").grid(row =r,column=1,sticky =W,padx=5 )
            Label(frame, text=str(items_list[i]['ep']),font = ("Caliber",10),bg="gray80").grid(row =r,column=2,sticky =W )
            r +=1
    Label(frame, text="",font = ("Caliber",11),bg="gray80").grid(row =r,column=0)
    r +=1

    Label(frame, text="Total",font = ("Caliber",11),bg="gray80").grid(row =r,column=0,sticky =W )
    Label(frame, text=str(total_bill),font = ("Caliber",11),bg="gray80").grid(row =r,column=1,columnspan=2,sticky =W+E )
    r +=1

    after_discount = total_bill - int((int(disc)*int(total_bill))/100) # total bill - discounted amount
    
    Label(frame, text="Discount",font = ("Caliber",11),bg="gray80").grid(row =r,column=0,sticky =W )
    Label(frame, text=str(str(disc)+"%"),font = ("Caliber",11),bg="gray80").grid(row =r,column=1,columnspan=2,sticky =W+E )
    r +=1
    Label(frame, text=str(after_discount),font = ("Caliber",11),bg="gray80").grid(row =r,column=1,columnspan=2,sticky =W+E )
    r +=1
    
    after_gst = after_discount + int((int(5)*int(after_discount))/100) # total bill - discounted amount
    
    Label(frame, text="GST",font = ("Caliber",11),bg="gray80").grid(row =r,column=0,sticky =W )
    Label(frame, text="5%",font = ("Caliber",11),bg="gray80").grid(row =r,column=1,columnspan=2,sticky =W+E )
    r +=1

    Label(frame, text="Grand Total",font = ("Caliber",11),bg="gray80").grid(row =r,column=0,sticky =W )
    Label(frame, text=str(after_gst),font = ("Caliber",11),bg="gray80").grid(row =r,column=1,columnspan=2,sticky =W+E )
    r +=1
    Label(frame, text="Payment Mode",font = ("Caliber",11),bg="gray80").grid(row =r,column=0,sticky =W )
    Label(frame, text=pmode,font = ("Caliber",11),bg="gray80").grid(row =r,column=1,columnspan=2,sticky =W+E )
    r +=1
    if pmode=="CARD":
        Label(frame, text="Card No",font = ("Caliber",11),bg="gray80").grid(row =r,column=0,sticky =W )
        Label(frame, text=card_number,font = ("Caliber",11),bg="gray80").grid(row =r,column=1,columnspan=2,sticky =W+E )
        r +=1
        
    Label(frame, text="",font = ("Caliber",11),bg="gray80").grid(row =r,column=0)
    r +=1
    invoice_pdf(invoice_no,name,add,mobile,disc,after_discount,5,after_gst,date,pmode,total_bill,items_list)

def items_window_widget():   #create items list and cart window with scroll bar ---------------------------------
    global Admin,current_login
    global test1

    test1=Tk()
    test1.title("Test for different frames")
    test1.geometry("980x600")
    Label(test1, text="Re-Life Store",font = ("Caliber",26),bg="alice blue").place(x=370,y=10)
    test1.configure(background='alice blue')
    
    create_nav_menu()
    create_search_bar()
    create_center_items_list()
    add_item_to_store_from_dict()
#    test1.mainloop()
    
#cart creation
    if current_login:
        create_cart()
    if current_login and not Admin:
        create_cart_option()
#*****
    
    add_item_to_store_from_dict()
def add_item_to_dict():
    global item_no
    global items_dict
    if len(IN.get())>28:
        temp = IN.get()
        item_name=temp[0:28]
    else:
        item_name=IN.get()


    item_no +=1
    items_dict[item_no] = {}
    items_dict[item_no]['item_id'] =item_no 
    items_dict[item_no]['item_name']=item_name
    items_dict[item_no]['quantity']=QTY.get()
    items_dict[item_no]['each_price']=EP.get()
    items_dict[item_no]['mfg_name']=MFGN.get()
    items_dict[item_no]['description']=DES.get()
    items_dict[item_no]['mfg_date']=MFGD.get()
    items_dict[item_no]['exp_date']=EXPD.get()
    items_dict[item_no]['item_unit']=IU.get()

    print(items_dict[item_no])
    item_widget(item_no,IN.get(),DES.get(),EP.get(),MFGN.get())
    


def add_item_to_cart(iname,qty,ep,mfgn):
    print("function call")
    global cart_index
    global cart_dict

    cart_index +=1

    cart_dict[cart_index] = {}
    cart_dict[cart_index]['item_id']=cart_index
    cart_dict[cart_index]['item_name']= iname
    cart_dict[cart_index]['quantity']= qty
    cart_dict[cart_index]['each_price']= ep
    cart_dict[cart_index]['mfg_name']= mfgn

    print("cart index when adding item to cart "+str(cart_index))
    print(cart_dict[cart_index])
    cart_item_widget(cart_index,iname,qty,ep)
    update_cart_values()
     

def validate_date(date):
    date_list=date.split("/")
    print(date_list)
    if is_valid_date(int(date_list[0]),int(date_list[1]),int(date_list[2])):
        return True
    else: print("invalid date"); return False

def add_item_to_db():
    add_item_to_dict()# delete after connection of dictionary and database table
    if len(IN.get())>28:
        temp = IN.get()
        item_name=temp[0:28]
    else:
        item_name=IN.get()
    sql = "INSERT INTO products (itemid,iname,quantity,eachprice,mfgname,description,mfgdate,expdate,unit) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    val = (item_no,item_name,int(QTY.get()),int(EP.get()),MFGN.get(),DES.get(),MFGD.get(),EXPD.get(),IU.get())
    mycursor.execute(sql,val)
    mydb.commit()

    print("from products table")
    mycursor.execute("SELECT *FROM products")
    myresult = mycursor.fetchall()

    for x in myresult:
      print(x)

    return True
        
def validate_add_item():
    count=0
    if len(IN.get())!=0:
        count +=1
    else: print("Enter item name")

    if QTY.get() > 0 and QTY.get()  < 50000:
        count +=1
    else: print("Enter Quantity between 1 to 50000")

    if EP.get() > 0 :
        count +=1
    else: print("Enter Price above 0")

    if len(MFGN.get())!=0:
        count +=1
    else: print("Enter mfg name")

    if len(DES.get())!=0:
        count +=1
    else: print("Enter Descritption")

    if len(MFGD.get())!=0 and len(MFGD.get()) == 10:
        if validate_date(str(MFGD.get())):
            count +=1
        else: print("Enter valid mfg date")
    else: print("Enter mfg date")

    if len(EXPD.get())!=0 and len(EXPD.get())==10:
        if validate_date(str(EXPD.get())):
            count +=1
        else: print("Enter valid exp date")
    else: print("Enter exp date")
    print(IU.get())
    if count== 7:
        print("validate Successful")
        if add_item_to_db():
            screen2.destroy()
    else: print("validation failed ")
 

def add_item_window():
    global screen2
    screen2=Toplevel(test1)
    screen2.title("Add item to inventory")
    screen2.geometry("400x500")

    global IN,QTY,EP,MFGN,DES,MFGD,EXPD,IU

    IN = StringVar()
    QTY = IntVar()
    EP = IntVar()
    MFGN = StringVar()
    DES = StringVar()
    MFGD = StringVar()
    EXPD = StringVar()
    IU = StringVar()
    
    Label(screen2,text="Item Name", font=("Caliber",15)).grid(row=0,column=0, sticky =W)
    Entry(screen2,font=("Caliber",15),textvariable = IN).grid(row=0,column=1)
    
    Label(screen2,text="Quantity", font=("Caliber",15)).grid(row=1,column=0, sticky =W)
    Entry(screen2,font=("Caliber",15),textvariable = QTY).grid(row=1,column=1)
    
    Label(screen2,text="Each Price", font=("Caliber",15)).grid(row=2,column=0, sticky =W)
    Entry(screen2,font=("Caliber",15),textvariable = EP).grid(row=2,column=1)
    
    Label(screen2,text="Manufacturer name", font=("Caliber",15)).grid(row=3,column=0, sticky =W)
    Entry(screen2,font=("Caliber",15),textvariable = MFGN).grid(row=3,column=1)
    
    Label(screen2,text="Description", font=("Caliber",15)).grid(row=4,column=0, sticky =W)
    Entry(screen2,font=("Caliber",15),textvariable = DES).grid(row=4,column=1)
    
    Label(screen2,text="Manufacture Date", font=("Caliber",15)).grid(row=5,column=0, sticky =W)
    Entry(screen2,font=("Caliber",15),textvariable = MFGD).grid(row=5,column=1)
    
    Label(screen2,text="Expiry Date", font=("Caliber",15)).grid(row=6,column=0, sticky =W)
    Entry(screen2, font=("Caliber",15),textvariable = EXPD).grid(row=6,column=1)
    
    Label(screen2,text="Item unit",font=("Caliber",15)).grid(row=7,column=0, sticky =W)
    IU.set("ml")
    OptionMenu(screen2, IU, "ml", "mg").grid(row=7,column=1, sticky =W)
    
    Label(screen2,text="").grid(row=8,column=0)
    Button(screen2,text="Add Item", font=("Caliber",15),command=validate_add_item).grid(row=9,column=1)
    
def register_user():
    username_info = username.get()
    password_info = password.get()

    username_entry.delete(0,END)
    password_entry.delete(0,END)

    Label(screen1,text="Registeration successfull").grid(row=10,column=0)
    screen1.destroy()

def is_valid_email(email):
    if re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email) != None:
        print("valid email")
        return True
    else:
        print("Invalid email")
        return False

def is_valid_mob(no):
    if re.match('(0/91)?[7-9][0-9]{9}',no)!=None:
        print("valid mobile no")
        return True
    else:
        print("invalid mobile no")
        return False 

def is_valid_year(year):
    if year > 1800:
        return True
    else:
        return False
    
def is_valid_month(month):
    if month > 0 and month < 13:
        return True
    else:
        return False

def is_leap_year(year):
    if year%4==0 and year%100!=0 or year%400==0 :
        print("This is leap year")
        return True
    return False

def is_valid_date(date,month,year):
    if is_valid_month(month) == True and is_valid_year(year) == True:
        if is_leap_year(year) ==  True:
            if month == 2 and (date > 0 and date <= 29):
                return True
            elif month!= 2 and date > 0 and date <=31:
                return True
            else:
                return False
        else:
            if month == 2 and (date > 0 and date <= 28):
                return True
            
            elif month!= 2 and date > 0 and date <=31:
                return True
            else:
                return False    
    
def is_valid_password(passw):
    flag = 0
    while True:   
        if (len(passw)<8): 
            flag = -1
            break
        elif not re.search("[a-z]", passw): 
            flag = -1
            break
        elif not re.search("[A-Z]", passw): 
            flag = -1
            break
        elif not re.search("[0-9]", passw): 
            flag = -1
            break
        elif not re.search("[_@$]", passw): 
            flag = -1
            break
        elif re.search("\s", passw): 
            flag = -1
            break
        else: 
            flag = 0 
            break
  
    if flag ==-1: 
        print("Not a Valid Password")
        return False
    else:
        print("Valid password")
        return True

def not_exist_in_db():
    found=0
    if drop_listvar.get() =="Admin":
        mycursor.execute("SELECT email FROM admins")
        myresult = mycursor.fetchall()

        for x in myresult:
            print(x)
            if email.get() in x :
                found=1
                break
    elif drop_listvar.get() =="User":
        mycursor.execute("SELECT email FROM customers")
        myresult = mycursor.fetchall()

        for x in myresult:
            print(x)
            if email.get() in x :
                found=1
                break
    if found==0:            
        return True
    else:
        return False



def insert_into_db():
    if not_exist_in_db():
        if gender.get()==1:
            gen="Male"
        elif gender.get() ==2:
            gen ="Female"
        if drop_listvar.get() =="User":
            sql = "INSERT INTO customers (fname,lname,email,mobno,gender,dob,client,pass,address) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            val = (fn.get(),ln.get(),email.get(),mob.get(),gen,DOB_d.get(),"User",password.get(),address.get("1.0","end-1c"))
            mycursor.execute(sql,val)
            mydb.commit()
        elif drop_listvar.get() =="Admin":
            sql = "INSERT INTO admins (fname,lname,email,mobno,gender,dob,client,pass,address) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            val = (fn.get(),ln.get(),email.get(),mob.get(),gen,DOB_d.get(),"Admin",password.get(),address.get("1.0","end-1c"))
            mycursor.execute(sql,val)
            mydb.commit()

        mycursor.execute("SELECT *FROM customers")
        myresult = mycursor.fetchall()

        for x in myresult:
          print(x)

        mycursor.execute("SELECT *FROM admins")
        myresult = mycursor.fetchall()

        for x in myresult:
          print(x)
        
        return True
    else:
        print("Email is already used to signup")

def validate_signup_form():
    count=0
    if len(fn.get())==0 or len(ln.get())== 0:
        print("Enter name please")
    else:
        count+=1
    
    if len(email.get())==0:
        print("Enter email please")
    else:
        if is_valid_email(email.get()):
            count+=1
            
    if len(mob.get())==0:
        print("Enter mobile number")
    elif len(mob.get())<10:
        print("Enter 10 digit mobile number")
    else:
        if is_valid_mob(mob.get()):
            count+=1

    if gender.get()==0:
        print("Select gender")
    elif gender.get()==1:
        print("Male")
        count+=1
    elif gender.get()==2:
        count+=1
        print("Female")

    if len(DOB_d.get())!=0 and len(DOB_d.get()) == 10:
        if validate_date(str(DOB_d.get())):
            count +=1
        else: print("Enter valid DOB")
    else: print("Enter DOB")

    if len(password.get()) == 0:
        print("Enter password please")
    else:
        if is_valid_password(password.get()):
            count+=1
    if len(address.get("1.0","end-1c")) ==0:
        print("Enter address please")
    else:
        count +=1
    print(drop_listvar.get())

    if count == 7:
        if insert_into_db():
            print("Signup successful")
            screen1.destroy()
        else:
            print("Signup Failed")
        
def signup():
    global screen1
    screen1=Toplevel(test1)
    screen1.title("Signup")
    screen1.geometry("280x350")

    global pass_e,password, fn_e, ln_e,drop_listvar, drop_list1, gender_e, email_e, mob_e 
    global DOB_d,address
    global fn, ln, gender, email, mob 
    
    email = StringVar()
    fn = StringVar()
    ln = StringVar()
    gender = IntVar()
    mob = StringVar()
    password = StringVar()
    DOB_d = StringVar()
#    address = StringVar()
    
    Label(screen1,text="Enter details below").grid(row=0, column=0,columnspan =3,sticky =W+E)
    Label(screen1,text="").grid(row=1, column=0)
        
    Label(screen1,text="First name").grid(row=4, column=0,sticky=W)
    fn_e = Entry(screen1,textvariable = fn,width=30).grid(row=4, column=1,columnspan =2,sticky=W)    

    Label(screen1,text="Last name").grid(row=5, column=0,sticky=W)
    ln_e = Entry(screen1,textvariable = ln,width=30).grid(row=5, column=1,columnspan =2,sticky=W)

    Label(screen1,text="Email").grid(row=6, column=0,sticky=W)
    email_e = Entry(screen1,textvariable = email,width=30).grid(row=6, column=1,columnspan =2,sticky=W)

    Label(screen1,text="Password").grid(row=3, column=0,sticky=W)
    pass_e = Entry(screen1,textvariable = password,width=30).grid(row=3, column=1,columnspan =2,sticky=W)

    Label(screen1,text="Mobile No").grid(row=7, column=0,sticky=W)
    mob_e = Entry(screen1,textvariable = mob,width=30).grid(row=7, column=1,columnspan =2,sticky=W)

    Label(screen1,text="Gender").grid(row=8, column=0,sticky=W)
    gender_e1 = Radiobutton(screen1,text="Male", variable = gender,value = 1).grid(row=8, column=1,sticky=W)
    gender_e2 = Radiobutton(screen1,text="Female", variable = gender,value = 2).grid(row=8, column=2,sticky=W)

    Label(screen1,text="DOB").grid(row=9, column=0,sticky=W)
    DOB_e = Entry(screen1,textvariable=DOB_d,width=30).grid(row=9, column=1,columnspan =2,sticky=W)        

    Label(screen1,text="Address").grid(row=10, column=0,sticky=W)
    address = Text(screen1,height=3,width=22)        
    address.grid(row=10, column=1,columnspan =2,sticky=W)
    
    drop_listvar = StringVar()
    drop_listvar.set("User")

    drop_list1 = OptionMenu(screen1, drop_listvar, "User", "Admin")
    drop_list1.grid(row=13, column=1,sticky=W)

    Label(screen1,text="").grid(row=14, column=0)
    
    Button(screen1,text="Submit", height="1", width="10", command=validate_signup_form).grid(row=15, column=0)
    Button(screen1,text="Cancel", height="1", width="10", command=screen1.destroy).grid(row=15, column=2)
"""
def login_widget():
    global screen4
    screen4=Toplevel(screen)
    screen4.title("Login")
    screen4.geometry("300x170")
#    global l_email,l_pass, drop_listvar

#    l_email = StringVar()
#    l_pass = StringVar()

    Label(screen4,text="Login",bg="gray", width=30, font = ("Calibri",13)).grid(row=0, column=0,columnspan=3)
    Label(screen4,text="").grid(row=1,column=0)
    Label(screen4,text="Email").grid(row=2,column=0)
    Entry(screen4,textvariable = l_email).grid(row=2,column=1)
    Label(screen4,text="Password").grid(row=3,column=0)
    Entry(screen4,textvariable = l_pass).grid(row=3,column=1)

    drop_listvar = StringVar()
    drop_listvar.set("User")

    drop_list2 = OptionMenu(screen4, drop_listvar, "User", "Admin").grid(row=4,column=1)

    Label(screen4,text="").grid(row=5,column=0)
    
    Button(screen4,text="Submit", height="1", width="10", command=login).grid(row=6, column=0,ipadx=5)
    Button(screen4,text="Cancel", height="1", width="10", command=screen4.destroy).grid(row=6, column=2)
    
    
    
def menu_window():
    t_frame=Frame(screen, width=800,height=100).grid(row=0, column=0)
    Label(t_frame,text="Online Medicine",bg="blue", font=("Caliber",20)).grid(row=0, column=0)

    l_frame=Frame(screen, width=30,height=60).grid(row=1, column=1)
    Label(l_frame,text="Note",bg="gray", width=30, font = ("Calibri",13)).grid(row=1, column=0)
    Button(l_frame,text="Signup", width=30, font = ("Calibri",13),command=signup).grid(row=2, column=0)
    Button(l_frame,text="Test", width=30, font = ("Calibri",13), command=items_window_widget).grid(row=3, column=0)
    Button(l_frame,text="Login", width=30, font = ("Calibri",13), command=login_widget).grid(row=4, column=0)
    Button(l_frame,text="Add item",width=30, font = ("Calibri",13), command=add_item_window).grid(row=5, column=0)
    
    
def main_screen():
    global screen
    screen = Tk()
    screen.geometry("800x600")
    screen.title("Notes 1.0")
    menu_window()

    screen.mainloop()"""
r=0
cart_r=0
cart_index=-1
cart_dict={}

Admin=False
current_login=False
qty=1
#global cd_e,cv_e,val_e
items_window_widget()
#main_screen()

