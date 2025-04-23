from datetime import datetime
import json
import os
import requests
import sys
import operator
import tkinter
from tkinter import messagebox, Label, messagebox
from tkinter.ttk import Treeview, Style

def getFilePath(fileName):
    # check if the program is running as an exe
    if getattr(sys, 'frozen', False):
        scriptDir = os.path.dirname(sys.executable)
    else:
        scriptDir = os.path.dirname(os.path.abspath(__file__)) # gets the directory of this program
    filePath = os.path.join(scriptDir, fileName) # finds path for file
    return filePath

def viewPortfolio(mainGUI):
    port = updatePortfolio()
    if port == -1:
        return
        
    # make new window on top of the mainGUI
    portGUI = tkinter.Toplevel(mainGUI)
    portGUI.geometry("1600x600")
    portGUI.title("Crypto Portfolio Table")

    # defines the columns as all the keys
    columns = list(port[0].keys())
    tree = Treeview(portGUI, columns=columns, show="headings")

    # Grab config values
    configFilePath = getFilePath("config.json")
    if not os.path.exists(configFilePath):
        messagebox.showerror("Error", "No 'config.json' file found")
        return -1
    with open(configFilePath, "r+") as configFile:
        try:
            config = json.load(configFile)
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Config file error")
        highlightNum = config["portforlio_highlight_percent"]
        highlightColor = config["portfolio_highlight_color"]

     # Column sorting function
    def sortTrees(tree, col, reverse):
        # converts strings to floats if applicable
        def convert(input):
            try:
                return float(input)
            except:
                ValueError
                return input

        items = []
        for k in tree.get_children(""):
            item = tree.set(k, col)
            item2 = item.translate(str.maketrans("", "", "$%")) # removes % and $ from string
            fixedItem = item2.replace("N/A", "-1") # replaces N/A with a -1
            items.append((convert(fixedItem), k))

        #items = [(float(tree.set(k, col)), k) for k in tree.get_children("")] # (tree.set(k, col) gets the value of column 'col' for row 'k'. tree.get_children("") gets all the row IDs
        items.sort(reverse=reverse, key=lambda x: x[0]) # sort by the first item in each list pair
        for i, (_, k) in enumerate(items):
            tree.move(k, "", i) # moves trees to correct spots
            portPer = (tree.item(k, "values")[1])
            portPerFix = portPer.replace("%", "")
            tree.item(k, tags=("sold" if float(portPerFix) < (highlightNum * 100) else "even" if i % 2 == 0 else "odd"))

        tree.heading(col, command=lambda: sortTrees(tree, col, not reverse))

    # name, text display, width
    tree.heading("ticker", text="Ticker", command=lambda: sortTrees(tree, "ticker", True))
    tree.heading("portfolioPer", text="Portfolio", command=lambda: sortTrees(tree, "portfolioPer", True))
    tree.heading("netCoins", text="Amount", command=lambda: sortTrees(tree, "netCoins", True))
    tree.heading("currentPrice", text="Price", command=lambda: sortTrees(tree, "currentPrice", True))
    tree.heading("averageBuyPrice", text="Average Buy Price", command=lambda: sortTrees(tree, "averageBuyPrice", True))
    tree.heading("averageSellPrice", text="Average Sell Price", command=lambda: sortTrees(tree, "averageSellPrice", True))
    tree.heading("value", text="Value", command=lambda: sortTrees(tree, "value", True))
    tree.heading("netUSDCPNL", text="PnL", command=lambda: sortTrees(tree, "netUSDCPNL", True))
    tree.heading("netPerPNL", text="PnL", command=lambda: sortTrees(tree, "netPerPNL", True))
    tree.heading("unrlUSDCPNL", text="Unrealized PnL", command=lambda: sortTrees(tree, "unrlUSDCPNL", True))
    tree.heading("unrlPerPNL", text="Unrealized PnL", command=lambda: sortTrees(tree, "unrlPerPNL", True))
    tree.heading("realUSDCPNL", text="Realized PnL", command=lambda: sortTrees(tree, "realUSDCPNL", True))
    tree.heading("realPerPNL", text="Realized PnL", command=lambda: sortTrees(tree, "realPerPNL", True))
    tree.heading("totalCoinBuys", text="Coins Bought", command=lambda: sortTrees(tree, "totalCoinBuys", True))
    tree.heading("totalCoinSells", text="Coins Sold", command=lambda: sortTrees(tree, "totalCoinSells", True))
    tree.heading("totalUSDCBuys", text="USDC Spent", command=lambda: sortTrees(tree, "totalUSDCBuys", True))
    tree.heading("totalUSDCSells", text="USDC Received", command=lambda: sortTrees(tree, "totalUSDCSells", True))
    tree.heading("leverage", text="Leverage", command=lambda: sortTrees(tree, "leverage", True))
    tree.heading("sector", text="Sector", command=lambda: sortTrees(tree, "sector", True))
        
    style=Style()
    style.configure("Treeview.Heading", foreground="black", font=("Helvetica", 10, "bold"))

    tree.tag_configure("even", background="#f0f0f0")
    tree.tag_configure("odd", background="#ffffff")
    tree.tag_configure("sold", background=highlightColor)

    # column formatting
    for col in columns:
        tree.column(col, anchor="center", width=50)

    i = 0
    for asset in port:
        values = []
        for col in columns:
            value = asset[col]

            # checks if value is an int or float
            if isinstance(value, (int, float)):
                # only significant digits x - 1
                if col in ["currentPrice", "averageBuyPrice", "averageSellPrice"]:
                    value = float(f"{value:.{5-1}e}")
                # remove decimal spots
                if col in ["value", "netUSDCPNL", "realUSDCPNL", "totalUSDCBuys", "totalUSDCSells", "unrlUSDCPNL"]:
                    value = f"{value:.2f}"
                # convert to $
                if col in ["currentPrice", "averageBuyPrice", "averageSellPrice", "value", "netUSDCPNL", "realUSDCPNL", "totalUSDCBuys", "totalUSDCSells", "unrlUSDCPNL"]:
                    value = f"${value}"
            # convert to %
            if col in ["portfolioPer", "netPerPNL", "unrlPerPNL", "realPerPNL"]:
                value = f"{(value * 100):.2f}%"

            # makes a whole row of values
            values.append(value)
            i += 1
        # adds all those values to the end of a row   
        tree.insert("", tkinter.END, values=values, tags=("sold" if asset["portfolioPer"] < .001 else "even" if i % 2 == 0 else "odd"))

    # default sorts the tree by portfolio percentage
    sortTrees(tree, "portfolioPer", True)

    # format the tree
    tree.pack(expand=True, fill="both")

    # Bottom calculations
    portUnrlUSDCPNL = 0
    portRealUSDCPNL = 0
    portTotalUSDCBuys = 0
    portValue = 0

    for asset in port:
        portUnrlUSDCPNL += asset["unrlUSDCPNL"]
        portRealUSDCPNL += asset["realUSDCPNL"]
        portTotalUSDCBuys += asset["totalUSDCBuys"]
        portValue += asset["value"]

    portUnrlPerPNL = portUnrlUSDCPNL / portTotalUSDCBuys
    portRealPerPNL = portRealUSDCPNL / portTotalUSDCBuys
    portUSDCPNL = portUnrlUSDCPNL + portRealUSDCPNL
    portPerPNL = portUSDCPNL / portTotalUSDCBuys

    # Bottom tree initializing 
    tree2 = Treeview(portGUI, columns=columns, show="headings")
    col2Headers = ["", "", "", "", "", "", "Total Value:", "PnL:", "", "Unrealized PnL:", "", "Realized PnL", "", "", "", "", "", "", ""]
    for col, header in zip(columns, col2Headers):
        tree2.heading(col, text=header)
        tree2.column(col, anchor="center", width=50)

    values2 = ["", "", "", "", "", "", f"${portValue:.2f}", f"${portUSDCPNL:.2f}", f"{(portPerPNL * 100):.2f}%", f"${portUnrlUSDCPNL:.2f}", f"{(portUnrlPerPNL * 100):.2f}%", f"${portRealUSDCPNL:.2f}", f"{(portRealPerPNL * 100):.2f}%", "", "", "", "", "", "", ""]
    tree2.insert("", tkinter.END, values=values2)

    tree2.pack(expand=False, fill="both")

