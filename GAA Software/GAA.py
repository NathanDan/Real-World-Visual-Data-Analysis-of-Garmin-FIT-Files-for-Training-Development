#REAL-WORLD VISUAL DATA ANALYSIS OF GARMIN FIT FILES 
#NATHAN JONES
#JUN-SEPT 2023
#MSc THESIS

from datetime import datetime, timedelta                         #IMPORTING THE DATETIME MODULE SO THAT THE CURRENT DATE AND TIME CAN BE HARNESED WITHIN THE PROGRAM 
from typing import Dict, Union, Optional,Tuple                   #ALLOWS FOR CERTAIN TYPES OF DATA TYPES TO BE HARNESSED WITHIN TEH PROGRAM
from tkinter import ttk                                          #IMPORTING THE TKK MODULE THAT ALLOWS FOR TABBED WIDGETS
from tkinter import messagebox, Label, Button, FALSE, Tk, Entry  #ALLOWING FOR TKINTER TO BE ACCESSED/UTILISED FOR THE PROGRAM TO USE ALL OF ITS FUNCTIONS AND GIVING THE PROGRAM A GUI
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  #ALLOWING FOR THE MATPLOTLIB GRAPHS TO BE INSERTED INTO THE TKINTER GUI'S
from PIL import Image, ImageTk                                   #ALLOWS FOR THE IMPORTS OF IMAGES INTO THE PROGGRAM TO MAKE IT VISUALLY LOOK MORE PROFESSIONAL
from scipy.stats import linregress                               #ALLOWS FOR THE REGRESSION MODELS WITHIN THE DATA PLOTS TO BE CREATED  

import tkinter as tk                                             #IMPORTING THE TKINTER MODULE TO BE USED IN THE PROGRAM
import sys                                                       #ALLOWS ACCESS TO THE SYSTEM FROM WITHIN PYTHON
import os.path                                                   #ALLOWS THE PROGRAM TO OPEN OTHER SPECIFIC APPLICATIONS, IN THIS CASE THE GC PROGRAMS
import os                                                        #ALLOWS FOR CONTROL OF THE MACHINE AND IS OS INCLUDING THE LIKES OF SAVING, OPENING/CLOSING FILES, ETC.
import matplotlib.pyplot as plt                                  #IMPORTING MATPLOTLIB SO THAT GRAPHS CAN BE CREATED AND PRODUCED IN THE PROGRAM
import matplotlib.dates as mdates                                #IMPORTING MATPLOTLIB SO THAT SPECIFIC DATES CAN BE USED WITHIN THE GRAPHS
import matplotlib.gridspec as gridspec                           #IMPORTING MATPLOTLIB SO THAT 
import matplotlib.colors as mcolors                              #IMPORTING MATPLOTLIB SO THAT
import pandas as pd                                              #ALLOWS FOR CERTIAN MATHMATICAL FUNCTIONS AND READING OF CSV DATA TO TAKE PLACE
import fitdecode                                                 #ALLOWING FOR THE PANDSAS DATA FRAMES TO BE UTILISED THROUGHOUT THE PROGRAM
import numpy as np                                               #ALLOWING FOR A MODULE TO BE UTILISED THAT ALLOWS FOR THE DECODING OF FIT FILES

############################################################################################################################################################################################################################################
#                                                                                                                                                                                                                                          #  
#   THE FOLLOWING FUNCTIONS: get_fit_lap_data, get_fit_point_data, AND get_dataframes ARE CODE SNIPPETS FROM THE FOLLOWING REPOSITORY: https://github.com/bunburya/fitness_tracker_data_parsing/blob/main/parse_fit.py (Bunburya ,2021)    #             
#                                                   WITH ADJUSTMENTS FOR THE REQUIRMENTS NEEDED FOR THE SOFTWARE SOLUTION TO BE DEEMED SUCCESSFUL                                                                                          #
#                                                                                                                                                                                                                                          # 
############################################################################################################################################################################################################################################

# The names of the columns we will use in our points DataFrame. For the data we will be getting
# from the FIT data, we use the same name as the field names to make it easier to parse the data.
POINTS_COLUMN_NAMES = ['latitude', 'longitude', 'lap', 'altitude', 'timestamp', 'heart_rate','power', 'cadence', 'speed', 'grade']

# The names of the columns we will use in our laps DataFrame. 
LAPS_COLUMN_NAMES = ['number', 'start_time', 'total_distance', 'total_elapsed_time',
                     'max_speed', 'max_heart_rate', 'avg_heart_rate', 'avg_power', 'max_power']

def get_fit_lap_data(frame: fitdecode.records.FitDataMessage) -> Dict[str, Union[float, datetime, timedelta, int]]:
    """Extract some data from a FIT frame representing a lap and return
    it as a dict.
    """
    
    data: Dict[str, Union[float, datetime, timedelta, int]] = {}
    
    for field in LAPS_COLUMN_NAMES[1:]:  # Exclude 'number' (lap number) because we don't get that # from the data but rather count it ourselves
        if frame.has_field(field):
            data[field] = frame.get_value(field)
    return data

def get_fit_point_data(frame: fitdecode.records.FitDataMessage) -> Optional[Dict[str, Union[float, int, str, datetime]]]:
    """Extract some data from an FIT frame representing a track point
    and return it as a dict.
    """
    
    data: Dict[str, Union[float, int, str, datetime]] = {}
    
    if not (frame.has_field('position_lat') and frame.has_field('position_long')):
        # Frame does not have any latitude or longitude data. We will ignore these frames in order to keep things
        # simple, as we did when parsing the TCX file.
        return None
    else:
        data['latitude'] = frame.get_value('position_lat') / ((2**32) / 360)
        data['longitude'] = frame.get_value('position_long') / ((2**32) / 360)
    
    for field in POINTS_COLUMN_NAMES[3:]:
        if frame.has_field(field):
            data[field] = frame.get_value(field)
    return data
    

