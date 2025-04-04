from flask import Flask, render_template, redirect, session, request, send_from_directory
import random as rand
import sqlite3 
from functools import wraps
from datetime import datetime
import logging
import pandas as pd
from pandasql import sqldf
import json

app = Flask(__name__, template_folder="templates")
app.secret_key = "HI"

order = {}



def initMenu():

    conn = sqlite3.connect("db/pizzadb.db")

    cursor = conn.cursor()

    cursor.execute('SELECT * FROM Item;')

    rows = cursor.fetchall()

    clearMenu()
        
    for row in rows:            
        addMenuItem(row[0], row[1], row[2], row[3])

    conn.commit()
    conn.close()



def addItemToReceipt(receiptNo, orderID, itemID, itemName, itemPrice):
    conn = sqlite3.connect("db/pizzadb.db")
    cursor = conn.cursor()

    cursor.execute("INSERT INTO ReceiptItems (ReceiptNo, OrderID, ItemID, ItemName, ItemCost) VALUES (?, ?, ?, ?, ?);",
                   (receiptNo, orderID, itemID, itemName, itemPrice))
    

    conn.commit()
    conn.close()

def addReceiptToDatabase(receiptNo, orderID, cart):

    for items in cart.getItems():
        item = menuData[items]
        addItemToReceipt(receiptNo, orderID, item.getItemID(), item.getItemName(), item.getPrice())


def addOrderToDatabase(orderID, receiptNo, date, firstName, lastName, cardNo, totalCost, status):
    conn = sqlite3.connect("db/pizzadb.db")
    cursor = conn.cursor()

    cursor.execute("INSERT INTO Orders (OrderID, ReceiptNo, Date, FirstName, LastName, CardNo, TotalCost, ACTIVE) VALUES (?,?,?,?,?,?,?,?);",
                   (orderID, receiptNo, date, firstName, lastName, cardNo, totalCost, status))

    conn.commit()
    conn.close()


class Order:

    

    def __init__(self, orderID, cart):

        #KINDA LIKE ENUMS
        self.PREPARING = "PREPARING"
        self.BAKING = "BAKING"
        self.BOXING = "BOXING"
        self.DELIVERY = "DELIVERY"

        #STUFF
        self.cart = cart
        self.orderID = orderID
        self.total = cart.total()
        self.status = self.PREPARING
        self.estimated_delivery = 0 #fix this later     
    
    def getStatus(self):
        return self.status
    
    def getCart(self):
        return self.cart


    
class MenuItem:

    def __init__(self, itemID, itemName, price, photoURL=None):
        self.itemID = itemID
        self.itemName = itemName
        self.price = price
        self.photoURL = photoURL

    def getPrice(self):
        return self.price
    
    def getItemName(self):
        return self.itemName

    def getItemID(self):
        return self.itemID    

    def getPhoto(self):
        return self.photoURL

menuData = {'123': MenuItem(123, "Cheese Pizza", 10.99, "static/cheese_pizza.png"),
        '232': MenuItem(232, "Pepperoni Pizza", 11.99, "static/pepperoni_pizza.png"),
        '443': MenuItem(443, "Sausage Pizza", 11.99, "static/sausage_pizza.png"),
        '702': MenuItem(702, "BBQ Chicken Pizza Pizza", 13.99),
        '331': MenuItem(331, "Calzone", 7.99), 
        '221': MenuItem(221, "Brownie", 8.99) }


def addMenuItem(itemID, itemName, itemCost, itemImageURL):
    print(itemImageURL)
    menuData.update({str(itemID): MenuItem(str(itemID), itemName, itemCost, itemImageURL)})
    print(menuData)

def clearMenu():

    menuData.clear()

class Cart:

    def __init__(self):
        self.cart = []
    def addToCart(self, id):
        self.cart.append(id)
    
    def getItems(self):
        return self.cart
    
    def serializeItems(self):
        serial = ""
        for item in self.cart:
            serial+=item

        return serial 
    
    def removeItem(self, id: str):
        chopList = ""

        for i in range(len(self.cart)):
            if(str(self.cart[i]) == id):
                chopList = i

        self.cart.pop(chopList)




    def total(self):
        totalPrice = 0.00
        for item in self.cart:
            totalPrice+=menuData[item].getPrice()
    
        return totalPrice

    def isEmpty(self):

        if(self.cart == []):
            return True

        return False
    def getCart(self):
        return self.cart 

    def setCart(self, cart):
        self.cart = cart
    def clear(self):
        self.cart = []