def updatePortfolio():
    # find path for transactions file
    file_path = getFilePath("transactions.json")

    # checks if 'transactions.json' exists
    if not os.path.exists(file_path):
        messagebox.showerror("Error", "No 'transactions.json' file found")
        return -1

    # Try to open 'transactions.json'
    with open(file_path, "r") as file: # opens the file for reading, with closes the files when done
        try:
            transactions = json.load(file) # reads the existing data on the file to a temporary dictionary
        except json.JSONDecodeError: # if the file is empty
            messagebox.showerror("Error", "Could not read transactions.json")
            return -1
        
        # try to open 'portfolio.json'
        portFilePath = getFilePath("portfolio.json")
        with open(portFilePath, "r+") as file2: # opens the file for reading, with closes the files when done
            try:
                oldPort = json.load(file2) # reads the existing data on the file to a temporary dictionary
            except json.JSONDecodeError: # if the file is empty
                messagebox.showerror("Error", "No 'portfolio.json' file found")
                return -1

            port = []    
            i = 1 # extra index since USDC is at 0
            # start with USDC value
            totalPortfolioValue = oldPort[0]["value"]

            # Keep stablecoin balance
            port.append({
                "ticker": "USDC",
                "portfolioPer": 0,
                "netCoins": oldPort[0]["netCoins"],
                "currentPrice": 1,
                "averageBuyPrice": 1,
                "averageSellPrice": "N/A",
                "value": oldPort[0]["value"],
                "netUSDCPNL": 0,
                "netPerPNL": 0,
                "unrlUSDCPNL": 0,
                "unrlPerPNL": 0,
                "realUSDCPNL": 0,
                "realPerPNL": 0,
                "totalCoinBuys": 0,
                "totalCoinSells": 0,
                "totalUSDCBuys": 0,
                "totalUSDCSells": 0,
                "leverage": 1,
                "sector": "Stablecoin"
            })

            for key, txList in transactions.items(): # loops through the dictionary
                # Checks if the ticker is in the portfolio
                port.append({
                    "ticker": key,
                    "portfolioPer": 0,
                    "netCoins": 0,
                    "currentPrice": 0,
                    "averageBuyPrice": 0,
                    "averageSellPrice": 0,
                    "value": 0,
                    "netUSDCPNL": 0,
                    "netPerPNL": 0,
                    "unrlUSDCPNL": 0,
                    "unrlPerPNL": 0,
                    "realUSDCPNL": 0,
                    "realPerPNL": 0,
                    "totalCoinBuys": 0,
                    "totalCoinSells": 0,
                    "totalUSDCBuys": 0,
                    "totalUSDCSells": 0,
                    "leverage": 1,
                    "sector": ""
                    })
                # Steals price data from old portfolio
                for asset in oldPort:
                    if key == asset["ticker"]:
                        port[i]["currentPrice"] = asset["currentPrice"]
                # loops through the transactions in each ticker
                for tx in txList:
                    # checks if its a buy transaction
                    if tx["transactionType"] == "bought":
                        port[i]["totalCoinBuys"] += tx["coinAmount"]
                        port[i]["totalUSDCBuys"] += tx["usdcAmount"]
                    # sell transactions
                    elif tx["transactionType"] == "sold":
                        port[i]["totalCoinSells"] += tx["coinAmount"]
                        port[i]["totalUSDCSells"] += tx["usdcAmount"]

                # quit program if any of the values turn negative
                port[i]["netCoins"] = port[i]["totalCoinBuys"] - port[i]["totalCoinSells"]
                if port[i]["netCoins"] < 0:
                    messagebox.showerror("Error", f"Negative value calculated for {key}.")
                    return -1
                # calculations
                port[i]["averageBuyPrice"] = port[i]["totalUSDCBuys"] / port[i]["totalCoinBuys"]
                try:
                    port[i]["averageSellPrice"] = port[i]["totalUSDCSells"] / port[i]["totalCoinSells"]
                except ZeroDivisionError:
                    port[i]["averageSellPrice"] = "N/A"
                port[i]["value"] = port[i]["netCoins"] * port[i]["currentPrice"]
                port[i]["unrlUSDCPNL"] = (port[i]["currentPrice"] - port[i]["averageBuyPrice"]) * port[i]["netCoins"]
                try:
                    port[i]["unrlPerPNL"] = port[i]["unrlUSDCPNL"] / (port[i]["averageBuyPrice"] * port[i]["netCoins"])
                except ZeroDivisionError:
                    port[i]["unrlPerPNL"] = 0
                try:
                    port[i]["realUSDCPNL"] = (port[i]["averageSellPrice"] - port[i]["averageBuyPrice"]) * port[i]["totalCoinSells"]
                except TypeError:
                    port[i]["realUSDCPNL"] = 0
                try:
                    port[i]["realPerPNL"] = (port[i]["averageSellPrice"] - port[i]["averageBuyPrice"]) / port[i]["averageBuyPrice"]
                except TypeError:
                    port[i]["realPerPNL"] = 0

                port[i]["netUSDCPNL"] = port[i]["unrlUSDCPNL"] + port[i]["realUSDCPNL"]  
                port[i]["netPerPNL"] = port[i]["netUSDCPNL"] / port[i]["totalUSDCBuys"]
                totalPortfolioValue += port[i]["value"]
                i += 1

            for index in port:
                index["portfolioPer"] = index["value"] / totalPortfolioValue

            file2.seek(0) # goes to beginning of file
            json.dump(port, file2, indent=4) # writes updated port list to file
            file2.truncate() # deletes any leftover data from file
    return port      
            