def get_dataframes(fname: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Takes the path to a FIT file (as a string) and returns two Pandas
    DataFrames: one containing data about the laps, and one containing
    data about the individual points.
    """
    points_data = []
    laps_data = []
    lap_no = 1
    with fitdecode.FitReader(fname) as fit_file:
        for frame in fit_file:
            if isinstance(frame, fitdecode.records.FitDataMessage):
                if frame.name == 'record':
                    single_point_data = get_fit_point_data(frame)
                    if single_point_data is not None:
                        single_point_data['lap'] = lap_no
                        points_data.append(single_point_data)
                elif frame.name == 'lap':
                    single_lap_data = get_fit_lap_data(frame)
                    single_lap_data['number'] = lap_no
                    laps_data.append(single_lap_data)
                    lap_no += 1
    
    # Create DataFrames from the data we have collected. If any information is missing from a particular lap or track
    # point, it will show up as a null value or "NaN" in the DataFrame.
    
    laps_df = pd.DataFrame(laps_data, columns=LAPS_COLUMN_NAMES)
    laps_df.set_index('number', inplace=True)
    points_df = pd.DataFrame(points_data, columns=POINTS_COLUMN_NAMES)
    
    return laps_df, points_df

############################################################################################################################################################################################################################################
############################################################################################################################################################################################################################################

def MainMenu():
    
    MENU = Tk()                                                          #CREATING THE WINDOW THAT WILL BE DISPLAYED TO THE USER AND HOUSES ALL OF THE DIFFERENT TABS
    MENU.title("Activity Analyser")                                      #GIVING THE WINDOW A TITLE
    MENU.resizable(width=FALSE, height=FALSE)                            #THE WINDOW WILL NOT ENTER FULLSCREEN MODE
    MENU.geometry("1690x800")                                            #CONFIGURING THE FIXED SIZE OF THE WINDOW WHICH WILL ALWAYS BE THIS SIZE
    tabControl = ttk.Notebook(MENU)                                      #TELLING THE PROGRAM THAT WILL WILL BE A TABBED WIDGET

    style = ttk.Style()                                                  #CREATING A TTK STYLE THAT WILL CHANGE THE COLOUR OF THE WIDGET
    style.configure("W.TFrame", foreground="white", background="white")  #SETTING THE BACKGROUND COLOUR TO BE WHITE, SO THAT THE WIDGET LOOKS SMARTER AND MORE PRESENTABLE
    
    HOMEPAGETAB = ttk.Frame(style="W.TFrame")                            #CREATING THE HOME TAB ALONG WITH ITS BACKGROUND COLOUR

    for line in open("temp.txt","r").readlines():                        #READING EACH LINE WITHIN THE 'temp' FILE AND ASSIGNING THE DATA TO VARIABLES BELOW
        data = line.split()                                              #SPLITTING THE TEXT UP INSIDE THE FILE SO THEY CAN BE ACCESSED AND ASSIGNED
        name = data[0]                                                   #TAKING THE 1ST ELEMENT OF THE FILE AND APPENDNING IT TO THE VARIABLE 'name' AS THIS IS THE USER'S NAME
        email = data[1]                                                  #TAKING THE 2ND ELEMENT OF THE FILE AND APPENDNING IT TO THE VARIABLE 'email' AS THIS IS THE USER'S EMAIL

    s1 = Label(HOMEPAGETAB, text=" ", bg="white")                                                                                                                 #CREATING AN EMPTY LABEL THAT WILL ACT AS A ONE LINE SPACE
    s1.pack()                                                                                                                                                     #DISPLAYING THE SPCAE LABEL                                                                                                
    l1 = Label(HOMEPAGETAB, text="Garmin Activity Analyser - Homepage", font='Helvetica 12 bold', bg="white")                                                     #CREATING A MAIN HEADING FOR THE TAB THAT WILL BE AT THE TOP
    l1.pack()                                                                                                                                                     #DISPLAYING THE LABEL
    s3 = Label(HOMEPAGETAB, text=" ",bg="white")                                                                                                                  #CREATING AN EMPTY LABEL THAT WILL ACT AS A ONE LINE SPACE 
    s3.pack()                                                                                                                                                     #DISPLAYING THE SPCAE LABEL
    l2 = Label(HOMEPAGETAB, text="Welcome To The Homepage!", font='Helvetica 10 bold', bg="white")                                                                #CREATING A SUB HEADING FOR THE DESCRIPTION 
    l2.pack()                                                                                                                                                     #DISPLAYING THE LABEL
    l3 = Label(HOMEPAGETAB, text=
    """ """,
    font='Helvetica 10 ', bg="white")                                                                                                                             #CREATING A DESCRIPTION OF THE PROGRAM FOR THE USER TO SEE
    l3.pack()                                                                                                                                                     #DISPLAYING THE LABEL
    WelcomeMsg = Label(HOMEPAGETAB, text="Welcome " +str(name)+", Please select the tab above for what area of your account you would like to see.",              #CREATING THE LABEL THAT ACTS AS A PERSONALISED WELCOME MESSAGE
                       font='Helvetica 10', bg="white") 
    WelcomeMsg.pack()                                                                                                                                             
    l4 = Label(HOMEPAGETAB, text=
    """ """,
    font='Helvetica 10 ', bg="white")                                                                                                                             #CREATING A DESCRIPTION OF THE DATA USED FOR THE USER TO SEE 
    l4.pack()                                                                                                                                                     #DISPLAYING THE LABEL
    
    l5 = Label(HOMEPAGETAB, text="Make sure to keep upto date with the latest updates and features with the website down below!",font='Helvetica 10', bg="white") #CREATING A SUB HEADING FOR THE DESCRIPTION  
    l5.pack()                                                                                                                                                     #DISPLAYING THE LABEL
    s3 = Label(HOMEPAGETAB, text=" ", bg="white")                                                                                                                 #CREATING AN EMPTY LABEL THAT WILL ACT AS A ONE LINE SPACE 
    s3.pack()                                                                                                                                                     #DISPLAYING THE SPCAE LABEL
    l6 = Label(HOMEPAGETAB, text="The Development Team",font='Helvetica 10 bold',bg="white")                                                                      #CREATING A SUB HEADING FOR THE DESCRIPTION  
    l6.pack()                                                                                                                                                     #DISPLAYING THE LABEL
    l7 = Label(HOMEPAGETAB, text=
    "Nathan Jones", font='Helvetica 10 ', bg="white")                                                                                                             #CREATING A LABEL THAT LISTS EVERY ONE WHO IS INVOLVED WITH THE PROGRAM 
    l7.pack()                                                                                                                                                     #DISPLAYING THE LABEL THAT LISTS EVERY ONE WHO IS INVOLVED
    s5 = Label(HOMEPAGETAB, text=" ", bg="white")                                                                                                                 #CREATING AN EMPTY LABEL THAT WILL ACT AS A ONE LINE SPACE 
    s5.pack()                                                                                                                                                     #DISPLAYING THE SPCAE LABEL
    l8 = Label(HOMEPAGETAB, text="The Coding Team",font='Helvetica 10 bold',bg="white")                                                                           #CREATING A SUB HEADING FOR THE DESCRIPTION  
    l8.pack()                                                                                                                                                     #DISPLAYING THE LABEL
    l9 = Label(HOMEPAGETAB, text=
    "Nathan Jones", font='Helvetica 10 ', bg="white")                                                                                                             #CREATING A LABEL THAT LISTS EVERY ONE WHO CODED WITH THE PROGRAM 
    l9.pack()                                                                                                                                                     #DISPLAYING THE LABEL THAT LISTS EVERY ONE WHO IS INVOLVED WITH THE PROGRAM 
    s6 = Label(HOMEPAGETAB, text=" ", bg="white")                                                                                                                 #CREATING AN EMPTY LABEL THAT WILL ACT AS A ONE LINE SPACE 
    s6.pack()                                                                                                                                                     #DISPLAYING THE SPCAE LABEL
    l10 = Label(HOMEPAGETAB, text="Contact Information",font='Helvetica 10 bold', bg="white")                                                                     #CREATING A SUB HEADING FOR THE CONTACT INFORMATION  
    l10.pack()                                                                                                                                                    #DISPLAYING THE LABEL
    l11 = Label(HOMEPAGETAB, text="Website: https://github.com/NathanDan/",font='Helvetica 10', bg="white")                                                       #CREATING A LABEL FOR THE DESCRIPTION OF THE CONTACT INFORMATION 
    l11.pack()                                                                                                                                                    #DISPLAYING THE LABEL

    def LogOut():

        messagebox.showinfo("logged out", "You Are Logged Out!")                     #DISPLAYS A MESSAGE TO THE USER STATING THEY HAVE LOGGED IN
        with open("temp.txt", "w") as file:                                          #WITH THE TEMP FILE OPEN THE FOLLOWING WILL BE WRITTEN TO TEMP FILE - BY WRITING A SPACE IT WILL CLEAR THE TEMP FILE SO ITS BLANK FOR THE NEXT LOG IN
                file.write(" ")                                                      #WRITING AN EMPTY SPACE BETWEEN THE USERS ENTRIES IN THE DATA FILE
                file.close()                                                         #CLOSING THE FILE AFTER ALL OF THE DATA HAS BEEN WRITTEN TO THE TEMP FILE 
        MENU.destroy()                                                               #CLOSING THE MAIN WINDOW AFTER A SUCCESSFUL LOG OUT
    
    LogOutButton = Button(HOMEPAGETAB, text="Log Out",fg="red", command=LogOut)      #CREATING THE LOG OUT BUTTON THAT IS ON THE WELCOME PAGE SO THAT THE USER CAN LOG OUT WHEN THEY ARE DONE
    LogOutButton.place(x=1615, y=720)                                                #DISPLAYING THE BUTTON
    
    l12 = Label(HOMEPAGETAB, text="Version 2.6",font='Helvetica 9 bold', bg="white") #CREATING A LABEL THAT SHOWS WHAT VERSION THE USER IS ON  
    l12.place(x=1615, y=750)                                                         #DISPLAYING THE LABEL

############################################################################################################################################################################################################################################
        
    def get_most_recent_file(Folder):
        if not os.path.exists(Folder):                                        #CHECKING IF THE PROVIDED FOLDER PATH EXISTS
            raise FileNotFoundError(f"The folder '{Folder}' does not exist.") #IF THE FOLDER DOES NOT EXIST THE FOLLOWING MESSAGE WILL BE DISPLAYED

        files = [os.path.join(Folder, file) for file in os.listdir(Folder)    #GETTING A LIST OF ALL THE FILES IN THE FOLDER 
                 if os.path.isfile(os.path.join(Folder, file))]               

        if not files:                                                         #IF THERE ARE NO FILES IN THE FOLDER
            return None                                                       #RETURN NONE AS THERE IS NO FILES 

        most_recent_file = max(files, key=os.path.getmtime)                   #GETTING THE MOST RECENT FILE FROM THE FOLDER BASED ON IT MODIFICATION TIME
        return os.path.basename(most_recent_file)                             #EXTRACTING THE FILENAME FROM THE FULL FILEPATH AND RETURNING IT

    global Folder                                                                                          #CREATING A GLOBAL VARIABLE THAT WILL STORE THE FOLDER OF THE USERS DATA
    Folder = 'C:/Users/natda/OneDrive/University/MSc Computer Science/Thesis/GAA/GAA Software/Activities'+'/'+str(name) #DEFING THE USERS FOLDER USING A PREDEFINED PATHWAY AND TAKING THEIR USERNAME FROM THEIR LOGIN TO NAVIGATE TO THEIR SPECIFIC FOLDER
    MRFile = get_most_recent_file(Folder)                                                                  #ACCESING THE MOST RECENT FILE WITHIN THE USERS FOLDER AS THE DEFAULT FILE
    
    global Activity                                              #CREATING A GLOBAL VARIABLE THAT WILL STORE THE USERS MOST RECENT FILE 
    Activity = str(Folder)+"/"+str(MRFile)                       #DEFING THE PATHWAY TO THE FILE
    laps_df, points_df = get_dataframes(Activity)                #PASING THE DATA FROM THE FILE INTO THE DECODER WITH SPECIFIC VALUES TO RETURN THE DESIRED DATA

    def SelectActivity():        
        selected_filename = dropdownAct.get()                    #GATHERING THE FILE SELECTED FROM THE DROPDOWN BOX

        global Folder                                            #ACCESSING THE GLOBAL 'Folder' VARIABLE
        global Activity                                          #ACCESSING THE GLOBAL 'Activity' VARIABLE

        Activity = os.path.join(folder_path, selected_filename)  #UPDATING THE ACTIVITY FILE WITH THE ONE SELECTED BY THE USER
        print("Selected File:", Activity)                        #THIS ACTS A DEBUG TO AKNOWLEDGE THE SELECTION

        laps_df, points_df = get_dataframes(Activity)            #CREATING THE NEW DATA POINTS FOR THE NEWLY SELECTED FILE
        print('LAPS:')                                           #PRINTING THE NEW DATA LAPS AND POINTS AS A DEBUG IN THE CONSOLE
        print(laps_df)                                           #PRINTING THE NEW DATA LAPS AND POINTS AS A DEBUG IN THE CONSOLE
        print('\nPOINTS:')                                       #PRINTING THE NEW DATA LAPS AND POINTS AS A DEBUG IN THE CONSOLE
        print(points_df)                                         #PRINTING THE NEW DATA LAPS AND POINTS AS A DEBUG IN THE CONSOLE

    def get_filenames_in_folder(folder_path):                       
        filenames = []                                           #CREATING AN ARRAY FOR THE FILENAMES TO BE STORED IN
        for filename in os.listdir(folder_path):
            if os.path.isfile(os.path.join(folder_path,
                                           filename)):           #IF THERE ARE ANY FILES WITHIN THE PATHWAY THE FOLLOWING TAKES PLACE
                filenames.append(filename)                       #APPENDING THE FILENAMES TO THE ARRAY
        return filenames                                         #RETURNING THE FILENAMES BACK

    def on_dropdown_select(event):
        selected_filename = dropdown_var.get()                   #GATHERING THE FILE SELECTED FROM THE DROPDOWN BOX VARIABLE 
        print("Selected File:", selected_filename)               #THIS ACTS A DEBUG TO AKNOWLEDGE THE SELECTION

###########################################################################################################################################################################################################################################
    
    def mps_to_mph(mps):
        mph = mps / 0.44704 #CALCULATING THE METERS PER SECOND INTO MILES PER HOUR(MPH)
        return mph          #RETURING THE MPH VALUE

    points_df['speed'] = points_df['speed'].apply(mps_to_mph) #APPLYING THE METERS PER SECOND TO MILES PER HOUR CALCULATION TO THE DATA
    
    heart_rate = points_df['heart_rate'] #DEFINING THE HEART RATE VARIABLE
    cadence = points_df['cadence']       #DEFINING THE CADENCE VARIABLE
    speed = points_df['speed']           #DEFINING THE SPEED VARIABLE
    altitude = points_df['altitude']     #DEFINING THE ALTITUDE VARIABLE
    power = points_df['power']           #DEFINING THE POWER VARIABLE

############################################################################################################################################################################################################################################
#                            COMBINED ACTIVITY GRAPHS                      #                               COMBINED ACTIVITY GRAPHS                            #                             COMBINED ACTIVITY GRAPHS                      #
############################################################################################################################################################################################################################################

    ActivityGraphsCombined = ttk.Frame(style="W.TFrame")                   #CREATING THE 'ActivityGraphsCombined' FRAME THAT WILL HOUSE THE COMBINED GRAPHS FOR THE USER TO SEE

    controls_frameAGC = ttk.Frame(ActivityGraphsCombined,style="W.TFrame") #CREATING A 'controls_frameAGC' THAT WILL HOUSE THE TITLE AND INFOMATION OF THE PAGE - THIS MEANS WHEN THE GRAPHS ARE UPDATED THESE STAY VISIBLE
    controls_frameAGC.grid(row=4, column=0)                                #DISPLAY THE 'controls_frameAGC' TO THE USER

    s1 = Label(controls_frameAGC, text=" ", bg="white")                                                             #CREATING AN EMPTY LABEL THAT WILL ACT AS A ONE LINE SPACE
    s1.grid(row=0, column=0)                                                                                        #DISPLAYING THE ONE LINE SPACE
    l1 = Label(controls_frameAGC, text="Activity Analyser - Combined Graphs", font='Helvetica 12 bold', bg="white") #CREATING THE MAIN HEADING FOR THE TAB THAT WILL BE DISPLAYED AT THE TOP OF THE FRAME
    l1.grid(row=1)                                                                                                  #DISPLAYING THE TITLE
    l2 = Label(controls_frameAGC, text="Graphs Produced From: " + str(Activity), font='Helvetica 9', bg="white")    #CREATING THE SUBTITLE FOR THE TAB THAT STATES THE FILE BEING USED 
    l2.grid(row=2, column=0)                                                                                        #DISPLAYING THE SUBTITLE

    def ClearActivityGraphsCombiFrame():
        for widget in ActivityGraphsCombined.winfo_children(): #FOR THE WIDGET OBJECT WITHIN THE 'ActivityGraphsCombined' THE FOLLOWING TOOK PLACE
            if widget != controls_frameAGC:                    #IF THE WIDGET OBJECT WAS NOT IN THE 'controls_frameAGC' THE FOLLOWING TOOK PLACE  
                widget.destroy()                               #THE WIDGET OBJECT IS DESTROYED ALLOWING FOR THE NEW GRAPHS TO BE DISPLAYED

    def ActivityScatterCombiGraphsPWR():
        ClearActivityGraphsCombiFrame()         #CALLING THE 'ClearActivityGraphsCombiFrame' FUNCTION TO CLEAR ANY PREVIOUS SUBPLOTS
        avg_power = points_df['power'].mean()   #CREATING A 'avg_power' VARIABLE THAT WILL STORE THE AVERAGE OF THE DATA THAT WILL UTILISED AS AN OVERLAY
        rounded_avg_power = round(avg_power)    #CREATING A VARIABLE THAT ROUNDS THE AVERAGE VARIABLE TO A WHOLE NUMBER

        #CREATING A FIGURE THAT WILL HOUSE THE GRID OF SUBPLOTS (2 ROWS, 2 COLUMNS)
        figSC = plt.figure(figsize=(14, 10))

        #CREATING A GRID OF SUBPLOTS FOR THE GRAPHS TO BE DISPLAYED
        ax1 = figSC.add_subplot(3, 2, 1)        #CREATING THE SUBPLOT FOR THE TOP LEFT GRAPH
        ax2 = figSC.add_subplot(3, 2, 2)        #CREATING THE SUBPLOT FOR THE TOP RIGHT GRAPH
        ax4 = figSC.add_subplot(3, 2, 3)        #CREATING THE SUBPLOT FOR THE BOTTOM LEFT GRAPH
        ax6 = figSC.add_subplot(3, 2, 4)        #CREATING THE SUBPLOT FOR THE BOTTOM RIGHT GRAPH
        ax8 = figSC.add_subplot(4, 1, 4)        #CREATING THE SUBPLOT THAT WILL GO ALONG THE BOTTOM

        #GRAPH PLOT 1 - POWER
        ax1.scatter(points_df['timestamp'], points_df['power'], color='orange', s=0.5)            #CREATING THE HEARTRATE PLOT THAT WILL BE COLOURED RED AS A VISUAL REPRESENTATION
        ax1.set_title('Power (Watts)')                                                            #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED
        ax1.set_xticks([])                                                                        #SETTING THE X-AXIS TO NOT HAVE A LABEL TO CREATE A CLEAN VISUAL
        ax1.axhline(avg_power, color='black', linestyle='--')                                     #ADDING AN AVERAGE LINE TO THE PLOT TO REPRESENT THE AVERAGE VALUE OF THE DATA
        ax1.text(points_df['timestamp'].iloc[-1] + 0.06 * (points_df['timestamp'].iloc[-1]        #CALCULATING AND DISPLAYING THE AVERAGE FOR THE DATA FOR THE USER TO SEE ALONGSIDE THE GRAPH
                                                           - points_df['timestamp'].iloc[0]),
                 avg_power, f'Avg: {rounded_avg_power}', ha='left', va='center')
        ax1.set_xticks([])                                                                        #SETTING THE X-AXIS TO NOT HAVE A LABEL TO CREATE A CLEAN VISUAL

        #GRAPH PLOT 2 - HEARTRATE  
        ax2.scatter(points_df['timestamp'], points_df['heart_rate'], color='red', s=0.5)          #CREATING THE HEARTRATE PLOT THAT WILL BE COLOURED RED AS A VISUAL REPRESENTATION
        ax2.set_title('Heart Rate (BPM)')                                                         #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED
        ax2.set_xticks([])                                                                        #SETTING THE X-AXIS TO NOT HAVE A LABEL TO CREATE A CLEAN VISUAL

        #GRAPH PLOT 2 - POWER OVERLAY
        ax3 = ax2.twinx()                                                                         #CREATING A SECOND Y-AXIS (RIGHT Y-AXIS) SHARING THE SAME AXIS
        ax3.scatter(points_df['timestamp'], points_df['power'], color='orange', s=0.3)            #PLOTTING THE DATA ONTO THE SECOND Y-AXIS (RIGHT Y-AXIS)
        ax3.set_ylabel('Power (Watts)')                                                           #SETTING THE LABEL OF THE RIGHT Y-AXIS TO THE DATA BEING PLOTTED AS THE OVERLAY

        #GRAPH PLOT 3 - SPEED
        ax4.scatter(points_df['timestamp'], points_df['speed'], color='lightblue', s=0.5)         #CREATING THE SPEED PLOT THAT WILL BE COLOURED LIGHT BLUE AS A VISUAL REPRESENTATION
        ax4.set_ylabel('MPH')                                                                     #SETTING THE LABEL OF THE Y-AXIS TO REPRESENT THE DATA BEING PLOTTED
        ax4.set_title('Speed (MPH)')                                                              #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED
        ax4.set_xticks([])                                                                        #SETTING THE X-AXIS TO NOT HAVE A LABEL TO CREATE A CLEAN VISUAL

        #GRAPH PLOT 3 - POWER OVERLAY
        ax5 = ax4.twinx()                                                                         #CREATING A SECOND Y-AXIS (RIGHT Y-AXIS) SHARING THE SAME AXIS
        ax5.scatter(points_df['timestamp'], points_df['power'], color='orange', s=0.3)            #PLOTTING THE DATA ONTO THE SECOND Y-AXIS (RIGHT Y-AXIS)
        ax5.set_ylabel('Power (Watts)')                                                           #SETTING THE LABEL OF THE RIGHT Y-AXIS TO THE DATA BEING PLOTTED AS THE OVERLAY

        ax6.scatter(points_df['timestamp'], points_df['cadence'], color='grey', s=0.5)            #CREATING THE CADENCE PLOT THAT WILL BE COLOURED GREY AS A VISUAL REPRESENTATION 
        ax6.set_title('Cadence (RPM)')                                                            #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED
        ax6.set_xticks([])                                                                        #SETTING THE LABEL OF THE RIGHT Y-AXIS TO THE DATA BEING PLOTTED AS THE OVERLAY

        #GRAPH PLOT 4 - POWER OVERLAY
        ax7 = ax6.twinx()                                                                         #CREATING A SECOND Y-AXIS (RIGHT Y-AXIS) SHARING THE SAME AXIS
        ax7.scatter(points_df['timestamp'], points_df['power'], color='orange', s=0.3)            #PLOTTING THE DATA ONTO THE SECOND Y-AXIS (RIGHT Y-AXIS)
        ax7.set_ylabel('Power (Watts)')                                                           #SETTING THE LABEL OF THE RIGHT Y-AXIS TO THE DATA BEING PLOTTED AS THE OVERLAY

        #GRAPH PLOT TOP - ALTITUDE
        ax8.fill_between(points_df['timestamp'], points_df['altitude'], color='green', alpha=0.4) #CREATING THE ALTITUDE PLOT THAT WILL BE COLOURED GREEN AS A VISUAL REPRESENTATION
        ax8.set_title('Altitude (m)')                                                             #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED
        ax8.set_ylabel('Altitude (m)')                                                            #SETTING THE LABEL OF THE Y-AXIS TO REPRESENT THE DATA BEING PLOTTED
        ax8.set_xticks([])                                                                        #SETTING THE X-AXIS TO NOT HAVE A LABEL TO CREATE A CLEAN VISUAL

        #GRAPH PLOT - POWER OVERLAY
        ax9 = ax8.twinx()                                                                         #CREATING A SECOND Y-AXIS (RIGHT Y-AXIS) SHARING THE SAME AXIS
        ax9.scatter(points_df['timestamp'], points_df['power'], color='orange', s=0.3)            #PLOTTING THE DATA ONTO THE SECOND Y-AXIS (RIGHT Y-AXIS)
        ax9.set_ylabel('Power (Watts)')                                                           #SETTING THE LABEL OF THE RIGHT Y-AXIS TO THE DATA BEING PLOTTED AS THE OVERLAY

        ActivityGraphsSC = FigureCanvasTkAgg(figSC, master=ActivityGraphsCombined)                #CREATING A 'FigureCanvasTkAgg' OBJECT TO DISPLAY THE FIGURE WITH THE SUBPLOTS WITHIN THE 'ActivityGraphsCombined' FRAME
        ActivityGraphsSC.draw()                                                                   #DISPLAYING THE SUBPLOTS TO THE USER
        ActivityGraphsSC.get_tk_widget().configure(width=1600, height=600)                        #SETTING THE SIZE OF THE CANVAS WIDGET
        ActivityGraphsSC.get_tk_widget().grid(row=5, column=0,sticky="w")                         #DISPLAYING THE CANVAS WIDGET WITHIN THE 'ActivityGraphsCombined' FRAME

    ActivityScatterCombiGraphsPWR()

    def ActivityScatterCombiGraphsHR():
        ClearActivityGraphsCombiFrame()                        #CALLING THE 'ClearActivityGraphsCombiFrame' FUNCTION TO CLEAR ANY PREVIOUS SUBPLOTS
        avg_heart_rate = points_df['heart_rate'].mean()        #CREATING A 'avg_heart_rate' VARIABLE THAT WILL STORE THE AVERAGE OF THE DATA THAT WILL UTILISED AS AN OVERLAY
        rounded_avg_heart_rate = round(avg_heart_rate)         #CREATING A VARIABLE THAT ROUNDS THE AVERAGE VARIABLE TO A WHOLE NUMBER

        #CREATING A FIGURE THAT WILL HOUSE THE GRID OF SUBPLOTS (2 ROWS, 2 COLUMNS)
        figSC = plt.figure(figsize=(14, 10))

        #CREATING A GRID OF SUBPLOTS FOR THE GRAPHS TO BE DISPLAYED
        ax1 = figSC.add_subplot(3, 2, 1)        #CREATING THE SUBPLOT FOR THE TOP LEFT GRAPH
        ax3 = figSC.add_subplot(3, 2, 2)        #CREATING THE SUBPLOT FOR THE TOP RIGHT GRAPH
        ax4 = figSC.add_subplot(3, 2, 3)        #CREATING THE SUBPLOT FOR THE BOTTOM LEFT GRAPH
        ax6 = figSC.add_subplot(3, 2, 4)        #CREATING THE SUBPLOT FOR THE BOTTOM RIGHT GRAPH
        ax8 = figSC.add_subplot(4, 1, 4)        #CREATING THE SUBPLOT THAT WILL GO ALONG THE BOTTOM

        #GRAPH PLOT 1 - POWER
        ax1.scatter(points_df['timestamp'], points_df['power'], color='orange', s=0.3)            #PLOTTING THE DATA ONTO THE SECOND Y-AXIS (RIGHT Y-AXIS)
        ax1.set_title('Power (Watts)')                                                            #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED
        ax1.set_ylabel('Watts')                                                                   #SETTING THE LABEL OF THE Y-AXIS TO REPRESENT THE DATA BEING PLOTTED
        ax1.set_xticks([])                                                                        #SETTING THE X-AXIS TO NOT HAVE A LABEL TO CREATE A CLEAN VISUAL

        #GRAPH PLOT 1 - HEARTRATE OVERLAY
        ax2 = ax1.twinx()                                                                         #CREATING A SECOND Y-AXIS (RIGHT Y-AXIS) SHARING THE SAME AXIS
        ax2.scatter(points_df['timestamp'], points_df['heart_rate'], color='red', s=0.3)          #PLOTTING THE DATA ONTO THE SECOND Y-AXIS (RIGHT Y-AXIS)
        ax2.set_ylabel('Heart Rate (BPM)')                                                        #SETTING THE LABEL OF THE RIGHT Y-AXIS TO THE DATA BEING PLOTTED AS THE OVERLAY

        #GRAPH PLOT 2 - HEARTRATE  
        ax3.scatter(points_df['timestamp'], points_df['heart_rate'], color='red', s=0.5)          #CREATING THE HEARTRATE PLOT THAT WILL BE COLOURED RED AS A VISUAL REPRESENTATION
        ax3.set_title('Heart Rate (BPM)')                                                         #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED
        ax3.set_xticks([])                                                                        #SETTING THE X-AXIS TO NOT HAVE A LABEL TO CREATE A CLEAN VISUAL
        ax3.axhline(avg_heart_rate, color='black', linestyle='--')                                #ADDING AN AVERAGE LINE TO THE PLOT TO REPRESENT THE AVERAGE VALUE OF THE DATA
        ax3.text(points_df['timestamp'].iloc[-1] + 0.06 * (points_df['timestamp'].iloc[-1]        #CALCULATING AND DISPLAYING THE AVERAGE FOR THE DATA FOR THE USER TO SEE ALONGSIDE THE GRAPH
                                                           - points_df['timestamp'].iloc[0]),
                 avg_heart_rate, f'Avg: {rounded_avg_heart_rate}', ha='left', va='center')
        ax3.set_xticks([])                                                                        #SETTING THE X-AXIS TO NOT HAVE A LABEL TO CREATE A CLEAN VISUAL 

        #GRAPH PLOT 3 - SPEED
        ax4.scatter(points_df['timestamp'], points_df['speed'], color='lightblue', s=0.5)         #CREATING THE SPEED PLOT THAT WILL BE COLOURED LIGHT BLUE AS A VISUAL REPRESENTATION
        ax4.set_ylabel('MPH')                                                                     #SETTING THE LABEL OF THE Y-AXIS TO REPRESENT THE DATA BEING PLOTTED
        ax4.set_title('Speed (MPH)')                                                              #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED
        ax4.set_xticks([])                                                                        #SETTING THE X-AXIS TO NOT HAVE A LABEL TO CREATE A CLEAN VISUAL

        #GRAPH PLOT 3 - HEARTRATE OVERLAY
        ax5 = ax4.twinx()                                                                         #CREATING A SECOND Y-AXIS (RIGHT Y-AXIS) SHARING THE SAME AXIS
        ax5.scatter(points_df['timestamp'], points_df['heart_rate'], color='red', s=0.3)          #PLOTTING THE DATA ONTO THE SECOND Y-AXIS (RIGHT Y-AXIS)
        ax5.set_ylabel('Heart Rate (BPM)')                                                        #SETTING THE LABEL OF THE RIGHT Y-AXIS TO THE DATA BEING PLOTTED AS THE OVERLAY

        ax6.scatter(points_df['timestamp'], points_df['cadence'], color='grey', s=0.5)            #CREATING THE CADENCE PLOT THAT WILL BE COLOURED GREY AS A VISUAL REPRESENTATION 
        ax6.set_title('Cadence (RPM)')                                                            #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED
        ax6.set_xticks([])                                                                        #SETTING THE LABEL OF THE RIGHT Y-AXIS TO THE DATA BEING PLOTTED AS THE OVERLAY

        #GRAPH PLOT 4 - HEARTRATE OVERLAY
        ax7 = ax6.twinx()                                                                         #CREATING A SECOND Y-AXIS (RIGHT Y-AXIS) SHARING THE SAME AXIS
        ax7.scatter(points_df['timestamp'], points_df['heart_rate'], color='red', s=0.3)          #PLOTTING THE DATA ONTO THE SECOND Y-AXIS (RIGHT Y-AXIS)
        ax7.set_ylabel('Heart Rate (BPM)')                                                        #SETTING THE LABEL OF THE RIGHT Y-AXIS TO THE DATA BEING PLOTTED AS THE OVERLAY

        #GRAPH PLOT - ALTITUDE
        ax8.fill_between(points_df['timestamp'], points_df['altitude'], color='green', alpha=0.4) #CREATING THE ALTITUDE PLOT THAT WILL BE COLOURED GREEN AS A VISUAL REPRESENTATION
        ax8.set_title('Altitude (m)')                                                             #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED
        ax8.set_ylabel('Altitude (m)')                                                            #SETTING THE LABEL OF THE Y-AXIS TO REPRESENT THE DATA BEING PLOTTED
        ax8.set_xticks([])                                                                        #SETTING THE X-AXIS TO NOT HAVE A LABEL TO CREATE A CLEAN VISUAL

        #GRAPH PLOT - HEARTRATE OVERLAY
        ax9 = ax8.twinx()                                                                         #CREATING A SECOND Y-AXIS (RIGHT Y-AXIS) SHARING THE SAME AXIS
        ax9.scatter(points_df['timestamp'], points_df['heart_rate'], color='red', s=0.3)          #PLOTTING THE DATA ONTO THE SECOND Y-AXIS (RIGHT Y-AXIS)
        ax9.set_ylabel('Heart Rate (BPM)')                                                        #SETTING THE LABEL OF THE RIGHT Y-AXIS TO THE DATA BEING PLOTTED AS THE OVERLAY

        ActivityGraphsSC = FigureCanvasTkAgg(figSC, master=ActivityGraphsCombined)                #CREATING A 'FigureCanvasTkAgg' OBJECT TO DISPLAY THE FIGURE WITH THE SUBPLOTS WITHIN THE 'ActivityGraphsCombined' FRAME
        ActivityGraphsSC.draw()                                                                   #DISPLAYING THE SUBPLOTS TO THE USER
        ActivityGraphsSC.get_tk_widget().configure(width=1600, height=600)                        #SETTING THE SIZE OF THE CANVAS WIDGET
        ActivityGraphsSC.get_tk_widget().grid(row=5, column=0,sticky="w")                         #DISPLAYING THE CANVAS WIDGET WITHIN THE 'ActivityGraphsCombined' FRAME

    ActivityScatterCombiGraphsHR()

    def ActivityScatterCombiGraphsSPD():
        ClearActivityGraphsCombiFrame()         #CALLING THE 'ClearActivityGraphsCombiFrame' FUNCTION TO CLEAR ANY PREVIOUS SUBPLOTS 
        avg_speed = points_df['speed'].mean()   #CREATING A 'avg_speed' VARIABLE THAT WILL STORE THE AVERAGE OF THE DATA THAT WILL UTILISED AS AN OVERLAY
        rounded_avg_speed = round(avg_speed)    #CREATING A VARIABLE THAT ROUNDS THE AVERAGE VARIABLE TO A WHOLE NUMBER

        #CREATING A FIGURE THAT WILL HOUSE THE GRID OF SUBPLOTS (3 ROWS, 2 COLUMNS)
        figSC = plt.figure(figsize=(14, 10))

        #CREATING A GRID OF SUBPLOTS FOR THE GRAPHS TO BE DISPLAYED
        ax1 = figSC.add_subplot(3, 2, 1)        #CREATING THE SUBPLOT FOR THE TOP LEFT GRAPH
        ax3 = figSC.add_subplot(3, 2, 2)        #CREATING THE SUBPLOT FOR THE TOP RIGHT GRAPH
        ax5 = figSC.add_subplot(3, 2, 3)        #CREATING THE SUBPLOT FOR THE BOTTOM LEFT GRAPH
        ax6 = figSC.add_subplot(3, 2, 4)        #CREATING THE SUBPLOT FOR THE BOTTOM RIGHT GRAPH
        ax8 = figSC.add_subplot(4, 1, 4)        #CREATING THE SUBPLOT THAT WILL GO ALONG THE BOTTOM 

        #GRAPH PLOT 1 - POWER     
        ax1.scatter(points_df['timestamp'], points_df['power'], color='orange', s=0.3)            #CREATING THE POWER PLOT THAT WILL BE ORANGE IN COLOUR AS A VISUAL REPRESENTATION
        ax1.set_title('Power (Watts)')                                                            #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED
        ax1.set_ylabel('Watts')                                                                   #SETTING THE Y-AXIS TO HAVE A LABEL TO CREATE A CLEAN VISUAL
        ax1.set_xticks([])                                                                        #SETTING THE X-AXIS TO NOT HAVE A LABEL TO CREATE A CLEAN VISUAL

        #GRAPH PLOT 1 - SPEED OVERLAY
        ax2 = ax1.twinx()                                                                         #CREATING A SECOND Y-AXIS (RIGHT Y-AXIS) SHARING THE SAME AXIS
        ax2.scatter(points_df['timestamp'], points_df['speed'], color='lightblue', s=0.5)         #PLOTTING THE DATA ONTO THE SECOND Y-AXIS (RIGHT Y-AXIS) 
        ax2.set_ylabel('Speed (mph)')                                                             #SETTING THE LABEL OF THE RIGHT Y-AXIS TO THE DATA BEING PLOTTED AS THE OVERLAY

        #GRAPH PLOT 2 - HEATRATE
        ax3.scatter(points_df['timestamp'], points_df['heart_rate'], color='red', s=0.5)          #CREATING THE HEARTRATE PLOT THAT WILL BE COLOURED RED AS A VISUAL REPRESENTATION
        ax3.set_ylabel('BPM')                                                                     #SETTING THE LABEL OF THE Y-AXIS TO REPRESENT THE DATA BEING PLOTTED
        ax3.set_title('Heart Rate (BPM)')                                                         #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED

        #GRAPH PLOT 2 - SPEED OVERLAY
        ax4 = ax3.twinx()                                                                         #CREATING A SECOND Y-AXIS (RIGHT Y-AXIS) SHARING THE SAME AXIS
        ax4.scatter(points_df['timestamp'], points_df['speed'], color='lightblue', s=0.5)         #PLOTTING THE DATA ONTO THE SECOND Y-AXIS (RIGHT Y-AXIS) 
        ax4.set_ylabel('Speed (mph)')                                                             #SETTING THE LABEL OF THE RIGHT Y-AXIS TO THE DATA BEING PLOTTED AS THE OVERLAY
        ax4.set_xticks([])                                                                        #SETTING THE X-AXIS TO NOT HAVE A LABEL TO CREATE A CLEAN VISUAL

        #GRAPH PLOT 3 - SPEED
        ax5.scatter(points_df['timestamp'], points_df['speed'], color='lightblue', s=0.5)         #CREATING THE SPEED PLOT THAT WILL BE COLOURED LIGHT BLUE AS A VISUAL REPRESENTATION 
        ax5.set_title('Speed (mph)')                                                              #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED
        ax5.set_xticks([])                                                                        #SETTING THE X-AXIS TO NOT HAVE A LABEL TO CREATE A CLEAN VISUAL
        ax5.axhline(avg_speed, color='black', linestyle='--')                                     #ADDING AN AVERAGE LINE TO THE PLOT TO REPRESENT THE AVERAGE VALUE OF THE DATA
        ax5.text(points_df['timestamp'].iloc[-1] + 0.06 * (points_df['timestamp'].iloc[-1]        #CALCULATING AND DISPLAYING THE AVERAGE FOR THE DATA FOR THE USER TO SEE ALONGSIDE THE GRAPH
                                                           - points_df['timestamp'].iloc[0]),  
                 avg_speed, f'Avg: {rounded_avg_speed}', ha='left', va='center')                                                   

        #GRAPH PLOT 4 - CADENCE
        ax6.scatter(points_df['timestamp'], points_df['cadence'], color='grey', s=0.5)            #CREATING THE CADENCE PLOT THAT WILL BE COLOURED GREY AS A VISUAL REPRESENTATION 
        ax6.set_title('Cadence (RPM)')                                                            #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED
        ax6.set_xticks([])                                                                        #SETTING THE X-AXIS TO NOT HAVE A LABEL TO CREATE A CLEAN VISUAL

        #GRAPH PLOT 4 - SPEED OVERLAY
        ax7 = ax6.twinx()                                                                         #CREATING A SECOND Y-AXIS (RIGHT Y-AXIS) SHARING THE SAME AXIS
        ax7.scatter(points_df['timestamp'], points_df['speed'], color='lightblue', s=0.5)         #PLOTTING THE DATA ONTO THE SECOND Y-AXIS (RIGHT Y-AXIS)
        ax7.set_ylabel('Speed (mph)')                                                             #SETTING THE LABEL OF THE RIGHT Y-AXIS TO THE DATA BEING PLOTTED AS THE OVERLAY

        #GRAPH PLOT - ALTITUDE
        ax8.fill_between(points_df['timestamp'], points_df['altitude'], color='green', alpha=0.4) #CREATING THE ALTITUDE PLOT THAT WILL BE COLOURED GREEN AS A VISUAL REPRESENTATION
        ax8.set_title('Altitude (m)')                                                             #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED
        ax8.set_ylabel('Altitude (m)')                                                            #SETTING THE LABEL OF THE Y-AXIS TO REPRESENT THE DATA BEING PLOTTED
        ax8.set_xticks([])                                                                        #SETTING THE X-AXIS TO NOT HAVE A LABEL TO CREATE A CLEAN VISUAL

        #GRAPH PLOT - SPEED OVERLAY
        ax9 = ax8.twinx()                                                                         #CREATING A SECOND Y-AXIS (RIGHT Y-AXIS) SHARING THE SAME AXIS
        ax9.scatter(points_df['timestamp'], points_df['speed'], color='lightblue', s=0.5)         #PLOTTING THE DATA ONTO THE SECOND Y-AXIS (RIGHT Y-AXIS)
        ax9.set_ylabel('Speed (mph)')                                                             #SETTING THE LABEL OF THE RIGHT Y-AXIS TO THE DATA BEING PLOTTED AS THE OVERLAY


        ActivityGraphsSC = FigureCanvasTkAgg(figSC, master=ActivityGraphsCombined)                #CREATING A 'FigureCanvasTkAgg' OBJECT TO DISPLAY THE FIGURE WITH THE SUBPLOTS WITHIN THE 'ActivityGraphsCombined' FRAME 
        ActivityGraphsSC.draw()                                                                   #DISPLAYING THE SUBPLOTS TO THE USER
        ActivityGraphsSC.get_tk_widget().configure(width=1600, height=600)                        #SETTING THE SIZE OF THE CANVAS WIDGET 
        ActivityGraphsSC.get_tk_widget().grid(row=5, column=0,sticky="w")                         #DISPLAYING THE CANVAS WIDGET WITHIN THE 'ActivityGraphsCombined' FRAME

    ActivityScatterCombiGraphsSPD()

    def ActivityScatterCombiGraphsRPM():
        ClearActivityGraphsCombiFrame()           #CALLING THE 'ClearActivityGraphsCombiFrame' FUNCTION TO CLEAR ANY PREVIOUS SUBPLOTS  
        avg_cadence = points_df['cadence'].mean() #CREATING A 'avg_cadence' VARIABLE THAT WILL STORE THE AVERAGE OF THE DATA THAT WILL UTILISED AS AN OVERLAY
        rounded_avg_cadence = round(avg_cadence)  #CREATING A VARIABLE THAT ROUNDS THE AVERAGE VARIABLE TO A WHOLE NUMBER

        #CREATING A FIGURE THAT WILL HOUSE THE GRID OF SUBPLOTS (2 ROWS, 2 COLUMNS)
        figSC = plt.figure(figsize=(14, 10))

        #CREATING A GRID OF SUBPLOTS FOR THE GRAPHS TO BE DISPLAYED
        ax1 = figSC.add_subplot(3, 2, 1)          #CREATING THE SUBPLOT FOR THE TOP LEFT GRAPH
        ax3 = figSC.add_subplot(3, 2, 2)          #CREATING THE SUBPLOT FOR THE TOP RIGHT GRAPH
        ax5 = figSC.add_subplot(3, 2, 3)          #CREATING THE SUBPLOT FOR THE BOTTOM LEFT GRAPH
        ax7 = figSC.add_subplot(3, 2, 4)          #CREATING THE SUBPLOT FOR THE BOTTOM RIGHT GRAPH
        ax8 = figSC.add_subplot(4, 1, 4)          #CREATING THE SUBPLOT THAT WILL GO ALONG THE BOTTOM
        
        #GRAPH PLOT 1 - POWER
        ax1.scatter(points_df['timestamp'], points_df['power'], color='orange', s=0.3)            #PLOTTING THE DATA ONTO THE SECOND Y-AXIS (RIGHT Y-AXIS)
        ax1.set_title('Power (Watts)')                                                            #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED
        ax1.set_ylabel('Watts')                                                                   #SETTING THE Y-AXIS TO HAVE A LABEL TO CREATE A CLEAN VISUAL
        ax1.set_xticks([])                                                                        #SETTING THE X-AXIS TO NOT HAVE A LABEL TO CREATE A CLEAN VISUAL

        #GRAPH PLOT 1 - CADENCE OVERLAY
        ax2 = ax1.twinx()                                                                         #CREATING A SECOND Y-AXIS (RIGHT Y-AXIS) SHARING THE SAME AXIS 
        ax2.scatter(points_df['timestamp'], points_df['cadence'], color='grey', s=0.5)            #PLOTTING THE DATA ONTO THE SECOND Y-AXIS (RIGHT Y-AXIS)
        ax2.set_ylabel('Cadence (RPM)')                                                           #SETTING THE LABEL OF THE RIGHT Y-AXIS TO THE DATA BEING PLOTTED AS THE OVERLAY
        ax2.set_xticks([])                                                                        #SETTING THE X-AXIS TO NOT HAVE A LABEL TO CREATE A CLEAN VISUAL

        #GRAPH PLOT 2 - HEARTRATE
        ax3.scatter(points_df['timestamp'], points_df['heart_rate'], color='red', s=0.5)          #CREATING THE HEARTRATE PLOT THAT WILL BE COLOURED RED AS A VISUAL REPRESENTATION
        ax3.set_ylabel('BPM')                                                                     #SETTING THE LABEL OF THE Y-AXIS TO REPRESENT THE DATA BEING PLOTTED
        ax3.set_title('Heart Rate (BPM)')                                                         #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED

        #GRAPH PLOT 2 - CADENCE OVERLAY
        ax4 = ax3.twinx()                                                                         #CREATING A SECOND Y-AXIS (RIGHT Y-AXIS) SHARING THE SAME AXIS 
        ax4.scatter(points_df['timestamp'], points_df['cadence'], color='grey', s=0.5)            #PLOTTING THE DATA ONTO THE SECOND Y-AXIS (RIGHT Y-AXIS) 
        ax4.set_ylabel('Cadence (RPM)')                                                           #SETTING THE LABEL OF THE RIGHT Y-AXIS TO THE DATA BEING PLOTTED AS THE OVERLAY
        ax4.set_xticks([])                                                                        #SETTING THE X-AXIS TO NOT HAVE A LABEL TO CREATE A CLEAN VISUAL

        #GRAPH PLOT 3 - SPEED
        ax5.scatter(points_df['timestamp'], points_df['speed'], color='lightblue', s=0.5)         #CREATING THE SPEED PLOT THAT WILL BE COLOURED LIGHT BLUE AS A VISUAL REPRESENTATION
        ax5.set_ylabel('MPH')                                                                     #SETTING THE LABEL OF THE Y-AXIS TO REPRESENT THE DATA BEING PLOTTED
        ax5.set_ylabel('Speed (mph)')                                                             #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED
        ax5.set_xticks([])                                                                        #SETTING THE X-AXIS TO NOT HAVE A LABEL TO CREATE A CLEAN VISUAL

        #GRAPH PLOT 3 - CADENCE OVERLAY
        ax6 = ax5.twinx()                                                                         #CREATING A SECOND Y-AXIS (RIGHT Y-AXIS) SHARING THE SAME AXIS 
        ax6.scatter(points_df['timestamp'], points_df['cadence'], color='grey', s=0.5)            #PLOTTING THE DATA ONTO THE SECOND Y-AXIS (RIGHT Y-AXIS)
        ax6.set_ylabel('Cadence (RPM)')                                                           #SETTING THE LABEL OF THE RIGHT Y-AXIS TO THE DATA BEING PLOTTED AS THE OVERLAY

        #GRAPH PLOT 4 - CADENCE 
        ax7.scatter(points_df['timestamp'], points_df['cadence'], color='grey', s=0.5)            #CREATING THE CADENCE PLOT THAT WILL BE COLOURED GREY AS A VISUAL REPRESENTATION 
        ax7.set_title('Cadence (RPM)')                                                            #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED
        ax7.set_xticks([])                                                                        #SETTING THE X-AXIS TO NOT HAVE A LABEL TO CREATE A CLEAN VISUAL
        ax7.axhline(avg_cadence, color='black', linestyle='--')                                   #ADDING AN AVERAGE LINE TO THE PLOT TO REPRESENT THE AVERAGE VALUE OF THE DATA
        ax7.text(points_df['timestamp'].iloc[-1] + 0.06 * (points_df['timestamp'].iloc[-1]        #CALCULATING AND DISPLAYING THE AVERAGE FOR THE DATA FOR THE USER TO SEE ALONGSIDE THE GRAPH
                                                           - points_df['timestamp'].iloc[0]),
                 avg_cadence, f'Avg: {rounded_avg_cadence}', ha='left', va='center')

        #GRAPH PLOT - ALTITUDE
        ax8.fill_between(points_df['timestamp'], points_df['altitude'], color='green', alpha=0.4) #CREATING THE ALTITUDE PLOT THAT WILL BE COLOURED GREEN AS A VISUAL REPRESENTATION
        ax8.set_title('Altitude (m)')                                                             #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED
        ax8.set_ylabel('Altitude (m)')                                                            #SETTING THE LABEL OF THE Y-AXIS TO REPRESENT THE DATA BEING PLOTTED
        ax8.set_xticks([])                                                                        #SETTING THE X-AXIS TO NOT HAVE A LABEL TO CREATE A CLEAN VISUAL

        #GRAPH PLOT - CADENCE OVERLAY
        ax9 = ax8.twinx()                                                                         #CREATING A SECOND Y-AXIS (RIGHT Y-AXIS) SHARING THE SAME AXIS 
        ax9.scatter(points_df['timestamp'], points_df['cadence'], color='grey', s=0.5)            #PLOTTING THE DATA ONTO THE SECOND Y-AXIS (RIGHT Y-AXIS)
        ax9.set_ylabel('Cadence (RPM)')                                                           #SETTING THE LABEL OF THE RIGHT Y-AXIS TO THE DATA BEING PLOTTED AS THE OVERLAY

        ActivityGraphsSC = FigureCanvasTkAgg(figSC, master=ActivityGraphsCombined)                #CREATING A 'FigureCanvasTkAgg' OBJECT TO DISPLAY THE FIGURE WITH THE SUBPLOTS WITHIN THE 'ActivityGraphsCombined' FRAME
        ActivityGraphsSC.draw()                                                                   #DISPLAYING THE SUBPLOTS TO THE USER
        ActivityGraphsSC.get_tk_widget().configure(width=1600, height=600)                        #SETTING THE SIZE OF THE CANVAS WIDGET 
        ActivityGraphsSC.get_tk_widget().grid(row=5, column=0,sticky="w")                         #DISPLAYING THE CANVAS WIDGET WITHIN THE 'ActivityGraphsCombined' FRAME

    ActivityScatterCombiGraphsRPM()

    def ActivityScatterCombiGraphsCLN():
        ClearActivityGraphsCombiFrame()                  #CALLING THE 'ClearActivityGraphsCombiFrame' FUNCTION TO CLEAR ANY PREVIOUS SUBPLOTS
        avg_power = points_df['power'].mean()            #CREATING A 'avg_heart_rate' VARIABLE THAT WILL STORE THE AVERAGE OF THE DATA THAT WILL UTILISED AS AN OVERLAY
        avg_cadence = points_df['cadence'].mean()        #CREATING A 'avg_cadence' VARIABLE THAT WILL STORE THE AVERAGE OF THE DATA THAT WILL UTILISED AS AN OVERLAY
        avg_speed = points_df['speed'].mean()            #CREATING A 'avg_speed' VARIABLE THAT WILL STORE THE AVERAGE OF THE DATA THAT WILL UTILISED AS AN OVERLAY
        avg_heart_rate = points_df['heart_rate'].mean()  #CREATING A 'avg_heart_rate' VARIABLE THAT WILL STORE THE AVERAGE OF THE DATA THAT WILL UTILISED AS AN OVERLAY

        rounded_avg_power = round(avg_power)             #CREATING A VARIABLE THAT ROUNDS THE AVERAGE VARIABLE TO A WHOLE NUMBER
        rounded_avg_cadence = round(avg_cadence)         #CREATING A VARIABLE THAT ROUNDS THE AVERAGE VARIABLE TO A WHOLE NUMBER
        rounded_avg_speed = round(avg_speed)             #CREATING A VARIABLE THAT ROUNDS THE AVERAGE VARIABLE TO A WHOLE NUMBER
        rounded_avg_heart_rate = round(avg_heart_rate)   #CREATING A VARIABLE THAT ROUNDS THE AVERAGE VARIABLE TO A WHOLE NUMBER      

        #CREATING A FIGURE THAT WILL HOUSE THE GRID OF SUBPLOTS (2 ROWS, 2 COLUMNS)
        figSC = plt.figure(figsize=(14, 10))

        #CREATING A GRID OF SUBPLOTS FOR THE GRAPHS TO BE DISPLAYED
        ax1 = figSC.add_subplot(3, 2, 1) #CREATING THE SUBPLOT FOR THE TOP LEFT GRAPH
        ax2 = figSC.add_subplot(3, 2, 2) #CREATING THE SUBPLOT FOR THE TOP RIGHT GRAPH
        ax3 = figSC.add_subplot(3, 2, 3) #CREATING THE SUBPLOT FOR THE BOTTOM LEFT GRAPH
        ax4 = figSC.add_subplot(3, 2, 4) #CREATING THE SUBPLOT FOR THE BOTTOM RIGHT GRAPH
        ax5 = figSC.add_subplot(4, 1, 4) #CREATING THE SUBPLOT FOR THE BOTTOM GRAPH

        #GRAPH PLOT 1 - POWER
        ax1.scatter(points_df['timestamp'], points_df['power'], color='orange', s=0.5)            #CREATING THE HEARTRATE PLOT THAT WILL BE COLOURED RED AS A VISUAL REPRESENTATION
        ax1.set_title('Power (Watts)')                                                            #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED
        ax1.set_ylabel('Watts')                                                                   #SETTING THE Y-AXIS TO HAVE A LABEL TO CREATE A CLEAN VISUAL
        ax1.set_xticks([])                                                                        #SETTING THE X-AXIS TO NOT HAVE A LABEL TO CREATE A CLEAN VISUAL
        ax1.axhline(avg_power, color='black', linestyle='--')                                     #ADDING AN AVERAGE LINE TO THE PLOT TO REPRESENT THE AVERAGE VALUE OF THE DATA
        ax1.text(points_df['timestamp'].iloc[-1] + 0.06 * (points_df['timestamp'].iloc[-1]        #CALCULATING AND DISPLAYING THE AVERAGE FOR THE DATA FOR THE USER TO SEE ALONGSIDE THE GRAPH
                                                           - points_df['timestamp'].iloc[0]),
                 avg_power, f'Avg: {rounded_avg_power}', ha='left', va='center')
        ax1.set_xticks([])                                                                        

        #GRAPH PLOT 2 - HEARTRATE  
        ax2.scatter(points_df['timestamp'], points_df['heart_rate'], color='red', s=0.5)          #CREATING THE HEARTRATE PLOT THAT WILL BE COLOURED RED AS A VISUAL REPRESENTATION
        ax2.set_title('Heart Rate (BPM)')                                                         #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED
        ax2.set_xticks([])                                                                        #SETTING THE X-AXIS TO NOT HAVE A LABEL TO CREATE A CLEAN VISUAL
        ax2.axhline(avg_heart_rate, color='black', linestyle='--')                                #ADDING AN AVERAGE LINE TO THE PLOT TO REPRESENT THE AVERAGE VALUE OF THE DATA
        ax2.text(points_df['timestamp'].iloc[-1] + 0.06 * (points_df['timestamp'].iloc[-1]        #CALCULATING AND DISPLAYING THE AVERAGE FOR THE DATA FOR THE USER TO SEE ALONGSIDE THE GRAPH
                                                           - points_df['timestamp'].iloc[0]),
                 avg_heart_rate, f'Avg: {rounded_avg_heart_rate}', ha='left', va='center')
        ax3.set_xticks([])                                                                        

        #GRAPH PLOT 3 - SPEED
        ax3.scatter(points_df['timestamp'], points_df['speed'], color='lightblue', s=0.5)         #CREATING THE SPEED PLOT THAT WILL BE COLOURED LIGHT BLUE AS A VISUAL REPRESENTATION 
        ax3.set_title('Speed (MPH)')                                                              #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED
        ax3.set_xticks([])                                                                        #SETTING THE X-AXIS TO NOT HAVE A LABEL TO CREATE A CLEAN VISUAL
        ax3.axhline(avg_speed, color='black', linestyle='--')                                     #ADDING AN AVERAGE LINE TO THE PLOT TO REPRESENT THE AVERAGE VALUE OF THE DATA
        ax3.text(points_df['timestamp'].iloc[-1] + 0.06 * (points_df['timestamp'].iloc[-1]        #CALCULATING AND DISPLAYING THE AVERAGE FOR THE DATA FOR THE USER TO SEE ALONGSIDE THE GRAPH
                                                           - points_df['timestamp'].iloc[0]),  
                 avg_speed, f'Avg: {rounded_avg_speed}', ha='left', va='center')                                                   
                                                                       
        #GRAPH PLOT 4 - CADENCE 
        ax4.scatter(points_df['timestamp'], points_df['cadence'], color='grey', s=0.5)            #CREATING THE CADENCE PLOT THAT WILL BE COLOURED GREY AS A VISUAL REPRESENTATION 
        ax4.set_title('Cadence (RPM)')                                                            #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED
        ax4.set_xticks([])                                                                        #SETTING THE X-AXIS TO NOT HAVE A LABEL TO CREATE A CLEAN VISUAL
        ax4.axhline(avg_cadence, color='black', linestyle='--')                                   #ADDING AN AVERAGE LINE TO THE PLOT TO REPRESENT THE AVERAGE VALUE OF THE DATA
        ax4.text(points_df['timestamp'].iloc[-1] + 0.06 * (points_df['timestamp'].iloc[-1]        #CALCULATING AND DISPLAYING THE AVERAGE FOR THE DATA FOR THE USER TO SEE ALONGSIDE THE GRAPH
                                                           - points_df['timestamp'].iloc[0]),
                 avg_cadence, f'Avg: {rounded_avg_cadence}', ha='left', va='center')

        #GRAPH PLOT TOP - ALTITUDE
        ax5.fill_between(points_df['timestamp'], points_df['altitude'], color='green', alpha=0.4) #CREATING THE ALTITUDE PLOT THAT WILL BE COLOURED GREEN AS A VISUAL REPRESENTATION
        ax5.set_title('Altitude (m)')                                                             #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED
        ax5.set_ylabel('Altitude (m)')                                                            #SETTING THE LABEL OF THE Y-AXIS TO REPRESENT THE DATA BEING PLOTTED
        ax5.set_xticks([])                                                                        #SETTING THE X-AXIS TO NOT HAVE A LABEL TO CREATE A CLEAN VISUAL


        ActivityGraphsSC = FigureCanvasTkAgg(figSC, master=ActivityGraphsCombined)                #CREATING A 'FigureCanvasTkAgg' OBJECT TO DISPLAY THE FIGURE WITH THE SUBPLOTS WITHIN THE 'ActivityGraphsCombined' FRAME
        ActivityGraphsSC.draw()                                                                   #DISPLAYING THE SUBPLOTS TO THE USER
        ActivityGraphsSC.get_tk_widget().configure(width=1600, height=600)                        #SETTING THE SIZE OF THE CANVAS WIDGET
        ActivityGraphsSC.get_tk_widget().grid(row=5, column=0,sticky="w")                         #DISPLAYING THE CANVAS WIDGET WITHIN THE 'ActivityGraphsCombined' FRAME

    ActivityScatterCombiGraphsCLN()

    folder_path = 'C:/Users/natda/OneDrive/University/MSc Computer Science/Thesis/GAA/GAA Software/Activities'+'/'+str(name) #DEFINIG THE USERS PATHWAY FOLDER
    filenames = get_filenames_in_folder(folder_path)                                                            #GATHERING THE FILENAMES FROM THE FOLDER DEFINED ABOVE

    dropdown_var = tk.StringVar()                                                              #CREATINGI A TKINTER STRING VARIABLE TO STORE ALL OF THE FILE NAMES
    dropdownAct = ttk.Combobox(controls_frameAGC, textvariable=dropdown_var, values=filenames) #DISPLAYING THE FILENAMES WITHIN THE DROPDOWN BOX
    dropdownAct.set("Select a File...")                                                        #CREATING A PLACE HOLDER THAT IS DISPLAYED UNTIL THE USER INTERACTS WITH THE DROPDOWN
    dropdownAct.grid(row=3, column=0)                                                          #DISPLAYING THE DROPDOWN BOX TO THE USER 

    dropdownAct.bind("<<ComboboxSelected>>", on_dropdown_select) #BINDING AN EVENT HANDER TO THE DROPDOWN BOX ALSO ACTS AS A DEBUGGER

    dropdown2 = ttk.Combobox(controls_frameAGC, values=["Combined Heart Rate Scatter",  #CREATING A DROPDOWN BOX THAT WILL STORE THE 3 DIFFERENT GRAPH VISUALS
                                                        "Combined Speed Scatter",
                                                        "Combined Cadence Scatter",
                                                        "Combined Power Scatter",
                                                        "Averages"])
    dropdown2.set("Select a Graph Style...")                                            #DISPLAYING A MESSAGE EXPLAINING TO THE USER WHAT THE DROPDOWN BOX DOES
    dropdown2.grid(row=3, column=2)                                                     #DISPLAYING THE DROPDOWN BOX FOR THE USER TO INTERACT WITH

    def SelectActivityCombiGraphStyle():
        selected_style = dropdown2.get()                      #GATHERING THE USER'S SELECTION FROM THE DROPDOWN BOX 
        if selected_style == "Combined Heart Rate Scatter":   #IF THE IF STATEMENT CONDITIONS ARE MET THE FOLLOWING TAKES PLACE:
            ActivityScatterCombiGraphsHR()                    #EXECUTING THE 'ActivityScatterCombiGraphsHR' FUNCTION
        elif selected_style == "Combined Speed Scatter":      #IF THE IF STATEMENT CONDITIONS ARE MET THE FOLLOWING TAKES PLACE:
            ActivityScatterCombiGraphsSPD()                   #EXECUTING THE 'ActivityScatterCombiGraphsSPD' FUNCTION
        elif selected_style == "Combined Cadence Scatter":    #IF THE IF STATEMENT CONDITIONS ARE MET THE FOLLOWING TAKES PLACE: 
            ActivityScatterCombiGraphsRPM()                   #EXECUTING THE 'ActivityScatterCombiGraphsRPM' FUNCTION
        elif selected_style == "Combined Power Scatter":      #IF THE IF STATEMENT CONDITIONS ARE MET THE FOLLOWING TAKES PLACE: 
            ActivityScatterCombiGraphsPWR()                   #EXECUTING THE 'ActivityScatterCombiGraphsPWR' FUNCTION
        elif selected_style == "Averages":                    #IF THE IF STATEMENT CONDITIONS ARE MET THE FOLLOWING TAKES PLACE: 
            ActivityScatterCombiGraphsCLN()                   #EXECUTING THE 'ActivityScatterCombiGraphsCLN' FUNCTION

    button1 = ttk.Button(controls_frameAGC, text="Select")    #CREATING THE BUTTON THAT WILL USER WILL INTERACT WITH
    button1.configure(command=SelectActivity)                 #BINDING THE 'SelectActivity' FUNCTION WITH THE BUTTON
    button1.grid(row=3, column=1)                             #DISPLAYING THE BUTTON TO THE USER 
    button2 = ttk.Button(controls_frameAGC, text="Select")    #CREATING THE BUTTON THAT WILL USER WILL INTERACT WITH
    button2.configure(command=SelectActivityCombiGraphStyle)  #BINDING THE 'SelectActivityCombiGraphStyle' FUNCTION WITH THE BUTTON
    button2.grid(row=3, column=3)                             #DISPLAYING THE BUTTON TO THE USER   

############################################################################################################################################################################################################################################
#       LINEAR REGRESSION GRAPHS        #       LINEAR REGRESSION GRAPHS        #       LINEAR REGRESSION GRAPHS        #       LINEAR REGRESSION GRAPHS     #       LINEAR REGRESSION GRAPHS        #     LINEAR REGRESSION GRAPHS        #
############################################################################################################################################################################################################################################

    LinearRegressionGraphs = ttk.Frame(style="W.TFrame")                   #CREATING THE 'LinearRegressionGraphs' FRAME THAT WILL HOUSE THE COMBINED GRAPHS FOR THE USER TO SEE

    controls_frameLRG = ttk.Frame(LinearRegressionGraphs,style="W.TFrame") #CREATING A 'controls_frameLRG' THAT WILL HOUSE THE TITLE AND INFOMATION OF THE PAGE - THIS MEANS WHEN THE GRAPHS ARE UPDATED THESE STAY VISIBLE
    controls_frameLRG.grid(row=4, column=0)                                #DISPLAY THE 'controls_frameLRG' TO THE USER

    s1 = Label(controls_frameLRG, text=" ", bg="white")                                                                      #CREATING AN EMPTY LABEL THAT WILL ACT AS A ONE LINE SPACE
    s1.grid(row=0, column=0)                                                                                                 #DISPLAYING THE ONE LINE SPACE
    l1 = Label(controls_frameLRG, text="Activity Analyser - Linear Regression Graphs", font='Helvetica 12 bold', bg="white") #CREATING THE MAIN HEADING FOR THE TAB THAT WILL BE DISPLAYED AT THE TOP OF THE FRAME
    l1.grid(row=1, column=0)                                                                                                 #DISPLAYING THE TITLE
    l2 = Label(controls_frameLRG, text="Graphs Produced From: " + str(Activity), font='Helvetica 9', bg="white")             #CREATING THE SUBTITLE FOR THE TAB THAT STATES THE FILE BEING USED 
    l2.grid(row=2, column=0)                                                                                                 #DISPLAYING THE SUBTITLE

    def ClearLinearRegressionFrame():
        for widget in LinearRegressionGraphs.winfo_children(): #FOR THE WIDGET OBJECT WITHIN THE 'LinearRegressionGraphs' THE FOLLOWING TOOK PLACE
            if widget != controls_frameLRG:                    #IF THE WIDGET OBJECT WAS NOT IN THE 'controls_frameLRG' THE FOLLOWING TOOK PLACE  
                widget.destroy()                               #THE WIDGET OBJECT IS DESTROYED ALLOWING FOR THE NEW GRAPHS TO BE DISPLAYED

    def ActivityLinearRegressionGraphsALT():
        ClearLinearRegressionFrame()                           #CALLING THE 'ClearLinearRegressionFrame' FUNCTION TO CLEAR ANY PREVIOUS SUBPLOTS

        #CREATING A FIGURE THAT WILL HOUSE THE GRID OF SUBPLOTS (2 ROWS, 2 COLUMNS)
        figLR = plt.figure(figsize=(14, 8))

        #CREATING A GRID OF SUBPLOTS FOR THE GRAPHS TO BE DISPLAYED
        ax1 = figLR.add_subplot(2, 2, 1)        #CREATING THE SUBPLOT FOR THE TOP LEFT GRAPH
        ax2 = figLR.add_subplot(2, 2, 2)        #CREATING THE SUBPLOT FOR THE TOP RIGHT GRAPH
        ax3 = figLR.add_subplot(2, 2, 3)        #CREATING THE SUBPLOT FOR THE BOTTOM LEFT GRAPH
        ax4 = figLR.add_subplot(2, 2, 4)        #CREATING THE SUBPLOT FOR THE BOTTOM RIGHT GRAPH

        #GRAPH PLOT 1 - POWER AND ALTITUDE
        non_zero_mask1 = (points_df['altitude'] != 0) & (points_df['power'] != 0)               #CREATING A ZERO MASK THAT WILL TAKE OUT AN ZERO VALUES THAT ARE NOT MEAN TO BE IN THE DATA
        x1 = points_df.loc[non_zero_mask1, 'altitude']                                          #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE X AXIS
        y1 = points_df.loc[non_zero_mask1, 'power']                                             #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE Y AXIS
        slope, intercept, r_value, p_value, std_err = linregress(x1, y1)                        #DEFIING THE LINEAR REGRESSION INTERCEPT, SLOPE AND VARIOUS VALUES RELATING TO THE MODEL
        predicted_cadence = slope * x1 + intercept                                              #PREDICITING WHERE THE INTECEPT WILL HAPPEN ALONG WITH PREDICTED FUTURE VALUES BASED UPON THE DATA
        ax1.scatter(x1, y1, label='Data', color='orange', s=0.5)                                #PLOTTING THE PERFORMANCE METRICS DATA ALONG WITH ITS COLOUR PROFILE
        ax1.plot(x1, predicted_cadence, color='black', label='Regression Line')                 #PLOTTING THE LINEAR REGRESSION LINE ON THE PLOT OVER THE PERFORMANCE METRIC
        ax1.set_title('Linear Regression: Power vs. Altitude')                                  #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED
                                                                            
        #GRAPH PLOT 2 - HEART RATE AND ALTITUDE
        non_zero_mask2 = (points_df['altitude'] != 0) & (points_df['heart_rate'] != 0)          #CREATING A ZERO MASK THAT WILL TAKE OUT AN ZERO VALUES THAT ARE NOT MEAN TO BE IN THE DATA
        x2 = points_df.loc[non_zero_mask2, 'altitude']                                          #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE X AXIS
        y2 = points_df.loc[non_zero_mask2, 'heart_rate']                                        #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE Y AXIS
        slope, intercept, r_value, p_value, std_err = linregress(x2, y2)                        #DEFIING THE LINEAR REGRESSION INTERCEPT, SLOPE AND VARIOUS VALUES RELATING TO THE MODEL
        predicted_heart_rate = slope * x2 + intercept                                           #PREDICITING WHERE THE INTECEPT WILL HAPPEN ALONG WITH PREDICTED FUTURE VALUES BASED UPON THE DATA
        ax2.scatter(x2, y2, label='Data', color='red', s=0.5)                                   #PLOTTING THE PERFORMANCE METRICS DATA ALONG WITH ITS COLOUR PROFILE
        ax2.plot(x2, predicted_heart_rate, color='black', label='Regression Line')              #PLOTTING THE LINEAR REGRESSION LINE ON THE PLOT OVER THE PERFORMANCE METRIC
        ax2.set_title('Linear Regression: Heart Rate vs. Altitude')                             #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED

        #GRAPH PLOT 3 - SPEED AND ALTITUDE
        non_zero_mask3 = (points_df['altitude'] != 0) & (points_df['speed'] != 0)               #CREATING A ZERO MASK THAT WILL TAKE OUT AN ZERO VALUES THAT ARE NOT MEAN TO BE IN THE DATA
        x3 = points_df.loc[non_zero_mask3, 'altitude']                                          #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE X AXIS
        y3 = points_df.loc[non_zero_mask3, 'speed']                                             #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE Y AXIS
        slope, intercept, r_value, p_value, std_err = linregress(x3, y3)                        #DEFIING THE LINEAR REGRESSION INTERCEPT, SLOPE AND VARIOUS VALUES RELATING TO THE MODEL
        predicted_speed = slope * x3 + intercept                                                #PREDICITING WHERE THE INTECEPT WILL HAPPEN ALONG WITH PREDICTED FUTURE VALUES BASED UPON THE DATA
        ax3.scatter(x3, y3, label='Data', color='lightblue', s=0.5)                             #PLOTTING THE PERFORMANCE METRICS DATA ALONG WITH ITS COLOUR PROFILE
        ax3.plot(x3, predicted_speed, color='black', label='Regression Line')                   #PLOTTING THE LINEAR REGRESSION LINE ON THE PLOT OVER THE PERFORMANCE METRIC
        ax3.set_title('Linear Regression: Speed vs. Altitude')                                  #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED

        #GRAPH PLOT 4 - ALTITUDE BASE PLOT
        ax4.fill_between(points_df['timestamp'],points_df['altitude'],color='green',alpha=0.4)  #CREATING THE ALTITUDE PLOT THAT WILL BE COLOURED GREEN AS A VISUAL REPRESENTATION
        ax4.set_title('Altitude (m)')                                                           #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED
        ax4.set_ylabel('Altitude (m)')                                                          #SETTING THE LABEL OF THE Y-AXIS TO REPRESENT THE DATA BEING PLOTTED
        ax4.set_xticks([])                                                                      #SETTING THE X-AXIS TO NOT HAVE A LABEL TO CREATE A CLEAN VISUAL

        ActivityGraphsLR = FigureCanvasTkAgg(figLR, master=LinearRegressionGraphs)              #CREATING A 'FigureCanvasTkAgg' OBJECT TO DISPLAY THE FIGURE WITH THE SUBPLOTS WITHIN THE 'ActivityGraphsLR' FRAME
        ActivityGraphsLR.draw()                                                                 #DISPLAYING THE SUBPLOTS TO THE USER
        ActivityGraphsLR.get_tk_widget().configure(width=1600, height=600)                      #SETTING THE SIZE OF THE CANVAS WIDGET
        ActivityGraphsLR.get_tk_widget().grid(row=5, column=0,sticky="w")                       #DISPLAYING THE CANVAS WIDGET WITHIN THE 'ActivityGraphsCombined' FRAME

    ActivityLinearRegressionGraphsALT()

    def ActivityLinearRegressionGraphsHR():
        ClearLinearRegressionFrame()                     #CALLING THE 'ClearActivityGraphsCombiFrame' FUNCTION TO CLEAR ANY PREVIOUS SUBPLOTS
        avg_heart_rate = points_df['heart_rate'].mean()  #CREATING A 'avg_heart_rate' VARIABLE THAT WILL STORE THE AVERAGE OF THE DATA THAT WILL UTILISED AS AN OVERLAY
        rounded_avg_heart_rate = round(avg_heart_rate)   #CREATING A VARIABLE THAT ROUNDS THE AVERAGE VARIABLE TO A WHOLE NUMBER

        #CREATING A FIGURE THAT WILL HOUSE THE GRID OF SUBPLOTS (2 ROWS, 2 COLUMNS)
        figLR = plt.figure(figsize=(14, 8))

        #CREATING A GRID OF SUBPLOTS FOR THE GRAPHS TO BE DISPLAYED
        ax1 = figLR.add_subplot(2, 2, 1)        #CREATING THE SUBPLOT FOR THE TOP LEFT GRAPH
        ax2 = figLR.add_subplot(2, 2, 2)        #CREATING THE SUBPLOT FOR THE TOP RIGHT GRAPH
        ax3 = figLR.add_subplot(2, 2, 3)        #CREATING THE SUBPLOT FOR THE BOTTOM LEFT GRAPH
        ax4 = figLR.add_subplot(2, 2, 4)        #CREATING THE SUBPLOT FOR THE BOTTOM RIGHT GRAPH

        #GRAPH PLOT 1 - POWER AND HEART RATE
        non_zero_mask1 = (points_df['heart_rate'] != 0) & (points_df['power'] != 0)             #CREATING A ZERO MASK THAT WILL TAKE OUT AN ZERO VALUES THAT ARE NOT MEAN TO BE IN THE DATA
        x1 = points_df.loc[non_zero_mask1, 'heart_rate']                                        #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE X AXIS
        y1 = points_df.loc[non_zero_mask1, 'power']                                             #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE Y AXIS
        slope, intercept, r_value, p_value, std_err = linregress(x1, y1)                        #DEFIING THE LINEAR REGRESSION INTERCEPT, SLOPE AND VARIOUS VALUES RELATING TO THE MODEL
        predicted_cadence = slope * x1 + intercept                                              #PREDICITING WHERE THE INTECEPT WILL HAPPEN ALONG WITH PREDICTED FUTURE VALUES BASED UPON THE DATA
        ax1.scatter(x1, y1, label='Data', color='orange', s=0.5)                                #PLOTTING THE PERFORMANCE METRICS DATA ALONG WITH ITS COLOUR PROFILE
        ax1.plot(x1, predicted_cadence, color='black', label='Regression Line')                 #PLOTTING THE LINEAR REGRESSION LINE ON THE PLOT OVER THE PERFORMANCE METRIC
        ax1.set_title('Linear Regression: Power vs. Heart Rate')                                #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED

        #GRAPH PLOT 2 - HEARTRATE BASE PLOT 
        ax2.scatter(points_df['timestamp'], points_df['heart_rate'], color='red', s=0.5)        #CREATING THE HEARTRATE PLOT THAT WILL BE COLOURED RED AS A VISUAL REPRESENTATION
        ax2.set_title('Heart Rate (BPM)')                                                       #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED
        ax2.set_xticks([])                                                                      #SETTING THE X-AXIS TO NOT HAVE A LABEL TO CREATE A CLEAN VISUAL
        ax2.axhline(avg_heart_rate, color='black', linestyle='--')                              #ADDING AN AVERAGE LINE TO THE PLOT TO REPRESENT THE AVERAGE VALUE OF THE DATA
        ax2.text(points_df['timestamp'].iloc[-1] + 0.06 * (points_df['timestamp'].iloc[-1]      #CALCULATING AND DISPLAYING THE AVERAGE FOR THE DATA FOR THE USER TO SEE ALONGSIDE THE GRAPH
                                                           - points_df['timestamp'].iloc[0]),
                 avg_heart_rate, f'Avg: {rounded_avg_heart_rate}', ha='left', va='center')      
        ax3.set_xticks([])                                                                  

        #GRAPH PLOT 3 - SPEED AND HEART RATE
        non_zero_mask3 = (points_df['heart_rate'] != 0) & (points_df['speed'] != 0)             #CREATING A ZERO MASK THAT WILL TAKE OUT AN ZERO VALUES THAT ARE NOT MEAN TO BE IN THE DATA
        x3 = points_df.loc[non_zero_mask3, 'heart_rate']                                        #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE X AXIS
        y3 = points_df.loc[non_zero_mask3, 'speed']                                             #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE Y AXIS
        slope, intercept, r_value, p_value, std_err = linregress(x3, y3)                        #DEFIING THE LINEAR REGRESSION INTERCEPT, SLOPE AND VARIOUS VALUES RELATING TO THE MODEL
        predicted_speed = slope * x3 + intercept                                                #PREDICITING WHERE THE INTECEPT WILL HAPPEN ALONG WITH PREDICTED FUTURE VALUES BASED UPON THE DATA
        ax3.scatter(x3, y3, label='Data', color='lightblue', s=0.5)                             #PLOTTING THE PERFORMANCE METRICS DATA ALONG WITH ITS COLOUR PROFILE
        ax3.plot(x3, predicted_speed, color='black', label='Regression Line')                   #PLOTTING THE LINEAR REGRESSION LINE ON THE PLOT OVER THE PERFORMANCE METRIC
        ax3.set_title('Linear Regression: Speed vs. Heart Rate')                                #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED
                                                                            
        #GRAPH PLOT 4 - ALTITUDE AND HEART RATE
        non_zero_mask4 = (points_df['heart_rate'] != 0) & (points_df['altitude'] != 0)          #CREATING A ZERO MASK THAT WILL TAKE OUT AN ZERO VALUES THAT ARE NOT MEAN TO BE IN THE DATA
        x4 = points_df.loc[non_zero_mask4, 'heart_rate']                                        #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE X AXIS
        y4 = points_df.loc[non_zero_mask4, 'altitude']                                          #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE Y AXIS
        slope, intercept, r_value, p_value, std_err = linregress(x4, y4)                        #DEFIING THE LINEAR REGRESSION INTERCEPT, SLOPE AND VARIOUS VALUES RELATING TO THE MODEL
        predicted_heart_rate = slope * x4 + intercept                                           #PREDICITING WHERE THE INTECEPT WILL HAPPEN ALONG WITH PREDICTED FUTURE VALUES BASED UPON THE DATA
        ax4.scatter(x4, y4, label='Data', color='green', s=0.5)                                 #PLOTTING THE PERFORMANCE METRICS DATA ALONG WITH ITS COLOUR PROFILE
        ax4.plot(x4, predicted_heart_rate, color='black', label='Regression Line')              #PLOTTING THE LINEAR REGRESSION LINE ON THE PLOT OVER THE PERFORMANCE METRIC
        ax4.set_title('Linear Regression: Heart Rate vs. Altitude')                             #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED

        ActivityGraphsLR = FigureCanvasTkAgg(figLR, master=LinearRegressionGraphs)              #CREATING A 'FigureCanvasTkAgg' OBJECT TO DISPLAY THE FIGURE WITH THE SUBPLOTS WITHIN THE 'ActivityGraphsLR' FRAME
        ActivityGraphsLR.draw()                                                                 #DISPLAYING THE SUBPLOTS TO THE USER
        ActivityGraphsLR.get_tk_widget().configure(width=1600, height=600)                      #SETTING THE SIZE OF THE CANVAS WIDGET
        ActivityGraphsLR.get_tk_widget().grid(row=5, column=0,sticky="w")                       #DISPLAYING THE CANVAS WIDGET WITHIN THE 'ActivityGraphsCombined' FRAME

    ActivityLinearRegressionGraphsHR()

    def ActivityLinearRegressionGraphsSPD():
        ClearLinearRegressionFrame()            #CALLING THE 'ClearActivityGraphsCombiFrame' FUNCTION TO CLEAR ANY PREVIOUS SUBPLOTS
        avg_speed = points_df['speed'].mean()   #CREATING A 'avg_speed' VARIABLE THAT WILL STORE THE AVERAGE OF THE DATA THAT WILL UTILISED AS AN OVERLAY
        rounded_avg_speed = round(avg_speed)    #CREATING A VARIABLE THAT ROUNDS THE AVERAGE VARIABLE TO A WHOLE NUMBER

        #CREATING A FIGURE THAT WILL HOUSE THE GRID OF SUBPLOTS (2 ROWS, 2 COLUMNS)
        figLR = plt.figure(figsize=(14, 8))

        #CREATING A GRID OF SUBPLOTS FOR THE GRAPHS TO BE DISPLAYED
        ax1 = figLR.add_subplot(2, 2, 1)        #CREATING THE SUBPLOT FOR THE TOP LEFT GRAPH
        ax2 = figLR.add_subplot(2, 2, 2)        #CREATING THE SUBPLOT FOR THE TOP RIGHT GRAPH
        ax3 = figLR.add_subplot(2, 2, 3)        #CREATING THE SUBPLOT FOR THE BOTTOM LEFT GRAPH
        ax4 = figLR.add_subplot(2, 2, 4)        #CREATING THE SUBPLOT FOR THE BOTTOM RIGHT GRAPH

        #GRAPH PLOT 1 - POWER AND SPEED
        non_zero_mask = (points_df['speed'] != 0) & (points_df['power'] != 0)                   #CREATING A ZERO MASK THAT WILL TAKE OUT AN ZERO VALUES THAT ARE NOT MEAN TO BE IN THE DATA
        x1 = points_df.loc[non_zero_mask, 'power']                                              #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE X AXIS
        y1 = points_df.loc[non_zero_mask, 'speed']                                              #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE Y AXIS
        slope, intercept, r_value, p_value, std_err = linregress(x1, y1)                        #DEFIING THE LINEAR REGRESSION INTERCEPT, SLOPE AND VARIOUS VALUES RELATING TO THE MODEL
        predicted_cadence = slope * x1 + intercept                                              #PREDICITING WHERE THE INTECEPT WILL HAPPEN ALONG WITH PREDICTED FUTURE VALUES BASED UPON THE DATA
        ax1.scatter(x1, y1, label='Data', color='orange', s=0.5)                                #PLOTTING THE PERFORMANCE METRICS DATA ALONG WITH ITS COLOUR PROFILE
        ax1.plot(x1, predicted_cadence, color='black', label='Regression Line')                 #PLOTTING THE LINEAR REGRESSION LINE ON THE PLOT OVER THE PERFORMANCE METRIC
        ax1.set_title('Linear Regression: Speed vs. Power')                                     #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED
                                                                                     
        #GRAPH PLOT 2 - HEART RATE AND SPEED
        non_zero_mask2 = (points_df['speed'] != 0) & (points_df['heart_rate'] != 0)             #CREATING A ZERO MASK THAT WILL TAKE OUT AN ZERO VALUES THAT ARE NOT MEAN TO BE IN THE DATA
        x2 = points_df.loc[non_zero_mask2, 'heart_rate']                                        #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE X AXIS
        y2 = points_df.loc[non_zero_mask2, 'speed']                                             #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE Y AXIS
        slope, intercept, r_value, p_value, std_err = linregress(x2, y2)                        #DEFIING THE LINEAR REGRESSION INTERCEPT, SLOPE AND VARIOUS VALUES RELATING TO THE MODEL
        predicted_heart_rate = slope * x2 + intercept                                           #PREDICITING WHERE THE INTECEPT WILL HAPPEN ALONG WITH PREDICTED FUTURE VALUES BASED UPON THE DATA
        ax2.scatter(x2, y2, label='Data', color='red', s=0.5)                                   #PLOTTING THE PERFORMANCE METRICS DATA ALONG WITH ITS COLOUR PROFILE
        ax2.plot(x2, predicted_heart_rate, color='black', label='Regression Line')              #PLOTTING THE LINEAR REGRESSION LINE ON THE PLOT OVER THE PERFORMANCE METRIC
        ax2.set_title('Linear Regression: Speed vs. Heart Rate')                                #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED

        #GRAPH PLOT 3 - SPEED BASE PLOT
        ax3.scatter(points_df['timestamp'], points_df['speed'], color='lightblue', s=0.5)       #CREATING THE SPEED PLOT THAT WILL BE COLOURED LIGHT BLUE AS A VISUAL REPRESENTATION 
        ax3.set_title('Speed (MPH)')                                                            #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED
        ax3.set_xticks([])                                                                      #SETTING THE X-AXIS TO NOT HAVE A LABEL TO CREATE A CLEAN VISUAL
        ax3.axhline(avg_speed, color='black', linestyle='--')                                   #ADDING AN AVERAGE LINE TO THE PLOT TO REPRESENT THE AVERAGE VALUE OF THE DATA
        ax3.text(points_df['timestamp'].iloc[-1] + 0.06 * (points_df['timestamp'].iloc[-1]      #CALCULATING AND DISPLAYING THE AVERAGE FOR THE DATA FOR THE USER TO SEE ALONGSIDE THE GRAPH
                                                           - points_df['timestamp'].iloc[0]),  
                 avg_speed, f'Avg: {rounded_avg_speed}', ha='left', va='center')

        #GRAPH PLOT 4 - ALTITUDE AND SPEED
        non_zero_mask4 = (points_df['speed'] != 0) & (points_df['altitude'] != 0)               #CREATING A ZERO MASK THAT WILL TAKE OUT AN ZERO VALUES THAT ARE NOT MEAN TO BE IN THE DATA
        x4 = points_df.loc[non_zero_mask4, 'altitude']                                          #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE X AXIS
        y4 = points_df.loc[non_zero_mask4, 'speed']                                             #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE Y AXIS
        slope, intercept, r_value, p_value, std_err = linregress(x4, y4)                        #DEFIING THE LINEAR REGRESSION INTERCEPT, SLOPE AND VARIOUS VALUES RELATING TO THE MODEL
        predicted_heart_rate = slope * x4 + intercept                                           #PREDICITING WHERE THE INTECEPT WILL HAPPEN ALONG WITH PREDICTED FUTURE VALUES BASED UPON THE DATA
        ax4.scatter(x4, y4, label='Data', color='green', s=0.5)                                 #PLOTTING THE PERFORMANCE METRICS DATA ALONG WITH ITS COLOUR PROFILE
        ax4.plot(x4, predicted_heart_rate, color='black', label='Regression Line')              #PLOTTING THE LINEAR REGRESSION LINE ON THE PLOT OVER THE PERFORMANCE METRIC
        ax4.set_title('Linear Regression: Speed vs. Altitude')                                  #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED

        ActivityGraphsLR = FigureCanvasTkAgg(figLR, master=LinearRegressionGraphs)              #CREATING A 'FigureCanvasTkAgg' OBJECT TO DISPLAY THE FIGURE WITH THE SUBPLOTS WITHIN THE 'ActivityGraphsLR' FRAME
        ActivityGraphsLR.draw()                                                                 #DISPLAYING THE SUBPLOTS TO THE USER
        ActivityGraphsLR.get_tk_widget().configure(width=1600, height=600)                      #SETTING THE SIZE OF THE CANVAS WIDGET
        ActivityGraphsLR.get_tk_widget().grid(row=5, column=0,sticky="w")                       #DISPLAYING THE CANVAS WIDGET WITHIN THE 'ActivityGraphsCombined' FRAME

    ActivityLinearRegressionGraphsSPD()

    def ActivityLinearRegressionGraphsPWR():
        ClearLinearRegressionFrame()            #CALLING THE 'ClearActivityGraphsCombiFrame' FUNCTION TO CLEAR ANY PREVIOUS SUBPLOTS
        avg_power = points_df['power'].mean()   #CREATING A 'avg_power' VARIABLE THAT WILL STORE THE AVERAGE OF THE DATA THAT WILL UTILISED AS AN OVERLAY
        rounded_avg_power = round(avg_power)    #CREATING A VARIABLE THAT ROUNDS THE AVERAGE VARIABLE TO A WHOLE NUMBER

        #CREATING A FIGURE THAT WILL HOUSE THE GRID OF SUBPLOTS (2 ROWS, 2 COLUMNS)
        figLR = plt.figure(figsize=(14, 8))

        #CREATING A GRID OF SUBPLOTS FOR THE GRAPHS TO BE DISPLAYED
        ax1 = figLR.add_subplot(2, 2, 1)        #CREATING THE SUBPLOT FOR THE TOP LEFT GRAPH
        ax2 = figLR.add_subplot(2, 2, 2)        #CREATING THE SUBPLOT FOR THE TOP RIGHT GRAPH
        ax3 = figLR.add_subplot(2, 2, 3)        #CREATING THE SUBPLOT FOR THE BOTTOM LEFT GRAPH
        ax4 = figLR.add_subplot(2, 2, 4)        #CREATING THE SUBPLOT FOR THE BOTTOM RIGHT GRAPH

        #GRAPH PLOT 1 - POWER BASE PLOT
        ax1.scatter(points_df['timestamp'], points_df['power'], color='orange', s=0.5)          #CREATING THE HEARTRATE PLOT THAT WILL BE COLOURED RED AS A VISUAL REPRESENTATION
        ax1.set_title('Power (Watts)')                                                          #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED
        ax1.set_ylabel('Watts')                                                                 #SETTING THE LABEL OF THE Y-AXIS TO REPRESENT THE DATA BEING PLOTTED
        ax1.set_xticks([])                                                                      #SETTING THE X-AXIS TO NOT HAVE A LABEL TO CREATE A CLEAN VISUAL
        ax1.axhline(avg_power, color='black', linestyle='--')                                   #ADDING AN AVERAGE LINE TO THE PLOT TO REPRESENT THE AVERAGE VALUE OF THE DATA
        ax1.text(points_df['timestamp'].iloc[-1] + 0.06 * (points_df['timestamp'].iloc[-1]      #CALCULATING AND DISPLAYING THE AVERAGE FOR THE DATA FOR THE USER TO SEE ALONGSIDE THE GRAPH
                                                           - points_df['timestamp'].iloc[0]),
                 avg_power, f'Avg: {rounded_avg_power}', ha='left', va='center')
        ax1.set_xticks([])                                                                      
                                                                                     
        #GRAPH PLOT 2 - HEART RATE AND POWER
        non_zero_mask2 = (points_df['power'] != 0) & (points_df['heart_rate'] != 0)             #CREATING A ZERO MASK THAT WILL TAKE OUT AN ZERO VALUES THAT ARE NOT MEAN TO BE IN THE DATA
        x2 = points_df.loc[non_zero_mask2, 'power']                                             #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE X AXIS
        y2 = points_df.loc[non_zero_mask2, 'heart_rate']                                        #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE Y AXIS
        slope, intercept, r_value, p_value, std_err = linregress(x2, y2)                        #DEFIING THE LINEAR REGRESSION INTERCEPT, SLOPE AND VARIOUS VALUES RELATING TO THE MODEL
        predicted_heart_rate = slope * x2 + intercept                                           #PREDICITING WHERE THE INTECEPT WILL HAPPEN ALONG WITH PREDICTED FUTURE VALUES BASED UPON THE DATA
        ax2.scatter(x2, y2, label='Data', color='red', s=0.5)                                   #PLOTTING THE PERFORMANCE METRICS DATA ALONG WITH ITS COLOUR PROFILE
        ax2.plot(x2, predicted_heart_rate, color='black', label='Regression Line')              #PLOTTING THE LINEAR REGRESSION LINE ON THE PLOT OVER THE PERFORMANCE METRIC
        ax2.set_title('Linear Regression: Heart Rate vs. Power')                                #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED

        #GRAPH PLOT 3 - SPEED AND POWER
        non_zero_mask3 = (points_df['power'] != 0) & (points_df['speed'] != 0)                  #CREATING A ZERO MASK THAT WILL TAKE OUT AN ZERO VALUES THAT ARE NOT MEAN TO BE IN THE DATA
        x3 = points_df.loc[non_zero_mask3, 'power']                                             #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE X AXIS
        y3 = points_df.loc[non_zero_mask3, 'speed']                                             #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE Y AXIS
        slope, intercept, r_value, p_value, std_err = linregress(x3, y3)                        #DEFIING THE LINEAR REGRESSION INTERCEPT, SLOPE AND VARIOUS VALUES RELATING TO THE MODEL
        predicted_speed = slope * x3 + intercept                                                #PREDICITING WHERE THE INTECEPT WILL HAPPEN ALONG WITH PREDICTED FUTURE VALUES BASED UPON THE DATA
        ax3.scatter(x3, y3, label='Data', color='lightblue', s=0.5)                             #PLOTTING THE PERFORMANCE METRICS DATA ALONG WITH ITS COLOUR PROFILE
        ax3.plot(x3, predicted_speed, color='black', label='Regression Line')                   #PLOTTING THE LINEAR REGRESSION LINE ON THE PLOT OVER THE PERFORMANCE METRIC
        ax3.set_title('Linear Regression: Speed vs. Power')                                     #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED

        #GRAPH PLOT 4 - CADENCE AND POWER
        non_zero_mask = (points_df['cadence'] != 0) & (points_df['power'] != 0)                 #CREATING A ZERO MASK THAT WILL TAKE OUT AN ZERO VALUES THAT ARE NOT MEAN TO BE IN THE DATA
        x4 = points_df.loc[non_zero_mask, 'power']                                              #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE X AXIS
        y4 = points_df.loc[non_zero_mask, 'cadence']                                            #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE Y AXIS
        slope, intercept, r_value, p_value, std_err = linregress(x4, y4)                        #DEFIING THE LINEAR REGRESSION INTERCEPT, SLOPE AND VARIOUS VALUES RELATING TO THE MODEL
        predicted_cadence = slope * x4 + intercept                                              #PREDICITING WHERE THE INTECEPT WILL HAPPEN ALONG WITH PREDICTED FUTURE VALUES BASED UPON THE DATA
        ax4.scatter(x4, y4, label='Data', color='grey', s=0.5)                                  #PLOTTING THE PERFORMANCE METRICS DATA ALONG WITH ITS COLOUR PROFILE
        ax4.plot(x4, predicted_cadence, color='black', label='Regression Line')                 #PLOTTING THE LINEAR REGRESSION LINE ON THE PLOT OVER THE PERFORMANCE METRIC
        ax4.set_title('Linear Regression: Cadence vs. Power')                                   #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED

        ActivityGraphsLR = FigureCanvasTkAgg(figLR, master=LinearRegressionGraphs)              #CREATING A 'FigureCanvasTkAgg' OBJECT TO DISPLAY THE FIGURE WITH THE SUBPLOTS WITHIN THE 'ActivityGraphsLR' FRAME
        ActivityGraphsLR.draw()                                                                 #DISPLAYING THE SUBPLOTS TO THE USER
        ActivityGraphsLR.get_tk_widget().configure(width=1600, height=600)                      #SETTING THE SIZE OF THE CANVAS WIDGET
        ActivityGraphsLR.get_tk_widget().grid(row=5, column=0,sticky="w")                       #DISPLAYING THE CANVAS WIDGET WITHIN THE 'LinearRegressionGraphs' FRAME

    ActivityLinearRegressionGraphsPWR()
    folder_path = 'C:/Users/natda/OneDrive/University/MSc Computer Science/Thesis/GAA/GAA Software/Activities'+'/'+str(name) #DEFINIG THE USERS PATHWAY FOLDER
    filenames = get_filenames_in_folder(folder_path)                                                            #GATHERING THE FILENAMES FROM THE FOLDER DEFINED ABOVE

    dropdown_var = tk.StringVar()                                                                 #CREATINGI A TKINTER STRING VARIABLE TO STORE ALL OF THE FILE NAMES
    dropdownAct = ttk.Combobox(controls_framelRG, textvariable=dropdown_var, values=filenames)    #DISPLAYING THE FILENAMES WITHIN THE DROPDOWN BOX
    dropdownAct.set("Select a File...")                                                           #CREATING A PLACE HOLDER THAT IS DISPLAYED UNTIL THE USER INTERACTS WITH THE DROPDOWN
    dropdownAct.grid(row=3, column=0)                                                             #DISPLAYING THE DROPDOWN BOX TO THE USER 

    dropdownAct.bind("<<ComboboxSelected>>", on_dropdown_select)                                  #BINDING AN EVENT HANDER TO THE DROPDOWN BOX ALSO ACTS AS A DEBUGGER

    dropdown3 = ttk.Combobox(controls_frameLRG, values=["Linear Regression - Power",              #CREATING A DROPDOWN BOX THAT WILL STORE THE 3 DIFFERENT GRAPH VISUALS
                                                        "Linear Regression - Speed",
                                                        "Linear Regression - Altitude",
                                                        "Linear Regression - Heart Rate"])
    dropdown3.set("Select a Graph Style...")                                                      #DISPLAYING A MESSAGE EXPLAINING TO THE USER WHAT THE DROPDOWN BOX DOES
    dropdown3.grid(row=3, column=1,sticky="w")                                                    #DISPLAYING THE DROPDOWN BOX FOR THE USER TO INTERACT WITH
    
    def SelectLinearRegressionGraphStyle():
        selected_style = dropdown3.get()                          #GATHERING THE USER'S SELECTION FROM THE DROPDOWN BOX 
        if selected_style == "Linear Regression - Power":         #IF THE IF STATEMENT CONDITIONS ARE MET THE FOLLOWING TAKES PLACE:
            ActivityLinearRegressionGraphsPWR()                   #EXECUTING THE 'ActivityLinearRegressionGraphsPWR' FUNCTION
        elif selected_style == "Linear Regression - Altitude":    #IF THE IF STATEMENT CONDITIONS ARE MET THE FOLLOWING TAKES PLACE:
            ActivityLinearRegressionGraphsALT()                   #EXECUTING THE 'ActivityLinearRegressionGraphsALT' FUNCTION
        elif selected_style == "Linear Regression - Speed":       #IF THE IF STATEMENT CONDITIONS ARE MET THE FOLLOWING TAKES PLACE: 
            ActivityLinearRegressionGraphsSPD()                   #EXECUTING THE 'ActivityLinearRegressionGraphsHR' FUNCTION
        elif selected_style == "Linear Regression - Heart Rate":  #IF THE IF STATEMENT CONDITIONS ARE MET THE FOLLOWING TAKES PLACE: 
            ActivityLinearRegressionGraphsHR()                    #EXECUTING THE 'ActivityLinearRegressionGraphsHR' FUNCTION

    button1 = ttk.Button(controls_frameLRG, text="Select")        #CREATING THE BUTTON THAT WILL USER WILL INTERACT WITH
    button1.configure(command=SelectActivity)                     #BINDING THE 'SelectActivity' FUNCTION WITH THE BUTTON
    button1.grid(row=3, column=1)                                 #DISPLAYING THE BUTTON TO THE USER 
    button3 = ttk.Button(controls_frameLRG, text="Select")        #CREATING THE BUTTON THAT WILL USER WILL INTERACT WITH
    button3.configure(command=SelectLinearRegressionGraphStyle)   #BINDING THE 'SelectLinearRegressionGraphStyle' FUNCTION WITH THE BUTTON
    button3.grid(row=3, column=2,sticky="e")                      #DISPLAYING THE BUTTON TO THE USER   

############################################################################################################################################################################################################################################
#     POLYNOMINAL REGRESSION      #     POLYNOMINAL REGRESSION          #     POLYNOMINAL REGRESSION      #     POLYNOMINAL REGRESSION      #     POLYNOMINAL REGRESSION      #     POLYNOMINAL REGRESSION      #     POLYNOMINAL REGRESSION
############################################################################################################################################################################################################################################
    PolynomialRegressionGraphs = ttk.Frame(style="W.TFrame")                   #CREATING THE 'ActivityGraphsCombined' FRAME THAT WILL HOUSE THE COMBINED GRAPHS FOR THE USER TO SEE

    controls_framePRG = ttk.Frame(PolynomialRegressionGraphs,style="W.TFrame") #CREATING A 'controls_frameAGC' THAT WILL HOUSE THE TITLE AND INFOMATION OF THE PAGE - THIS MEANS WHEN THE GRAPHS ARE UPDATED THESE STAY VISIBLE
    controls_framePRG.grid(row=4, column=0)                                #DISPLAY THE 'controls_frameAGC' TO THE USER

    s1 = Label(controls_framePRG, text=" ", bg="white")                                                                      #CREATING AN EMPTY LABEL THAT WILL ACT AS A ONE LINE SPACE
    s1.grid(row=0, column=0)                                                                                                 #DISPLAYING THE ONE LINE SPACE
    l1 = Label(controls_framePRG, text="Activity Analyser - Linear Regression Graphs", font='Helvetica 12 bold', bg="white") #CREATING THE MAIN HEADING FOR THE TAB THAT WILL BE DISPLAYED AT THE TOP OF THE FRAME
    l1.grid(row=1, column=0)                                                                                                 #DISPLAYING THE TITLE
    l2 = Label(controls_framePRG, text="Graphs Produced From: " + str(Activity), font='Helvetica 9', bg="white")             #CREATING THE SUBTITLE FOR THE TAB THAT STATES THE FILE BEING USED 
    l2.grid(row=2, column=0)                                                                                                 #DISPLAYING THE SUBTITLE

    def ClearPolynomialRegressionFrame():
        for widget in PolynomialRegressionGraphs.winfo_children(): #FOR THE WIDGET OBJECT WITHIN THE 'PolynomialRegressionGraphs' THE FOLLOWING TOOK PLACE
            if widget != controls_framePRG:                        #IF THE WIDGET OBJECT WAS NOT IN THE 'controls_framePRG' THE FOLLOWING TOOK PLACE  
                widget.destroy()                                   #THE WIDGET OBJECT IS DESTROYED ALLOWING FOR THE NEW GRAPHS TO BE DISPLAYED
                
    def ActivityPolynomialRegressionGraphsALT():
        ClearPolynomialRegressionFrame()                           # CALLING THE 'ClearPolynomialRegressionFrame' FUNCTION TO CLEAR ANY PREVIOUS SUBPLOTS

        # CREATING A FIGURE THAT WILL HOUSE THE GRID OF SUBPLOTS (2 ROWS, 2 COLUMNS)
        figPR = plt.figure(figsize=(14, 8))

        # CREATING A GRID OF SUBPLOTS FOR THE GRAPHS TO BE DISPLAYED
        ax1 = figPR.add_subplot(2, 2, 1)  # CREATING THE SUBPLOT FOR THE TOP LEFT GRAPH
        ax2 = figPR.add_subplot(2, 2, 2)  # CREATING THE SUBPLOT FOR THE TOP RIGHT GRAPH
        ax3 = figPR.add_subplot(2, 2, 3)  # CREATING THE SUBPLOT FOR THE BOTTOM LEFT GRAPH
        ax4 = figPR.add_subplot(2, 2, 4)  # CREATING THE SUBPLOT FOR THE BOTTOM RIGHT GRAPH

        # GRAPH PLOT 1 - POWER AND ALTITUDE
        non_zero_mask1 = (points_df['altitude'] != 0) & (points_df['power'] != 0)          #CREATING A ZERO MASK THAT WILL TAKE OUT AN ZERO VALUES THAT ARE NOT MEAN TO BE IN THE DATA
        x1 = points_df.loc[non_zero_mask1, 'altitude']                                     #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE X AXIS
        y1 = points_df.loc[non_zero_mask1, 'power']                                        #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE Y AXIS
        coeffs = np.polyfit(x1, y1, deg=2)                                                 #PERFORMING THE POLYNOMIAL REGRESSION OF 2 DEGREES
        polynomial = np.poly1d(coeffs)                                                     #CREATING THE POLYNOMIAL MODEL USING THE DEGREES VALUE AND PERFORMANCE METRIC VALUES  
        x_fit = np.linspace(min(x1), max(x1), 100)                                         #FITTING THE POLYNOMIAL REGRESSION MODEL TO THE X AXIS WITH MIN AND MAX BOUNDS
        y_fit = polynomial(x_fit)                                                          #FITTING THE POLYNOMIAL REGRESSION MODEL TO THE Y AXIS                                                        
        ax1.scatter(x1, y1, label='Data', color='orange', s=0.5)                           #PLOTTING THE PERFORMANCE METRICS DATA ALONG WITH ITS COLOUR PROFILE
        ax1.plot(x_fit, y_fit, color='black', label='Polynomial Regression')               #PLOTTING THE POLYNOMIAL REGRESSION LINE ON THE PLOT OVER THE PERFORMANCE METRIC
        ax1.set_title('Polynomial Regression: Power vs. Altitude')                         #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED

        # GRAPH PLOT 2 - HEART RATE AND ALTITUDE
        non_zero_mask2 = (points_df['altitude'] != 0) & (points_df['heart_rate'] != 0)     #CREATING A ZERO MASK THAT WILL TAKE OUT AN ZERO VALUES THAT ARE NOT MEAN TO BE IN THE DATA
        x2 = points_df.loc[non_zero_mask2, 'altitude']                                     #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE X AXIS
        y2 = points_df.loc[non_zero_mask2, 'heart_rate']                                   #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE Y AXIS
        coeffs = np.polyfit(x2, y2, deg=2)                                                 #PERFORMING THE POLYNOMIAL REGRESSION OF 2 DEGREES
        polynomial = np.poly1d(coeffs)                                                     #CREATING THE POLYNOMIAL MODEL USING THE DEGREES VALUE AND PERFORMANCE METRIC VALUES 
        x_fit = np.linspace(min(x2), max(x2), 100)                                         #FITTING THE POLYNOMIAL REGRESSION MODEL TO THE X AXIS WITH MIN AND MAX BOUNDS
        y_fit = polynomial(x_fit)                                                          #FITTING THE POLYNOMIAL REGRESSION MODEL TO THE Y AXIS
        ax2.scatter(x2, y2, label='Data', color='red', s=0.5)                              #PLOTTING THE PERFORMANCE METRICS DATA ALONG WITH ITS COLOUR PROFILE
        ax2.plot(x_fit, y_fit, color='black', label='Polynomial Regression')               #PLOTTING THE POLYNOMIAL REGRESSION LINE ON THE PLOT OVER THE PERFORMANCE METRIC
        ax2.set_title('Polynomial Regression: Heart Rate vs. Altitude')                    #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED

        # GRAPH PLOT 3 - SPEED AND ALTITUDE
        non_zero_mask3 = (points_df['altitude'] != 0) & (points_df['speed'] != 0)          #CREATING A ZERO MASK THAT WILL TAKE OUT AN ZERO VALUES THAT ARE NOT MEAN TO BE IN THE DATA
        x3 = points_df.loc[non_zero_mask3, 'altitude']                                     #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE X AXIS
        y3 = points_df.loc[non_zero_mask3, 'speed']                                        #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE Y AXIS
        coeffs = np.polyfit(x3, y3, deg=2)                                                 #PERFORMING THE POLYNOMIAL REGRESSION OF 2 DEGREES
        polynomial = np.poly1d(coeffs)                                                     #CREATING THE POLYNOMIAL MODEL USING THE DEGREES VALUE AND PERFORMANCE METRIC VALUES 
        x_fit = np.linspace(min(x3), max(x3), 100)                                         #FITTING THE POLYNOMIAL REGRESSION MODEL TO THE X AXIS WITH MIN AND MAX BOUNDS
        y_fit = polynomial(x_fit)                                                          #FITTING THE POLYNOMIAL REGRESSION MODEL TO THE Y AXIS
        ax3.scatter(x3, y3, label='Data', color='lightblue', s=0.5)                        #PLOTTING THE PERFORMANCE METRICS DATA ALONG WITH ITS COLOUR PROFILE
        ax3.plot(x_fit, y_fit, color='black', label='Polynomial Regression')               #PLOTTING THE POLYNOMIAL REGRESSION LINE ON THE PLOT OVER THE PERFORMANCE METRIC
        ax3.set_title('Polynomial Regression: Speed vs. Altitude')                         #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED

        # GRAPH PLOT 3 - SPEED AND ALTITUDE
        non_zero_mask4 = (points_df['altitude'] != 0) & (points_df['cadence'] != 0)        #CREATING A ZERO MASK THAT WILL TAKE OUT AN ZERO VALUES THAT ARE NOT MEAN TO BE IN THE DATA
        x4 = points_df.loc[non_zero_mask4, 'altitude']                                     #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE X AXIS
        y4 = points_df.loc[non_zero_mask4, 'cadence']                                      #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE Y AXIS
        coeffs = np.polyfit(x4, y4, deg=2)                                                 #PERFORMING THE POLYNOMIAL REGRESSION OF 2 DEGREES
        polynomial = np.poly1d(coeffs)                                                     #CREATING THE POLYNOMIAL MODEL USING THE DEGREES VALUE AND PERFORMANCE METRIC VALUES 
        x_fit = np.linspace(min(x4), max(x4), 100)                                         #FITTING THE POLYNOMIAL REGRESSION MODEL TO THE X AXIS WITH MIN AND MAX BOUNDS
        y_fit = polynomial(x_fit)                                                          #FITTING THE POLYNOMIAL REGRESSION MODEL TO THE Y AXIS
        ax4.scatter(x4, y4, label='Data', color='grey', s=0.5)                             #PLOTTING THE PERFORMANCE METRICS DATA ALONG WITH ITS COLOUR PROFILE
        ax4.plot(x_fit, y_fit, color='black', label='Polynomial Regression')               #PLOTTING THE POLYNOMIAL REGRESSION LINE ON THE PLOT OVER THE PERFORMANCE METRIC
        ax4.set_title('Polynomial Regression: Cadence vs. Altitude')                       #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED

        ActivityGraphsPR = FigureCanvasTkAgg(figPR, master=PolynomialRegressionGraphs)     #CREATING A 'FigureCanvasTkAgg' OBJECT TO DISPLAY THE FIGURE WITH THE SUBPLOTS WITHIN THE 'ActivityGraphsPR' FRAME
        ActivityGraphsPR.draw()                                                            #DISPLAYING THE SUBPLOTS TO THE USER
        ActivityGraphsPR.get_tk_widget().configure(width=1600, height=600)                 #SETTING THE SIZE OF THE CANVAS WIDGET
        ActivityGraphsPR.get_tk_widget().grid(row=5, column=0, sticky="w")                 #DISPLAYING THE CANVAS WIDGET WITHIN THE 'PolynomialRegressionGraphs' FRAME

    ActivityPolynomialRegressionGraphsALT()
    
    def ActivityPolynomialRegressionGraphsSPD():
        ClearPolynomialRegressionFrame()  # CALLING THE 'ClearActivityGraphsCombiFrame' FUNCTION TO CLEAR ANY PREVIOUS SUBPLOTS

        # CREATING A FIGURE THAT WILL HOUSE THE GRID OF SUBPLOTS (2 ROWS, 2 COLUMNS)
        figPR = plt.figure(figsize=(14, 8))

        # CREATING A GRID OF SUBPLOTS FOR THE GRAPHS TO BE DISPLAYED
        ax1 = figPR.add_subplot(2, 2, 1)  # CREATING THE SUBPLOT FOR THE TOP LEFT GRAPH
        ax2 = figPR.add_subplot(2, 2, 2)  # CREATING THE SUBPLOT FOR THE TOP RIGHT GRAPH
        ax3 = figPR.add_subplot(2, 2, 3)  # CREATING THE SUBPLOT FOR THE BOTTOM LEFT GRAPH
        ax4 = figPR.add_subplot(2, 2, 4)  # CREATING THE SUBPLOT FOR THE BOTTOM RIGHT GRAPH

                # GRAPH PLOT 4
        non_zero_mask1 = (points_df['speed'] != 0) & (points_df['power'] != 0)                  #CREATING A ZERO MASK THAT WILL TAKE OUT AN ZERO VALUES THAT ARE NOT MEAN TO BE IN THE DATA
        x1 = points_df.loc[non_zero_mask1, 'speed']                                             #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE X AXIS
        y1 = points_df.loc[non_zero_mask1, 'power']                                             #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE Y AXIS
        degree = 3                                                                              #SETTING THE POLYNOMIAL REGRESSION DEGREE OF 3
        coeffs = np.polyfit(x1, y1, deg=degree)                                                 #PERFORMING THE POLYNOMIAL REGRESSION OF THE CHOSEN DEGREE
        polynomial = np.poly1d(coeffs)                                                          #CREATING THE POLYNOMIAL MODEL USING THE DEGREES VALUE AND PERFORMANCE METRIC VALUES 
        x_fit = np.linspace(min(x1), max(x1), 100)                                              #FITTING THE POLYNOMIAL REGRESSION MODEL TO THE X AXIS WITH MIN AND MAX BOUNDS
        y_fit = polynomial(x_fit)                                                               #FITTING THE POLYNOMIAL REGRESSION MODEL TO THE Y AXIS
        ax1.scatter(x1, y1, label='Data', color='orange', s=0.5)                                #PLOTTING THE PERFORMANCE METRICS DATA ALONG WITH ITS COLOUR PROFILE
        ax1.plot(x_fit, y_fit, color='black', label=f'Polynomial Regression (Degree {degree})') #PLOTTING THE POLYNOMIAL REGRESSION LINE ON THE PLOT OVER THE PERFORMANCE METRIC
        ax1.set_title(f'Polynomial Regression: Power vs. Speed (Degree {degree})')              #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED

        # GRAPH PLOT 2 - HEART RATE AND SPEED
        non_zero_mask2 = (points_df['speed'] != 0) & (points_df['heart_rate'] != 0)             #CREATING A ZERO MASK THAT WILL TAKE OUT AN ZERO VALUES THAT ARE NOT MEAN TO BE IN THE DATA
        x2 = points_df.loc[non_zero_mask2, 'speed']                                             #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE X AXIS
        y2 = points_df.loc[non_zero_mask2, 'heart_rate']                                        #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE Y AXIS
        degree = 4                                                                              #SETTING THE POLYNOMIAL REGRESSION DEGREE OF 4
        coeffs = np.polyfit(x2, y2, deg=degree)                                                 #PERFORMING THE POLYNOMIAL REGRESSION OF THE CHOSEN DEGREE
        polynomial = np.poly1d(coeffs)                                                          #CREATING THE POLYNOMIAL MODEL USING THE DEGREES VALUE AND PERFORMANCE METRIC VALUES
        x_fit = np.linspace(min(x2), max(x2), 100)                                              #FITTING THE POLYNOMIAL REGRESSION MODEL TO THE X AXIS WITH MIN AND MAX BOUNDS
        y_fit = polynomial(x_fit)                                                               #FITTING THE POLYNOMIAL REGRESSION MODEL TO THE Y AXIS
        ax2.scatter(x2, y2, label='Data', color='red', s=0.5)                                   #PLOTTING THE PERFORMANCE METRICS DATA ALONG WITH ITS COLOUR PROFILE
        ax2.plot(x_fit, y_fit, color='black', label=f'Polynomial Regression (Degree {degree})') #PLOTTING THE POLYNOMIAL REGRESSION LINE ON THE PLOT OVER THE PERFORMANCE METRIC
        ax2.set_title(f'Polynomial Regression: Heart Rate vs. Speed (Degree {degree})')         #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED

        # GRAPH PLOT 3 - SPEED AND ALTITUDE
        non_zero_mask3 = (points_df['speed'] != 0) & (points_df['cadence'] != 0)                #CREATING A ZERO MASK THAT WILL TAKE OUT AN ZERO VALUES THAT ARE NOT MEAN TO BE IN THE DATA
        x3 = points_df.loc[non_zero_mask3, 'speed']                                             #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE X AXIS
        y3 = points_df.loc[non_zero_mask3, 'cadence']                                           #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE Y AXIS
        degree = 4                                                                              #SETTING THE POLYNOMIAL REGRESSION DEGREE OF 4
        coeffs = np.polyfit(x3, y3, deg=degree)                                                 #PERFORMING THE POLYNOMIAL REGRESSION OF THE CHOSEN DEGREE
        polynomial = np.poly1d(coeffs)                                                          #CREATING THE POLYNOMIAL MODEL USING THE DEGREES VALUE AND PERFORMANCE METRIC VALUES 
        x_fit = np.linspace(min(x3), max(x3), 100)                                              #FITTING THE POLYNOMIAL REGRESSION MODEL TO THE X AXIS WITH MIN AND MAX BOUNDS
        y_fit = polynomial(x_fit)                                                               #FITTING THE POLYNOMIAL REGRESSION MODEL TO THE Y AXIS
        ax3.scatter(x3, y3, label='Data', color='grey', s=0.5)                                  #PLOTTING THE PERFORMANCE METRICS DATA ALONG WITH ITS COLOUR PROFILE
        ax3.plot(x_fit, y_fit, color='black', label=f'Polynomial Regression (Degree {degree})') #PLOTTING THE POLYNOMIAL REGRESSION LINE ON THE PLOT OVER THE PERFORMANCE METRIC
        ax3.set_title(f'Polynomial Regression: Heart Rate vs. Cadence (Degree {degree})')       #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED

        # GRAPH PLOT 4
        non_zero_mask4 = (points_df['speed'] != 0) & (points_df['altitude'] != 0)               #CREATING A ZERO MASK THAT WILL TAKE OUT AN ZERO VALUES THAT ARE NOT MEAN TO BE IN THE DATA
        x4 = points_df.loc[non_zero_mask4, 'speed']                                             #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE X AXIS
        y4 = points_df.loc[non_zero_mask4, 'altitude']                                          #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE Y AXIS
        degree = 3                                                                              #SETTING THE POLYNOMIAL REGRESSION DEGREE OF 3
        coeffs = np.polyfit(x4, y4, deg=degree)                                                 #PERFORMING THE POLYNOMIAL REGRESSION OF THE CHOSEN DEGREE
        polynomial = np.poly1d(coeffs)                                                          #CREATING THE POLYNOMIAL MODEL USING THE DEGREES VALUE AND PERFORMANCE METRIC VALUES 
        x_fit = np.linspace(min(x4), max(x4), 100)                                              #FITTING THE POLYNOMIAL REGRESSION MODEL TO THE X AXIS WITH MIN AND MAX BOUNDS
        y_fit = polynomial(x_fit)                                                               #FITTING THE POLYNOMIAL REGRESSION MODEL TO THE Y AXIS
        ax4.scatter(x4, y4, label='Data', color='green', s=0.5)                                 #PLOTTING THE PERFORMANCE METRICS DATA ALONG WITH ITS COLOUR PROFILE
        ax4.plot(x_fit, y_fit, color='black', label=f'Polynomial Regression (Degree {degree})') #PLOTTING THE POLYNOMIAL REGRESSION LINE ON THE PLOT OVER THE PERFORMANCE METRIC
        ax4.set_title(f'Polynomial Regression: Speed vs. Altitude (Degree {degree})')           #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED

        ActivityGraphsPR = FigureCanvasTkAgg(figPR, master=PolynomialRegressionGraphs)          #CREATING A 'FigureCanvasTkAgg' OBJECT TO DISPLAY THE FIGURE WITH THE SUBPLOTS WITHIN THE 'ActivityGraphsPR' FRAME
        ActivityGraphsPR.draw()                                                                 #DISPLAYING THE SUBPLOTS TO THE USER
        ActivityGraphsPR.get_tk_widget().configure(width=1600, height=600)                      #SETTING THE SIZE OF THE CANVAS WIDGET
        ActivityGraphsPR.get_tk_widget().grid(row=5, column=0, sticky="w")                      #DISPLAYING THE CANVAS WIDGET WITHIN THE 'PolynomialRegressionGraphs' FRAME

    ActivityPolynomialRegressionGraphsSPD()
    
    def ActivityPolynomialRegressionGraphsHR():
        ClearPolynomialRegressionFrame()  #CALLING THE 'ClearActivityGraphsCombiFrame' FUNCTION TO CLEAR ANY PREVIOUS SUBPLOTS

        #CREATING A FIGURE THAT WILL HOUSE THE GRID OF SUBPLOTS (2 ROWS, 2 COLUMNS)
        figPR = plt.figure(figsize=(14, 8))

        #CREATING A GRID OF SUBPLOTS FOR THE GRAPHS TO BE DISPLAYED
        ax1 = figPR.add_subplot(2, 2, 1)  #CREATING THE SUBPLOT FOR THE TOP LEFT GRAPH
        ax2 = figPR.add_subplot(2, 2, 2)  #CREATING THE SUBPLOT FOR THE TOP RIGHT GRAPH
        ax3 = figPR.add_subplot(2, 2, 3)  #CREATING THE SUBPLOT FOR THE BOTTOM LEFT GRAPH
        ax4 = figPR.add_subplot(2, 2, 4)  #CREATING THE SUBPLOT FOR THE BOTTOM RIGHT GRAPH

        # GRAPH PLOT 1 - POWER AND ALTITUDE
        non_zero_mask1 = (points_df['heart_rate'] != 0) & (points_df['power'] != 0)             #CREATING A ZERO MASK THAT WILL TAKE OUT AN ZERO VALUES THAT ARE NOT MEAN TO BE IN THE DATA
        x1 = points_df.loc[non_zero_mask1, 'heart_rate']                                        #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE X AXIS
        y1 = points_df.loc[non_zero_mask1, 'power']                                             #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE Y AXIS
        degree = 4                                                                              #SETTING THE POLYNOMIAL REGRESSION DEGREE OF 4
        coeffs = np.polyfit(x1, y1, deg=degree)                                                 #PERFORMING THE POLYNOMIAL REGRESSION OF THE CHOSEN DEGREE
        polynomial = np.poly1d(coeffs)                                                          #CREATING THE POLYNOMIAL MODEL USING THE DEGREES VALUE AND PERFORMANCE METRIC VALUES 
        x_fit = np.linspace(min(x1), max(x1), 100)                                              #FITTING THE POLYNOMIAL REGRESSION MODEL TO THE X AXIS WITH MIN AND MAX BOUNDS
        y_fit = polynomial(x_fit)                                                               #FITTING THE POLYNOMIAL REGRESSION MODEL TO THE Y AXIS
        ax1.scatter(x1, y1, label='Data', color='orange', s=0.5)                                #PLOTTING THE PERFORMANCE METRICS DATA ALONG WITH ITS COLOUR PROFILE
        ax1.plot(x_fit, y_fit, color='black', label=f'Polynomial Regression (Degree {degree})') #PLOTTING THE POLYNOMIAL REGRESSION LINE ON THE PLOT OVER THE PERFORMANCE METRIC
        ax1.set_title(f'Polynomial Regression: Heart Rate vs. Power (Degree {degree})')         #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED

        # GRAPH PLOT 3 - SPEED AND ALTITUDE
        non_zero_mask2 = (points_df['heart_rate'] != 0) & (points_df['cadence'] != 0)           #CREATING A ZERO MASK THAT WILL TAKE OUT AN ZERO VALUES THAT ARE NOT MEAN TO BE IN THE DATA
        x2 = points_df.loc[non_zero_mask2, 'heart_rate']                                        #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE X AXIS
        y2 = points_df.loc[non_zero_mask2, 'cadence']                                           #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE Y AXIS
        degree = 4                                                                              #SETTING THE POLYNOMIAL REGRESSION DEGREE OF 4
        coeffs = np.polyfit(x2, y2, deg=degree)                                                 #PERFORMING THE POLYNOMIAL REGRESSION OF THE CHOSEN DEGREE
        polynomial = np.poly1d(coeffs)                                                          #CREATING THE POLYNOMIAL MODEL USING THE DEGREES VALUE AND PERFORMANCE METRIC VALUES 
        x_fit = np.linspace(min(x2), max(x2), 100)                                              #FITTING THE POLYNOMIAL REGRESSION MODEL TO THE X AXIS WITH MIN AND MAX BOUNDS
        y_fit = polynomial(x_fit)                                                               #FITTING THE POLYNOMIAL REGRESSION MODEL TO THE Y AXIS
        ax2.scatter(x2, y2, label='Data', color='grey', s=0.5)                                  #PLOTTING THE PERFORMANCE METRICS DATA ALONG WITH ITS COLOUR PROFILE
        ax2.plot(x_fit, y_fit, color='black', label=f'Polynomial Regression (Degree {degree})') #PLOTTING THE POLYNOMIAL REGRESSION LINE ON THE PLOT OVER THE PERFORMANCE METRIC
        ax2.set_title(f'Polynomial Regression: Heart Rate vs. Cadence (Degree {degree})')       #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED
        
        # GRAPH PLOT 3 - SPEED AND ALTITUDE
        non_zero_mask3 = (points_df['heart_rate'] != 0) & (points_df['speed'] != 0)             #CREATING A ZERO MASK THAT WILL TAKE OUT AN ZERO VALUES THAT ARE NOT MEAN TO BE IN THE DATA
        x3 = points_df.loc[non_zero_mask3, 'heart_rate']                                        #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE X AXIS
        y3 = points_df.loc[non_zero_mask3, 'speed']                                             #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE Y AXIS
        degree = 4                                                                              #SETTING THE POLYNOMIAL REGRESSION DEGREE OF 4
        coeffs = np.polyfit(x3, y3, deg=degree)                                                 #PERFORMING THE POLYNOMIAL REGRESSION OF THE CHOSEN DEGREE
        polynomial = np.poly1d(coeffs)                                                          #CREATING THE POLYNOMIAL MODEL USING THE DEGREES VALUE AND PERFORMANCE METRIC VALUES 
        x_fit = np.linspace(min(x3), max(x3), 100)                                              #FITTING THE POLYNOMIAL REGRESSION MODEL TO THE X AXIS WITH MIN AND MAX BOUNDS
        y_fit = polynomial(x_fit)                                                               #FITTING THE POLYNOMIAL REGRESSION MODEL TO THE Y AXIS
        ax3.scatter(x3, y3, label='Data', color='lightblue', s=0.5)                             #PLOTTING THE PERFORMANCE METRICS DATA ALONG WITH ITS COLOUR PROFILE
        ax3.plot(x_fit, y_fit, color='black', label=f'Polynomial Regression (Degree {degree})') #PLOTTING THE POLYNOMIAL REGRESSION LINE ON THE PLOT OVER THE PERFORMANCE METRIC
        ax3.set_title(f'Polynomial Regression: Heart Rate vs. Speed (Degree {degree})')         #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED

        # GRAPH PLOT 4
        non_zero_mask4 = (points_df['heart_rate'] != 0) & (points_df['altitude'] != 0)          #CREATING A ZERO MASK THAT WILL TAKE OUT AN ZERO VALUES THAT ARE NOT MEAN TO BE IN THE DATA
        x4 = points_df.loc[non_zero_mask4, 'heart_rate']                                        #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE X AXIS
        y4 = points_df.loc[non_zero_mask4, 'altitude']                                          #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE Y AXIS
        degree = 3                                                                              #SETTING THE POLYNOMIAL REGRESSION DEGREE OF 3
        coeffs = np.polyfit(x4, y4, deg=degree)                                                 #PERFORMING THE POLYNOMIAL REGRESSION OF THE CHOSEN DEGREE
        polynomial = np.poly1d(coeffs)                                                          #CREATING THE POLYNOMIAL MODEL USING THE DEGREES VALUE AND PERFORMANCE METRIC VALUES 
        x_fit = np.linspace(min(x4), max(x4), 100)                                              #FITTING THE POLYNOMIAL REGRESSION MODEL TO THE X AXIS WITH MIN AND MAX BOUNDS
        y_fit = polynomial(x_fit)                                                               #FITTING THE POLYNOMIAL REGRESSION MODEL TO THE Y AXIS
        ax4.scatter(x4, y4, label='Data', color='green', s=0.5)                                 #PLOTTING THE PERFORMANCE METRICS DATA ALONG WITH ITS COLOUR PROFILE
        ax4.plot(x_fit, y_fit, color='black', label=f'Polynomial Regression (Degree {degree})') #PLOTTING THE POLYNOMIAL REGRESSION LINE ON THE PLOT OVER THE PERFORMANCE METRIC
        ax4.set_title(f'Polynomial Regression: Heart Rate vs. Altitude (Degree {degree})')      #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED

        ActivityGraphsPR = FigureCanvasTkAgg(figPR, master=PolynomialRegressionGraphs)          #CREATING A 'FigureCanvasTkAgg' OBJECT TO DISPLAY THE FIGURE WITH THE SUBPLOTS WITHIN THE 'ActivityGraphsPR' FRAME
        ActivityGraphsPR.draw()                                                                 #DISPLAYING THE SUBPLOTS TO THE USER
        ActivityGraphsPR.get_tk_widget().configure(width=1600, height=600)                      #SETTING THE SIZE OF THE CANVAS WIDGET
        ActivityGraphsPR.get_tk_widget().grid(row=5, column=0, sticky="w")                      #DISPLAYING THE CANVAS WIDGET WITHIN THE 'PolynomialRegressionGraphs' FRAME

    ActivityPolynomialRegressionGraphsHR()

    def ActivityPolynomialRegressionGraphsPWR():
        ClearPolynomialRegressionFrame()  # CALLING THE 'ClearActivityGraphsCombiFrame' FUNCTION TO CLEAR ANY PREVIOUS SUBPLOTS

        # CREATING A FIGURE THAT WILL HOUSE THE GRID OF SUBPLOTS (2 ROWS, 2 COLUMNS)
        figPR = plt.figure(figsize=(14, 8))

        # CREATING A GRID OF SUBPLOTS FOR THE GRAPHS TO BE DISPLAYED
        ax1 = figPR.add_subplot(2, 2, 1)  #CREATING THE SUBPLOT FOR THE TOP LEFT GRAPH
        ax2 = figPR.add_subplot(2, 2, 2)  #CREATING THE SUBPLOT FOR THE TOP RIGHT GRAPH
        ax3 = figPR.add_subplot(2, 2, 3)  #CREATING THE SUBPLOT FOR THE BOTTOM LEFT GRAPH
        ax4 = figPR.add_subplot(2, 2, 4)  #CREATING THE SUBPLOT FOR THE BOTTOM RIGHT GRAPH

                # GRAPH PLOT 4
        non_zero_mask1 = (points_df['power'] != 0) & (points_df['cadence'] != 0)                #CREATING A ZERO MASK THAT WILL TAKE OUT AN ZERO VALUES THAT ARE NOT MEAN TO BE IN THE DATA
        x1 = points_df.loc[non_zero_mask1, 'power']                                             #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE X AXIS
        y1 = points_df.loc[non_zero_mask1, 'cadence']                                           #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE Y AXIS
        degree = 3                                                                              #SETTING THE POLYNOMIAL REGRESSION DEGREE OF 3
        coeffs = np.polyfit(x1, y1, deg=degree)                                                 #PERFORMING THE POLYNOMIAL REGRESSION OF THE CHOSEN DEGREE
        polynomial = np.poly1d(coeffs)                                                          #CREATING THE POLYNOMIAL MODEL USING THE DEGREES VALUE AND PERFORMANCE METRIC VALUES 
        x_fit = np.linspace(min(x1), max(x1), 100)                                              #FITTING THE POLYNOMIAL REGRESSION MODEL TO THE X AXIS WITH MIN AND MAX BOUNDS
        y_fit = polynomial(x_fit)                                                               #FITTING THE POLYNOMIAL REGRESSION MODEL TO THE Y AXIS
        ax1.scatter(x1, y1, label='Data', color='grey', s=0.5)                                  #PLOTTING THE PERFORMANCE METRICS DATA ALONG WITH ITS COLOUR PROFILE
        ax1.plot(x_fit, y_fit, color='black', label=f'Polynomial Regression (Degree {degree})') #PLOTTING THE POLYNOMIAL REGRESSION LINE ON THE PLOT OVER THE PERFORMANCE METRIC
        ax1.set_title(f'Polynomial Regression: Cadence vs. Power (Degree {degree})')            #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED

        # GRAPH PLOT 2 - HEART RATE AND ALTITUDE
        non_zero_mask2 = (points_df['power'] != 0) & (points_df['heart_rate'] != 0)             #CREATING A ZERO MASK THAT WILL TAKE OUT AN ZERO VALUES THAT ARE NOT MEAN TO BE IN THE DATA
        x2 = points_df.loc[non_zero_mask2, 'power']                                             #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE X AXIS
        y2 = points_df.loc[non_zero_mask2, 'heart_rate']                                        #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE Y AXIS
        degree = 4                                                                              #SETTING THE POLYNOMIAL REGRESSION DEGREE OF 4
        coeffs = np.polyfit(x2, y2, deg=degree)                                                 #PERFORMING THE POLYNOMIAL REGRESSION OF THE CHOSEN DEGREE
        polynomial = np.poly1d(coeffs)                                                          #CREATING THE POLYNOMIAL MODEL USING THE DEGREES VALUE AND PERFORMANCE METRIC VALUES 
        x_fit = np.linspace(min(x2), max(x2), 100)                                              #FITTING THE POLYNOMIAL REGRESSION MODEL TO THE X AXIS WITH MIN AND MAX BOUNDS
        y_fit = polynomial(x_fit)                                                               #FITTING THE POLYNOMIAL REGRESSION MODEL TO THE Y AXIS
        ax2.scatter(x2, y2, label='Data', color='red', s=0.5)                                   #PLOTTING THE PERFORMANCE METRICS DATA ALONG WITH ITS COLOUR PROFILE
        ax2.plot(x_fit, y_fit, color='black', label=f'Polynomial Regression (Degree {degree})') #PLOTTING THE POLYNOMIAL REGRESSION LINE ON THE PLOT OVER THE PERFORMANCE METRIC
        ax2.set_title(f'Polynomial Regression: Heart Rate vs. Power (Degree {degree})')         #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED

        # GRAPH PLOT 3 - SPEED AND ALTITUDE
        non_zero_mask3 = (points_df['power'] != 0) & (points_df['speed'] != 0)                  #CREATING A ZERO MASK THAT WILL TAKE OUT AN ZERO VALUES THAT ARE NOT MEAN TO BE IN THE DATA
        x3 = points_df.loc[non_zero_mask3, 'power']                                             #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE X AXIS
        y3 = points_df.loc[non_zero_mask3, 'speed']                                             #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE Y AXIS
        degree = 4                                                                              #SETTING THE POLYNOMIAL REGRESSION DEGREE OF 4
        coeffs = np.polyfit(x3, y3, deg=degree)                                                 #PERFORMING THE POLYNOMIAL REGRESSION OF THE CHOSEN DEGREE
        polynomial = np.poly1d(coeffs)                                                          #CREATING THE POLYNOMIAL MODEL USING THE DEGREES VALUE AND PERFORMANCE METRIC VALUES 
        x_fit = np.linspace(min(x3), max(x3), 100)                                              #FITTING THE POLYNOMIAL REGRESSION MODEL TO THE X AXIS WITH MIN AND MAX BOUNDS
        y_fit = polynomial(x_fit)                                                               #FITTING THE POLYNOMIAL REGRESSION MODEL TO THE Y AXIS
        ax3.scatter(x3, y3, label='Data', color='lightblue', s=0.5)                             #PLOTTING THE PERFORMANCE METRICS DATA ALONG WITH ITS COLOUR PROFILE
        ax3.plot(x_fit, y_fit, color='black', label=f'Polynomial Regression (Degree {degree})') #PLOTTING THE POLYNOMIAL REGRESSION LINE ON THE PLOT OVER THE PERFORMANCE METRIC
        ax3.set_title(f'Polynomial Regression: Speed vs. Power (Degree {degree})')              #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED

        # GRAPH PLOT 4
        non_zero_mask4 = (points_df['power'] != 0) & (points_df['altitude'] != 0)               #CREATING A ZERO MASK THAT WILL TAKE OUT AN ZERO VALUES THAT ARE NOT MEAN TO BE IN THE DATA
        x4 = points_df.loc[non_zero_mask4, 'power']                                             #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE X AXIS
        y4 = points_df.loc[non_zero_mask4, 'altitude']                                          #APPLYING THE ZERO MASK TO THE PERFORMANCE METRIC ON THE Y AXIS
        degree = 3                                                                              #SETTING THE POLYNOMIAL REGRESSION DEGREE OF 3
        coeffs = np.polyfit(x4, y4, deg=degree)                                                 #PERFORMING THE POLYNOMIAL REGRESSION OF THE CHOSEN DEGREE
        polynomial = np.poly1d(coeffs)                                                          #CREATING THE POLYNOMIAL MODEL USING THE DEGREES VALUE AND PERFORMANCE METRIC VALUES 
        x_fit = np.linspace(min(x4), max(x4), 100)                                              #FITTING THE POLYNOMIAL REGRESSION MODEL TO THE X AXIS WITH MIN AND MAX BOUNDS
        y_fit = polynomial(x_fit)                                                               #FITTING THE POLYNOMIAL REGRESSION MODEL TO THE Y AXIS
        ax4.scatter(x4, y4, label='Data', color='green', s=0.5)                                 #PLOTTING THE PERFORMANCE METRICS DATA ALONG WITH ITS COLOUR PROFILE
        ax4.plot(x_fit, y_fit, color='black', label=f'Polynomial Regression (Degree {degree})') #PLOTTING THE POLYNOMIAL REGRESSION LINE ON THE PLOT OVER THE PERFORMANCE METRIC
        ax4.set_title(f'Polynomial Regression: Altitude vs. Power (Degree {degree})')           #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED

        ActivityGraphsPR = FigureCanvasTkAgg(figPR, master=PolynomialRegressionGraphs)          #CREATING A 'FigureCanvasTkAgg' OBJECT TO DISPLAY THE FIGURE WITH THE SUBPLOTS WITHIN THE 'ActivityGraphsPR' FRAME
        ActivityGraphsPR.draw()                                                                 #DISPLAYING THE SUBPLOTS TO THE USER
        ActivityGraphsPR.get_tk_widget().configure(width=1600, height=600)                      #SETTING THE SIZE OF THE CANVAS WIDGET
        ActivityGraphsPR.get_tk_widget().grid(row=5, column=0, sticky="w")                      #DISPLAYING THE CANVAS WIDGET WITHIN THE 'PolynomialRegressionGraphs' FRAME

    ActivityPolynomialRegressionGraphsPWR()
    folder_path = 'C:/Users/natda/OneDrive/University/MSc Computer Science/Thesis/GAA/GAA Software/Activities'+'/'+str(name) #DEFINIG THE USERS PATHWAY FOLDER
    filenames = get_filenames_in_folder(folder_path)                                                            #GATHERING THE FILENAMES FROM THE FOLDER DEFINED ABOVE

    dropdown_var = tk.StringVar()                                                                 #CREATINGI A TKINTER STRING VARIABLE TO STORE ALL OF THE FILE NAMES
    dropdownAct = ttk.Combobox(controls_framePRG, textvariable=dropdown_var, values=filenames)    #DISPLAYING THE FILENAMES WITHIN THE DROPDOWN BOX
    dropdownAct.set("Select a File...")                                                           #CREATING A PLACE HOLDER THAT IS DISPLAYED UNTIL THE USER INTERACTS WITH THE DROPDOWN
    dropdownAct.grid(row=3, column=0)                                                             #DISPLAYING THE DROPDOWN BOX TO THE USER 

    dropdownAct.bind("<<ComboboxSelected>>", on_dropdown_select)                                  #BINDING AN EVENT HANDER TO THE DROPDOWN BOX ALSO ACTS AS A DEBUGGER
   
    dropdown4 = ttk.Combobox(controls_framePRG, values=["Polynomial Regression - Power",          #CREATING A DROPDOWN BOX THAT WILL STORE THE 3 DIFFERENT GRAPH VISUALS
                                                        "Polynomial Regression - Speed",
                                                        "Polynomial Regression - Altitude",
                                                        "Polynomial Regression - Heart Rate"])
    dropdown4.set("Select a Graph Style...")                                                      #DISPLAYING A MESSAGE EXPLAINING TO THE USER WHAT THE DROPDOWN BOX DOES
    dropdown4.grid(row=3, column=1,sticky="w")                                                    #DISPLAYING THE DROPDOWN BOX FOR THE USER TO INTERACT WITH
    
    def SelectPolynomialRegressionGraphStyle():
        selected_style = dropdown4.get()                              #GATHERING THE USER'S SELECTION FROM THE DROPDOWN BOX 
        if selected_style == "Polynomial Regression - Power":         #IF THE IF STATEMENT CONDITIONS ARE MET THE FOLLOWING TAKES PLACE:
            ActivityPolynomialRegressionGraphsPWR()                   #EXECUTING THE 'ActivityLinearRegressionGraphsPWR' FUNCTION
        elif selected_style == "Polynomial Regression - Altitude":    #IF THE IF STATEMENT CONDITIONS ARE MET THE FOLLOWING TAKES PLACE:
            ActivityPolynomialRegressionGraphsALT()                   #EXECUTING THE 'ActivityLinearRegressionGraphsALT' FUNCTION
        elif selected_style == "Polynomial Regression - Speed":       #IF THE IF STATEMENT CONDITIONS ARE MET THE FOLLOWING TAKES PLACE: 
            ActivityPolynomialRegressionGraphsSPD()                   #EXECUTING THE 'ActivityLinearRegressionGraphsHR' FUNCTION
        elif selected_style == "Polynomial Regression - Heart Rate":  #IF THE IF STATEMENT CONDITIONS ARE MET THE FOLLOWING TAKES PLACE: 
            ActivityPolynomialRegressionGraphsHR()                    #EXECUTING THE 'ActivityLinearRegressionGraphsHR' FUNCTION

    button1 = ttk.Button(controls_framePRG, text="Select")            #CREATING THE BUTTON THAT WILL USER WILL INTERACT WITH
    button1.configure(command=SelectActivity)                         #BINDING THE 'SelectActivity' FUNCTION WITH THE BUTTON
    button1.grid(row=3, column=1)                                     #DISPLAYING THE BUTTON TO THE USER 
    button4 = ttk.Button(controls_framePRG, text="Select")            #CREATING THE BUTTON THAT WILL USER WILL INTERACT WITH
    button4.configure(command=SelectPolynomialRegressionGraphStyle)   #BINDING THE 'SelectLinearRegressionGraphStyle' FUNCTION WITH THE BUTTON
    button4.grid(row=3, column=2,sticky="e")                          #DISPLAYING THE BUTTON TO THE USER   

############################################################################################################################################################################################################################################
#  BOX PLOTS  #  BOX PLOTS  #  BOX PLOTS  #  BOX PLOTS  #  BOX PLOTS  #  BOX PLOTS  #  BOX PLOTS  #  BOX PLOTS  #  BOX PLOTS  #  BOX PLOTS  #  BOX PLOTS  #  BOX PLOTS  #  BOX PLOTS  #  BOX PLOTS  #  BOX PLOTS  #  BOX PLOTS # BOX PLOTS #
############################################################################################################################################################################################################################################

    ActivityBoxPlots = ttk.Frame(style="W.TFrame")                  #CREATING THE 'ActivityBoxPlots' FRAME THAT WILL HOUSE THE COMBINED GRAPHS FOR THE USER TO SEE

    controls_frameBP = ttk.Frame(ActivityBoxPlots,style="W.TFrame") #CREATING A 'controls_frameAGC' THAT WILL HOUSE THE TITLE AND INFOMATION OF THE PAGE - THIS MEANS WHEN THE GRAPHS ARE UPDATED THESE STAY VISIBLE
    controls_frameBP.grid(row=4, column=0)                          #DISPLAY THE 'controls_frameAGC' TO THE USER

    s1 = Label(controls_frameBP, text=" ", bg="white")                                                              #CREATING AN EMPTY LABEL THAT WILL ACT AS A ONE LINE SPACE
    s1.grid(row=0, column=0)                                                                                        #DISPLAYING THE ONE LINE SPACE
    l1 = Label(controls_frameBP, text="Activity Analyser - Box Plots Graphs", font='Helvetica 12 bold', bg="white") #CREATING THE MAIN HEADING FOR THE TAB THAT WILL BE DISPLAYED AT THE TOP OF THE FRAME
    l1.grid(row=1)                                                                                                  #DISPLAYING THE TITLE
    l2 = Label(controls_frameBP, text="Plots Produced From: " + str(Activity), font='Helvetica 9', bg="white")      #CREATING THE SUBTITLE FOR THE TAB THAT STATES THE FILE BEING USED 
    l2.grid(row=2, column=0)                                                                                        #DISPLAYING THE SUBTITLE

    def ClearActivityBoxPlotsFrame():
        for widget in ActivityBoxPlots.winfo_children():  #FOR THE WIDGET OBJECT WITHIN THE 'ActivityBoxPlots' THE FOLLOWING TOOK PLACE
            if widget != controls_frameBP:                #IF THE WIDGET OBJECT WAS NOT IN THE 'controls_frameBP' THE FOLLOWING TOOK PLACE  
                widget.destroy()                          #THE WIDGET OBJECT IS DESTROYED ALLOWING FOR THE NEW GRAPHS TO BE DISPLAYED

    def ActivityBoxPlotsCLN():
        ClearActivityBoxPlotsFrame()        #CALLING THE 'ClearActivityBoxPlotsFrame' FUNCTION TO CLEAR ANY PREVIOUS SUBPLOTS

        #CREATING A FIGURE THAT WILL HOUSE THE GRID OF SUBPLOTS (2 ROWS, 2 COLUMNS)
        figBP = plt.figure(figsize=(14, 10))
        plt.subplots_adjust(hspace=0.5)

        #CREATING A GRID OF SUBPLOTS FOR THE GRAPHS TO BE DISPLAYED
        ax1 = figBP.add_subplot(3, 1, 1)    #CREATING THE SUBPLOT FOR THE TOP LEFT GRAPH
        ax2 = figBP.add_subplot(3, 1, 2)    #CREATING THE SUBPLOT FOR THE TOP RIGHT GRAPH
        ax3 = figBP.add_subplot(3, 1, 3)    #CREATING THE SUBPLOT FOR THE BOTTOM LEFT GRAPH

        #GRAPH PLOT 1 - POWER
        ax1.boxplot(points_df['power'], vert=False)                             #CREATING THE POWER BOXPLOT 
        ax1.set_title('Power (Watts)')                                          #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED
        
        #GRAPH PLOT 2 - HEARTRATE  
        ax2.boxplot(points_df['heart_rate'], vert=False)                        #CREATING THE HEARTRATE BOX PLOT 
        ax2.set_title('Heart Rate (BPM)')                                       #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED
        
        #GRAPH PLOT 3 - SPEED
        ax3.boxplot(points_df['speed'], vert=False)                             #CREATING THE SPEED BOX PLOT  
        ax3.set_title('Speed (MPH)')                                            #SETTING THE TITLE OF THE PLOT TO REPRESENT THE DATA THAT IS DISPLAYED
                                                                  
        ActivityGraphsBP = FigureCanvasTkAgg(figBP, master=ActivityBoxPlots)    #CREATING A 'FigureCanvasTkAgg' OBJECT TO DISPLAY THE FIGURE WITH THE SUBPLOTS WITHIN THE 'ActivityBoxPlots' FRAME
        ActivityGraphsBP.draw()                                                 #DISPLAYING THE SUBPLOTS TO THE USER
        ActivityGraphsBP.get_tk_widget().configure(width=1600, height=600)      #SETTING THE SIZE OF THE CANVAS WIDGET
        ActivityGraphsBP.get_tk_widget().grid(row=5, column=0,sticky="w")       #DISPLAYING THE CANVAS WIDGET WITHIN THE 'ActivityBoxPlots' FRAME

    ActivityBoxPlotsCLN()

############################################################################################################################################################################################################################################
#   STATISTICS   #   STATISTICS   #   STATISTICS   #   STATISTICS   #   STATISTICS   #   STATISTICS   #   STATISTICS   #   STATISTICS   #   STATISTICS   #   STATISTICS   #   STATISTICS   #   STATISTICS   #  STATISTICS   # STATISTICS   #
############################################################################################################################################################################################################################################


    ActivityStats = ttk.Frame(style="W.TFrame")                     #CREATING THE 'ActivityBoxPlots' FRAME THAT WILL HOUSE THE COMBINED GRAPHS FOR THE USER TO SEE

    controls_frameST = ttk.Frame(ActivityStats,style="W.TFrame")    #CREATING A 'controls_frameAGC' THAT WILL HOUSE THE TITLE AND INFOMATION OF THE PAGE - THIS MEANS WHEN THE GRAPHS ARE UPDATED THESE STAY VISIBLE
    controls_frameST.grid(row=4, column=0)                          #DISPLAY THE 'controls_frameAGC' TO THE USER

    s1 = Label(controls_frameST, text=" ", bg="white")                                                              #CREATING AN EMPTY LABEL THAT WILL ACT AS A ONE LINE SPACE
    s1.grid(row=0, column=0)                                                                                        #DISPLAYING THE ONE LINE SPACE
    l1 = Label(controls_frameST, text="Activity Analyser - Statistics", font='Helvetica 12 bold', bg="white")       #CREATING THE MAIN HEADING FOR THE TAB THAT WILL BE DISPLAYED AT THE TOP OF THE FRAME
    l1.grid(row=1)                                                                                                  #DISPLAYING THE TITLE
    l2 = Label(controls_frameST, text="Statistics Produced From: " + str(Activity), font='Helvetica 9', bg="white") #CREATING THE SUBTITLE FOR THE TAB THAT STATES THE FILE BEING USED 
    l2.grid(row=2, column=0)                                                                                        #DISPLAYING THE SUBTITLE

    def ClearActivityStatsFrame():
        for widget in ActivityStats.winfo_children():  #FOR THE WIDGET OBJECT WITHIN THE 'ActivityStats' THE FOLLOWING TOOK PLACE
            if widget != controls_frameST:             #IF THE WIDGET OBJECT WAS NOT IN THE 'controls_frameST' THE FOLLOWING TOOK PLACE  
                widget.destroy()                       #THE WIDGET OBJECT IS DESTROYED ALLOWING FOR THE NEW GRAPHS TO BE DISPLAYED
                
    def CalcAge(DoB):
        Now = datetime.today()                                                                #GATHERING THE CURRENT DATE 
        DoBDate = datetime.strptime(DoB,'%d/%m/%Y')                                           #TAKING THE USERS DAT OF BIRTH IN THE dd/mm/YYYY FORMAT
        Age = Now.year - DoBDate.year - ((Now.month, Now.day) < (DoBDate.month, DoBDate.day)) #CALCULATING THE USERS CURRENT AGE BY TAKING AWAY THE CURRENT YEAR FROM BIRTH YEAR
        return int(Age)                                                                       #RETURING THEIR AGE

    def CalcHRZones(Age):
        if Age <= 30:                                                                         #IF THE USERS AGE IS UNDER 30 THEN THE FOLLOWING TAKES PLACE
            Zones = {'Zone 1': (100, 133), 'Zone 2': (134, 152), 'Zone 3': (153, 167),   
                 'Zone 4': (168, 183), 'Zone 5': (184, 220)}                                  #SETTING THEIR HEART RATE ZONES AS THE FOLLOWING BASED UPON THEIR AGE
        else:                                                                                 #IF THEIR AGE IS ABOVE 30 THEN THE FOLLOWING TAKES PLACE
            Zones = {'Zone 1': (80, 113), 'Zone 2': (114, 132), 'Zone 3': (133, 147), 
                 'Zone 4': (148, 163), 'Zone 5': (164, 200)}                                  #SETTING THEIR HEART RATE ZONES AS THE FOLLOWING BASED UPON THEIR AGE
        return Zones                                                                          #RETURING THE HEART RATE ZONES 

    def CalcPerZones(Data, ZoneRange):
        InZone = Data[(Data >= ZoneRange[0]) & (Data <= ZoneRange[1])].count()                #CALCULATING HOW LONG THE USER HAS STAYED IN EACH HEART RATE ZONE
        Total = len(Data)                                                                     #APPENDING THIS TO A VARIABLE
        Percentage = (InZone / Total) * 100                                                   #CALCULATING THE PERCENTAGE OF THE TIME SPENT IN EACH ZONE
        return Percentage                                                                     #RETURING THE PERCENTAGE

    def StatsSubplots(dataframe, ax, title):
        stats = dataframe.describe().apply(lambda x: format(x, '.3f'))                        #USING THE DESCRIBE METHOD TO EXTRACT THE DESCRIPTIVE DATA FROM EACH PERFORMANCE METRIC TO ACT AS THE RAW DATA OUTPUT
        ax.axis('off')                                                                        #MAKING SURE THEIR IS NO X AXIS AS THIS IS NOT NEEDED
        ax.text(0.5, 0.5, f'{title}\n{stats}', ha='center', va='center', fontsize=10)         #SETTING THE SIZE OF THE FONT AND LOCATION OF THE TITLES FOR EACH METRIC

    def ActivityStatsCLN():
        ClearActivityStatsFrame()        #CALLING THE 'ClearActivityStatsFrame' FUNCTION TO CLEAR ANY PREVIOUS SUBPLOTS

        #CREATING THE FIGURE THAT WILL HOLD ALL OF STATS DESCRITIVE PLOTS        
        figST = plt.figure(figsize=(12, 8))                                  
        gs = gridspec.GridSpec(3, 3, figure=figST, hspace=0.5, wspace=0.3)  #CREATING A 3x3 LAYOUT

        ax_power = figST.add_subplot(gs[0, 0])                              #THE POWER PLOT IS IN THE TOP LEFT
        ax_heart_rate = figST.add_subplot(gs[0, 1])                         #THE HEART RATE PLOT IS IN THE TOP RIGHT
        ax_speed = figST.add_subplot(gs[1, 0])                              #THE SPEED PLOT IS IN THE BOTTOM LEFT
        ax_cadence = figST.add_subplot(gs[1, 1])                            #THE CADENCE PLOT IS ON THE BOTTOM RIGHT
        ax_pie = figST.add_subplot(gs[:, 2])                                #THE PIE CHART FOR HEART RATE ZONES IS IN THE RIGHT COLUMN
        
        StatsSubplots(points_df['power'], ax_power, "Power")                #CREATING THE POWER PLOT 
        StatsSubplots(points_df['heart_rate'], ax_heart_rate, "Heart Rate") #CREATING THE HEART RATE PLOT
        StatsSubplots(points_df['speed'], ax_speed, "Speed")                #CREATING THE SPEED PLOT
        StatsSubplots(points_df['cadence'], ax_cadence, "Cadence")          #CREATING THE CADENCE PLOT 

        AltStats = points_df['altitude'].describe().apply(lambda x: format(x, '.3f'))        #CREATING A ALTITUDE PLOT THE WILL BE BELOW THE CADENCE PLOT
        AltText = plt.figtext(0.51, 0.03, f'Altitude\n{AltStats}', ha='center', fontsize=10) #SETTING THE SIZE OF THE FONT AND LOCATION OF THE TITLES FOR THE ALTITUDE METRIC

        for line in open("temp.txt","r").readlines(): #READING EACH LINE WITHIN THE 'temp' FILE AND ASSIGNING THE DATA TO VARIABLES BELOW
            data = line.split()                       #SPLITTING THE TEXT UP INSIDE THE FILE SO THEY CAN BE ACCESSED AND ASSIGNED
            if len(data) > 2:
                UsersAge = data[2]                    #GATHERING THE USERS AGE FROM THE TEMP FILE IF IT EXISTS    

        if UsersAge is not None:                                            #IF THEIR IS NO AGE THE DEFULT HEART RATE ZONES WILL BE USED
            Age = CalcAge(UsersAge)                                         #IF THEIR IS NO AGE THE DEFULT HEART RATE ZONES WILL BE USED
            HRZones = CalcHRZones(Age)                                      #IF THEIR IS NO AGE THE DEFULT HEART RATE ZONES WILL BE USED
            ZoneLabels = list(HRZones.keys())                               #IF THEIR IS NO AGE THE DEFULT HEART RATE ZONES WILL BE USED
            ZonePers = [CalcPerZones(points_df['heart_rate'],
                                     HRZones[Zone]) for Zone in ZoneLabels] #IF THEIR IS NO AGE THE DEFULT HEART RATE ZONES WILL BE USED
        
        pie_ax = ax_pie                                #CREATING THE PIE CHART
        pie_ax.pie(ZonePers, labels=ZoneLabels,
                   autopct='%1.1f%%', startangle=140,
                   colors=plt.cm.Paired.colors)        #GIVING THE PIE CHART DEFAULT COLOURS
        pie_ax.set_title(f"Heart Rate Zones")          #CREATING A TITLE FOR THE PIE CHART
        pie_ax.axis('equal')                           #MAKING SURE THAT EACH LABEL IS AN EQUAL SIZE 

                                                    
        ActivityGraphsST = FigureCanvasTkAgg(figST, master=ActivityStats)  #CREATING A 'FigureCanvasTkAgg' OBJECT TO DISPLAY THE FIGURE WITH THE SUBPLOTS WITHIN THE 'ActivityStats' FRAME
        ActivityGraphsST.draw()                                            #DISPLAYING THE SUBPLOTS TO THE USER
        ActivityGraphsST.get_tk_widget().configure(width=1600, height=600) #SETTING THE SIZE OF THE CANVAS WIDGET
        ActivityGraphsST.get_tk_widget().grid(row=5, column=0,sticky="w")  #DISPLAYING THE CANVAS WIDGET WITHIN THE 'ActivityStats' FRAME

    ActivityStatsCLN()
    
############################################################################################################################################################################################################################################
#       TAB CONTROL SECTION         #        TAB CONTROL SECTION           #         TAB CONTROL SECTION           #         TAB CONTROL SECTION           #         TAB CONTROL SECTION           #         TAB CONTROL SECTION           #       
############################################################################################################################################################################################################################################

    tabControl.add(HOMEPAGETAB, text ='Homepage')              #GIVING THE TAB ITS SPECIFIC NAME 'Homepage'
    tabControl.add(ActivityGraphsCombined,                     #GIVING THE TAB ITS SPECIFIC NAME 'Combined Activity Graphs'                
                   text ='Combined Activity Graphs')
    tabControl.add(LinearRegressionGraphs,                     #GIVING THE TAB ITS SPECIFIC NAME 'Linear Regression Graphs'                
                   text ='Linear Regression Graphs')
    tabControl.add(PolynomialRegressionGraphs,                 #GIVING THE TAB ITS SPECIFIC NAME 'Multiple Regression Graphs'                
                   text ='Polynomial Regression Graphs')
    tabControl.add(ActivityBoxPlots, text='Box Plots')         #GIVING THE TAB ITS SPECIFIC NAME 'Box Plots'
    tabControl.add(ActivityStats, text ='Statistics')          #GIVING THE TAB ITS SPECIFIC NAME 'Statistics'
    tabControl.pack(expand = 1, fill ="both")                  #DISPLAYING THE TABS FOR THE USER TO INTERACT WITH

############################################################################################################################################################################################################################################
#        SIGNUP WINDOW        #        SIGNUP WINDOW        #        SIGNUP WINDOW       #        SIGNUP WINDOW      #        SIGNUP WINDOW      #         SIGNUP WINDOW        #         SIGNUP WINDOW      #        SIGNUP WINDOW        #
############################################################################################################################################################################################################################################

def SignUpApp():

    def SignUp():

        with open("data.txt", "a") as file:     #WITH THE DATA FILE OPEN THE FOLLOWING WILL BE APPEDED TO DATA FILE
            file.write(username.get())          #GETTING THE USERS INPUT OF THEIR USERNAME AND APPEDEDING IT TO THE DATA FILE 
            file.write(" ")                     #WRITING AN EMPTY SPACE BETWEEN THE USERS ENTRIES IN THE DATA FILE
            file.write(password.get())          #GETTING THE USERS INPUT OF THEIR PASSWORD AND APPEDEDING IT TO THE DATA FILE  
            file.write(" ")                     #WRITING AN EMPTY SPACE BETWEEN THE USERS ENTRIES IN THE DATA FILE
            file.write(fname.get())             #GETTING THE USERS INPUT OF THEIR FIRST NAME AND APPEDEDING IT TO THE DATA FILE  
            file.write(" ")                     #WRITING AN EMPTY SPACE BETWEEN THE USERS ENTRIES IN THE DATA FILE
            file.write(sname.get())             #GETTING THE USERS INPUT OF THEIR LAST NAME AND APPEDEDING IT TO THE DATA FILE  
            file.write(" ")                     #WRITING AN EMPTY SPACE BETWEEN THE USERS ENTRIES IN THE DATA FILE
            file.write(dob.get())               #GETTING THE USERS INPUT OF THEIR DOB AND APPEDEDING IT TO THE DATA FILE  
            file.write("\n")                    #WRITING AN EMPTY LINE AFTER THE USERS INPUTS FOR THE NEXT USERS ENTRIES
            file.close()                        #CLOSING THE FILE AFTER ALL OF THE DATA HAS BEEN APPENED TO THE DATA FILE
            
            username_foldername = fname.get()   #GATHERING THE USERS NAME TO CREATE A FOLDER IN THEIR NAME AS A NEW ACCOUNT
            folder_path = os.path.join("C:\\Users\\natda\\OneDrive\\University\\MSc Computer Science\\Thesis\\GAA\\GAA Software\\Activities", username_foldername)
            try:
                os.makedirs(folder_path)                                             #CREATING THE NEW FOLDER FOR THE USER USING THEIR NAME THEY ENTERED
                messagebox.showinfo("information", "Your account has been CREATED!") #DISPLAYING A MESSAGE STATING THAT THEIR ACCOUNT HAS BEEN CREATED
                signupwin.destroy()                                                  #CLOSING THE SIGN UP WINDOW AS THE LOGIN WINDOW OPENS

            except FileExistsError:                                                            #IF THE FOLDER EXISTS THEN A MESSAGE WILL BE DISPLAYED EXPLAINNING THIS
                messagebox.showinfo("   ERROR!   ", "  Account Already Exists!", icon="error") #DISPLAYING THE ERROR MESSAGE BOX THAT THE ACCOUNT ALREADY EXISTS
                signupwin.destroy()                                                            #CLSOING THE SIGN UP WINDOW TO ENTER THE DETAILS AGAIN
                SignUpApp()                                                                    #RELOADING THE SIGNUP WINDOW

    signupwin = Tk()                                       #DEFINING WHAT THE TKINTER WINDOW WILL BE DEFINED AS
    signupwin.resizable(0,0)                               #THE WINDOW WILL NOT ENTER FULLSCREEN MODE
    signupwin.resizable(width=FALSE, height=FALSE)         #THE USER CANNOT CHANGE THE SIZE OF THE LOGIN WINDOW
    signupwin.title ("Garmin Activity Analyser Sign Up")   #GIVING THE SIGNUP WINDOW ITS NAME THAT WILL BE DISPLAYED IN THE BAR
    signupwin.geometry("500x350")                          #CONFIGURING THE FIXED SIZE OF THE SIGNUP WINDOW WHICH WILL ALWAYS BE THIS SIZE            
    signupwin.configure(background='white')                #CONFIGURING THE BACKGROUND OF THE SIGNUP WINDOW TO BE WHITE

    S1 = Label(signupwin, text=" ", background="white")                                                        #CREATING A LABEL THAT WILL ACT AS A ONE LINE SPACE BETWEEN 
    Title = Label (signupwin, text="Garmin Activity Analyser Sign Up", font='Helvetica 16 bold',
                   background="white")                                                                         #CREATING A TITLE FOR THE SIGNUP WINDOW
    S2 = Label(signupwin, text=" ", background="white")                                                        #CREATING A LABEL THAT WILL ACT AS A ONE LINE SPACE BETWEEN 

    FName = Label (signupwin, text="Enter First Name:", font='Helvetica 10', background="white")               #CREATING THE LABEL THAT WILL SAY FIRST NAME ABOVE THE ENTRY BOX
    fname = Entry (signupwin, background="light grey")                                                         #CREATING AN ENTRY BOX WHERE THE USER WILL INPUT THEIR FIRST NAME, IT WILL HAVE A LIGHT GREY BACKGROUND WITHIN THE BOX
    SName = Label (signupwin, text="Enter Last Name:", font='Helvetica 10', background="white")                #CREATING THE LABEL THAT WILL SAY LAST NAME ABOVE THE ENTRY BOX
    sname = Entry (signupwin, background="light grey")                                                         #CREATING AN ENTRY BOX WHERE THE USER WILL INPUT THEIR LAST NAME, IT WILL HAVE A LIGHT GREY BACKGROUND WITHIN THE BOX
    DOB = Label (signupwin, text="Enter Date of Birth:", font='Helvetica 10', background="white")              #CREATING THE LABEL THAT WILL SAY DOB ABOVE THE ENTRY BOX
    dob = Entry (signupwin, background="light grey")                                                           #CREATING AN ENTRY BOX WHERE THE USER WILL INPUT THEIR DOB, IT WILL HAVE A LIGHT GREY BACKGROUND WITHIN THE BOX
    Username = Label (signupwin, text="Create Username (Email):", font='Helvetica 10', background="white")     #CREATING THE LABEL THAT WILL SAY 'Create Username' ABOVE THE ENTRY BOX
    username = Entry (signupwin, background="light grey")                                                      #CREATING AN ENTRY BOX WHERE THE USER WILL INPUT THEIR USERNAME, IT WILL HAVE A LIGHT GREY BACKGROUND WITHIN THE BOX 
    Password = Label (signupwin, text="Create Password:", font='Helvetica 10', background="white")             #CREATING THE LABEL TAHT WILL SAY 'create Password' ABOVE THE ENTRY BOX
    password = Entry (signupwin, background="light grey", show="*")                                            #CREATING AN ENTRY BOX WHERE THE USER WILL INPUT THEIR PASSOWRD, IT WILL HAVE A LIGHT GREY BACKGROUND WITHIN THE BOX 
    
    S3 = Label(signupwin, text=" ", background="white")                                                        #CREATING A LABEL THAT WILL ACT AS A ONE LINE SPACE BETWEEN 

    SignUp = Button (signupwin, text="     SIGN UP     ", fg="red", command=SignUp)                                       #CREATING THE SIGN UP BUTTON THAT WILL BE DISPLAYED

    S1.pack()           #DISPLAYING THE SPACE LABEL
    Title.pack()        #DISPLAYING THE TITLE OF THE WINDOW
    S2.pack()           #DISPLAYING THE SPACE LABEL
    FName.pack()        #DISPLAYING THE FIRST NAME LABEL THAT WILL SIT ABOVE THE ENTRY BOX
    fname.pack()        #DISPLAYING THE ENTRY BOX FOR THE USER TO INPUT THEIR FIRST NAME
    SName.pack()        #DISPLAYING THE LAST NAME LABEL THAT WILL SIT ABOVE THE ENTRY BOX
    sname.pack()        #DISPLAYING THE ENTRY BOX FOR THE USER TO INPUT THEIR LAST NAME
    DOB.pack()          #DISPLAYING THE DOB LABEL THAT WILL SIT ABOVE THE ENTRY BOX
    dob.pack()          #DISPLAYING THE ENTRY BOX FOR THE USER TO INPUT THEIR DOB
    Username.pack()     #DISPLAYING THE USERNAME LABEL THAT WILL SIT ABOVE THE ENTRY BOX
    username.pack()     #DISPLAYING THE ENTRY BOX FOR THE USER TO INPUT THEIR USERNAME
    Password.pack()     #DISPLAYING THE PASSWORD LABEL THAT WILL SIT ABOVE THE ENTRY BOX
    password.pack()     #DISPLAYING THE ENTRY BOX FOR THE USER TO INPUT THEIR PASSWORD
    S3.pack()           #DISPLAYING THE SPACE LABEL
    SignUp.pack()       #DISPLAYING THE SIGN UP BUTTON
    

############################################################################################################################################################################################################################################
#        LOGIN WINDOW         #        LOGIN WINDOW         #        LOGIN WINDOW        #        LOGIN WINDOW         #        LOGIN WINDOW        #        LOGIN WINDOW        #        LOGIN WINDOW        #        LOGIN WINDOW        #
############################################################################################################################################################################################################################################

TRYS = 0           #KEEPING COUNT OF HOW MANY TRYS THE USER HAS HAD WHEN LOGGING IN
trys = 2           #USED TO CREATE A COUNT DOWN OF HOW MANY MORE ATTEMPTS THE USER HAS FOR THE LOG IN 

def donothing():   #CREATING THE FUNCTION THAT WILL LITERALLY DO NOTHING BY THE USE OF THE 'pass' FUNCTION WITHIN PYTHON
    pass           #CALLING THE 'pass' FUNCTION TO DO NOTHING

def Login():
    global TRYS    #IMPORTING THE 'TRYS' ARRAY TO KEEP TRACK OF HOW MANY ATTEMPTS THEY HAVE HAD AT LOGGING IN
    global trys    #IMPORTING THE 'trys' ARRAY TO CREATE A COUNT DOWN OF HOW MANY MORE ATTEMPTS THEY HAVE AT LOGGING IN
    
    uname = username.get()                                                                                       #TAKING THE USER'S INPUT OF THEIR USERNAME FROM THE ENTRY BOX
    pword = password.get()                                                                                       #TAKING THE USER'S INPUT OF THEIR PASSWORD FROM THE ENTRY BOX

    SuccessfulLogin = False
    
    for line in open("data.txt","r").readlines():                                                                #READING EACH LINE WITHIN THE 'data' FILE
        data = line.split()                                                                                      #SPLITTING EACH WORD ON THE SPACE AND STORING THE RESULTS IN A LIST OF TWO STRINGS
        name = data[2]                                                                                           #ASSIGING THE 3RD ELEMENT IN THE FILE TO BE 'name'
        ID = data[0]                                                                                             #ASSIGING THE 1ST ELEMENT IN THE FILE TO BE 'ID'
        age = data[4]

        if uname == data[0] and pword == data[1]:                                                                #IF THE USERNAME AND PASSWORD MATCH THE FOLLOWING TAKES PLACE
            SuccessfulLogin = True
            messagebox.showinfo("welcome", "You Are Logged In!")                                                 #DISPLAYS A MESSAGE TO THE USER STATING THEY HAVE LOGGED IN 
            with open("temp.txt", "w") as file:                                                                  #WITH THE TEMP FILE OPEN THE FOLLOWING WILL BE WRITTEN TO TEMP FILE
                file.write(name)                                                                                 #GETTING THE USERS NAME ASSOCIATED WITH THE ACCOUNT AND WRTITING IT TO THE TEMP FILE
                file.write(" ")                                                                                  #WRITING AN EMPTY SPACE BETWEEN THE USERS ENTRIES IN THE DATA FILE
                file.write(ID)                                                                                   #GETTING THE USERS NAME ASSOCIATED WITH THE ACCOUNT AND WRTITING IT TO THE TEMP FILE
                file.write(" ")                                                                                  #WRITING AN EMPTY SPACE BETWEEN THE USERS ENTRIES IN THE DATA FILE
                file.write(age)                                                                                  #GETTING THE USERS NAME ASSOCIATED WITH THE ACCOUNT AND WRTITING IT TO THE TEMP FILE
                file.close()                                                                                     #CLOSING THE FILE AFTER ALL OF THE DATA HAS BEEN WRITTEN TO THE TEMP FILE                                
            window.destroy()                                                                                     #DESTROYS THE LOGIN WINDOW BEFORE OPENING THE MAIN APPLICATION
            MainMenu()                                                                                           #STARTING THE MAIN BANKING PROGRAM WITH THE USERS CREDENTIALS
            
        elif uname != data[0] or pword != data[1]:                                                               #IF THE USERNAME AND/OR PASSWORD DO NOT MATCH ANY OF THE USERNAME/PASSWORD SET THE FOLLOWING STATEMENTS WILL COME INTO PLAY
            if SuccessfulLogin:
                break
            if trys == 0:                                                                                        #IF THE USER HAS 0 TRYS LEFT THEN THE FOLLOWING WILL TAKE PLACE
                messagebox.showinfo("   ERROR!   ", """  Your username and/or password was incorrect!                                                        
                You have """+str(trys)+str(" attempts left! And Have been LOCKED OUT!") , icon="error")          #DISPLAYING THE ERROR MESSAGE BOX STATING THEY HAVE BEEN LOCKED OUT
                window.destroy()                                                                                 #CLOSING THE LOGIN APPLICATION AFTER THE 'OK' HAS BEEN CLICKED ON THE MESSAGE BOX
                 
            elif trys > 0:                                                                                       #IF THE USER HAS MORE THAN 0 TRYS LEFT THEN THE FOLLOWING ACTIONS TAKE PLACE
                messagebox.showinfo("   ERROR!   ", """  Your username and/or password was incorrect!                                                        
                         You have """+str(trys)+str(" attempts left!") , icon="error")                           #DISPLAYING THE ERROR MESSAGE BOX WITH ATTEMPTS LEFT
                TRYS = TRYS+1                                                                                    #ADDS +1 TO THE 'TRYS' ARRAY TO KEEP COUNT
                trys = trys-1                                                                                    #TAKES -1 AWAY FROM THE 'trys' ARRAY TO DISPLAY REMAINDER OF ATTMEPTS 


def SignUpLoginWin():
    
    SignUpApp()      #STARTING THE SIGN UP APPLICATION FOR THE USER TO SIGN UP IF THEY DO NOT HAVE AN ACCOUNT

window = Tk()                                 #DEFINING WHAT THE TKINTER WINDOW WILL BE DEFINED AS
window.resizable(0,0)                         #THE WINDOW WILL NOT ENTER FULLSCREEN MODE
window.resizable(width=FALSE, height=FALSE)   #THE USER CANNOT CHANGE THE SIZE OF THE LOGIN WINDOW
window.title ("Garmin Activity Analyser")     #GIVING THE LOGIN WINDOW ITS NAME THAT WILL BE DISPLAYED IN THE BAR
window.geometry("500x300")                    #CONFIGURING THE FIXED SIZE OF THE LOGIN WINDOW WHICH WILL ALWAYS BE THIS SIZE            
window.configure(background='white')          #CONFIGURING THE BACKGROUND OF THE LOGIN WINDOW TO BE WHITE

S1 = Label(window, text=" ", background="white")                                                      #CREATING A LABEL THAT WILL ACT AS A ONE LINE SPACE BETWEEN 
Title = Label (window, text="Garmin Activity Analyser", font='Helvetica 14 bold', background="white") #CREATING A TITLE FOR THE LOGIN WINDOW
S2 = Label(window, text=" ", background="white")                                                      #CREATING A LABEL THAT WILL ACT AS A ONE LINE SPACE BETWEEN 

Username = Label (window, text="Username:", font='Helvetica 10', background="white")         #CREATING THE LABEL THAT WILL SAY 'Username' ABOVE THE ENTRY BOX
username = Entry (window, background="light grey")                                           #CREATING AN ENTRY BOX WHERE THE USER WILL INPUT THEIR USERNAME, IT WILL HAVE A LIGHT GREY BACKGROUND WITHIN THE BOX 
Password = Label (window, text="Password:", font='Helvetica 10', background="white")         #CREATING THE LABEL TAHT WILL SAY 'Password' ABOVE THE ENTRY BOX
password = Entry (window, background="light grey", show="*")                                 #CREATING AN ENTRY BOX WHERE THE USER WILL INPUT THEIR PASSOWRD, IT WILL HAVE A LIGHT GREY BACKGROUND WITHIN THE BOX 
S3 = Label(window, text=" ", background="white")                                             #CREATING A LABEL THAT WILL ACT AS A ONE LINE SPACE BETWEEN 

Login = Button (text="      LOGIN      ", fg="green", command=Login)                         #CREATING THE LOGIN BUTTON 

S4 = Label(window, text=" ", background="white")                                                                                   #CREATING A LABEL THAT WILL ACT AS A ONE LINE SPACE BETWEEN 
signup = Label (window, text="No Account? Why Don't You Sign Up Today By Clicking Below!", font='Helvetica 8', background="white") #CREATING A LABEL THAT STATES A USER CAN SIGN UP FOR AN ACCOUNT
SignUp = Button (text="     SIGN UP     ", fg="red", command=SignUpLoginWin)                                                       #CREATING THE SIGN UP BUTTON 

S1.pack()          #DISPLAYING THE SPACE LABEL
Title.pack()       #DISPLAYING THE TITLE OF THE WINDOW
S2.pack()          #DISPLAYING THE SPACE LABEL
Username.pack()    #DISPLAYING THE USERNAME LABEL THAT WILL SIT ABOVE THE ENTRY BOX
username.pack()    #DISPLAYING THE ENTRY BOX FOR THE USER TO INPUT THEIR USERNAME
Password.pack()    #DISPLAYING THE PASSWORD LABEL THAT WILL SIT ABOVE THE ENTRY BOX
password.pack()    #DISPLAYING THE ENTRY BOX FOR THE USER TO INPUT THEIR PASSWORD
S3.pack()          #DISPLAYING THE SPACE LABEL
Login.pack()       #DISPLAYING THE LOGIN BUTTON 
S4.pack()          #DISPLAYING THE SPACE LABEL
signup.pack()      #DISPLAYING THE SIGN UP MESSAGE
SignUp.pack()      #DISPLAYING THE SIGN UP BUTTON



#NATHAN JONES
#JUN-SEPT 2023
#MSc THESIS
#REAL-WORLD VISUAL DATA ANALYSIS OF GARMIN FIT FILES 
