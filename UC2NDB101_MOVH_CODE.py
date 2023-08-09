from tkinter import *
import tkinter as tk
from tkinter import filedialog
import tkinter.font as tkfont
from tkinter import messagebox
from pymongo import MongoClient
from PIL import Image, ImageTk
import datetime as dt
import shutil, os, bson

#Class to connect to the database once and retrieve the Finnplus database
class Connect_MongoDB:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.activedb = self.client["Finnplus_Mark_Movh"]

        try:
            #Create a for loop for all the files in the directory, then check if they end with bson
            for collection in os.listdir("Finnplus"):
                if collection.endswith('.bson'):
                    #If the file is named bson open it, and then retrieve it, through os.path.join create
                    #a buffer interface which allows for read and write of the input streams
                    with open(os.path.join("Finnplus", collection), 'rb+') as f:
                        #Use a split to slice, and get the collection names, then insert from the bson file
                        self.activedb[collection.split('.')[0]].insert_many(bson.decode_all(f.read()))
        except:
            pass  
    
    #Getter for the database
    def get_current_database(self):
        return self.activedb

#Main class that initiates the program, this is where all the frames/menus are generated
class Database_Project(tk.Tk):

    def __init__(self):
        tk.Tk.__init__(self)
        
        #Created a container that is a frame which will hold all these frames
        self.stack_frame_container = tk.Frame(self)
        self.stack_frame_container.grid_columnconfigure(0, weight=1)
        self.stack_frame_container.grid_rowconfigure(0, weight=1)
        self.stack_frame_container.pack(side="top", fill="both", expand=True)

        #This dictionary is created that will hold all the frames, the key being the frame, while they value being the instance of that frame
        self.frameslist = {}

        #Only input classes(frames) which are okay to run from start before program even launches
        #This for loop regards the current frame method. It will raise a frame, meaning all information is stored on it, even if clicked away
        for frame in (LoginPage, SignupPage):
            frame_occurrence = frame.__name__
            active_frame = frame(parent=self.stack_frame_container, controller=self)
            self.frameslist[frame_occurrence] = active_frame
            #Set all frames to same area, then raise to move between them
            active_frame.grid(row=0, column=0, sticky="snew")

        #Running frame checks for what frame is running, at the start it is none
        self.running_frame = None
        self.reload_frame(MainPage)
            
    #Create a method to call the frame, with it being in the dictionary self.frameslist
    def current_frame(self, frame_occurrence):
        active_frame = self.frameslist[frame_occurrence]
        active_frame.tkraise()

    #Method to destroy the frame if it exists, and then recreate the frame.
    def reload_frame(self, new_frame_class):
        active_frame = new_frame_class

        if self.running_frame:
            self.running_frame.destroy()
        
        #Set the running frame and its grid positioning
        self.running_frame = active_frame(self.stack_frame_container, controller=self)
        self.running_frame.grid(row=0, column=0, sticky="snew")

#These are values which will be inherited by all classes
class Pages:
    database = ""
    #Check for users that are logged in
    loggedin = False
    #Saves the user which is logged in (Only one at a time)
    user = ""
    #Other common occurrences among menus
    logo_font = ("Calibri", 20, "bold")
    slogan_font = ("Calibri", 15)
    currentdate = dt.datetime.today()

#This is the starting menu class
class MainPage(tk.Frame, Pages):
    #Each class has the following init statement, taking self, parent, controller
    #self being the frame, parent being its parent frame which is the stack container in the database_project class
    #controller allows for calling of the parent class, and its methods
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        #Connect to the database via calling the class when the starting page is initiated
        self.database_connect = Connect_MongoDB()
        #Call function to set the database globally
        self.get_set_database()

        general_label_font = ("Calibri", 15, "bold")
        product_buttons = ("Calibri", 20)

        #Most of the length in the code of this project is due to the widgets and their customisation. Often there are three lines per widget.
        #The reason for this, is that a widget must have its grid set separately in order to be able to be configured, otherwise it will register
        #the object as not having an attribute configure
        logolabel = Label(self, text="  FINNPLUS  ", background="#06bffc", foreground="#fff")
        logolabel.grid(row=0, column=0, padx=(10, 5), pady=10)
        logolabel.configure(font=Pages.logo_font)

        sloganlabel = Label(self, text="The market of possibilities")
        sloganlabel.grid(row=0, column=1)
        sloganlabel.configure(font=Pages.slogan_font)

        #This is a special case on all pages/frames which include a log in button.
        #The program must know if a user is logged in or not. Depending on if the inherited value "Pages.loggedin" is true or not,
        #it will call functions that will configure the loginbutton to either log in or log out.
        if Pages.loggedin == False:
            self.loginbutton = Button(self, text="Log in", background="#fff", command=self.login, cursor="hand2")
            self.loginbutton.grid(row=0, column=3, padx=(10, 0), sticky="w")
            self.loginbutton.configure(font=general_label_font)
        else:
            self.userloggedin = Label(self, text=Pages.user)
            self.userloggedin.grid(row=0, column=2, sticky="w")
            self.userloggedin.configure(font=general_label_font)

            self.loginbutton = Button(self, text="Log out", background="#fff", command=self.logout, cursor="hand2")
            self.loginbutton.grid(row=0, column=3, padx=(10, 0), sticky="w")
            self.loginbutton.configure(font=general_label_font)

        #Here is a common example of a button. What is to be highlighted here is how classes are connected with each other.
        #The controller as mentioned, makes it possible to switch between classes by calling upon other frames. Here a lambda function is used
        #and required because otherwise, this function will be called without the click of a button. A lambda prevents this from occurring.
        cartlabel = Button(self, text="CART", background="#06bffc", foreground="#fff", command= lambda: controller.reload_frame(ShoppingCart), cursor="hand2")
        cartlabel.grid(row=0, column=4, padx=(10, 25), pady=10, sticky="w")
        cartlabel.configure(font=general_label_font)

        welcomelabel = Label(self, text="Welcome! What would you like to do?", foreground="#505050")
        welcomelabel.grid(row=1, column=1, padx=25, pady=25)
        welcomelabel.configure(font=tkfont.Font(family="Calibri", size=25))

        create_product_button = Button(self, text="Post your own product", background="#0063fb", foreground="#fff", command= lambda: controller.reload_frame(PostProductPage), cursor="hand2")
        create_product_button.grid(row=2, column=1, padx=(0, 300), pady=25)
        create_product_button.configure(font=product_buttons)
        search_product_button = Button(self, text="Search for a product", background="#0063fb", foreground="#fff", command= lambda: controller.reload_frame(SearchProductPage), cursor="hand2")
        search_product_button.grid(row=2, column=1, padx=(300, 0), pady=25)
        search_product_button.configure(font=product_buttons)

    def get_set_database(self):
        #Call the method in the Connect_MongoDB class
        mydb = self.database_connect.get_current_database()
        #Set inheritable value to the database
        Pages.database = mydb

    def login(self):
        #When user is logged in, configure the login button to logout
        self.loginbutton.configure(text="Log out")
        #Raise the loginpage frame into view, to allow for user to login
        self.controller.current_frame("LoginPage")

    def logout(self):
        #When user logs out, update login button, update inheritable values and then reload the mainpage to set the updates
        self.loginbutton.configure(text="Log in")
        Pages.loggedin = False
        Pages.user = ""
        self.controller.reload_frame(MainPage)    

