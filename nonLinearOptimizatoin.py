    """Chewse was a startup that managed the corporate catering experience for their customers.
        This program was designed to reduce the Costs of Goods Sold (COGS) for Chewse by reducing
        the amount of money spent on catering orders. Chewse had a great idea to find lower prices for 
        meals provided by resteraunt vendors by securing price discounts based on guarunteed order
        volumes for the month. This created a challenging optimization problem because a vendor would have
        several levels of pricing, depending on volume (ie $11 per meal for <300 meals, $9 for >300 and <800 meals, and $6.60 for >800 meals).
        Optimal pricing was also subject to complext constraints such as ensuring corporate clients
        received a sufficient variety of cuisines, as well as a myriad of other customer preferences.

        The non-linear optimization was originally solved by a special type of piecewise-linear approximation
        called Specialed Ordered Set - Type 2, or SOS2. It used a very useful Google Operations Research library
        which wrapped C++ functions into python using SWIG.

        The users of this code could interact with it through a Spreadsheet menu button enabled by Google Apps Script
        The script would call this python code through an http request to the AWS server, which initiated the optimization
        through the Flask framework.

        After Google Apps Script received the optimal assignments of meals for the customers and vendors, it would create 
        several pivot tables and charts to visualize several performance metrics. This human-machine interaction
        allowed for Chewse to either override some decisions or select custom assignments for customer
        orders that were not feasible under the constraints (the program would suggest several options in this circumstance)


    """


from __future__ import print_function

import pandas as pd
from flask import Flask
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import httplib2
import os
import datetime
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from ortools.linear_solver import pywraplp

from datetime import datetime, time

class customer(object):
    ID = ""
    address = 0
    vendorHistory = []
    dateHistory = []
    generalCuisineHistory = []
    customerFrequency = 0
    vendorThreshold = 4
    generalThreshold = 4
    specificThreshold = 4
    specificCuisineHistory = []
    customerNoServeList = set()
    vendorLimits = [0, 2, 5, 9, 13]
    generalLimits = [0, 2, 5, 9, 13]
    specificLimits = [0, 2, 5, 9, 13]
    vendorFreqs = [8, 12, 16, 18, 20]
    generalFreqs = [4, 6, 7, 8 , 9]
    specificFreqs = [8, 12, 16, 18, 20]
    def update_vendorHistory(self, vendor):
        self.vendorHistory.insert(0, vendor)
    def update_dateHistory(self, date):
        self.dateHistory.append(date)
    def update_generalCuisineHistory(self, vendor):
        self.generalCuisineHistory.insert(0, vendor)
    def update_specificCuisineHistory(self, vendor):
        self.specificCuisineHistory.insert(0, vendor)
    def update_customerNoServeList(self, vendor):
        self.customerNoServeList.add(vendor)
    def update_frequency(self, frequency):
        self.customerFrequency = frequency
    def update_vendorThreshold(self, threshold):
        self.vendorThreshold = threshold
    def update_generalThreshold(self, threshold):
        self.generalThreshold = threshold
    def update_specificThreshold(self, threshold):
        self.specificThreshold = threshold
    #todo: fix some of these 'process' functions to accomodate certain frequencies
    def process_VendorThreshold(self, frequency):
        f = frequency
        for t in range(0, len(self.vendorLimits)-2):
            if(f >= self.vendorLimits[t] and f < self.vendorLimits[t+1]):
                #self.update_frequency(f)
                self.update_vendorThreshold(self.vendorFreqs[t])
            elif(f > self.vendorLimits[len(self.vendorLimits)- 1]):
                #self.update_frequency(f)
                self.update_vendorThreshold(self.vendorFreqs[len(self.vendorLimits) - 1])
            elif(f == self.vendorLimits[len(self.vendorLimits)-1]):
                #self.update_frequency(f)
                self.update_vendorThreshold(self.vendorFreqs[len(self.vendorLimits) - 1])
    def process_generalThreshold(self, frequency):
                f = frequency
                for t in range(0, len(self.generalLimits)-2):
                    if((f > self.generalLimits[t] or f == self.generalLimits[t]) and f < self.generalLimits[t+1]):
                        #self.update_frequency(f)
                        self.update_generalThreshold(self.generalFreqs[t])
                    elif(f > self.generalLimits[len(self.generalLimits)- 1]):
                        #self.update_frequency(f)
                        self.update_generalThreshold(self.generalFreqs[len(self.generalLimits) - 1])
                    elif(f == self.generalLimits[len(self.generalLimits)-1]):
                        #self.update_frequency(f)
                        self.update_generalThreshold(self.generalFreqs[len(self.generalLimits) - 1])
    def process_specificThreshold(self, frequency):
                f = frequency
                for t in range(0, len(self.specificLimits)-2):
                    if((f > self.specificLimits[t] or f == self.specificLimits[t]) and f < self.specificLimits[t+1]):
                        #self.update_frequency(f)
                        self.update_specificThreshold(self.specificFreqs[t])
                    elif(f > self.specificLimits[len(self.specificLimits)- 1]):
                        #self.update_frequency(f)
                        self.update_specificThreshold(self.specificFreqs[len(self.specificLimits) - 1])
                    elif(f == self.specificLimits[len(self.specificLimits)-1]):
                        #self.update_frequency(f)
                        self.update_specificThreshold(self.specificFreqs[len(self.specificLimits) - 1])

    

    
    def __init__(self, ID, address):
        self.ID = ID
        self.address = address
        self.vendorHistory = []
        self.generalCuisineHistory = []
        self.specificCuisineHistory = []
        self.customerNoServeList = set()
        self.customerFrequency = 0
        self.vendorThreshold = 4
        self.specificCuisineHistory = []
        self.customerNoServeList = set()
        self.vendorLimits = [0, 2, 5, 9, 13]
        self.generalLimits = [0, 2, 5, 9, 13]
        self.specificLimits = [0, 2, 5, 9, 13]
        self.vendorFreqs = [8, 12, 16, 18, 20]
        self.generalFreqs = [4, 6, 7, 8 , 9]
        self.specificFreqs = [8, 12, 16, 18, 20]


