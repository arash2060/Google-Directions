print('Loading ...')
import logging
from googlemaps import Client
from numpy import number, issubdtype
from os import path, remove
from configparser import RawConfigParser
from tkinter import *
from tkinter import messagebox
import random
waitlist = ['Wanna go get some press covfefe... and come back? Just kidding!',
            'This will be ready soon! No need for another Snapchat...',
            'Good things happen after you wait a gazillion years, OR you make them happen!',
            'A few more seconds... ...']
print(random.choice(waitlist))
from tkinter.ttk import *
from pandas import ExcelFile, ExcelWriter, merge, to_numeric
#import pandas as pd
from datetime import datetime
import time
import sys
from pandas.io.json import json_normalize
import tkcalendar
import tkinter.simpledialog as tkSimpleDialog
import json




class Logger(object):
    def __init__(self, filename="Default.log"):
        self.terminal = sys.stdout
        self.log = open(filename, "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

sys.stderr = Logger("errors.log")
sys.stdout = Logger("output.log")

logging.basicConfig(filename='./Address_Check.log', level=logging.DEBUG)


print('Almost ready!')
# Logging includes private information to the log i.e. Google API Key and
# the addresses searched. You should add ./Address_Check.log to .gitignore


fields = ['Google API Key', 'Input File']
combos = ['Business Name:', 'Legal Name:', 'Street Address:', 'Street Number:',
          'Street Name:', 'City/Borough:', 'Zipcode:', 'Boro Code:', 'State:', 'Latitude:', 'Longitude:']

def fetch(entries):
    for entry in entries:
        field = entry[0]
        text = entry[1].get()
        print('%s: "%s"' % (field, text))


def makeform(root, fields):
    entries = []
    for field in fields:
        row = Frame(root)
        lab = Label(row, width=20, text=field, anchor='w')
        ent = Entry(row, width=60)
        if field != fields[-1]:
            row.pack(side=TOP, fill=X, padx=5, pady=5)
        lab.pack(side=LEFT, padx=5, pady=5)
        ent.pack(side=LEFT, expand=YES, fill=X)
        entries.append((field, ent))
    return entries, row


def makecomboboxes(root, combos):
    comboboxes = []
    row = Frame(root)
    row.pack(side=TOP, fill=X, padx=5, pady=5)
    lab = Label(row, width=15, text='', anchor='w')
    lab1 = Label(row, width=20, text='From:', anchor='w')
    lab2 = Label(row, width=20, text='To:', anchor='w')
    lab.pack(side=LEFT, padx=15, pady=5)
    lab1.pack(side=LEFT, padx=10, expand=YES, fill=X)
    lab2.pack(side=LEFT, padx=10, expand=YES, fill=X)

    for combo in combos:
        row = Frame(root)
        lab = Label(row, width=15, text=combo, anchor='w')
        ent0 = Combobox(row, width=20, state='disabled')
        ent1 = Combobox(row, width=20, state='disabled')
        row.pack(side=TOP, fill=X, padx=5, pady=5)
        lab.pack(side=LEFT, padx=15, pady=5)
        ent0.pack(side=LEFT, padx=10, expand=YES, fill=X)
        ent1.pack(side=LEFT, padx=10, expand=YES, fill=X)
        comboboxes.append((combo, ent0, ent1))
    return comboboxes, row


def set_text(text):
    ents[1][1].delete(0, END)
    ents[1][1].insert(0, text)
    return


def keyfunction(x):
    '''
        used to sort mixed list of column names
    '''
    v = x
    if isinstance(v, int):
        v = '0%d' % v
    return v


class CalendarDialog(tkSimpleDialog.Dialog):
    """Dialog box that displays a calendar and returns the selected date"""
    def body(self, master):
        self.calendar = tkcalendar.Calendar(master)
        self.calendar.pack()

    def apply(self):
        self.result = self.calendar.selection_get()

def get_date():
        cd = CalendarDialog(root)
        print(cd.result, datetime.now().time().strftime("%H:%M"))
        dep_time['state'] = 'enabled'
        dep_time.delete(0, END)
        dt = "%s %s" % (cd.result, datetime.now().time().strftime("%H:%M"))
        dep_time.insert(0, dt)


def choose_default(i, j, collist, field):
    '''
        If default fields exist on the excel sheet,
        automatically choose them in the combobox values
    '''
    if field in ['streetnumber', 'streetname'] and 'originaladdress' in collist:
        combs[i][j].current(0)
    elif field in sorted(collist, key=keyfunction):
        location = [i for i,x in enumerate(sorted(collist, key=keyfunction)) if x == field][0]
        combs[i][j].current(location)
    else:
        combs[i][j].current(0)


def browsexlsx():
    from tkinter.filedialog import askopenfilename
    from os import path

    root1 = Tk()
    root1.withdraw()
    # possible other option: multifile=1
    # '.xls*' doesn't work on Mac.
    filenames = askopenfilename(parent=root, filetypes=[('Excel files', ['.xlsx','.xls']), ('All files', '.*')],
                                initialdir=path.dirname(r"Z:\EAD\DOL Data\QCEW to RPAD address merge\forgbat"))
    # response = root1.tk.splitlist(filenames)
    # for f in response:
    #     print(f)
    print(filenames)
    set_text(filenames)


def loadxlsx():
    '''
    Get the sheet names in the chosen excel file.
    '''
    filename = ents[1][1].get()
    if (filename.endswith(".xlsx") or filename.endswith(".xls")):
        # Read in the Load The Sheets.
        print("Processing: %s" % filename.encode().decode())
        f = path.basename(filename)
        status.set("Status: loading sheets of %s" % f.encode().decode())
        adds = ExcelFile(filename)
        print("This Excel file includes these sheets: %s" % adds.sheet_names)
        sheet_combo['state'] = 'enabled'
        frow['state'] = 'enabled'
        b3['state'] = 'enabled'
        output['state'] = 'enabled'
        sheet_combo['values'] = adds.sheet_names
        output.delete(0, END)
        output.insert(0, filename.replace(".xls", "_out.xls"))
        sheet_combo.current(0)
        status.set("Status: Choose which sheet of %s to process and press 'Load Fields'" % f.encode().decode())
    else:
        messagebox.showinfo(title="Not Excel File", message="Enter and Excel File")


def loadfields():
    '''
    Get the variable names in the chosen excel sheet
    '''

    filename = ents[1][1].get()
    f = path.basename(filename)
    status.set("Status: loading data and column names of %s" % f.encode().decode())
    adds = ExcelFile(filename)
    sheet = sheet_combo.get()
#   if first row is not entered, assume 1 and set the form to 1.
    if frow.get() == "":
        frow.insert(0, 1)
        first_row = 1
    else:
        first_row = int(frow.get())
    print("%s and %s onwards chosen." % (sheet, first_row))
    df = adds.parse(sheet, skiprows=first_row - 1)
    #print(df.columns.values)
    print("There are %s observations on this file." % len(df.index))
    ['Business Name:', 'Street Number:',
     'Street Name:', 'City/Borough:', 'Zipcode:', 'Boro Code:']
    defaults = {0: 'trade',
                1: 'legal',
                2: 'originaladdress',
                3: 'streetnumber',
                4: 'streetname',
                5: 'Borough',
                6: 'pzip',
                7: 'boro',
                8: 'state',
                9: '',
                10: ''}
    for i in range(len(combos)):
        collist = list(df.columns.values)
        collist.append("")
        combs[i][1]['state'] = 'enabled'
        combs[i][2]['state'] = 'enabled'
        combs[i][1]['values'] = sorted(collist, key=keyfunction)
        combs[i][2]['values'] = sorted(collist, key=keyfunction)
        choose_default(i, 1, collist, defaults[i])
        choose_default(i, 2, collist, defaults[i])
    chk['state'] = 'enabled'
    b4['state'] = 'enabled'
#    print(combs[0][0], df[combs[0][1].get()].head(10))
    status.set("Status: Choose address fields, optionally edit output file, and press 'Geocode'")
    global DFrame
    DFrame = df
    return df





def Geocode(df, combs):
    '''
        Description: Geocodes the records that were not found in
        GBAT using Google API.
        By default all the years are in the exclude list so that 
        we don't redo any years and don't pay Google twice.
    '''

    # Get the date and time for directions from the form.
    dt_formatted = datetime.strptime(dep_time.get().strip(), '%Y-%m-%d %H:%M')
 

    status.set("Status: began retreiving direction data.")
    google_api_key2 = ents[0][1].get()

    try:
        gmaps = Client(key=google_api_key2)
    except:
        try:
            config = RawConfigParser()
            config.read('./API_Keys.cfg')
            google_api_key = config.get('Google', 'QCEW_API_Key')
            gmaps = Client(key=google_api_key)
        except:
            messagebox.showinfo("Can't Connect to Google", "Oups! Please check \
that your API key is valid, doesn't have leading/trailing spaces, and you are \
connected to internet! \nYour API key looks like vNIXE0xscrmjlyV-12Nj_BvUPaw")
            return None

    # test
    try:
        transit_result = gmaps.directions("Indepenent Buget Office, New York, NY 10003",
                                     "309 W 84 st, new york, ny",
                                     mode='driving',
                                     departure_time=datetime.now())
        # print(geocode_result[0]['geometry']['location']['lat'],
        #      geocode_result[0]['geometry']['location']['lng'])
        print("Google Connection Test Completed successfully.")
    except:
        print("Google Connection Test Failed.")
    # print(geocode_result)
    # print("DFrame\n\n", df.head())
    # Dictionary of boros to be used in for Addresses.
    Boros = {1: 'Manhattan', 2: 'Bronx', 3: 'Brooklyn',
             4: 'Queens', 5: 'Staten Island', 9: 'New York'}

    df.fillna('')
    # trade2 is trade name when available, and legal name when not.
    for i in range(1,3):
        if combs[9][i].get() == "" and combs[10][i].get() =="":
            df['trade2%s' % i] = ""
            #   trade
            if combs[0][i].get() != "":
                df.loc[df[combs[0][1].get()].fillna('') != '', 'trade2%s' % i] = df[combs[0][i].get()]
                #   legal
                if combs[1][i].get() != "":
                    df.loc[df[combs[0][i].get()].fillna('') == '', 'trade2%s' % i] = df[combs[1][i].get()]
                else:
                    df.loc[df[combs[0][i].get()].fillna('') == '', 'trade2%s' % i] = ""
            else:
                df['trade2%s' % i] = ""

            # Handle missing fields.
            if combs[2][i].get() == '' and (combs[3][i].get() == '' or combs[4][i].get() == ''):
                messagebox.showinfo("No Address!", "Either 'Street Address' or ''Street Number' and 'Street Name'' are required.")
                return None
            elif combs[3][i].get() != '' or combs[4][i].get() != '':
                df['Generated_streetaddress%s' % i] = df[combs[3][i].get()] + " " + df[combs[4][i].get()]
            else:
                df['Generated_streetaddress%s' % i] = df[combs[2][i].get()]

            if combs[7][i].get() == '':
                if combs[5][i].get() == '':
                    df['no_boro%s' % i] = 1
                    vals = combs[7][i]['values'] + ('no_boro%s' % i,)
                    combs[7][i]['values'] = sorted(vals, key=keyfunction)
                    choose_default(7, i, vals, 'no_boro%s' % i)
                    df['no_city%s' % i] = 'New York'
                else:
                    df['no_city%s' % i] = df[combs[5][i].get()]
                    df['no_boro%s' % i] = ''
            else:
                try:
                    to_numeric(df[combs[7][i].get()], errors='raise')
                except:
                    messagebox.showinfo("Error: Non-numeric Boro Codes!", "Boro code is needs to be a number\
between 1 and 5. Either choose a different field or no field at all. \n\nChoosing no field will \
result in 'New York City' assumed for all addresses.")
                    return None
                df['no_boro%s' % i] = df[combs[7][i].get()]
                df['no_city%s' % i] = df['no_boro%s' % i].map(Boros)

            if combs[6][i].get() == '':
                df['no_zip%s' % i] = ''
                vals = combs[7][i]['values'] + ('no_zip%s' % i,)
                combs[6][i]['values'] = sorted(vals, key=keyfunction)
                choose_default(6, i, vals, 'no_zip%s' % i)
            else:
                if issubdtype(df[combs[6][i].get()].dtype, number):
                    df['no_zip%s' % i] = df[combs[6][i].get()].round(0)
                else:
                    df['no_zip%s' % i] = df[combs[6][i].get()]

            if combs[8][i].get() == '':
                df['no_state%s' % i] = 'NY'
                vals = combs[7][i]['values'] + ('no_state%s' % i,)
                combs[6][i]['values'] = sorted(vals, key=keyfunction)
                choose_default(6, i, vals, 'no_state%s' % i)
            else:
                df['no_state%s' % i] = df[combs[8][i].get()]

            # trade(or legal) name + Original Address + City, State, Zip
            df['temp_add%s' % i] = ""
            #   originaladdress field
            df['Generated_streetaddress%s' % i] = df['Generated_streetaddress%s' % i].replace('*** NEED PHYSICAL ADDRESS ***', '')
            df.loc[df['Generated_streetaddress%s' % i].fillna('') != '',
                   'temp_add%s' % i] = df['Generated_streetaddress%s' % i].fillna('') + ', '
            # the last bit maps boro code to borough name
            df['NameAddress%s' % i] = (df['trade2%s' % i].fillna('') + ', ' +
                                 df['temp_add%s' % i] + df['no_city%s' % i] +
                                 ', ' + df['no_state%s' % i] + ' ' + df['no_zip%s' % i].apply(str))
            df['Address%s' % i] = (df['temp_add%s' % i] + df['no_city%s' % i] +
                             ', ' + df['no_state%s' % i] + ' ' + df['no_zip%s' % i].apply(str))
            df['NameAddress%s' % i].head()
            print(df.head())

            # drop some temp fields.
            df.drop(['temp_add%s' % i, 'no_boro%s' % i, 'no_zip%s' % i, 'no_city%s' % i, 'no_state%s' % i], axis=1, inplace=True)
        else:
            if combs[9][i].get() =="" or combs[10][i].get() == "":
                messagebox.showerror(title='Both Latitude and Longitude Needed!', 
                                        message='Enter both Latitude and Longitude or neither')
                return
            else:
                df['Address%s' % i] = df[combs[9][i].get()].apply(str) + ',' + df[combs[10][i].get()].apply(str)
                df['Generated_streetaddress%s' % i] = df['Address%s' % i]


    df = df.fillna('')

    # Run google API twice, for the Address only and Name+Address.
    df.reset_index(inplace=True)
    df['Goog_ID'] = df.index
    if (second_run_state.get() is True and
        combs[0][1].get() != "" and
        combs[1][1].get() != ""):
        add_list = ['Address', 'NameAddress']
        # Create a dataframe with unique observations on add_list
        df_unique = df[['Address2', 'NameAddress2', 'Generated_streetaddress2',
                        'Address1', 'NameAddress1', 'Generated_streetaddress1', 'Goog_ID']].copy()
        df_unique.drop_duplicates(subset=['Address1', 'NameAddress1', 'Address2', 'NameAddress2'], keep="first", inplace=True)
        df_unique.reset_index(inplace=True)

        obs = len(df_unique.index) * 2
        print('There are %s unique observations to process...' % (obs))
    else:
        add_list = ['Address']
        # Create a dataframe with unique observations on add_list
        df_unique = df[['Address1', 'Generated_streetaddress1', 'Address2', 'Generated_streetaddress2', 'Goog_ID']].copy()
        df_unique.drop_duplicates(subset=['Address1', 'Address2'], keep="first", inplace=True)
        df_unique.reset_index(inplace=True)

        obs = len(df_unique.index)
        print('There are %s unique observations to process...' % (obs))

    i = -1
    # print(add_list)
    startTime = time.time()

    directory = path.dirname(output.get())
    count_query = 0

    # Finally we can get directions.
    for var in add_list:
        print('Started checking variable ', var)
        i += 1
        for index, row in df_unique.iterrows():
            # set index <= len(df_unique.index) to process all observations.
            if index <= len(df_unique.index) and not(var in ['Address'] and (row['Generated_streetaddress1'] == '' or row['Generated_streetaddress2'] == '')):
                if arrival_state.get() == 1:
                    transit_result = gmaps.directions(row["%s1" % var],
                                         row["%s2" % var],
                                         mode=tm_combo.get(),
                                         arrival_time=dt_formatted)
                else:
                    transit_result = gmaps.directions(row["%s1" % var],
                                         row["%s2" % var],
                                         mode=tm_combo.get(),
                                         departure_time=dt_formatted)
                count_query += 1
                print(json.dumps(transit_result, indent=4))
                status.set("Status: looking up observation %s of %s" % (count_query, obs))
                temp_df0 = json_normalize(transit_result[0]['legs'])
                temp_df0['Goog_ID'] = row['Goog_ID']
                temp_df1 = json_normalize(transit_result[0]['legs'][0]['steps'])
                temp_df1['Goog_ID'] = row['Goog_ID']
                print(temp_df1)
                #temp_df0.merge(temp_df1, left_on='id', right_on='id', how='outer')
                if index > 0:
                    dfLegs = dfLegs.append(temp_df0, ignore_index=True)
                    dfSteps = dfSteps.append(temp_df1, ignore_index=True)
                    #print('here:\n', dfLegs.head())
                else:
                    dfLegs = temp_df0.copy()
                    dfSteps = temp_df1.copy()
                    #print('There:\n', dfLegs.head())

                if index % 500 ==0:
                    writer = ExcelWriter(path.join(directory, "GOOGLE_recovery.xlsx").encode().decode())
                    dfLegs.to_excel(writer, 'Sheet1')
                    writer.save()
                    print("Recovery File GOOGLE_recovery.xlsx Saved when index was %s at %s" % (index, datetime.now()))
                # Make sure that we are getting the results of the correct query saved.
                transit_result = None

    # Save The Results
    # Drop the temporary variables.
    df.drop(['Generated_streetaddress1','Generated_streetaddress2'], axis=1, inplace=True)
    df_unique.drop(['Address2', 'Generated_streetaddress2','Address1', 'Generated_streetaddress1'], axis=1, inplace=True)
    try:
        df_unique.drop(['NameAddress1', 'NameAddress2'], axis=1, inplace=True)
    except:
        None

    # Merge back unique addresses with geocodes with original df.
    results0 = merge(df_unique, dfLegs, on='Goog_ID', how='outer')
    result = merge(df, results0, on='Goog_ID', how='outer')
    # steps are saved separately
    result.drop(['index_x', 'steps'], axis=1, inplace=True)
    # # Update Google output fields with new values if they already existed on the file.
    # for col in ['Gformatted_address0', 'Glat0', 'Glon0', 'GPartial0', 'Gtypes0', 'Gformatted_address1',
    #             'Glat1', 'Glon1', 'GPartial1', 'Gtypes1', 'Borough0', 'Borough1', 'Gzip0', 'Gzip1',
    #             'Gnumber0', 'Gnumber1', 'Gstreet0', 'Gstreet1', 'Both_Run_Same']:
    #     # print(col)
    #     if (col + '_y' in result.columns.values) and (col + '_x' in result.columns.values):
    #         result[col] = result[col + '_y'].fillna(result[col + '_x'])
    #         result.drop([col + '_y', col + '_x'], axis=1, inplace=True)

    # ExcelFile(output.get())
    try:
        writer = ExcelWriter(output.get())
        writerSteps = ExcelWriter(output.get().replace(".xls","_steps.xls"))
        result.to_excel(writer, 'wTransit')
        dfSteps.to_excel(writerSteps, 'Transit_Steps')
        writerSteps.save()
        writer.save()
        message = output.get() + "\n was successfully saved!\n There were %s queries made to Google Directions API" % (count_query)
    except:
        writer = ExcelWriter(path.join(directory, "wGoogle_Transit" +
                                       time.strftime("%Y%m%d-%H%M%S") +
                                       ".xlsx").encode().decode())
        writerSteps = ExcelWriter(path.join(directory, "wGoogle_TransitSteps" +
                                       time.strftime("%Y%m%d-%H%M%S") +
                                       ".xlsx").encode().decode())
        result.to_excel(writer, 'With_Transit')
        dfSteps.to_excel(writerSteps, 'Transit_Steps')
        writerSteps.save()
        writer.save()
        message = ("Couldn't write to " + output.get() + "\n saved Google_Geocoded_"
                    + time.strftime("%Y%m%d-%H%M%S") +".xlsx to the same directory.\n There were %s queries made to Google Directions API" % (count_query))
#   remove the recovery file.

    remove(path.join(directory, "GOOGLE_recovery.xlsx").encode().decode())
    print('Processed data and saved: ', output.get())

    endTime = time.time()
    t = (endTime - startTime) / 60
    status.set('Status: Done. It took %s minutes to make %s queries.' % (round(t, 2), count_query))
    print('Took %s minutes to run.' % round(t, 2))

    messagebox.showinfo('Success!', message)


# Run the program.
if __name__ == '__main__':
    root = Tk()

    # Quick workaround: Window background is white on Mac while buttons ... are grey.
    #root.configure(background='grey91')

    root.title("Google Geocoding")
    ents, row = makeform(root, fields)
    root.bind('<Return>', (lambda event, e=ents: fetch(e)))
    b1 = Button(row, text='Browse...', command=browsexlsx)
    b1.pack(side=LEFT, padx=5, pady=5)
    b2 = Button(row, text='Load Sheets', command=loadxlsx)
    b2.pack(side=LEFT, padx=5, pady=5, anchor=W)
    row.pack(side=TOP, fill=X, padx=5, pady=5)



    row = Frame(root)
    lbl_sheet = Label(row, text="Choose Input Sheet:", width=20, anchor='w')
    sheet_combo = Combobox(row, width=20, state='disabled')
    lbl_frow = Label(row, text="First Row?", width=10, anchor='w')
    frow = Entry(row, width=5, state='disabled')
    lbl_sheet.pack(side=LEFT, padx=5, pady=5)
    sheet_combo.pack(side=LEFT, expand=YES, fill=X)
    lbl_frow.pack(side=LEFT, padx=5, pady=5)
    frow.pack(side=LEFT, expand=YES, fill=X)

    b3 = Button(row, text='Load Fields', command=loadfields, state='disabled')

    b3.pack(side=LEFT, padx=5, pady=5, anchor='w')
    row.pack(side=TOP, fill=X, padx=5, pady=5)

    combs, row2 = makecomboboxes(root, combos)

    row = Frame(root)
    second_run_state = BooleanVar()
    second_run_state.set(True) #set check state
    chk = Checkbutton(row, text="Run twice using Address and Trade & Address", var=second_run_state, state='disabled')
    chk.pack(side=LEFT, expand=YES, padx=15, pady=5, anchor='w')
    arrival_state = BooleanVar()
    arrival_state_lab = Label(row, text="Use Arrival Time instead of Departure Time?")
    arrival_state_lab.pack(side=LEFT, padx=15, pady=5, anchor='w')
    MODES = [
    ("Arrival Time", 1),
    ("Departure Time", 2)
    ]
    arrival_state = IntVar()
    arrival_state.set(2)
    for text, mode in MODES:
        b = Radiobutton(row, text=text,
                        variable=arrival_state, value=mode)
        b.pack(anchor=W)
    row.pack(side=TOP, fill=X, padx=5, pady=5)

    # Travel Time and Mode
    row = Frame(root)
    lbl_tm = Label(row, text="Transportation Mode:", width=20, anchor='w')
    tm_combo = Combobox(row, width=10, state='enabled')
    tm_combo['values'] = ['transit', 'driving', 'walking', 'cycling']
    tm_combo.current(0)
    lbl_time = Label(row, text="Date/Time:", width=15, anchor='w')
    dep_time = Entry(row, width=18, state='disabled')
    getDate = Button(row, text="Choose Date ...", width=17, command=get_date)
    lbl_tm.pack(side=LEFT, padx=5, pady=5)
    tm_combo.pack(side=LEFT, padx=28, pady=5, expand=YES, fill=X)
    lbl_time.pack(side=LEFT, padx=5, pady=5)
    dep_time.pack(side=LEFT, padx=5, pady=5, expand=YES, fill=X)
    getDate.pack(side=LEFT, expand=NO, fill=X)
    row.pack(side=TOP, fill=X, padx=5, pady=5)

    # Retreive Button and Output File Row.
    row = Frame(root)
    b4 = Button(row, text='Retreive Directions', command=lambda: Geocode(DFrame, combs), state='disabled')
    out_lbl = Label(row, text="Output File", width=20, anchor='w')
    output = Entry(row, width=40, state='disabled')
    out_lbl.pack(side=LEFT, padx=5, pady=5)
    output.pack(side=LEFT, expand=YES, fill=X)
    b4.pack(side=LEFT, padx=5, pady=5, anchor='w')
    row.pack(side=TOP, fill=X, padx=5, pady=5)

    row = Frame(root)
    status = StringVar()
    status.set("Status: waiting for user input ...")
    status_bar = Label(row, textvariable=status, bo=0.1,
                       relief=SUNKEN, anchor='w')
    status_bar.pack(side=BOTTOM, fill=X, padx=5, pady=5)
    row.pack(side=TOP, fill=X, padx=5, pady=5)


    root.mainloop()