def updatePrices(mainGUI):
    def grabInput():
        # make sure a positive number was entered
        try:
            customPrice = float(entry1.get())
        except ValueError:
            messagebox.showerror("Error", "Must enter a positive number")
            return
        if customPrice <= 0:
            messagebox.showerror("Error", "Must enter a positive number")
            return
        
        asset["currentPrice"] = customPrice
        
        addPriceGUI.destroy()

    portFilePath = getFilePath("portfolio.json")
    configFilePath = getFilePath("config.json")

    with open(configFilePath, "r+") as configFile:
        config = json.load(configFile)
        api_key = config["api_key"]

    # checks if 'portfolio.json' exists
    if not os.path.exists(portFilePath):
        messagebox.showerror("Error", "No 'portfolio.json' found")
        return
    # checks if 'portfolio.json' has data
    with open(portFilePath, "r+") as file: # opens the file for reading/writing
        try:
            port = json.load(file) # reads the existing data on the file to a temporary dictionary
        except json.JSONDecodeError: # if the file is empty
            messagebox.showerror("Error", "No 'portfolio.json' found")
            return
        
        for asset in port: # loops through the dictionary
            # Only if still holding at least 1% of your buys
            if not asset["totalCoinSells"] or abs(asset["totalCoinBuys"] - asset["totalCoinSells"]) > .01 * asset["totalCoinBuys"]:
                # Live price updating
                parameters = {
                    "symbol": asset["ticker"],
                    "convert": "USD"  
                }
                headers = {
                    "X-CMC_PRO_API_KEY": api_key,
                    "Accept": "application/json"
                    }
                response = requests.get("https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest", headers=headers, params=parameters)        
                dat = response.json()
                # checks if no data was retrieved
                if dat["status"]["error_code"] != 0:
                    messagebox.showerror("Error", f"{dat['status']['error_message']}")
                    return
                else:
                    try:
                        asset["currentPrice"] = dat["data"][asset["ticker"]]["quote"]["USD"]["price"]
                    except KeyError:
                        if messagebox.askyesno("Warning", f"Error retrieving price data for {asset['ticker']}. Would you like to enter its price manually?"):
                            addPriceGUI = tkinter.Toplevel(mainGUI)
                            addPriceGUI.title("Transactions Log")

                            text1 = Label(addPriceGUI, text=f"Enter price for {asset['ticker']}:")
                            entry1 = tkinter.Entry(addPriceGUI)

                            addPriceGUI.bind("<Return>", lambda event: grabInput())
                            submitButton = tkinter.Button(addPriceGUI, text="Submit", command=lambda: grabInput())

                            text1.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
                            entry1.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
                            submitButton.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

                            # Wait until window is destroyed to continue
                            addPriceGUI.wait_window()

        file.seek(0) # goes to beginning of file
        json.dump(port, file, indent=4) # writes updated port list to file
        file.truncate() # deletes any leftover data from file   
        messagebox.showinfo("Done!", "Prices successfully updated")        

