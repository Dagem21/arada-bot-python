import os
import json
import psycopg2
import classes

DATABASE_URL = ''
with open('config.env', 'r') as openfile:
    json_object = json.load(openfile)
    DATABASE_URL = json_object["DB_URL"]
    
# conn = psycopg2.connect(DATABASE_URL, sslmode='require')
conn = None
cur = None
def connectDB():
    global conn
    global cur
    conn = psycopg2.connect(database="aradabotdb", user = "postgres", password = "postgres", host = "127.0.0.1", port = "5432")
    cur = conn.cursor()

def addUser(userid, username, firstname):
    try:
        connectDB()
        query = "INSERT INTO users (userid, username, first_name) VALUES ( %s, %s, %s);"
        if(username is None):
            query = "INSERT INTO users (userid, first_name) VALUES ( %s, %s);"
            cur.execute(query,(str(userid),str(firstname),))
            conn.commit()
        else:
            cur.execute(query,(str(userid),username,str(firstname),))
            conn.commit()
        conn.close()
    except Exception as e:
        return e

def updateuser(userid, username,firstname, phone):
    try:
        connectDB()
        if(username is None):
            query = "UPDATE users SET first_name = %s, phone = %s WHERE userid = %s"
            cur.execute(query,(firstname, phone, str(userid),))
        else:
            query = "UPDATE users SET username = %s, first_name = %s, phone = %s WHERE userid = %s"
            cur.execute(query,(username, firstname, phone, str(userid),))
        conn.commit()
        conn.close()
        return
    except Exception as e:
        return e

def getuser(userid):
    connectDB()
    query = "SELECT * FROM users WHERE userid = %s;"
    cur.execute(query,(str(userid),))
    rows = cur.fetchall()
    for row in rows:
        user = classes.User(row[0],row[1],row[2],row[3],row[4])
        conn.close()
        return user

def notregistered(userid):
    connectDB()
    query = "SELECT * FROM users WHERE userid = %s;"
    cur.execute(query,(str(userid),))
    rows = cur.fetchall()
    if (len(rows)>0):
        conn.close()
        return False
    return True

def additem(itemid, messageid, itemtype, title, color, printtype, imagepath, price):
    try:
        connectDB()
        if(printtype is None):
            query = "INSERT INTO items (itemid, message_id, item_type, title, color, image_path, price) VALUES ( %s, %s, %s, %s, %s, %s, %s);"
            cur.execute(query,(str(itemid), str(messageid), itemtype, title, color, imagepath, price,))
        else:
            query = "INSERT INTO items (itemid, message_id, item_type, title, color, print_type, image_path, price) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s);"
            cur.execute(query,(str(itemid), str(messageid), itemtype, title, color, printtype, imagepath, price,))
        conn.commit()
        conn.close()
    except Exception as e:
        return e

def updateitem(itemid, itemtype, title, color, printtype, imagepath):
    try:
        connectDB()
        if(printtype is None):
            query = "UPDATE items SET item_type = %s title = %s, color = %s, image_path = %s WHERE itemid = %s"
            cur.execute(query,(itemtype, title, color, imagepath, str(itemid),))
        else:
            query = "UPDATE items SET item_type = %s title = %s, color = %s, print_type = %s, image_path = %s WHERE itemid = %s"
            cur.execute(query,(itemtype, title, color, printtype, imagepath, str(itemid),))
        conn.commit()
        conn.close()
        return
    except Exception as e:
        return e

def updateordernumber(itemid, number):
    try:
        itemorders = getitem(itemid).orders
        new = itemorders+number
        query = "UPDATE items SET orders = %s WHERE itemid = %s"
        cur.execute(query,(new, itemid,))
        conn.commit()
        conn.close
        return
    except Exception as e:
        return e
    
def updatepriceofitem(itemid, price):
    try:
        connectDB()
        query = "UPDATE items SET price = %s WHERE itemid = %s"
        cur.execute(query, (price, itemid,))
        conn.commit()
        conn.close()
        return
    except Exception as e:
        return e