carts = {}

initMenu()

def verifyCarts():
    try:
        x = session['cartID']
        x = carts[session['cartID']]

    except:
        session['cartID'] = gen_ran_chars(12)
        carts[session['cartID']] = Cart()

####

@app.route("/")
def hello_world():
    return render_template("index.html")

@app.route("/menu")
def menu():

    menu = menuData

    return render_template('menu.html', menu=menu)

@app.route("/cart")
def cart():
    verifyCarts()
    cart =  carts[session['cartID']]
    menu = menuData
    totalCost = cart.total()

    return render_template("cart.html", cart=cart, totalcost=totalCost, menu=menu)

def gen_ran_chars(length):
    c = ""
    rands = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    for i in range(length):
        c+=rands[rand.randint(0,len(rands) - 1)]
    
    return c

def gen_ran_numbers(length):
    c = ""
    rands = "1234567890"
    for i in range(length):
        c+=rands[rand.randint(0,len(rands) - 1)]
    
    return c

@app.route("/addToCart")
def addToCart():
    
    verifyCarts()
    itemID = request.args.get("id")
    carts[session['cartID']].addToCart(str(itemID))

    return redirect("/menu")

@app.route("/removeFromCart")
def removeFromCart():
    verifyCarts()
    itemID = request.args.get("id")
    carts[session['cartID']].removeItem(str(itemID))

    return redirect("cart")

@app.route("/checkout")
def checkout():
    if(carts[session['cartID']].isEmpty()):
        return redirect("cart")
    return render_template('checkout.html')

@app.route("/processOrder")
def processOrder():
    first_name = request.args.get("first_name")
    last_name = request.args.get("last_name")
    address = request.args.get("address")
    card_no = request.args.get("cardno")
    cvv = request.args.get("cvv")
    cardholder_name = request.args.get("cardhold_name")
    cardholder_zipcode = request.args.get("cardhold_zip")

    #validation
    
    if(len(first_name) < 1):
        return redirect("checkout")
    if(len(last_name) < 1):
        return redirect("checkout")
    
    if(len(card_no) != 16):
        return redirect("checkout")
    if(len(cvv) != 3):
        return redirect("checkout")
    
    receiptNo = gen_ran_numbers(10)
    orderID = gen_ran_chars(35)
    totalCost = carts[session['cartID']].total()
    

    now = datetime.now()
    date = now.strftime('%Y-%m-%d %H:%M:%S')


    addOrderToDatabase(orderID, receiptNo, date, first_name, last_name, card_no, totalCost, True) #TRUE basically meaning the order is active which by default should be
                                                                                                  #since the order was just made 
    addReceiptToDatabase(receiptNo, orderID, carts[session['cartID']])

    session['currentOrder'] = orderID
    newCart = Cart()
    newCart.setCart(carts[session['cartID']].getCart())
    order[orderID] = Order(orderID,newCart)
    carts[session['cartID']].clear()

    return redirect('/order') #unsafe fix later

@app.route("/order")
def orderRedirect():
    try:
        return redirect('/order/'+str(session['currentOrder'])) # THIS IS NOT SAFE FIX LATER
    except:
        return redirect('/')

    return "HI"

@app.route("/order/<orderID>")
def orderView(orderID=None):

    try:
        currentOrder = order[orderID]
        orderStatus = currentOrder.getStatus()
        print(orderStatus)
        #stuff from cart
        orderCart = currentOrder.getCart()
        totalCost = orderCart.total()
        orderItems = orderCart.getItems()

        return render_template('orderStatusPage.html', orderItems=orderItems, menu=menuData, totalcost=totalCost, orderstatus=orderStatus)
    
    except Exception as e:
        print(e)
    
    return redirect('/')



#ERROR HANDLING
@app.errorhandler(404)
def notFound(e):
    return render_template("error/404.html")

@app.errorhandler(500)
def notFound(e):
    return render_template("error/500.html")



#ADMIN [TO DO LATER]