def addTransaction(mainGUI):
    # checks if 'portfolio.json' exists
    filePath2 = getFilePath("portfolio.json")
    if not os.path.exists(filePath2):
        messagebox.showerror("Error", "No 'portfolio.json' found")
        return

    # create new window
    addTxGUI = tkinter.Toplevel(mainGUI)
    addTxGUI.geometry("250x150")
    addTxGUI.title("Add a Transaction")

    # create text labels
    ques1 = Label(addTxGUI, text='Buy or Sell:')
    ques2 = Label(addTxGUI, text='Ticker:')
    ques3 = Label(addTxGUI, text='# of Coins:')
    ques4 = Label(addTxGUI, text='USDC:')

    # create text entries
    entry1 = tkinter.Entry(addTxGUI)
    entry2 = tkinter.Entry(addTxGUI)
    entry3 = tkinter.Entry(addTxGUI)
    entry4 = tkinter.Entry(addTxGUI)

    # create grid
    ques1.grid(row=0, column=0, padx=5, pady=5, sticky="e") # pad = space around grid, sticky is orientation
    entry1.grid(row=0, column=1, padx=5, pady=5)
    ques2.grid(row=1, column=0, padx=5, pady=5, sticky="e")
    entry2.grid(row=1, column=1, padx=5, pady=5)
    ques3.grid(row=2, column=0, padx=5, pady=5, sticky="e")
    entry3.grid(row=2, column=1, padx=5, pady=5)
    ques4.grid(row=3, column=0, padx=5, pady=5, sticky="e")
    entry4.grid(row=3, column=1, padx=5, pady=5)

    def grabInput():
        file_path = getFilePath("transactions.json") # finds path for transaction file
        with open(file_path, "a+") as file: # opens the file in append and read mode, with closes the files when done. Creates the file if it doesn't exist
            try:
                file.seek(0)
                transactions = json.load(file) # reads the existing data on the file to a temporary dictionary
            except json.JSONDecodeError: # if the file is empty or doesn't exist
                transactions = {} # empty dictionary
                messagebox.showwarning("Warning", "No transactions.json file found, creating new one")

            with open(filePath2, "r+") as file2:
                try:
                    port = json.load(file2)
                except json.JSONDecodeError:
                    messagebox.showerror("Error", "Could not read 'portfolio.json'")
                    return
            
                # gets input and stores in vars
                transactionType = entry1.get().lower()

                ticker = entry2.get().upper()
                
                try:
                    usdcAmount = float(entry4.get())
                except ValueError:
                    messagebox.showerror("Error", "Must enter a positive number in 'USDC'")
                    return
                if usdcAmount <= 0:
                    messagebox.showerror("Error", "Must enter a positive number in 'USDC'")
                    return

                if transactionType not in ("buy", "sell"):
                    messagebox.showerror("Error", "Must be a 'Buy' or 'Sell' transaction.")
                    return
                
                # change stablecoin balance
                ops = {
                    "+": operator.add,
                    "-": operator.sub
                }
                if ticker == "USDC": # edge case
                    if transactionType == "buy":
                        choice = "increase"
                        op = "+"
                    else:
                        choice = "decrease"
                        op = "-"
                    newBalance = ops[op](port[0]["netCoins"], usdcAmount)
                    if messagebox.askyesno("Info", f"You inputted 'USDC' for the ticker. Would you like to {choice} your stablecoin balance by {usdcAmount}? (New USDC balance: {newBalance})"):
                        if choice == "decrease" and port[0]["netCoins"] - usdcAmount < 0:
                            messagebox.showerror("Error", "Can't have a negative USDC balance")
                            return
                        else:
                            if transactionType == "buy":
                                port[0]["netCoins"] += usdcAmount
                                port[0]["value"] += usdcAmount
                            else:
                                port[0]["netCoins"] -= usdcAmount
                                port[0]["value"] -= usdcAmount
                    else:
                        return
                else: # normal transactions
                    # coinAmount check
                    try:
                        coinAmount = float(entry3.get())
                    except ValueError:
                        messagebox.showerror("Error", "Must enter a positive number in '# of Coins'")
                        return
                    if coinAmount <= 0:
                        messagebox.showerror("Error", "Must enter a positive number in '# of Coins'")
                        return
                    
                    # update USDC amount
                    if transactionType == "buy":
                        transactionType = "bought"
                        port[0]["netCoins"] -= usdcAmount
                        port[0]["value"] -= usdcAmount
                    else:
                        transactionType = "sold"
                        port[0]["netCoins"] += usdcAmount
                        port[0]["value"] += usdcAmount

                    timeOfTransaction = datetime.now().isoformat() # gets current date and time from datetime module, converts to ISO format for json
                    newTransaction = {"transactionType": transactionType, "coinAmount": coinAmount,"usdcAmount": usdcAmount, "dateOfTransaction": timeOfTransaction}
                    if ticker not in transactions:
                        transactions[ticker] = [] # if first transaction with ticker, initializes
                    transactions[ticker].append(newTransaction) # adds new transaction to the ticker

                file2.seek(0)
                json.dump(port, file2, indent=4) # write updated 'portfolio.json'
                file2.truncate()

            file.seek(0) # goes to beginning of file
            file.truncate(0) # deletes any data from file
            json.dump(transactions, file, indent=4) # writes updated 'transactions' dictionary to file

            addTxGUI.destroy()

    # Press the submit button to grab the 4 inputs
    addTxGUI.bind("<Return>", lambda event: grabInput())
    submitButton = tkinter.Button(addTxGUI, text="Submit", command=grabInput)
    submitButton.grid(row=4, column=1, padx=5, pady=5)