def updatepricebytype(itemtype, price):
    try:
        connectDB()
        query = "UPDATE items SET price = %s WHERE item_type = %s"
        cur.execute(query, (price, itemtype,))
        conn.commit()
        conn.close()
        return
    except Exception as e:
        return e

def getitem(itemid):
    connectDB()
    query = "SELECT * FROM items WHERE itemid = %s;"
    cur.execute(query,(str(itemid),))
    rows = cur.fetchall()
    for row in rows:
        item = classes.Item(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9])
        conn.close()
        return item
    return None

def initems(itemid):
    connectDB()
    query = "SELECT * FROM items WHERE itemid = %s"
    cur.execute(query,(str(itemid),))
    rows = cur.fetchall()
    if(len(rows)!=0):
        conn.close()
        return True
    conn.close()
    return False

def addnewitemtype(itemname, price, discount):
    try:
        connectDB()
        query = "INSERT INTO defaultprice(item_type, price, discount) VALUES (%s, %s, %s);"
        cur.execute(query, (itemname, price, discount))
        conn.commit()
        conn.close
        return
    except Exception as e:
        return e

def getprice(itemtype):
    connectDB()
    query = "SELECT price FROM defaultprice WHERE item_type = %s"
    cur.execute(query, (itemtype,))
    rows = cur.fetchall()
    for row in rows:
        return row
    return None
    
def getprices():
    connectDB()
    query = "SELECT * FROM defaultprice"
    cur.execute(query)
    prices = []
    rows = cur.fetchall()
    for row in rows:
        item = classes.Price(row[0], row[1], row[2], row[3])
        prices.append(item)
    conn.close()
    return prices
    
def updatedefaultprice(itemtype, price, discount):
    try:
        connectDB()
        query = "UPDATE defaultprice set price = %s, discount = %s WHERE item_type = %s"
        cur.execute(query, (price, discount, itemtype,))
        conn.commit()
        conn.close()
    except Exception as e:
        return e

def addcart_order(userid, itemid, title, count, color, size, type, date):
    try:
        connectDB()
        query = "INSERT INTO cartandorder(userid, itemid, title, count, color, size, type, date) VALUES \
            (%s, %s, %s, %s, %s, %s, %s, %s);"
        cur.execute(query,(str(userid), str(itemid), title, count, color, size, type.lower(), date,))
        conn.commit()
        cur.execute('SELECT LASTVAL()')
        new_id = cur.fetchone()[-1]
        conn.close()
        return new_id
    except Exception as e:
        print(e)
        return

def updatecart(userid, itemid, count, color, size, date):
    try:
        connectDB()
        query = "UPDATE cartandorder SET count = %s, color = %s, size = %s, date = %s WHERE userid = %s AND itemid = %s AND type = 'cart'"
        cur.execute(query,(count, color, size, date, str(userid), str(itemid),))
        conn.commit()
        conn.close()
        return
    except Exception as e:
        return e

def getcart(userid):
    connectDB()
    query = "SELECT * FROM cartandorder WHERE userid = %s AND type = 'cart'"
    cur.execute(query,(userid,))
    rows = cur.fetchall()
    cart_list = []
    for row in rows:
        cart = classes.Cartandorder(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10])
        cart_list.append(cart)
    conn.close()
    return cart_list

def getItemInCart(userid, itemid, from_cart):
    connectDB()
    if(from_cart):
        query = "SELECT * FROM cartandorder WHERE userid = %s AND itemid = %s AND type = 'cart'"
        cur.execute(query,(str(userid),str(itemid),))
    else:
        query = "SELECT * FROM cartandorder WHERE userid = %s AND itemid = %s"
        cur.execute(query,(str(userid),str(itemid),))
    rows = cur.fetchall()
    for row in rows:
        cart = classes.Cartandorder(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10])
        conn.close()
        return cart
    
def removefromcart(userid, itemid):
    try:
        connectDB()
        query = "DELETE FROM cartandorder WHERE userid = %s AND itemid = %s AND type = 'cart'"
        cur.execute(query,(str(userid), str(itemid),))
        conn.commit()
        conn.close()
        return
    except Exception as e:
        return e