class PostProductPage(tk.Frame, Pages):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label_font = ("Calibri", 13)

        #Check that the user is logged in, a product cannot be created without a user logged in
        if Pages.loggedin == True:
            
            #Code creates an abundance of labels,  entries and buttons, whose functionality has been described above.
            logolabel = Button(self, text="  FINNPLUS  ", background="#06bffc", foreground="#fff", highlightthickness = 0, bd = 0, command= lambda: controller.reload_frame(MainPage), cursor="hand2")
            logolabel.grid(row=0, column=0, padx=(10, 5), pady=10)
            logolabel.configure(font=Pages.logo_font)

            sloganlabel = Label(self, text="The market of possibilities")
            sloganlabel.grid(row=0, column=1)
            sloganlabel.configure(font=Pages.slogan_font)

            productnamelabel = Label(self, text="What is the name of the product?")
            productnamelabel.grid(row=1, column=1, padx=0, pady=15, sticky = 'w')
            productnamelabel.configure(font=label_font)

            productdesclabel = Label(self, text="Give a description of product")
            productdesclabel.grid(row=1, column=2, padx=(50, 0), pady=15, sticky = 'w')
            productdesclabel.configure(font=label_font)

            #One particular thing to highlight, the reason why the entries are self. variables is so that they can be collected when a method is called
            self.productnameentry = Entry(self, borderwidth=5, width=40)
            self.productnameentry.grid(row=2, column=1, padx=0, sticky = 'nw')
            
            self.productdesctext = Text(self, borderwidth=5, height=7, width=50)
            self.productdesctext.grid(row=2, column=2, padx=(50,0))

            productcategory = Label(self, text="What category is this product?")
            productcategory.grid(row=3, column=1, padx=0, pady=15, sticky = 'w')
            productcategory.configure(font=label_font)

            #However, the lambda does not always need to be utilised. At least, not when parameters aren't passed through to a method.
            productimagebutton = Button(self, text="Choose image file", borderwidth=3, cursor="hand2", command=self.filebrowse)
            productimagebutton.grid(row=3, column=2, padx=(50,0), pady=(15, 0), sticky = 'w')
            productimagebutton.configure(font=label_font)

            self.productcategoryentry = Entry(self, borderwidth=5, width=40)
            self.productcategoryentry.grid(row=3, column=1, padx=0, pady=(80, 0), sticky="n")

            productimagewarning = Label(self, text="Note, image will be rescaled to 250x150. \nBelow is what your image would look like.")
            productimagewarning.grid(row=3, column=2, padx=(50, 0), pady=(100,0), stick="w")
            productimagewarning.configure(font=tkfont.Font(family="Calibri", size=10))

            self.productimagelabel = Label(self, text="")
            self.productimagelabel.configure(font=label_font)
        
            productpricelabel = Label(self, text="Price of product?")
            productpricelabel.grid(row=5, column=1, padx=0, pady=15, sticky = 'w')
            productpricelabel.configure(font=label_font)

            productcondition = Label(self, text="What is the condition?")
            productcondition.grid(row=5, column=2, padx=(50,0), pady=15, sticky = 'w')
            productcondition.configure(font=label_font)

            self.productpriceentry = Entry(self, borderwidth=5, width=20)
            self.productpriceentry.grid(row=6, column=1, padx=0, pady=(0,15), sticky= 'w')

            pricecurrency = Label(self, text="NOK")
            pricecurrency.grid(row=6, column=1, padx=(50,0), pady=(0,15))
            pricecurrency.configure(font=label_font)

            self.productconditionentry = Entry(self, borderwidth=5, width=30)
            self.productconditionentry.grid(row=6, column=2, padx=(50, 0), pady=(0,15), sticky= 'w')

            #Call method in the class to then publish the product when fields are filled out
            self.submit_button = Button(self, text="Publish Product", background="#0063fb", foreground="#fff", command=self.publish_product)
            self.submit_button.grid(row=7, column=1, pady=25, sticky="w")
            self.submit_button.configure(font=tkfont.Font(family="Calibri", size=15))
        #If not logged in, reroute them to the loginpage
        else:
            self.controller.current_frame("LoginPage")

    def filebrowse(self):
        #Create a grid forget label, that removes image if user chooses to change mind
        self.productimagelabel.grid_forget()
        #self.imagefilename opens a file.explorer browser where a user can choose an image of their liking
        self.imagefilename = filedialog.askopenfilename(initialdir= "/", title="Choose PNG Image", filetype=[("png",".png")])
        self.productimage = self.imagefilename
        self.productimagelabel.grid(row=4, column=2, padx=(50, 0), pady=15, sticky = 'w')
        #To demonstrate to the user how their image would look, open the file, resize the image and set it to the label
        productimage = Image.open(self.productimage)
        productimage = productimage.resize((250,150), Image.ANTIALIAS)
        productpicture = ImageTk.PhotoImage(productimage)
        #Make sure image is visible by applying .photo to have the object anchored to the image, then update  and configure
        self.productimagelabel.photo = productpicture
        self.productimagelabel.configure(image=productpicture)
        
    def publish_product(self):
        #When a product is published it must go through several stages of checking to be determined as valid, hence the creation for a list and a boolean value
        entry_list = []
        self.entrycheck = None

        #The try statement checks that all entries can be collected. This mostly refers to the price, which must be an integer. If it isn't, return an error.
        try:
            productname = self.productnameentry.get()
            productdesc = self.productdesctext.get("1.0", "end-1c")
            productcategory = self.productcategoryentry.get()
            productimage = self.productimage
            productprice = int(self.productpriceentry.get())
            productcondition = self.productconditionentry.get()
    
            #If successful, append to list and then check if all entries have been filled
            entry_list.extend((productname, productdesc, productcategory, productimage, productprice, productcondition))

            #If entries are filled, True will be returned, and the rest of the code can execute
            for any in entry_list:
                if len(str(any)) == 0:
                    self.entrycheck = False
                    break
                else:
                    self.entrycheck = True
            
            if self.entrycheck:
                #Once all field entries are valid, connect to the product collection
                mydb = Pages.database
                mycol = mydb["Products"]
                #Retrieve logged in user and the date from the inherited Pages class
                postedby = Pages.user
                posteddate = (str(Pages.currentdate.year) + "-" + str(Pages.currentdate.month) + "-" + str(Pages.currentdate.day))

                #A product must be checked that the name is unique, as is the image to avoid data consistency later
                checkproduct = mycol.find_one( { "ProductName": productname } )
                checkimage = mycol.find_one( { "ProductImage": self.productimage } )
                #When the image is selected, the filename is required. The filebrowse method returns the directory of the image
                #Using the built in .rfind function, the index of the last "/" is found. The stirng of the product image is sliced, and then saved to images + the actual image name
                indexplace = productimage.rfind("/")
                adjustimage = "Images" + productimage[indexplace:]

                #Check that both product and iamge are valid, if there is no document return, then proceed
                if checkproduct == None:
                    if checkimage == None:
                        #Use try statement incase invalid values are used that mess with MongoDB
                        try:
                            #Submit the product and insert it into the collection
                            submit_product = mycol.insert_one( { "ProductName": productname, "ProductDescription": productdesc, "ProductCategory": productcategory, "ProductImage": adjustimage, 
                                                                "ProductPrice": productprice, "Condition": productcondition, "PostedBy": postedby, "DateCreated": posteddate } )
                            #Get a copy of the image, and move it into the file "Images"
                            shutil.copy(self.imagefilename, "Images")
                            #Return successful message, and then redirect to MainPage
                            messagebox.showinfo("Finnplus Product Submission", "Your product has now been successfully submitted, and can be viewed in the application.")
                            self.controller.reload_frame(MainPage)

                        except:
                            messagebox.showerror("Error", "Invalid inputs.")
                    else:
                        messagebox.showerror("Error", "Product Image name taken, please change it.")
                else:
                    messagebox.showerror("Error", "Product already exists.")
            #Otherwise, it will report missing values
            else:           
                messagebox.showerror("Error", "Missing values.")
        except:
            messagebox.showerror("Error", "Price is not integer or Image is missing.")