def viewTransactions(mainGUI):
    file_path = getFilePath("transactions.json") # finds path for transaction file

    # checks if 'transactions.json' exists
    if not os.path.exists(file_path):
        messagebox.showerror("Error", "No 'transactions.json' found")
        return

    with open(file_path, "r") as file: # opens the file for reading and closes the files when done
        try:
            transactions = json.load(file) # reads the existing data on the file to a temporary dictionary
        except json.JSONDecodeError: # if the files is empty
            messagebox.showerror("Error", "Could not read 'transactions.json'")
            return
        
        viewTransGUI = tkinter.Toplevel(mainGUI)
        viewTransGUI.title("Transactions Log")

        # create text labels
        text1 = Label(viewTransGUI, text="'All' or specific ticker:")
        text2 = Label(viewTransGUI, text="# of transactions:")

        # create entry boxes
        entry1 = tkinter.Entry(viewTransGUI)
        entry2 = tkinter.Entry(viewTransGUI)

        # create grid
        text1.grid(row=0, column=0, padx=5, pady=5)
        text2.grid(row=1, column=0, padx=5, pady=5)
        entry1.grid(row=0, column=1, padx=5, pady=5)
        entry2.grid(row=1, column=1, padx=5, pady=5)

        def grabInput(transactions):
            # make sure numOfEntries is an integer
            try:
                numOfEntries = int(entry2.get())
            except ValueError:
                messagebox.showerror("Error", "Enter an integer")
                return

            # tickerInput checks
            tickerInput = entry1.get().upper()
            if tickerInput != "ALL" and tickerInput not in transactions:
                messagebox.showerror("Error", "Invalid ticker, try again")
                return
            
            # New window
            transactionsGUI = tkinter.Toplevel(mainGUI)
            transactionsGUI.title("Transactions Log")

            # Initializes tree for table
            tree = Treeview(transactionsGUI, columns=["Index", "Transaction Type", "Ticker", "Coin Amount", "USDC Amount", "Average Price", "Time of Transactions"], show="headings")
            for i in ["Index", "Transaction Type", "Ticker", "Coin Amount", "USDC Amount", "Average Price", "Time of Transactions"]:
                tree.heading(i, text=i)

            # header formatting
            style=Style()
            style.configure("Treeview.Heading", foreground="black", font=("Helvetica", 10, "bold"))

            viewTransGUI.destroy()
                
            def calculations(index, ticker, transaction):
                avgP = transaction["usdcAmount"] / transaction["coinAmount"] # average price for the transaction
                averagePrice = f"${float(f'{avgP:.{5-1}e}')}" # only 5 significant digits
                dateAndTime = datetime.strptime(transaction["dateOfTransaction"], "%Y-%m-%dT%H:%M:%S.%f") # formats the dateOfTransaction string into a dateTime object
                formattedTime = dateAndTime.strftime("%m/%d/%y %I:%M %p") # turns dateTime into a readable string

                return [index + 1, transaction['transactionType'], ticker, transaction['coinAmount'], f"${transaction['usdcAmount']}", averagePrice, formattedTime]

            if tickerInput == "ALL":
                # puts all the nested transactions into a single list
                allTransactions = []
                for key, transactions in transactions.items(): # loops through the dictionary
                    for transaction in transactions: # loops through the transactions in each ticker
                        allTransactions.append((key, transaction)) # adds the transaction

                # sorts all transactions by the lambda function, which converts the transaction time to a datetime variable
                allTransactions.sort(
                    key=lambda x: datetime.strptime(x[1]["dateOfTransaction"], "%Y-%m-%dT%H:%M:%S.%f"), # sorts
                    reverse=True) # sorts in descending order

                for index, (ticker, transaction) in enumerate(allTransactions[:numOfEntries]): # loops through the ticker and transaction for "index" times
                    # formats the tree for each row
                    tree.insert("", tkinter.END, values=calculations(index, ticker, transaction), tags="even" if index % 2 == 0 else "odd")

            elif tickerInput in transactions:
                # selects the last n elements of the list
                recentTransactions = transactions[tickerInput][-numOfEntries:]

                # reverse the transactions list, newest first
                for i, transaction in enumerate(reversed(recentTransactions)):
                    tree.insert("", tkinter.END, values=calculations(i, tickerInput, transaction), tags="even" if i % 2 == 0 else "odd")            

            tree.tag_configure("even", background="#f0f0f0")
            tree.tag_configure("odd", background="#ffffff")
            tree.pack()

        viewTransGUI.bind("<Return>", lambda event: grabInput(transactions))
        submitButton = tkinter.Button(viewTransGUI, text="Submit", command=lambda: grabInput(transactions))
        submitButton.grid(row=2, column=1, padx=5, pady=5)