@app.route("/admin")
def admin():

    if(session['adminAuth']):
        return render_template('admin/admin.html')
    
    return redirect("/admin/login")

@app.route('/admin/res/<path:filename>')
def admin_res(filename):
    if(session['adminAuth']):
        return send_from_directory('restricted', filename)
    
    return 404

@app.route("/admin/logout")
def admin_logout():
    session['adminAuth'] = False

    return redirect('/admin/login')

@app.route("/admin/login")
def admin_login():
    
    return render_template('admin/login.html')

@app.route("/admin/actions/deleteMenuItem/<itemID>")
def admin_deletemenuitem(itemID):
    if(session['adminAuth']):
        print("Request received")
        conn = sqlite3.connect("db/pizzadb.db")
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM Item WHERE ItemID = ?;", (itemID,))

        conn.commit()
        conn.close()

        return "200"

    return redirect('/admin/login')
@app.route("/admin/actions/deleteOrder/<orderID>")
def admin_deleteorder(orderID):

    if(session['adminAuth']):
        print("Request received")
        conn = sqlite3.connect("db/pizzadb.db")
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM Orders WHERE OrderID = ?;", (orderID,))

        conn.commit()
        conn.close()

        return "test"

    return redirect('/admin/login')

@app.route("/admin/actions/updateMenu")
def updateMenu():

    if(session['adminAuth']):
        ItemID = request.args.get('ItemID')
        ItemName = request.args.get("ItemName")
        ItemCost = request.args.get("ItemCost")
        ItemImageURL = request.args.get("ItemImageURL")

        conn = sqlite3.connect("db/pizzadb.db")
        cursor = conn.cursor()

        cursor.execute("UPDATE Item SET ItemName = ?, ItemCost = ?, ItemImageURL=? WHERE ItemID = ?;", (ItemName, ItemCost,ItemImageURL, ItemID))

        conn.commit()
        conn.close()
    
    return "200"


@app.route("/admin/actions/updateOrder")
def admin_updateorder():

    if(session['adminAuth']):
        orderID = request.args.get("orderID")
        first_name = request.args.get("firstName")
        last_name = request.args.get("lastName")
        card_no = request.args.get("cardNo")
        total_cost = request.args.get("totalCost")
        date = request.args.get("date")
        active = request.args.get("active")

        print(date)
        conn = sqlite3.connect("db/pizzadb.db")
        cursor = conn.cursor()

        cursor.execute("""UPDATE Orders SET FirstName = ?, LastName = ?, 
                        CardNo = ?, TotalCost = ?, date = ?, ACTIVE = ?
                    WHERE OrderID = ?;""", (first_name, last_name, card_no, total_cost, date, active, orderID))
        
        conn.commit()
        conn.close()

        return "200"

    return redirect('/admin/login')