class SearchProductPage(tk.Frame, Pages):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        #Set various fonts, and then call the main class
        self.top_widgets_font = ("Calibri", 15, "bold")
        self.product_labels = ("Calibri", 15)
        self.product_page_labels = ("Calibri", 12)
        self.main()

    #Important to have a main method that can allow the user to return to if they wish to see other products
    def main(self):
        #Connect to collection, and create a class to store all widgets for the products
        self.mydb = Pages.database
        self.mycol = self.mydb["Products"]
        self.productlistwidgets = []

        #This section is split up into two frames, the first frame initiates a search for the product which returns limited information on a product, 
        #while the second frame is the actual product page, which displays all the product's information.
        self.product_search_frame = Frame(self)
        self.product_search_frame.grid(row=0, column=0)
        self.product_page_frame = Frame(self)

        logolabel = Button(self.product_search_frame, text="  FINNPLUS  ", background="#06bffc", foreground="#fff", highlightthickness = 0, bd = 0, command= lambda: self.controller.reload_frame(MainPage), cursor="hand2")
        logolabel.grid(row=0, column=0, padx=(10, 5), pady=10)
        logolabel.configure(font=Pages.logo_font)

        self.searchbox = Entry(self.product_search_frame, borderwidth=5, width=35)
        self.searchbox.grid(row=0, column=1)
        self.searchbox.configure(font=tkfont.Font(family="Calibri", size=20))

        #Once search is input, and search button clicked, the search method will start
        searchbutton = Button(self.product_search_frame, text="Search", background="#000000", foreground="#fff", command=self.search, cursor="hand2")
        searchbutton.grid(row=0, column=2, padx=(10,0))
        searchbutton.configure(font=self.top_widgets_font)

        if Pages.loggedin == False:
            self.loginbutton = Button(self.product_search_frame, text="Log in", background="#fff", command=self.login, cursor="hand2")
            self.loginbutton.grid(row=0, column=3, padx=(10,0))
            self.loginbutton.configure(font=self.top_widgets_font)
        else:
            self.loginbutton = Button(self.product_search_frame, text="Log out", background="#fff", command=self.logout, cursor="hand2")
            self.loginbutton.grid(row=0, column=3, padx=(10,0))
            self.loginbutton.configure(font=self.top_widgets_font)

        cartlabel = Button(self.product_search_frame, text="CART", background="#06bffc", foreground="#fff", command= lambda: self.controller.reload_frame(ShoppingCart), cursor="hand2")
        cartlabel.grid(row=0, column=4, padx=(10,0))
        cartlabel.configure(font=self.top_widgets_font)

    def search(self): 
        #Set various variables and lists required
        productname = self.searchbox.get()
        productlist = []
        productpictures = []

        #Use regular expression in query to find results similar to what was searched, instead of word for word
        query_return = self.mycol.find( { "ProductName": { "$regex": '.*' + productname + '.*'} } )
        #Append all documents found to the productlist
        for document in query_return:
            productlist.append(document)

        #If a user repeats a search then all the last products should be forgotten, hence the productwidgetlist is checked
        #and then all widgets will be cleared by column (one product per row), and the list gets cleared
        if len(self.productlistwidgets) != 0:
                for some_widget in self.productlistwidgets:
                    some_widget[0].grid_forget()
                    some_widget[1].grid_forget()
                    some_widget[2].grid_forget()
                    some_widget[3].grid_forget()
                    some_widget[4].grid_forget()
                self.productlistwidgets.clear()

        #This for loop creates all the widgets for the products that were appended to the product list
        #However, instead of a range, enumarate is used to retrieve images
        for imagekey, products in enumerate(productlist):
            #Open image, resize it and then append it to the productpictures list. The reason for this requirement, is that
            #if they weren't appended and called separately in the for loop, tkinter will consistenly update the image, and
            #in turn, will only return one image to be displayed. To avoid this, a list was created.
            self.productimage = Image.open(products["ProductImage"])
            self.productimage = self.productimage.resize((250,150), Image.ANTIALIAS)
            productpictures.append(ImageTk.PhotoImage(self.productimage))

            product_value = products["ProductName"]

            #Generate all widgets, since the query returns dictionary values, all information can be retrieved by calling them with the dictionary key
            widgets = [Label(self.product_search_frame, image=productpictures[imagekey]),
                       Button(self.product_search_frame, text=products["ProductName"], highlightthickness = 0, cursor="hand2", command= lambda product_value=product_value: self.product_page(product_value)),
                       Label(self.product_search_frame, text=products["Condition"]),
                       Label(self.product_search_frame, text=products["PostedBy"]),
                       Label(self.product_search_frame, text=str(products["ProductPrice"]) + "NOK")]

            #Move them to the list of widgets
            self.productlistwidgets.append(widgets)
        
        #Once more to now set all these values of one product at a time, a for loop is utilized
        #enumerate being used once more, so that the index values (rows), can be used for the row in the grid
        for rows, widget in enumerate(self.productlistwidgets):
            #adjust row to + 1 because of the widgets at the top of the frame
            actual_row = rows + 1

            #additionaly use rows to get the corresponding image from the productpictures list 
            #(they were added in order), hence should be retrieved in order
            widget[0].photo = productpictures[rows]
            widget[0].grid(row=actual_row, column=0, padx=5, pady=5)
            widget[1].grid(row=actual_row, column=1, padx=5, pady=5)
            widget[1].configure(font=self.product_labels)
            widget[2].grid(row=actual_row, column=2, padx=5, pady=5)
            widget[2].configure(font=self.product_labels)
            widget[3].grid(row=actual_row, column=3, padx=5, pady=5)
            widget[3].configure(font=self.product_labels)
            widget[4].grid(row=actual_row, column=4, padx=5, pady=5)
            widget[4].configure(font=self.product_labels)

            #Limit document search to 4 products per page, if product is not visible, then the search can be adjusted since a regular expression is used.
            if rows == 3:
                break

    #Once a product name button is clicked, it will pass the value of the buttons text to the product_page method
    def product_page(self, nameofproduct):
        #Important, that since this is still inside one class (one frame), it is split among two frames. Hence, to remove all aspects of the product search frame, a grid_forget() is used.
        self.product_search_frame.grid_forget()
        self.product_page_frame.grid(row=0, column=0)

        #Generate labels
        logolabel = tk.Button(self.product_page_frame, text="  FINNPLUS  ", background="#06bffc", foreground="#fff", highlightthickness = 0, bd = 0, command= lambda: self.controller.reload_frame(MainPage), cursor="hand2")
        logolabel.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="w")
        logolabel.configure(font=Pages.logo_font)

        backbutton = tk.Button(self.product_page_frame, text="Back", background="#000000", foreground="#fff", command=self.switch_to_search, cursor="hand2")
        backbutton.grid(row=0, column=2, padx=(10,0))
        backbutton.configure(font=self.top_widgets_font)

        if Pages.loggedin == False:
            self.loginbutton = tk.Button(self.product_page_frame, text="Log in", background="#fff", command=self.login, cursor="hand2")
            self.loginbutton.grid(row=0, column=3, padx=(10,0))
            self.loginbutton.configure(font=self.top_widgets_font)
        else:
            self.loginbutton = tk.Button(self.product_page_frame, text="Log out", background="#fff", command=self.logout, cursor="hand2")
            self.loginbutton.grid(row=0, column=3, padx=(10,0))
            self.loginbutton.configure(font=self.top_widgets_font)

        cartlabel = tk.Button(self.product_page_frame, text="CART", background="#06bffc", foreground="#fff", command= lambda: self.controller.reload_frame(ShoppingCart), cursor="hand2")
        cartlabel.grid(row=0, column=4, padx=(10,0))
        cartlabel.configure(font=self.top_widgets_font)

        #The value passed will be used to identify the product and retrieve its information
        selected_product = self.mycol.find_one( { "ProductName": nameofproduct} )

        #Open and set the image once more, resizing it to a larger portion
        productimage = Image.open(selected_product["ProductImage"])
        productimage = productimage.resize((325,225), Image.ANTIALIAS)
        productpicture = ImageTk.PhotoImage(productimage)

        name = Label(self.product_page_frame, text=selected_product["ProductName"])
        name.grid(row=1, column=1, padx=10, pady=10, stick="w")
        name.configure(font=self.top_widgets_font)

        img = Label(self.product_page_frame, image=productpicture)
        img.photo = productpicture
        img.grid(row=2, column=0, pady=10)

        #A difference in this label is that it uses wraplength. To avoid having the description stretch across 3 monitors, some limit needed to be put into place.
        #Then the labels are using justify left, to move all text and organise it to the left side.
        desc = Label(self.product_page_frame, text=selected_product["ProductDescription"], wraplength=450, justify=LEFT)
        desc.grid(row=2, column=1, padx=10, pady=10, sticky="n")
        desc.configure(font=self.product_page_labels)

        category = Label(self.product_page_frame, text="Product Category: \n" + selected_product["ProductCategory"], justify=LEFT)
        category.grid(row=3, column=0, padx=(50,0), pady=10, sticky="w")
        category.configure(font=self.product_page_labels)

        condition = Label(self.product_page_frame, text="Product Condition: \n" + selected_product["Condition"], justify=LEFT)
        condition.grid(row=3, column=1, padx=30, sticky="w")
        condition.configure(font=self.product_page_labels)

        seller = Label(self.product_page_frame, text="Posted by: \n" + selected_product["PostedBy"], justify=LEFT)
        seller.grid(row=4, column=0, padx=(50,0), sticky="w")
        seller.configure(font=self.product_page_labels)

        #Assure that even integer values are converted to string, or else they could not be used in a label's text.
        price = Label(self.product_page_frame, text="Price: \n" + str(selected_product["ProductPrice"]) + "NOK", justify=LEFT)
        price.grid(row=4, column=1, padx=30, sticky="w")
        price.configure(font=self.product_page_labels)

        datecreated = Label(self.product_page_frame, text="Date Created: \n" + selected_product["DateCreated"], justify=LEFT)
        datecreated.grid(row=5, column=0, padx=(50,0), pady=(10,30), sticky="w")
        datecreated.configure(font=self.product_page_labels)

        quantity_label = Label(self.product_page_frame, text="Quantity", justify=LEFT)
        quantity_label.grid(row=3, column=2, sticky="sw")
        quantity_label.configure(font=self.product_page_labels)
        self.quantity_entry = Entry(self.product_page_frame, borderwidth=5, width=5)
        self.quantity_entry.grid(row=4, column=2)
        self.quantity_entry.configure(font=self.product_page_labels)

        #Last part of the product section is to make sure the user can add it to the cart. The product name, user who posted the product, and the price are passed on as these are the relevant values needed.
        add_to_cart = Button(self.product_page_frame, text="Add to cart", background="#000000", foreground="#fff", command=lambda: self.add_to_cart(selected_product["ProductName"], selected_product["PostedBy"], selected_product["ProductPrice"]))
        add_to_cart.grid(row=5, column=1, columnspan=2, sticky="e")
        add_to_cart.configure(font=tkfont.Font(family="Calibri", size=20, weight="bold"))

    def add_to_cart(self, pname, userpost, pricing):
        #Although products can be viewed, once the add cart button is clicked, then a user must be logged in. Hence it checks, and if not true it redirects them to the loginpage
        if Pages.loggedin == True:
            newcol = self.mydb["Shopping_Cart"]
            #First check is to make sure that the quanity is an integer, if not return error.
            try:
                quantity = int(self.quantity_entry.get())
                subtotal = pricing * quantity

                #Guarentee that quanity is not empty or equal to 0
                if quantity == "" or quantity == 0:
                    messagebox.showerror("Error", "Invalid quantity.")

                else:
                    #Further checks, check if the product exists in the users shopping cart, check by user name and by product name
                    check_product_in_cart = newcol.find_one( { "user": Pages.user, "products.ProductName": pname })

                    if check_product_in_cart == None:
                        #If no query is returned, then product can be added, but first since the database structure makes it
                        #so that every user has their own shopping cart, it must be checked if it exists or not
                        check_user_cart = newcol.find_one( { "user": Pages.user } )
                        
                        if check_user_cart == None:
                            #If it does not exist, simply create a new one through an insert. Return messagebox
                            create_add = newcol.insert_one( { "user": Pages.user, "products": [ {"ProductName": pname, "PostedBy": userpost, "Quantity": quantity, "ProductPrice": pricing, "Subtotal": subtotal} ] } )
                            messagebox.showinfo("Finnplus Cart", "Product was added to cart.")                    
                        else:
                            #If it does not exist, then simply push the product into the products section of the document
                            add = newcol.update_one( { "user": Pages.user}, { "$push": { "products": {"ProductName": pname, "PostedBy": userpost, "Quantity": quantity, "ProductPrice": pricing, "Subtotal": subtotal} } })
                            messagebox.showinfo("Finnplus Cart", "Product was added to cart.")
                    else:
                        #If however, the user chooses to click the add_cart again, while the product already exists in the shopping cart, then it must be updated with this value (it is added)
                        #Because "check_product_in_cart" returns an array of dictionaries, first the program goes into products and the first value, because only one is returned. Then the quantity
                        #and subtotal must be updated (subtotal is a result of quantity, as can be seen above, below the try statement)
                        print(quantity)
                        print(check_product_in_cart["products"][0]["Quantity"])
                        new_quantity = check_product_in_cart["products"][0]["Quantity"] + quantity
                        print(new_quantity)
                        new_subtotal = check_product_in_cart["products"][0]["ProductPrice"] * new_quantity
                        
                        #Because the collection has documents, where the products are an array of embedded documents, a regular set aggregate would not work. The reason being that it would remove all items
                        #instead of actually updating the already existing ones. A "$" must be placed between the product and the wanted field because it must retrieve that occurence
                        add = newcol.update_one( { "user": Pages.user, "products.ProductName": pname }, { "$set": { "products.$.Quantity": new_quantity, "products.$.Subtotal": new_subtotal} } )
                        messagebox.showinfo("Finnplus Cart", "Cart has been updated with new quantity.")
            except:
                messagebox.showerror("Error", "Quantity is not integer or missing value.")
        else:
            self.controller.current_frame("LoginPage")

    def login(self):
        self.loginbutton.configure(text="Log out")
        self.controller.current_frame("LoginPage")

    def logout(self):
        self.loginbutton.configure(text="Log in")
        Pages.loggedin = False
        Pages.user = ""
        self.controller.reload_frame(MainPage)

    #Back button method
    def switch_to_search(self):
        #Forget the product page grid, return to main
        self.product_page_frame.grid_forget()
        self.main()