def newPort(filePath): # creates a new portfolio file if there is none
    answer = messagebox.askyesno("Missing file", "You need a 'portfolio.json' file, would you like to create one?")
    if answer:
        with open(filePath, "w") as file:
            pass

        popupGUI = tkinter.Toplevel()
        popupGUI.title("Initial Stablecoins")
        text1 = Label(popupGUI, text="How much USDC do you currently have?")
        text1.pack()
        entry1 = tkinter.Entry(popupGUI)
        entry1.pack()

        def submit():
            # gets a valid input
            try:
                stableBal = float(entry1.get())
                if stableBal > 0:
                    port = []
                    port.append({
                    "ticker": "USDC",
                    "portfolioPer": 0,
                    "netCoins": stableBal,
                    "currentPrice": 1,
                    "averageBuyPrice": 1,
                    "averageSellPrice": "N/A",
                    "value": stableBal,
                    "netUSDCPNL": 0,
                    "netPerPNL": 0,
                    "unrlUSDCPNL": 0,
                    "unrlPerPNL": 0,
                    "realUSDCPNL": 0,
                    "realPerPNL": 0,
                    "totalCoinBuys": 0,
                    "totalCoinSells": 0,
                    "totalUSDCBuys": 0,
                    "totalUSDCSells": 0,
                    "leverage": 1,
                    "sector": "Stablecoin"
                    })
                    with open(filePath, "w") as file:
                        json.dump(port, file, indent=4)
                    popupGUI.destroy()
                else:
                    messagebox.showerror("Error", "Must enter a number bigger than 0")
            except ValueError:
                messagebox.showerror("Error", "Must enter a number")

        popupGUI.bind("<Return>", lambda event: submit())
        submitButton = tkinter.Button(popupGUI, text="Submit", command=lambda: submit())
        submitButton.pack()

