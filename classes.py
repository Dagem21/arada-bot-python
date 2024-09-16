class User:
       
    def __init__(self, id, userid, username, first_name, phone):
        self.id = id
        self.userid = userid
        self.username = username
        self.firstname = first_name
        self.phone = phone
        
class Item:
    
    def __init__(self, id, itemid, messageid, itemtype, title, color, printtype, imagepath, orders, price):
        self.id = id
        self.itemid = itemid
        self.messageid = messageid
        self.itemtype = itemtype
        self.title = title
        self.color =color
        self.printtype = printtype
        self.imagepath =imagepath
        self.orders =orders
        self.price = price
        
class Cartandorder:
    
    def __init__(self, id, userid, itemid, title, count, color, size, type, paid, delivered, date):
        self.id = id
        self.userid = userid
        self.itemid = itemid
        self.title = title
        self.count = count
        self.color = color
        self.size = size
        self.type = type
        self.paid = paid
        self.delivered = delivered
        self.date = date
        
class Available:
    
    def __init__(self, id, type, color, size, count):
        self.id = id
        self.type = type
        self.color = color
        self.size = size
        self.count = count
        
class Price:
    
    def __init__(self, id, itemtype, price, discount):
        self.id = id
        self.itemtype = itemtype
        self.price = price
        self.discount = discount