class ShoppingCart(tk.Frame, Pages):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        #Connect to the shopping cart database, set to self. to be accessible by all methods
        self.mydb = Pages.database
        self.mycol = self.mydb["Shopping_Cart"]

        title_label_font = ("Calibri", 15, "bold")
        items_font = ("Calibri", 13)

        #Shopping cart cannot be accessed if user is not logged in
        if Pages.loggedin == True:
            logolabel = tk.Button(self, text="  FINNPLUS  ", background="#06bffc", foreground="#fff", highlightthickness = 0, bd = 0, command= lambda: self.controller.reload_frame(MainPage), cursor="hand2")
            logolabel.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="w")
            logolabel.configure(font=Pages.logo_font)

            sloganlabel = tk.Label(self, text="logo logo logo, go to finn.no")
            sloganlabel.grid(row=0, column=1)
            sloganlabel.configure(font=Pages.slogan_font)

            #Check if the cart exists
            usercart = self.mycol.find_one( {"user": Pages.user})
            
            #If the cart does not exist yet, then the user should not see an empty cart, instead they should be notified.
            #Therefore, redirect this situation to a different shopping cart frame design
            if usercart == None:
                self.empty_cart()

            else:
                #Retrieve length of the user cart to display as total amount of products
                self.total_items = len(usercart["products"])

                #Check if the cart is empty, if empty redirect, else set the appropriate labels
                if self.total_items != 0:
                    pnamelabel = Label(self, text="Name")
                    pnamelabel.grid(row=1, column=0, pady=10)
                    pnamelabel.configure(font=title_label_font)

                    oplabel = Label(self, text="Posted By")
                    oplabel.grid(row=1,column=1, pady=10)
                    oplabel.configure(font=title_label_font)

                    amountlabel = Label(self, text="Quantity")
                    amountlabel.grid(row=1,column=2, pady=10)
                    amountlabel.configure(font=title_label_font)

                    pricelabel = Label(self, text="Price")
                    pricelabel.grid(row=1,column=3, pady=10)
                    pricelabel.configure(font=title_label_font)

                    subtotallabel = Label(self, text="Subtotal")
                    subtotallabel.grid(row=1,column=4, pady=10)
                    subtotallabel.configure(font=title_label_font)

                    #Utilize a for loop with a range. This way, rows can be set via the index of the range
                    for item in range(self.total_items):
                        #Since various labels already exist before this, add 2 to avoid writing over widgets
                        adjusted_row = item + 2

                        #When the query is not empty, it returns an array of embedded documents. This means that, additionaly
                        #the index of the product in the shopping cart can be retrieved through "item", and then the corresponding values from the required fields
                        product_name = usercart["products"][item]["ProductName"]
                        pname = Label(self, text=product_name)
                        pname.grid(row=adjusted_row, column=0, padx=25, pady=10)
                        pname.configure(font=items_font)

                        op = Label(self, text=usercart["products"][item]["PostedBy"])
                        op.grid(row=adjusted_row, column=1, padx=25, pady=10)
                        op.configure(font=items_font)

                        pname = Label(self, text=usercart["products"][item]["Quantity"])
                        pname.grid(row=adjusted_row, column=2, padx=25, pady=10)
                        pname.configure(font=items_font)

                        pname = Label(self, text=usercart["products"][item]["ProductPrice"])
                        pname.grid(row=adjusted_row, column=3, padx=25, pady=10)
                        pname.configure(font=items_font)

                        pname = Label(self, text=usercart["products"][item]["Subtotal"])
                        pname.grid(row=adjusted_row, column=4, padx=25, pady=10)
                        pname.configure(font=items_font)

                        #For each product a button exists, where a lambda function is used to pass on the productname
                        self.removeproduct = Button(self, text="×", background="#000000", foreground="#fff", width=4, cursor="hand2", command=lambda product_name=product_name: self.remove_product(product_name))
                        self.removeproduct.grid(row=adjusted_row, column=5, padx=25, pady=10)
                        self.removeproduct.configure(font=items_font)

                    #Aggregate through the shopping cart collections, and return the sum of all the subtotals found in the array of embedded documents.
                    #Since it is an array, unwind must be used, while also using a match statement to find the users shopping cart. Finally, all of it is grouped together through a group aggregate
                    total_price_query = list(self.mycol.aggregate( [ { "$match": { "user": Pages.user } }, { "$unwind": "$products" }, { "$group": { "_id": "$user", "total": { "$sum": "$products.Subtotal" } } } ] ))
                    total_price = total_price_query[0]["total"]

                    totalpricelabel = Label(self, text="Total Amount")
                    totalpricelabel.grid(row=self.total_items+2, column=4, padx=25, pady=10)
                    totalpricelabel.configure(font=title_label_font)

                    totalpricelabel = Label(self, text=total_price)
                    totalpricelabel.grid(row=self.total_items+3, column=4, pady=10)
                    totalpricelabel.configure(font=items_font)

                    totalitemslabel = Label(self, text="Amount of unique items")
                    totalitemslabel.grid(row=self.total_items+2, column=2, columnspan=2, padx=25, pady=10)
                    totalitemslabel.configure(font=title_label_font)

                    totalitemslabel = Label(self, text=self.total_items)
                    totalitemslabel.grid(row=self.total_items+3, column=2, columnspan=2, pady=10)
                    totalitemslabel.configure(font=items_font)

                    checkoutbutton = Button(self, text="Check out", background="#0063fb", foreground="#fff", command= lambda: self.controller.reload_frame(Checkout), cursor="hand2")
                    checkoutbutton.grid(row=self.total_items+2, rowspan=2, column=0, columnspan=2, pady=10)
                    checkoutbutton.configure(font=title_label_font)

                else:
                    self.empty_cart()

        else:
            self.controller.current_frame("LoginPage")

    def empty_cart(self):
        #When the cart is empty, a label is created which notifies the user, furthermore the button for product search is added below, where when clicked, redirects to the SearchProductPage class
        empty_label = Label(self, text="This cart is empty! Go find some products at product search.")
        empty_label.grid(row=1,column=1, pady=(100, 25))
        empty_label.configure(font=tkfont.Font(family="Calibri", size=25, weight="bold"))

        search_product_button = tk.Button(self, text="Search for a product", background="#0063fb", foreground="#fff", command= lambda: self.controller.reload_frame(SearchProductPage), cursor="hand2")
        search_product_button.grid(row=2, column=1, pady=25)
        search_product_button.configure(font=tkfont.Font(family="Calibri", size=20))
        
    def remove_product(self, name):
        #When a product is removed, a pull aggregate is used to remove the specified product from the products array.
        #This must be pulled from the user that is logged in, and the product being the value passed from clicking the button
        self.mycol.update_one( { "user": Pages.user, "products.ProductName": name }, { "$pull": { "products": { "ProductName": name } } })

        #However, if a shopping_cart page is empty, then entirely delete the shopping cart document as it is no longer useful. Reload the frame to update changes.
        if self.total_items == 1:
            self.mycol.delete_one( { "user": Pages.user } )
        self.controller.reload_frame(ShoppingCart)