def make_customer(self, ID, address):
    customer = customer(ID, address)
    return customer


class order(object):
    ID = ""
    customerObject = ""
    orderAddress = ""
    orderTime = datetime.time
    orderDate = datetime.date
    numMeals = 0
    pricePerPerson = 0.00
    GMV = 0
    #potentialVendors = []
    #def update_potentialVendors(self, vendor):
    #    self.update_vendorHistory.append(vendor)
    def update_numMeals(self, numMeals):
        self.numMeals += numMeals
    

    
    def __init__(self, ID, customerObject, orderAddress, orderTime, orderDate, numMeals, pricePerPerson):
        self.ID = ID
        self.customerObject = customerObject
        self.orderAddress = orderAddress
        self.orderTime = orderTime
        self.orderDate = orderDate
        self.numMeals = int(numMeals)
        self.pricePerPerson = pricePerPerson
        self.GMV = numMeals*pricePerPerson



def make_order(self, ID, customerObject, orderAddress, orderTime, orderDate, numMeals, pricePerPerson):
    order = order(self, ID, customerObject, orderTime, orderDate, numMeals, pricePerPerson)
    return order

class vendor(object):
    ID = ""
    specialtyCuisineID = ""
    generalCuisineID = ""
    currentMealsMonth = {
        'January' : 0,
        'February' : 0,
        'March' : 0,
        'April' : 0,
        'May' : 0,
        'June' : 0,
        'July' : 0,
        'September' : 0,
        'October' : 0,
        'November' : 0,
        'December' : 0,
        }
    currentMealsDay = [500]
    dailyMaxMeals = 750
    monthlyMaxMeals = 1250
    dailyMaxOrders = 300
    tierUpperBound = [500]
    tierPrice = [500]
    
    y = []
    z = []
    def update_currentMealsMonth(month, meals):
            currentMealsMonth[month] +=  meals
            return;
    def update_currentMealsDay(day, meals):
            currentMealsDay[day] += meals    
            return;
    
        
        
    #These generating functions are the heart of the parametrization. They allow for SOS2 (Special Ordered Set of Type 2) constraints
    def generateXvars(self):
        x = [0.000000 for i in range(0, 10)]
        for i in range(0, 10):
            x.append(0)
        x[0] = 0
        x[1] =  (self.tierUpperBound[0]*self.tierPrice[1])/self.tierPrice[0]
        x[2] = self.tierUpperBound[0]
        x[3] = (self.tierUpperBound[1]*self.tierPrice[2])/self.tierPrice[1]
        x[4] = self.tierUpperBound[1]
        x[5] = (self.tierUpperBound[2]*self.tierPrice[3])/self.tierPrice[2]
        x[6] = self.tierUpperBound[2]
        x[7] = (self.tierUpperBound[3]*self.tierPrice[4])/self.tierPrice[3]
        x[8] = self.tierUpperBound[3]
        x[9] = (self.tierUpperBound[4]*self.tierPrice[5])/self.tierPrice[4]
        return  x

    def generateYvars(self):
        y = [10]
        for i in range(10):
            y.append(0)
        for i in range(0,10):
            y[i] = 0
            return y

    def generateZvars(self):
        z = [10]
        for i in range(10):
            z.append(0)
        z[0] = 0
        z[1] = self.tierPrice[1]*self.tierUpperBound[0]
        z[2] = self.tierPrice[1]*self.tierUpperBound[0]
        z[3] = self.tierPrice[2]*self.tierUpperBound[1]
        z[4] = self.tierPrice[2]*self.tierUpperBound[1]
        z[5] = self.tierPrice[3]*self.tierUpperBound[2]
        z[6] = self.tierPrice[3]*self.tierUpperBound[2]
        z[7] = self.tierPrice[4]*self.tierUpperBound[3]
        z[8] = self.tierPrice[4]*self.tierUpperBound[3]
        z[9] = self.tierPrice[5]*self.tierUpperBound[4]
        return z





     
    def __init__(self, ID, specialtyCuisineID, generalCuisineID, dailyMaxMeals, monthlyMaxMeals, dailyMaxOrders, tierPrice, tierUpperBound):
        self.ID = ID
        self.specialtyCuisineID = specialtyCuisineID
        self.generalCuisineID = generalCuisineID
        self.currentMealsMonth = {
            'January' : 0,
            'February' : 0,
            'March' : 0,
            'April' : 0,
            'May' : 0,
            'June' : 0,
            'July' : 0,
            'September' : 0,
            'October' : 0,
            'November' : 0,
            'December' : 0,
            }
        self.currentMealsDay = []
        self.dailyMaxMeals = dailyMaxMeals
        self.monthlyMaxMeals = monthlyMaxMeals
        self.dailyMaxOrders = dailyMaxOrders
        self.tierUpperBound = tierUpperBound
        self.tierPrice = tierPrice
        self.x = self.generateXvars
        self.y = self.generateYvars
        self.z = self.generateZvars
         


def make_vendor(self, ID, specialtyCuisineID, generalCuisineID, dailyMaxMeals, monthlyMaxMeals, dailyMaxOrders, tierPrice, tierUpperBound):
    vendor = vendor(self, ID, specialtyCuisineID, generalCuisineID, dailyMaxMeals, monthlyMaxMeals, monthlyMaxOrders, tierPrice, tierUpperBound)
    return vendor

header_text = '''
    <html>\n<head> <title>EB Flask Test</title> </head>\n<body>'''
instructions = '''
    <p><em>Hint</em>: This is a RESTful web service! Append a username
    to the URL (for example: <code>/Thelonious</code>) to say hello to
    someone specific.</p>\n'''
home_link = '<p><a href="/">Back</a></p>\n'
footer_text = '</body>\n</html>'