@app.route("/admin/action/getSalesData")
def get_salesdata():
    
    if(session['adminAuth']):
        totalRevenue = 0
        noSales = 0
        noSalesPerMonth = {'Jan': 0, 'Feb': 0, 'Mar': 0, 'Apr': 0, 'May': 0, 'Jun': 0, 'Jul': 0, 'Aug': 0, 'Sep': 0, 'Oct': 0, 'Nov': 0, 'Dec': 0}
        revenuePerMonth = {'Jan': 0, 'Feb': 0, 'Mar': 0, 'Apr': 0, 'May': 0, 'Jun': 0, 'Jul': 0, 'Aug': 0, 'Sep': 0, 'Oct': 0, 'Nov': 0, 'Dec': 0}

        salesDataQuery = []
        conn = sqlite3.connect("db/pizzadb.db")

        cursor = conn.cursor()

        today = datetime.today()
        
        cursor.execute("SELECT * FROM Orders WHERE date BETWEEN '"+str(today.year)+"-01-01' AND '"+str(today.year)+"-12-31';")
        rows = cursor.fetchall()

        mos = {1:'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
        # SELECT COUNT(OrderID), SUM(TotalCost), strftime('%m', Date) AS Month FROM ORDERS GROUP BY Month;

        for row in rows:
            rowData = {'orderID': row[0], 
                    'receiptNo.': row[1], 
                    'date': row[2], 
                    'first_name': row[3], 
                    'last_name': row[4], 
                    'card_no': row[5], 
                    'total_cost':row[6],
                    'active': row[7],
                    'orderSerial': row[8], 
                    'month': mos[datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S').month]}
            
            totalRevenue += float(row[6])
            noSales += 1
            revenuePerMonth[rowData['month']]+=float(row[6])
            noSalesPerMonth[rowData['month']]+=1

            salesDataQuery.append(rowData)

        conn.commit()
        conn.close()

        salesData = {'totalRevenue': totalRevenue, 'noSales': noSales, 'revenuePerMonth': revenuePerMonth, 'noSalesPerMonth': noSalesPerMonth}

        return salesData
    
    return redirect("/admin/login")


@app.route("/admin/auth")
def authenticate():
    username = request.args.get("username")
    password = request.args.get("password")

    admin_username = ''
    admin_password = ''
    
    with open('config.json', 'r') as file:
        data = json.load(file)
        admin_username = data['admin_username']
        admin_password = data['admin_password']

    if(username == admin_username and password == admin_password):
        session['adminAuth'] = True

        return redirect("/admin")
    else:

        return redirect('/admin/login')

@app.route("/admin/action/getMenuData")
def get_menudata():

    if(session['adminAuth']):

        data = []

        conn = sqlite3.connect("db/pizzadb.db")

        cursor = conn.cursor()

        cursor.execute('SELECT * FROM Item;')

        rows = cursor.fetchall()

        clearMenu()

        for row in rows:
            rowData = {"ItemID": row[0],
                       "ItemName": row[1],
                       "ItemCost": row[2],
                       "ItemImageURL": row[3]}
            
            
            addMenuItem(row[0], row[1], row[2], row[3])
            data.append(rowData)

        conn.commit()
        conn.close()

        return data

    return redirect('/admin/login')

@app.route("/admin/action/getItemData")
def get_itemdata():
    
    if(session['adminAuth']):
        itemsData = {}


        #i don't care if it's ugly rn, i'm going to do a major refactor in the near future, so this will be fine for now.

        conn = sqlite3.connect("db/pizzadb.db")

        cursor = conn.cursor()

        cursor.execute('SELECT ItemName, COUNT(ReceiptNo) FROM ReceiptItems GROUP BY ItemName;')

        rows = cursor.fetchall()

        labels = []
        values = []
        for row in rows:
            labels.append(row[0])
            values.append(row[1])

        data1 = {'labels': labels, 'values': values}
        
        conn.commit()
        conn.close()
        
        conn = sqlite3.connect("db/pizzadb.db")

        cursor = conn.cursor()

        cursor.execute("SELECT ItemName, COUNT(ItemName), strftime('%m', Date) AS Month FROM ReceiptItems LEFT JOIN Orders ON ReceiptItems.OrderID = Orders.OrderID GROUP BY ItemName;")
        rows = cursor.fetchall()
        data2 = []
        for row in rows:
            data2.append((row[0], row[1], row[2]))

        conn.commit()
        conn.close()

        # SELECT ItemName, COUNT(ReceiptNo) FROM ReceiptItems GROUP BY ItemName;
        # SELECT ItemName, COUNT(ItemName), strftime('%m', Date) AS Month FROM ReceiptItems LEFT JOIN Orders ON ReceiptItems.OrderID = Orders.OrderID GROUP BY ItemName;

        return {'totalItemCount': data1, 'itemsCountPerMonth': data2}

    return redirect('/admin/login')

@app.route("/admin/actions/getOrders")
def admin_getorders():
    
    if(session['adminAuth']):
        conn = sqlite3.connect("db/pizzadb.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Orders;")
        rows = cursor.fetchall()

        data = []

        for row in rows:
            rowData = {'orderID': row[0], 
                    'receiptNo.': row[1], 
                    'date': row[2], 
                    'first_name': row[3], 
                    'last_name': row[4], 
                    'card_no': row[5], 
                    'total_cost':row[6],
                    'active': row[7],
                    'orderSerial': row[8],
                    'status': "idk"}
            
            data.append(rowData)
        conn.commit()
        conn.close()

        return data
    return redirect('/admin/login')


#delete later
def genrannum(size):
    n = '1234567890'
    z = ''
    for i in range(size):
        z+=n[rand.randint(0,len(n)) - 1]
    return int(z)

app.run(port=5000, debug=True)