class Checkout(tk.Frame, Pages):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label_font = ("Calibri", 15, "bold")
        button_font = ("Calibri", 20, "bold")

        checkoutlabel = Label(self, text="Checkout")
        checkoutlabel.grid(row=0, column=0, columnspan=2, padx=(325, 25), pady=15)
        checkoutlabel.configure(font=tkfont.Font(family="Calibri", size=30, weight="bold"))

        cardnumberlabel = Label(self, text="Input credit card number")
        cardnumberlabel.grid(row=1, column=0, padx=(275,0), pady=(0,10), stick="w")
        cardnumberlabel.configure(font=label_font)

        billingaddresslabel = Label(self, text="Billing Address")
        billingaddresslabel.grid(row=1, column=1, padx=(25, 0), pady=(0,10), stick="w")
        billingaddresslabel.configure(font=label_font)

        self.cardnumberentry = Entry(self, borderwidth=5, width=16)
        self.cardnumberentry .grid(row=2, column=0, padx=(275,0), stick="w")

        self.billingaddressentry = Entry(self, borderwidth=5, width=25)
        self.billingaddressentry.grid(row=2, column=1, padx=(25, 0), stick="w")

        firstnamelabel = Label(self, text="First Name")
        firstnamelabel.grid(row=3, column=0, padx=(275,0), pady=(0,10), stick="w")
        firstnamelabel.configure(font=label_font)

        lastnamelabel = Label(self, text="Last Name")
        lastnamelabel.grid(row=3, column=1, padx=(25, 0), pady=(0,10), stick="w")
        lastnamelabel.configure(font=label_font)

        self.firstnameentry = Entry(self, borderwidth=5, width=15)
        self.firstnameentry.grid(row=4, column=0, padx=(275,0), stick="w")

        self.lastnameentry = Entry(self, borderwidth=5, width=15)
        self.lastnameentry.grid(row=4, column=1, padx=(25, 0), stick="w")

        countrylabel = Label(self, text="Country")
        countrylabel.grid(row=5, column=0, padx=(275,0), pady=(0,10), stick="w")
        countrylabel.configure(font=label_font)

        phonelabel = Label(self, text="Phone")
        phonelabel.grid(row=5, column=1, padx=(25, 0), pady=(0,10), stick="w")
        phonelabel.configure(font=label_font)

        self.countryentry = Entry(self, borderwidth=5, width=15)
        self.countryentry.grid(row=6, column=0, padx=(275,0), stick="w")

        self.phoneentry = Entry(self, borderwidth=5, width=15)
        self.phoneentry.grid(row=6, column=1, padx=(25, 0),  stick="w")

        #Two buttons, one for cancelling the process and one for finalising it, wioth finalising calling the storepurchase method.
        self.cancelbutton = Button(self, text="Cancel and Go Back", background="#000000", foreground="#fff", command= lambda: self.controller.reload_frame(ShoppingCart), cursor="hand2")
        self.cancelbutton.grid(row=7, column=0, padx=(275, 0), pady=15, sticky="w")
        self.cancelbutton.configure(font=button_font)

        self.purchasebutton = Button(self, text="Finalise Purchase", background="#0063fb", foreground="#fff", command=self.storepurchase, cursor="hand2")
        self.purchasebutton.grid(row=7, column=1, padx=(25, 0), pady=15)
        self.purchasebutton.configure(font=button_font)

    def storepurchase(self):
        #Similar to before, check values by creating a list and iterating through them
        entry_list = []
        self.entrycheck = None

        cardnumber = self.cardnumberentry.get()
        address = self.billingaddressentry.get()
        fullname = str(self.firstnameentry.get() + self.lastnameentry.get())
        country = self.countryentry.get()
        phone = self.phoneentry.get()

        entry_list.extend((cardnumber, address, fullname, country, phone))

        for any in entry_list:
            if len(str(any)) == 0:
                self.entrycheck = False
                break
            else:
                self.entrycheck = True
        
        if self.entrycheck:
            #Card length has to be 16
            if len(cardnumber) == 16:
                #Even though it is a string, it should still contain only digits
                if cardnumber.isdigit():
                    #Get the collection that will be written to
                    mydb = Pages.database
                    order_col = mydb["orderinformation"]
                    cart_col = mydb["Shopping_Cart"]
                    #Retrieve any other pieces of information, such as the current date, the products, and the ordernumber.
                    orderdate = (str(Pages.currentdate.year) + "-" + str(Pages.currentdate.month) + "-" + str(Pages.currentdate.day))
                    product_query = cart_col.find_one( { "user": Pages.user }, { "_id": 0, "products": 1})
                    ordernumber = cart_col.find().count() + 1
                    
                    #Submit the order with the collected values for the fields, and then notify user of successful purchase. 
                    submit_order = order_col.insert_one( { "OrderNumber": ordernumber, "User": Pages.user, 
                                                            "FullName": fullname, "DateOrdered": orderdate, 
                                                            "CardNumber": cardnumber, "BillingAddress": address,
                                                            "Country": country, "PhoneNumber": phone, "ProductsOrdered": product_query } )

                    messagebox.showinfo("Finnplus Order Completed", "Thank you for purchasing at Finnplus")
                    #Delete the shopping cart as it is now irrelevant and send user back to the mainpage
                    delete_cart = cart_col.delete_one( {"user": Pages.user })
                    self.controller.reload_frame(MainPage)

                else:
                    messagebox.showerror("Card Error", "Card number must contain digits")
            else:
                messagebox.showerror("Card Error", "Card must be 16 digits")
        else:
            messagebox.showerror("Error", "Missing values")