def incart(userid, itemid):
    connectDB()
    query = "SELECT * FROM cartandorder WHERE userid = %s AND itemid = %s AND type = 'cart'"
    cur.execute(query,(str(userid),str(itemid),))
    rows = cur.fetchall()
    if(len(rows)!=0):
        conn.close()
        return True
    conn.close()
    return False

def inorders(userid, itemid):
    connectDB()
    query = "SELECT * FROM cartandorder WHERE userid = %s AND itemid = %s AND type = 'order'"
    cur.execute(query,(str(userid),str(itemid),))
    rows = cur.fetchall()
    if(len(rows)!=0):
        conn.close()
        return True
    conn.close()
    return False

def updateorder(id):
    try:
        connectDB()
        query = "UPDATE cartandorder SET paid = '1' WHERE id = %s AND type = 'order'"
        cur.execute(query,(id,))
        conn.commit()
        conn.close()
        return
    except Exception as e:
        return e

def updateorderdelivered(id):
    try:
        connectDB()
        query = "UPDATE cartandorder SET delivered = '1' WHERE id = %s AND type = 'order'"
        cur.execute(query,(id,))
        conn.commit()
        conn.close()
        return
    except Exception as e:
        return e

def getorders(userid):
    connectDB()
    query = "SELECT * FROM cartandorder WHERE userid = %s AND type = 'order'"
    cur.execute(query,(userid,))
    rows = cur.fetchall()
    orders = []
    for row in rows:
        order = classes.Cartandorder(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10])
        orders.append(order)
    conn.close()
    return orders

def getnotdeliveredorders():
    connectDB()
    # query = "SELECT * FROM cartandorder WHERE delivered = '0' AND type = 'order' AND paid = '1'"
    query = "SELECT * FROM cartandorder WHERE delivered = '0' AND type = 'order'"
    cur.execute(query)
    rows = cur.fetchall()
    orders = []
    for row in rows:
        order = classes.Cartandorder(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],row[10])
        orders.append(order)
    conn.close()
    return orders

def addnewitem(type, color, size, count):
    try:
        connectDB()
        if(size is None):
            query = "INSERT INTO available (item_type, color, amount) VALUES (%s, %s, %s);"
            cur.execute(query,(type, color, count,))
        else:
            query = "INSERT INTO available (item_type, color, size, amount) VALUES (%s, %s, %s, %s);"
            cur.execute(query,(type, color, size, count,))
        conn.commit()
        conn.close()
        return
    except Exception as e:
        return e

def inavailable(type, color, size):
    connectDB()
    if(size is None):
        query = "SELECT * FROM available WHERE item_type = %s AND color = %s;"
        cur.execute(query,(type, color,))
    else:
        query = "SELECT * FROM available WHERE item_type = %s AND color = %s AND size = %s;"
        cur.execute(query,(type, color, size,))
    rows = cur.fetchall()
    for row in rows:
        iteminstock = classes.Available(row[0],row[1],row[2],row[3],row[4])
        return iteminstock.count
    conn.close()
    return 0

def updateavailableitem(id, amount):
    try:
        connectDB()
        query = "UPDATE available SET amount = %s WHERE id = %s"
        cur.execute(query,(amount, id,))
        conn.commit()
        conn.close()
        return
    except Exception as e:
        return e

def getavailableitems():
    connectDB()
    query = "SELECT * FROM available"
    cur.execute(query)
    rows = cur.fetchall()
    items = []
    for row in rows:
        itemcount = classes.Available(row[0], row[1], row[2], row[3], row[4])
        items.append(itemcount)
    conn.close()
    return items

def getitemcount(type, size, color):
    connectDB()
    query = "SELECT * FROM available WHERE item_type = %s AND size = %s AND color = %s"
    cur.execute(query,(type, size, color,))
    rows = cur.fetchall()
    for row in rows:
        itemcount = classes.Available(row[0], row[1], row[2], row[3], row[4])
        conn.close()
        return itemcount

def main():
    print("Running database")

if (__name__ == "__main__"):
    main()