def newConfig(configFP):
    # creates file
    with open(configFP, "w") as file:
        pass

    config = {
    "api_key": "your_api_key_here",
    "portforlio_highlight_percent": 0.1,
    "portfolio_highlight_color": "light blue"
    }

    # saves config to 'config.json'
    with open(configFP, "w") as file:
        file.seek(0) # goes to beginning of file
        json.dump(config, file, indent=4)
        messagebox.showinfo("Update", "New 'config.json' file has been created, please update the API key for live price updates. Also feel free to view the other customizable options.")

def windowSize(GUI, x, y):
    screenWidth = GUI.winfo_screenwidth()
    screenHeight = GUI.winfo_screenheight()
    # sets the window size to x% of the screen size
    windowWidth = int((screenWidth * x))
    windowHeight = int((screenHeight * y))
    # finds the middle position and rounds the number down
    xPos = (screenWidth - windowWidth) // 2
    yPos = (screenHeight - windowWidth) // 2

    GUI.geometry(f"{windowWidth}x{windowHeight}+{xPos}+{yPos}")

    return windowWidth

def main():
    # make the main window in Tkinter and get width and height of the window
    mainGUI = tkinter.Tk(screenName=None, baseName=None, className="Crypto Portfolio", useTk=1)

    # set window size and save width
    windowWidth = windowSize(mainGUI, .2, .35)

    # both height and width cannot be resized
    mainGUI.resizable(False, False)

    # make the main label
    title = Label(mainGUI, text='Crypto Portfolio', font=("Helvetica", int(windowWidth * 0.1)))

    # Buttons
    viewPort = tkinter.Button(mainGUI, text="View Portfolio", font=("Helvetica", int(windowWidth * .06)), width=20, command=lambda: viewPortfolio(mainGUI))
    addTx = tkinter.Button(mainGUI, text="Add Transaction", font=("Helvetica", int(windowWidth * .06)), width=20, command=lambda: addTransaction(mainGUI))
    updatePrice = tkinter.Button(mainGUI, text="Update Prices", font=("Helvetica", int(windowWidth * .06)), width=20, command=lambda: updatePrices(mainGUI))
    viewStuff = tkinter.Button(mainGUI, text="View Transactions", font=("Helvetica", int(windowWidth * .06)), width=20, command=lambda: viewTransactions(mainGUI))
    quit = tkinter.Button(mainGUI, text="Stop Program", font=("Helvetica", int(windowWidth * .06)), width=20, command=mainGUI.destroy)

    title.pack()
    viewPort.pack()
    addTx.pack()
    updatePrice.pack()
    viewStuff.pack()
    quit.pack()

    # check if 'portfolio.json' exists
    portFilePath = getFilePath("portfolio.json")
    if not os.path.isfile(portFilePath):
        newPort(portFilePath)

    # check if 'config.json' exists
    configFilePath = getFilePath("config.json")
    if not os.path.isfile(configFilePath):
        newConfig(configFilePath)

    mainGUI.mainloop()

main()