class LoginPage(tk.Frame, Pages):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.label_font = ("Calibri", 15)
        self.button_font = ("Calibri", 15, "bold")
        self.main_tab()
    
    def main_tab(self):
        labelframelogin = Label(self, text="Sign-In")
        labelframelogin.grid(row=0, column=0, padx=350, pady=15)
        labelframelogin.configure(font=tkfont.Font(family="Calibri", size=20))

        labelusername = Label(self, text="Enter your username or email you signed up with")
        labelusername.grid(row=1, column=0, padx=250)
        labelusername.configure(font=self.label_font)

        self.entryusername = Entry(self, borderwidth=5, width=50)
        self.entryusername.grid(row=2, column=0, padx=350, pady=5)

        labelusername = Label(self, text="Enter your password")
        labelusername.grid(row=3, column=0, padx=350)
        labelusername.configure(font=self.label_font)

        #A difference to note here is the, 'show="*"'. This makes it that what is being typed is hidden.
        #Adding some level of security to the application
        self.entrypassword = Entry(self, show="*", borderwidth=5, width=50)
        self.entrypassword.grid(row=4, column=0, padx=350, pady=5)

        buttonlogin = Button(self, text="Login", width=30, background="#0063fb", foreground="#fff", command=self.submitdetails, cursor="hand2")
        buttonlogin.grid(row=5, column=0, padx=350, pady=5)
        buttonlogin.configure(font=self.button_font)

        buttonsignup = Button(self, text="Create New Account", width=30, background="#fff", foreground="#0063fb", command= lambda: self.controller.current_frame("SignupPage"), cursor="hand2")
        buttonsignup.grid(row=6, column=0, padx=350, pady=5)
        buttonsignup.configure(font=self.button_font)

        buttoncancel = Button(self, text="Cancel and go back", width=30, background="#000000", foreground="#fff", command= lambda: self.controller.reload_frame(MainPage), cursor="hand2")
        buttoncancel .grid(row=7, column=0, padx=350, pady=(5, 25))
        buttoncancel .configure(font=self.button_font)

    def submitdetails(self):
        mydb = Pages.database
        mycol = mydb["login"]

        username = self.entryusername.get()
        password = self.entrypassword.get()

        #Do a try statement to check that the values added will not cause error in database
        try:
            #Username should be either same as username or email
            login_result = mycol.find_one( { "$or": [ {"user.username": username}, {"user.email": username } ] } )
            #Added if statement to give error if no password is input
            if len(password) != 0:
                #If password is the same as database update values, go back to main page
                if login_result["password"] == password:
                    Pages.loggedin = True
                    Pages.user = username
                    self.controller.reload_frame(MainPage)         
                    
                else:
                    messagebox.showerror("Error", "Username or Password incorrect.")
            else:
                messagebox.showerror("Error", "No password detected.")
        except:
            messagebox.showerror("Error", "Username or Password incorrect.")