application = Flask(__name__)
application.add_url_rule('/', 'index', (lambda: header_text + main() + instructions + footer_text))
def main():

    #When I'm testing this on my local machine I switch where the program get's its credentials from
    scope = ['https://spreadsheets.google.com/feeds']
    #credentials = ServiceAccountCredentials.from_json_keyfile_name('C:/users/nickmlb56/source/repos/chewseOptimization3/eb-flask/5f80ce9025c4.json', scope)
    credentials = ServiceAccountCredentials.from_json_keyfile_name('5f80ce9025c4.json', scope)

    gc = gspread.authorize(credentials)
    

    # Open a worksheet from the shared Google Sheet
    wks = gc.open("Nonlinear Model Workspace")
    sh = wks.worksheet("Cloud Output")
    gsOrders = wks.worksheet("Orders")
    gsHistory = wks.worksheet("History")
    gsPreferences = wks.worksheet("Preferences")
    gsVendors = wks.worksheet("Vendors")


    #Read and store Vendor Data in a pandas dataframe
    vendorDF = pd.DataFrame(gsVendors.get_all_records())
    
    vendorSet = set()
    firstVendors = set()


    vendors = {}
    currentVendor = ""
    onOff = 0
    currentGeneralCuisine = ""
    currentSpecificCuisine = ""
    currentVendor = ""
    currentTierPrice = []
    currentUpperBound = []
    currentDailyMax = 1000
    currentMonthlyMax = 50000
    currentDailyOrderMax = 300
    testXvar = []
    originalVendorSet = set()

    for r in range(0, len(vendorDF)):
                onOff = int(vendorDF.iloc[r].on_off)
                currentVendor = str(vendorDF.iloc[r].Vendor)
                currentGeneralCuisine = str(vendorDF.iloc[r].general_cuisine)
                currentSpecificCuisine = str(vendorDF.iloc[r].specific_cuisine)
                currentDailyMax = int(vendorDF.iloc[r].Daily_Max_Meals)
                currentMonthlyMax = int(vendorDF.iloc[r].Monthly_Max_Meals)
                currentDailyOrderMax = int(vendorDF.iloc[r].Daily_Max_Orders)
                currentUpperBound.append(int(vendorDF.iloc[r].Tier_1_Minimum))
                currentUpperBound.append(int(vendorDF.iloc[r].Tier_2_Minimum))
                currentUpperBound.append(int(vendorDF.iloc[r].Tier_3_Minimum))
                currentUpperBound.append(int(vendorDF.iloc[r].Tier_4_Minimum))
                currentUpperBound.append(int(vendorDF.iloc[r].Tier_5_Minimum))
                currentTierPrice.append(float(vendorDF.iloc[r].Tier_0_Price))
                currentTierPrice.append(float(vendorDF.iloc[r].Tier_1_Price))
                currentTierPrice.append(float(vendorDF.iloc[r].Tier_2_Price))
                currentTierPrice.append(float(vendorDF.iloc[r].Tier_3_Price))
                currentTierPrice.append(float(vendorDF.iloc[r].Tier_4_Price))
                currentTierPrice.append(float(vendorDF.iloc[r].Tier_5_Price))
                
                
                if(onOff == 1):
                    firstVendors.add(currentVendor)
                vendorSet.add(currentVendor)
                vendors[currentVendor] = vendor(currentVendor, "", "", currentDailyMax, currentMonthlyMax, currentDailyOrderMax, currentTierPrice, currentUpperBound)
            
            
                currentUpperBound = []
                currentTierPrice = []

    


    #Excel Code to read in Customer Data
    custDF = pd.DataFrame(gsHistory.get_all_records())
    
    customerSet = set()
    customers = {}
    customerHistories = []
    currentCustomer = ""
    currentDate = datetime.date
    currentVendor = ""
    currentSpecificCuisine = ""
    currentGeneralCuisine = ""
    for r in range(0, len(custDF)):
            currentCustomer = str(custDF.iloc[r].organization)
            currentVendor = custDF.iloc[r].vendor_name
            currentSpecificCuisine = str(custDF.iloc[r].specific_cuisine)
            currentGeneralCuisine = str(custDF.iloc[r].general_cuisine)
            

            if currentCustomer not in customerSet:
                customerSet.add(currentCustomer)
                customerHistories.append(currentVendor)
                customers[currentCustomer] = customer(currentCustomer, "")
                customers[currentCustomer].update_vendorHistory(currentVendor)
                #customers[currentCustomer].update_dateHistory(currentDate)
                customers[currentCustomer].update_generalCuisineHistory(currentGeneralCuisine)
                customers[currentCustomer].update_specificCuisineHistory(currentSpecificCuisine)
                
                if(str(currentVendor) not in vendorSet):
                   vendorSet.add(str(currentVendor))
                   vendors[currentVendor] = vendor(currentVendor, "", "", 750, 1250, 300, [9, 9, 9, 9, 9, 9], [1000, 2000, 3000, 4000, 5000])
                vendors[str(currentVendor)].specialtyCuisineID = str(currentSpecificCuisine)
                vendors[str(currentVendor)].generalCuisineID = str(currentGeneralCuisine)
                while(customerHistories): customerHistories.pop()
            else:
                customers[currentCustomer].update_vendorHistory(currentVendor)
                #customers[currentCustomer].update_dateHistory(currentDate)
                customers[currentCustomer].update_generalCuisineHistory(currentGeneralCuisine)
                customers[currentCustomer].update_specificCuisineHistory(currentSpecificCuisine)
            
   

    
    #read in customer preferences
    prefDF = pd.DataFrame(gsPreferences.get_all_records())
    
    
    j = 0
    i = 0
    for i in range(0, len(prefDF)):
        
        currentCustomer = str(prefDF.iloc[i].Customer)
        currentVendor = str(prefDF.iloc[i].Restaurant)
        if(str(prefDF.iloc[i].Loved) == "FALSE"):
            if currentCustomer not in customerSet:
                customerSet.add(currentCustomer)
                
                customers[currentCustomer] = customer(currentCustomer, "")
            customers[currentCustomer].update_customerNoServeList(currentVendor)

    
    

    #Excel Code to read in Order Data
    #read from wb
    results = pd.DataFrame(gsOrders.get_all_records())
    
    df = results.copy()


    
    
    df['Lunch'] = 0
    df['newIndex'] = 0

    lunch = 0
    j=0
    customerSet2 = set()
    currentCustomer = ""
    currentTime = datetime.time
    
    
    j = 0
    beforelunch = time(10, 30, 00)
    afterlunch = time(15, 30, 00)
    

    for i in range(0, len(df)):
        
        currentTime = datetime.strptime(df.iloc[i].orderTime, '%H:%M:%S').time()
        islunch = currentTime > beforelunch and currentTime < afterlunch
        if(islunch):
            lunch = 1
            j += 1
            df.loc[i, 'newIndex'] = j
        else:
            lunch = 0
        df.loc[i, 'Lunch'] = lunch
    numLunches = j    
    selection = df.Lunch < 1
    df2 = df[~selection]
    df2 = df2.reset_index()
    del df2['index']
    df2['numberOrder'] = 0
    df2['isDuplicate'] = 0
    j =0
    futureOrder = ""
    print("df2 length: " + str(len(df2)))
    i = 0
    #populate numberOrder
    for i in range(0, len(df2)):
            
            currentCustomer = df2.iloc[i].Customer
        
            if(currentCustomer not in customerSet2):
                j = 0
                customerSet2.add(currentCustomer)
            else:
                j += 1
            df2.loc[i, 'numberOrder'] = j 
            df2['orderDate'] = pd.to_datetime(df2['orderDate'])
            selection2 = df2.Customer != df2.iloc[i].Customer
            df_sub = df2[~selection2]
            df_sub = df_sub.reset_index()
            firstRun = 0
            for k in range(0, len(df_sub)):
                
                if(df_sub.iloc[k].orderDate == df2.iloc[i].orderDate):
                    if(df_sub.iloc[k].orderTime == df2.iloc[i].orderTime):
                        #if(df_sub.iloc[k].Address == df2.iloc[i].Address):
                            if(firstRun > 0):
                                df2.loc[i, 'guestCount'] = df_sub.iloc[k].guestCount + df2.iloc[i].guestCount
                                df2.loc[df_sub.iloc[k]['index'], 'isDuplicate'] = 1
                            else:
                                firstRun += 1
                                        

    df5 = df2[df2.isDuplicate == 0]

    
    j =0
    currentOrder = 0
    currentCustomer = ""
    currentAddress = ""
    orderCustomerSet = set()
    currentDate = datetime.date
    currentTime = datetime.time
    orderNumMeals = 0
    orderPricePerPerson = 0
    numberOrder = 0
    orders = {}
    orderKeys = set()
    orderSchedule = ""
    numberedOrders = [[] for k in range(100000)]
    for o in range(0, len(df5)):
        
                    currentOrder = j
                    currentCustomer = str(df5.iloc[o].Customer)
                    orderCustomerSet.add(currentCustomer)
                    if(currentCustomer not in customerSet):
                        customerSet.add(currentCustomer)
                        customers[currentCustomer] = customer(currentCustomer, currentAddress)
                    
                    currentAddress = str(df5.iloc[o].Address)
                    currentDate = df5.iloc[o].orderDate
                    customers[str(currentCustomer)].update_dateHistory(currentDate)
                    currentTime = df5.iloc[o].orderTime
                    orderNumMeals = int(df5.iloc[o].guestCount)
                    orderPricePerPerson = int(df5.iloc[o].price)
                    numberOrder = int(df5.iloc[o].numberOrder)
                    j += 1
            
                    orders[currentCustomer] = order(currentOrder, currentCustomer, currentAddress, currentTime, currentDate, orderNumMeals, orderPricePerPerson)
                    numberedOrders[numberOrder].append(orders[currentCustomer])

            
    
    #This code breaks down the orders into manageable chunks to process at a time. The way the sheet is sorted allows it to focus on all customer's first orders, then all customer's second orders for the month...and so on
    adjustedNumberedOrders = []
    blankList = []
    j =0
    s =0
    
    q = 0
    w = 0
    for nb in numberedOrders:
        if(len(nb)>0):
            while(q < len(nb)-21):
                q += 20
                for w in range(q-20, q):
                    blankList.append(nb[w])
                adjustedNumberedOrders.append(blankList.copy())
                while(blankList): blankList.pop()
            while(q < len(nb)):
            
                blankList.append(nb[q])
                q +=1
            adjustedNumberedOrders.append(blankList.copy())
            while(blankList): blankList.pop()
            q =0
    #Update a customer's tolerance for getting the same vendor or type of cuisine based on how often they are ordering
    freq = 0
    for c in customerSet:
        freq = len(df5[df5.Customer == c])
        customers[c].update_frequency(freq)
        customers[c].process_VendorThreshold(freq)
        customers[c].process_generalThreshold(freq)
        customers[c].process_specificThreshold(freq)

    #Writing output for diagnostic purposes
    print("Done with program input")
    




    
    #save time in testing input/output by switiching to false
    if( 1 > 0):

        #initializing global variables that will accumulate over multiple optimization iterations
        num_vendors = len(firstVendors)
        #Cumulative Meals Throughout Iteration
        xValues = [0 for i in range(num_vendors)]
        oValues = [0 for i in range(num_vendors)]
        xValues2 = [0 for i in range(num_vendors)]
        oValues2 = [0 for i in range(num_vendors)]
        dValues2 = [[0 for d in range(0, 31)] for i in range(num_vendors)]
        xdValues2 = [[0 for d in range(0, 31)] for i in range(num_vendors)]
        ordersOutput = {}
        orderID = [0 for i in range(0, len(df2))]
        orderCust = ["" for i in range(0, len(df2))]
        orderAddress = ["" for i in range(0, len(df2))]
        orderDate = [datetime.date for i in range(0, len(df2))]
        orderTime = [time(8, 8, 8) for i in range(0, len(df2))]
        orderMeals = [0 for i in range(0, len(df2))]
        vendorID = ["" for i in range(0, len(df2))]
        vendorGID = ["" for i in range(0, len(df2))]
        vendorSID = ["" for i in range(0, len(df2))]
        customerFrequency = [0 for i in range(0, len(df2))]
        customerVendorHistory = ["" for i in range(0, len(df2))]
        customerGeneralHistory = ["" for i in range(0, len(df2))]
        customerSpecificHistory = ["" for i in range(0, len(df2))]
        customerPreferenceHistory = ["" for i in range(0, len(df2))]

        violatedConstraints = {'vendor' : set(), 'General' : {'Order' : set(), 'Cuisine' : set()}, 'Specific' : set(), 'Preference' : set()}
        totalTime = 0.0
            
        totalCost = 0
        run = 0
        orderCount = 0

        for nb in adjustedNumberedOrders:
            print("len nb")
            print(len(nb))
            
            # Instantiate a mixed-integer solver.
            solver = pywraplp.Solver('SolveAssignmentProblemMIP',
                                       pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

            vendorStart = 0
            orderStart = 0
            num_orders = (len(nb)+orderStart)*31
            dailyLimitOrders = True
            dailyLimitMeals = True
            monthlyLimitMeals = True
            customerVendorLimit = True
            customerSpecificCuisineLimit = True
            customerGeneralCuisineLimit = True
            customerPreferenceLimit = True
            
            dateSet = set()

            
        

   
            #Set up decision variable array
    
            x = {}
 
            for i in range(0, num_vendors):
                for j in range(0, num_orders):
                    x[i, j] = solver.BoolVar('x[%i,%i]' % (i, j))

    


            # Create Piecewise linear costs for each vendor with SOS2 constraints
    
            xi = [[0 for i in range(10)] for j in range(num_vendors)]
            yi = [[0 for i in range(10)] for j in range(num_vendors)]
            zi = [[0 for i in range(10)] for j in range(num_vendors)]
            xr = [[0 for i in range(10)] for j in range(num_vendors)]
            yr = [[0 for i in range(10)] for j in range(num_vendors)]
            orderArray = [[0 for j in range(num_orders)] for i in range(num_vendors)]
            penalty = [[0 for j in range(num_orders)] for i in range(num_vendors)]
            j = 0   
            i=0
        
            #Populate the 'order array' and keept track of indices in the sparse array that actually have meaningful values
            for v in sorted(firstVendors):
                if(i < num_vendors):
                
                    for k in nb:
                        for d in range(0,31):        
                            if(j<num_orders):
                                if(d == int(k.orderDate.day - 1)):
                                    orderArray[i][j] = int(k.numMeals)
                                    dateSet.add(j)                    
                                j += 1  
                i += 1        
                j=0
            i=0
            #initialize all penalty costs to have a scalar of 1
            for v in sorted(firstVendors):
                if(i < num_vendors):
                    for j in dateSet:
                        penalty[i][j] = 1
                i += 1        
                j=0
            i=0

            #All orders must be assigned to a vendor
            for j in dateSet:
                        solver.Add(solver.Sum([x[i, j] for i in range(num_vendors)]) == 1)
                    
        
            j=0






            




        
            xi = [[0 for h in range(10)] for t in range(num_vendors)]
            zi = [[0 for h in range(10)] for t in range(num_vendors)]
            yi = [[0 for h in range(10)] for t in range(num_vendors)]
            z = [0 for v in range(num_vendors)]
            b=0
            for v in sorted(firstVendors):
                if(b<num_vendors):
                    for n in range(0,10):
                        xr[b][n] = solver.NumVar(0.0000000, 1.0000000, 'xr[%i, %i]' % (b, n))
            
                    xi[b] = vendors[v].generateXvars()
            
                    for n in range(0,10):
                
                        yr[b][n] = solver.IntVar(0,1,'yr[%i,%i]' % (b, n))
                
                    zi[b] = vendors[v].generateZvars()

                    #Below are unique SOS2 constraints
            
                    solver.Add(solver.Sum([xr[b][i] for i in range(10)]) == 1)
                
                    constraints = [0]*10
                    for i in range(10):
                
                        solver.Add(xr[b][i] <= yr[b][i])
                    solver.Add(solver.Sum([yr[b][i] for i in range(10)]) <=2)
                    #if yi[0] is positive, then only yi[1] can be positive, etc.
                    solver.Add(yr[b][0] + solver.Sum([yr[b][0+i] for i in range(2, 10, 1)]) <= 1)
                    solver.Add(yr[b][1] + solver.Sum([yr[b][1+i] for i in range(2, 9, 1)]) <= 1)
                    solver.Add(yr[b][2] + solver.Sum([yr[b][2+i] for i in range(2, 8, 1)]) <= 1)
                    solver.Add(yr[b][3] + solver.Sum([yr[b][3+i] for i in range(2, 7, 1)]) <= 1)
                    solver.Add(yr[b][4] + solver.Sum([yr[b][4+i] for i in range(2, 6, 1)]) <= 1)
                    solver.Add(yr[b][5] + solver.Sum([yr[b][5+i] for i in range(2, 5, 1)]) <= 1)
                    solver.Add(yr[b][6] + solver.Sum([yr[b][6+i] for i in range(2, 4, 1)]) <= 1)
                    solver.Add(yr[b][7] + solver.Sum([yr[b][7+i] for i in range(2, 3, 1)]) <= 1)
            
            
          
        
                b +=1
        
            # Constraints
        
            #Customer Vendor History Constraint
            tempHist = []
            tempVendor = ""
            frequencyThreshold = 4
            hist = 0
            i=0
            j=0
            if(customerVendorLimit):
                for k in nb:
                    if(j < int(num_orders/31)):
                        if(k.customerObject in customerSet):

                            tempHist = customers[str(k.customerObject)].vendorHistory

                            for h in tempHist:
                                if(hist < customers[k.customerObject].vendorThreshold):
                            
                                    #TODO: make this constraint a sum, something like sum x[i, j] for j in range(num_orders/2) >= sum[i, j] 
                                    for v in sorted(firstVendors):
                                        if(i<num_vendors):
                                            if(h == vendors[v].ID):

                                                solver.Add(x[i, int(j*31 + k.orderDate.day - 1)] == 0)
                                        i += 1
                                hist += 1
                                i =0
                    j += 1
                    hist = 0
            j=0
            tempHist = []
            tempVendor = ""
            frequencyThreshold = 4
            hist = 0
            i=0
            if(customerSpecificCuisineLimit):
                for k in nb:
                    if(j<num_orders):
                        tempHist = customers[str(k.customerObject)].specificCuisineHistory

                        for h in tempHist:
                            if(hist < customers[k.customerObject].specificThreshold):
                            
                                #TODO: make this constraint a sum, something like sum x[i, j] for j in range(num_orders/2) >= sum[i, j] 
                                for v in sorted(firstVendors):
                                    if(i<num_vendors):
                                        if(h == vendors[v].specialtyCuisineID and vendors[v].specialtyCuisineID != ""):
                                            #todo: make these penalties adjust based on how far away the hist iterator has gone
                                            penalty[i][j*31 + int(k.orderDate.day - 1)] += 10
                                    i += 1
                            hist += 1
                    j += 1
            j=0
            tempHist = []
            tempVendor = ""
            frequencyThreshold = 4
            hist = 0
            i=0
            if(customerGeneralCuisineLimit):
                for k in nb:
                    if(j<num_orders):
                        tempHist = customers[str(k.customerObject)].generalCuisineHistory
                        
                        for h in tempHist:
                            if(hist < customers[k.customerObject].generalThreshold):
                            
                        
                                for v in sorted(firstVendors):
                                    if(i<num_vendors):
                                        if(h == vendors[v].generalCuisineID and vendors[v].generalCuisineID != "" ):
                                            penalty[i][j*31 + int(k.orderDate.day - 1)] += 5
                                    i += 1
                            hist += 1
                    j += 1





            #Each vendor is not assigned more orders than their daily order maximum
            if(dailyLimitOrders):
                i=0
                for v in sorted(firstVendors):
                    for d in range(0,31):
                        if(i<num_vendors):
                           solver.Add(solver.Sum([x[i, j + d] for j in range(0, num_orders, 31)]) + dValues2[i][d] <= vendors[v].dailyMaxOrders)
                    i +=1


            # The total meals assigned to a vendor in the month cannot exceed their maximum monthly meal limit
            if(monthlyLimitMeals):
                i =0
                for v in sorted(firstVendors):
                    if(i<num_vendors):
                       solver.Add(solver.Sum([x[i, j]*orderArray[i][j] for j in dateSet]) + xValues2[i] <= vendors[v].monthlyMaxMeals)
                    i +=1
      

            
            j=0
            b=0
            for b in range(num_vendors):
                solver.Add(solver.Sum([xi[b][i] * xr[b][i] for i in range(10)]) == solver.Sum([x[b, j]*orderArray[b][j] for j in dateSet]) + xValues[b])
    

            if(dailyLimitMeals):
               i=0
               for v in sorted(firstVendors):
                    for d in range(0,31):
                        if(i<num_vendors):
                           solver.Add(solver.Sum([x[i, j + d]*orderArray[i][j+d] for j in range(0, num_orders, 31)]) + xdValues2[i][d] <= vendors[v].dailyMaxMeals)
                    i +=1
       

            #Customer Preference Constraints
            if(customerPreferenceLimit):
                for k in nb:
                    for b in sorted(firstVendors):
                        if(i < num_vendors):
                           for h in range(0, len(customers[k.customerObject].customerNoServeList)):
                               if(customers[k.customerObject].customerNoServeList[h] == vendors[b].ID):
                                  penalty[i][j*31 + int(k.orderDate.day - 1)] += 100
                        i += 1
                    j += 1

            # Objective
            solver.Minimize(solver.Sum([zi[b][j]*xr[b][j]*penalty[b][k] for b in range(0, num_vendors) for j in range(0, 10) for k in dateSet]))
        


       
            sol = solver.Solve()
            sol2 = solver.set_time_limit(2000)
            totalCost += solver.Objective().Value()
            print('Total cost = ', totalCost)
            
            i = 0
            j= 0
            vendorPrint = []
            orderPrint = []
            for v in sorted(firstVendors):
                if(i<num_vendors):
                    vendorPrint.append(vendors[v])
                    #print(vendors[v].ID)
                    #print(i)
                i +=1
            for k in nb:
                if(j<num_orders):
                    orderPrint.append(k)
                    #print(k)
                    #print(j) 
                j +=1
            i=0
            j=0
            totalTime += solver.wall_time()
            print("Time = ", solver.WallTime(), " milliseconds")
            print("Total Time = ", str(totalTime), " milliseconds")
            #print()
        
            for b in range(0, num_vendors):
                xValues[b] = solver.Sum([x[b, j].solution_value()*orderArray[b][j] for j in range(num_orders)])
                oValues[b] = solver.Sum([x[b, j].solution_value() for j in range(num_orders)])
            
            for b in range(0, num_vendors):
                for j in range(num_orders):
                    xValues2[b] += int(x[b, j].solution_value()*orderArray[b][j])
                    oValues2[b] += int(x[b, j].solution_value())
            print(xValues2)
            for b in range(0, num_vendors):
                for d in range(0, 31):
                    for j in range(0, num_orders, 31):
                        xdValues2[b][d] += int(x[b, j + d].solution_value()*orderArray[b][j+d])
                        dValues2[b][d] += int(x[b, j + d].solution_value())        
        
        
            
            
            

            #Recording the results
            a = 0
            b = ""
            c = ""
            d = datetime.date
            e = datetime.time
            f = 0
            g = ""
            h = ""
            id = ""
            jd = ""
            k = ""
            l = ""
            for j in range(0,num_orders):
                for i in range(0,num_vendors):
                    orderCount += 1
                    if x[i, j].solution_value() > 0:
            
                        customerFrequency[run] = str(customers[str(orderPrint[int(j/31)].customerObject)].customerFrequency)
                        customerVendorHistory[run] =  str(customers[str(orderPrint[int(j/31)].customerObject)].vendorHistory)
                        customerGeneralHistory[run] =  str(customers[str(orderPrint[int(j/31)].customerObject)].generalCuisineHistory)
                        customerSpecificHistory[run] =  str(customers[str(orderPrint[int(j/31)].customerObject)].specificCuisineHistory)
                        customerPreferenceHistory[run] = str(customers[str(orderPrint[int(j/31)].customerObject)].customerNoServeList)

                        customers[str(orderPrint[int(j/31)].customerObject)].update_vendorHistory(str(vendorPrint[i].ID))
                        customers[str(orderPrint[int(j/31)].customerObject)].update_generalCuisineHistory(str(vendorPrint[i].generalCuisineID))
                        customers[str(orderPrint[int(j/31)].customerObject)].update_specificCuisineHistory(str(vendorPrint[i].specialtyCuisineID))
                        a = str(orderPrint[int(j/31)].ID)
                        orderID[run] = a
            
                        b = str(orderPrint[int(j/31)].customerObject)
                        orderCust[run] = b
            
                        c = str(orderPrint[int(j/31)].orderAddress)
                        orderAddress[run] = c
            
                        d = orderPrint[int(j/31)].orderDate
                        orderDate[run] = d
            
                        e = orderPrint[int(j/31)].orderTime
                        orderTime[run] = e
            
                        f = orderPrint[int(j/31)].numMeals
                        orderMeals[run] = f
            
                        g = str(vendorPrint[i].ID)
                        vendorID[run] = g
            
                        h = str(vendorPrint[i].generalCuisineID)
                        vendorGID[run] = h
            
                        id = str(vendorPrint[i].specialtyCuisineID)
                        vendorSID[run] = id
                        

            
                        run += 1
            print(run)
            print(orderCount)
            i=0
            j=0
            for v in sorted(firstVendors):
               if(i < num_vendors):
                   for k in nb:
                            for d in range(0,31):        
                                if(j<num_orders):
                                    if(penalty[i][j] >= 100):
                                        violatedConstraints['Preference'].add(orderPrint[int(j/31)].ID)
                                        penalty[i][j] -= 100
                                    if(penalty[i][j] >= 10):
                                        violatedConstraints['Specific'].add(orderPrint[int(j/31)].ID)
                                        penalty[i][j] -= 10
                                    if(penalty[i][j] >= 5):
                                        violatedConstraints['General']['Order'].add(orderPrint[int(j/31)].ID)
                                        
                                        penalty[i][j] -= 5
                                j += 1
                   i += 1
                   j =0
            i=0
        #once all of the optimization iterations are complete, populate a dataframe from the dictionaries to compute and display the results
        ordersOutput['orderID'] = [orderID[i] for i in range(0, run)]
        ordersOutput['orderCust'] = [orderCust[i] for i in range(0, run)]
        ordersOutput['orderAddress'] = [orderAddress[i] for i in range(0, run)]
        ordersOutput['orderDate'] = [orderDate[i] for i in range(0, run)]
        ordersOutput['orderTime'] = [orderTime[i] for i in range(0, run)]
        ordersOutput['orderMeals'] = [orderMeals[i] for i in range(0, run)]
        ordersOutput['vendorID'] = [vendorID[i] for i in range(0, run)]
        ordersOutput['vendorGID'] = [vendorGID[i] for i in range(0, run)]
        ordersOutput['vendorSID'] = [vendorSID[i] for i in range(0, run)]
        ordersOutput['customerFrequency'] = [customerFrequency[i] for i in range(0, run)]
        ordersOutput['customerVendorHistory'] = [customerVendorHistory[i] for i in range(0, run)]
        ordersOutput['customerGeneralHistory'] = [customerGeneralHistory[i] for i in range(0, run)]
        ordersOutput['customerSpecificHistory'] = [customerSpecificHistory[i] for i in range(0, run)]
        ordersOutput['customerPreferenceHistory'] = [customerPreferenceHistory[i] for i in range(0, run)]

        assignmentDF = pd.DataFrame(ordersOutput)
        
        #potential way of implementing xvalues and ovalues in the future, irrelevant at the moment
        print("" + str(len(ordersOutput['orderCust'])) + " orders processed")
        assignmentDF['orderDay'] = 0
        dateObj = datetime.date
        for i in range(0, len(assignmentDF)):
            dateObj = assignmentDF.iloc[i].orderDate
            assignmentDF.iloc[i].orderDay = dateObj.day - 1
        oValues2 = [0 for i in range(0, num_vendors)]
        xValues2 = [0 for i in range(0, num_vendors)]
        i=0
        for b in sorted(firstVendors):
            if(i < num_vendors):
                oValues2[i] = len(assignmentDF[assignmentDF.vendorID == b])
                selection3 = assignmentDF.vendorID != b
                a_sub = assignmentDF[~selection3]
                a_sub = a_sub.reset_index()
                for j in range(0, len(a_sub)):
                    xValues2[i] += int(a_sub.iloc[j].orderMeals)
            i += 1

        i=0
        dValues2 = [[0 for i in range(0, 31)] for i in range(0, num_vendors)]
        xdValues2 = [[0 for i in range(0, 31)] for i in range(0, num_vendors)]
        for b in sorted(firstVendors):
               if(i < num_vendors):
                    selection4 = assignmentDF.vendorID != b
                    a_sub = assignmentDF[~selection4]
                    a_sub = a_sub.reset_index()
                    for d in range(0, 31):
                                          
                                        dValues2[i][d] += len(a_sub[a_sub.orderDay == d])       
                                        selection5 = a_sub.orderDay != d
                                        d_sub = a_sub[~selection5]
                                        d_sub = d_sub.reset_index()
                                        for j in range(0, len(d_sub)):
                                            xdValues2[i][d] += d_sub.iloc[j].orderMeals
               i += 1
        #print to console for diagnostic purposes
        print(xValues2)
        print(oValues2)
        print(xdValues2)
        print(dValues2)
        
        #Determine the Final Costs
        j = 0
        volumeDeals = 0
        cost = [0.00 for c in range(0, len(vendors))]
        vendorFreq = [0 for v in range(0, len(vendors))]
        for b in sorted(firstVendors):
            if(j < num_vendors):
                vendorFreq[j] = xValues2[j]
                if(vendorFreq[j] > vendors[b].tierUpperBound[4]):
                       cost[j] = vendors[b].tierPrice[5]
                       volumeDeals += 1
                else:
                    for t in range(0, len(vendors[b].tierUpperBound)):
                
                        if(vendorFreq[j] < vendors[b].tierUpperBound[t]):
                                
                                cost[j] = vendors[b].tierPrice[t]
                                if(t>0):
                                    volumeDeals += 1
                                break
                            
            j +=1
            
        print(sorted(firstVendors))
        print(vendorFreq)
        print(cost)
        print(violatedConstraints['Preference'])
        print(violatedConstraints['Specific'])
        print(violatedConstraints['General']['Order'])
        
        
        
        totalRealCost = 0.00
        totalGMV = -.00
        
        for b in range(0, num_vendors):
            totalRealCost += vendorFreq[b]*cost[b]
            totalGMV += vendorFreq[b]*15

        #Populate the google spreadsheet with the answers
        print(totalRealCost)
        today = str(datetime.today())
        short = ""
        for v in range(8,17):
            short += today[v]
        sheetName = short + ' Summary'
        sum = wks.add_worksheet(sheetName, 500, 500)
        range_build = 'E1:F4'
        cell_list = sum.range(range_build)
        cell_list[0].value = "COGS"
        cell_list[1].value = totalRealCost
        cell_list[2].value = "GMV"
        cell_list[3].value = totalGMV
        cell_list[4].value = "%Ratio"
        cell_list[5].value = totalRealCost/totalGMV
        cell_list[6].value = "# of Volume Vendors"
        cell_list[7].value = volumeDeals
        sum.update_cells(cell_list)


        j = 0
        range_build = 'A1:C100'
        cell_list = sum.range(range_build)
        for b in sorted(firstVendors):
            cell_list[0 +j*3].value = b
            cell_list[1+j*3].value = vendorFreq[j]
            cell_list[2+j*3].value = cost[j]
            j+=1
        sum.update_cells(cell_list)
        
        i = 0
        range_build = 'A1:N1'
        cell_list = sh.range(range_build)
        cell_list[0].value = "ID"
        cell_list[1].value = "Customer"
        cell_list[2].value = "Address"
        cell_list[3].value = "Date"
        cell_list[4].value = "Time"
        cell_list[5].value = "Meals"
        cell_list[6].value = "Vendor"
        cell_list[7].value = "General Cuisine ID"
        cell_list[8].value = "Specific Cuisine ID"
        cell_list[9].value = "Customer Frequency"
        cell_list[10].value = "Customer Vendor History"
        cell_list[11].value = "Customer General History"
        cell_list[12].value = "Customer Specific History"
        cell_list[13].value = "Customer Preference History"

        sh.update_cells(cell_list)
        range_build = 'A2:N2000'
        cell_list = sh.range(range_build)
        for j in range(0, len(assignmentDF)):
            cell_list[0+j*14].value = assignmentDF.iloc[j].orderID
            cell_list[1+j*14].value = assignmentDF.iloc[j].orderCust
            cell_list[2+j*14].value = assignmentDF.iloc[j].orderAddress
            cell_list[3+j*14].value = assignmentDF.iloc[j].orderDate
            cell_list[4+j*14].value = assignmentDF.iloc[j].orderTime
            cell_list[5+j*14].value = assignmentDF.iloc[j].orderMeals
            cell_list[6+j*14].value = assignmentDF.iloc[j].vendorID
            cell_list[7+j*14].value = assignmentDF.iloc[j].vendorGID
            cell_list[8+j*14].value = assignmentDF.iloc[j].vendorSID
            cell_list[9+j*14].value = assignmentDF.iloc[j].customerFrequency
            cell_list[10+j*14].value = assignmentDF.iloc[j].customerVendorHistory
            cell_list[11+j*14].value = assignmentDF.iloc[j].customerGeneralHistory
            cell_list[12+j*14].value = assignmentDF.iloc[j].customerSpecificHistory
            cell_list[13+j*14].value = assignmentDF.iloc[j].customerPreferenceHistory

        sh.update_cells(cell_list)
        
        j = 1
        range_build = 'J1:J500'
        cell_list = sum.range(range_build)
        cell_list[0].value = 'Violated Preferences'
        for b in sorted(violatedConstraints['Preference']):
            if(j< len(violatedConstraints['Preference'])):
                cell_list[j].value = b
            j+=1
        sum.update_cells(cell_list)
        j = 1
        range_build = 'K1:K500'
        cell_list = sum.range(range_build)
        cell_list[0].value = 'Violated General Cuisine Rule'
        for b in sorted(violatedConstraints['General']['Order']):
            if(j< len(violatedConstraints['General']['Order'])):
                cell_list[j].value = b
            j+=1
        sum.update_cells(cell_list)
        j = 1
        range_build = 'L1:L500'
        cell_list = sum.range(range_build)
        cell_list[0].value = 'Violated Specific Cuisine Rule'
        for b in sorted(violatedConstraints['Specific']):
            if(j< len(violatedConstraints['Specific'])):
                cell_list[j].value = b
            j+=1
        sum.update_cells(cell_list)
        
        gasReturn = {'vendors' : sorted(firstVendors), 'vendorFreq' : vendorFreq, 'costs' : cost,  'totalCost' : totalRealCost}
        #todo: possibly give google apps script something back to work with for easier spreadsheet analysis by the operator        
        return gasReturn





if __name__=='__main__':
    application.debug = True
    application.run()    