class SignupPage(tk.Frame, Pages):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label_font = ("Calibri", 12)
        button_font = ("Calibri", 15, "bold")

        signuplabel = Label(self, text="Create A New Account")
        signuplabel.grid(row=0, column=0, padx=(350,20), pady=10)
        signuplabel.configure(font=tkfont.Font(family="Calibri", size=20))

        userentrylabel = Label(self, text="Enter valid username")
        userentrylabel.grid(row=1, column=0, padx=(125,0), pady=5)
        userentrylabel.configure(font=label_font )

        emailentrylabel = Label(self, text="Enter valid email address")
        emailentrylabel.grid(row=1, column=0, padx=(500,0), pady=5)
        emailentrylabel.configure(font=label_font )

        self.userentry = Entry(self, borderwidth=5, width=25)
        self.userentry.grid(row=2, column=0, padx=(125,0), pady=5)

        self.emailentry = Entry(self, borderwidth=5, width=25)
        self.emailentry.grid(row=2, column=0, padx=(500,0), pady=5)

        passwordlabel = Label(self, text="Enter suitable password")
        passwordlabel.grid(row=3, column=0, padx=(350,20), pady=10)
        passwordlabel.configure(font=label_font )

        self.password = Entry(self, show="*", borderwidth=5, width=50)
        self.password.grid(row=4, column=0, padx=(310,0), pady=5)

        passwordconfirmlabel = Label(self, text="Re-enter password to confirm")
        passwordconfirmlabel.grid(row=5, column=0, padx=(350,20), pady=10)
        passwordconfirmlabel.configure(font=label_font )

        self.passwordconfirm = Entry(self, show="*", borderwidth=5, width=50)
        self.passwordconfirm.grid(row=6, column=0, padx=(310,0), pady=5)

        buttonsubmit = Button(self, text="Create Account and Login", width=30, background="#0063fb", foreground="#fff", command=self.create_account, cursor="hand2")
        buttonsubmit.grid(row=7, column=0, padx=(310,0), pady=5)
        buttonsubmit.configure(font=button_font)

        buttoncancel = Button(self, text="Cancel and go back", width=30, background="#000000", foreground="#fff", command= lambda: self.controller.reload_frame(MainPage), cursor="hand2")
        buttoncancel .grid(row=8, column=0, padx=(310,0), pady=(5, 25))
        buttoncancel .configure(font=button_font)

    def create_account(self):
        mydb = Pages.database
        mycol = mydb["login"]

        entry_list = []
        self.entrycheck = None

        username = self.userentry.get()
        email = self.emailentry.get()
        password = self.password.get()
        passwordconfirm = self.passwordconfirm.get()

        entry_list.extend((username, email, password, passwordconfirm))

        for any in entry_list:
            if len(str(any)) == 0:
                self.entrycheck = False
                break
            else:
                self.entrycheck = True

        if self.entrycheck:
            #Make sure that the two fields for passwords match each other
            if str(password) == str(passwordconfirm):
                #Check user and email is unique, cannot have duplicates
                usercheck = mycol.find_one( { "user.username": username })
                checkemail = mycol.find_one( { "user.email": email })
                if usercheck == None and checkemail == None:
                    #If neither exist in the database, then attempt to insert the account into the login collection.
                    #Otherwise the values are not appropriate for the database. Show successful message, and redirect to loginpage to login.
                    try:
                        create_account = mycol.insert_one( {"user" : { "username" : str(username), "email" : str(email) }, "password" : str(password) } )
                        messagebox.showinfo("Finnplus Sign Up Form", "You have been signed up!")
                        self.controller.current_frame("LoginPage")
                    except:
                        messagebox.showerror("Error", "Values given are not valid.")
                else:
                    messagebox.showerror("Error", "User and/or Email already used.")
            else:
                messagebox.showerror("Error", "Password's do not match.")
        else:           
            messagebox.showerror("Error", "Missing values")

if __name__ == "__main__":
    NoSQL_Project = Database_Project()
    NoSQL_Project.title("Finnplus")
    NoSQL_Project.mainloop()