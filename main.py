import threading
import telebot
import json
import datetime
import database
from threading import Timer

pending_orders_channel = "https://t.me/aradapend/"
main_channel = "https://t.me/aradapend/"

API_KEY = ""
with open('config.env', 'r') as openfile:
    json_object = json.load(openfile)
    API_KEY = json_object["API_KEY"]

adminlist = ['344325595']
bot = telebot.TeleBot(API_KEY)

markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard = True)
itembtn1 = telebot.types.KeyboardButton('Order Item From Channel')
itembtn2 = telebot.types.KeyboardButton('Order Custom Made Item')
itembtn3 = telebot.types.KeyboardButton('Give Us A Feedback')
itembtn4 = telebot.types.KeyboardButton('Cart')
itembtn5 = telebot.types.KeyboardButton('Orders')
markup.row(itembtn1)
markup.row(itembtn2)
markup.row(itembtn4, itembtn5)
markup.row(itembtn3)

markup_admin = telebot.types.ReplyKeyboardMarkup(resize_keyboard = True)
admbtn1 = telebot.types.KeyboardButton('Update Item')
admbtn2 = telebot.types.KeyboardButton('Pending Orders')
admbtn3 = telebot.types.KeyboardButton('Add Items to Stock')
admbtn4 = telebot.types.KeyboardButton('Update Items in Stock')
admbtn5 = telebot.types.KeyboardButton('New Item Type')
admbtn6 = telebot.types.KeyboardButton('Edit Item Type')
markup_admin.row(admbtn1)
markup_admin.row(admbtn2)
markup_admin.row(admbtn3, admbtn4)
markup_admin.row(admbtn5, admbtn6)

@bot.message_handler(commands=['Start','start'])
def start(message):
  user_id = message.chat.id
  if(str(user_id) not in adminlist):
    if(database.notregistered(user_id)):
      keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
      share_contact_btn = telebot.types.KeyboardButton(text="Share", request_contact=True)
      cancel_btn = telebot.types.KeyboardButton(text="Cancel")
      keyboard.row(share_contact_btn, cancel_btn)
      database.addUser(user_id,message.chat.username, message.chat.first_name)
      bot.send_message(user_id, "Share your number with us?\nYour number will only be used when you place an order to send you your payments and to contact you during deliveries.", reply_markup=keyboard)
    else:
      bot.send_message(user_id, "What would you like to do:", reply_markup=markup)
  else:
    bot.send_message(user_id, "What would you like to do:", reply_markup=markup_admin)

@bot.message_handler(func=lambda m: True)
def message_handler(message):
  user_id = message.chat.id
  try:
    if(str(user_id) not in adminlist):
      user_message_handler(message)
    else:
      admin_message_handler(message)
  except Exception as e:
    print(e)

def user_message_handler(message):
  try:
    user_id = message.chat.id
    if (message.text=="Order Item From Channel"):
      bot.send_message(user_id, "Ok forward the item from the channel or send me the item number.", reply_markup=markup)
    elif (message.text=="Order Custom Made Item"):
      bot.send_message(user_id, "To order any custom made item please contact admins of the channel \n @Yoyo_101 or @A_Sentient_Being ", reply_markup=markup)
    elif (message.text=="Give Us A Feedback"):
      markupkb = telebot.types.ForceReply(selective=True)
      bot.send_message(user_id, "Have a feedback? We would love to hear it.", reply_markup=markupkb)
    elif (message.text=="Cart"):
      send_cartlist(user_id, None)
    elif (message.text=="Orders"):
      send_orderslist(user_id)
    elif (message.text=='Cancel'):
      bot.send_message(user_id, "What would you like to do:", reply_markup=markup)
    elif(message.reply_to_message != None):
      if(message.reply_to_message.text=="Have a feedback? We would love to hear it."):
        username = message.chat.username
        date = datetime.datetime.fromtimestamp(message.date).strftime("%d-%b, %Y")
        if(username is None):
          username = "User has no Username"
        else:
          username = '@' + username
        chat_id = "-1001585347050",
        text = "From : "+message.chat.first_name+"\nUsername : "+username+"\nMessage : "+message.text+"\n Date : "+date
        bot.send_message(chat_id, text, reply_markup=markup)
    else:
      text = message.text
      if text.isdigit():
        item_id = int(text)
        send_item(user_id, item_id, message.message_id)
      else:
        bot.send_message(user_id, "Please choose an option from the commands available below.", reply_markup=markup)
  except Exception as e:
    return e
      
def admin_message_handler(message):
  try:
    user_id = message.chat.id
    text = "What is the item name?"
    if(message.text == 'Update Item'):
      bot.send_message(user_id, "Ok forward the item from the channel or send me the item number.", reply_markup=markup_admin)
    elif(message.text == 'Pending Orders'):
      sendpendingorders(message.chat.id)
    elif(message.text == 'Add Items to Stock'):
      markupkb = telebot.types.ForceReply(selective=True)
      bot.send_message(user_id, text, reply_markup=markupkb)
    elif (message.text == 'Update Items in Stock'):
      availableitems(user_id)
    elif (message.text == 'New Item Type'):
      markupkb = telebot.types.ForceReply(selective=True)
      bot.send_message(user_id, "New Item Name", reply_markup=markupkb)
    elif (message.text == 'Edit Item Type'):
      senditemtypes(user_id)
    elif(message.reply_to_message != None):
      if(message.reply_to_message.text==text):
        item_name = message.text
        colors_str = None
        first_color = None
        size_txt = 'None'
        if(item_name.upper() in ['TSHIRT', 'T-SHIRT', 'HOODIE', 'MUG']):
          colors_str = 'White,Black,Gray,Red,Yellow,Green,Blue'
          first_color = 'White'
          size_txt = 'M'
        elif(item_name.upper() in ['MASON JAR', 'MASON-JAR', 'MASONJAR']):
          colors_str = 'Clear,Frost'
          first_color = 'Clear'
        else:
          colors_str = 'White,Black,Gray,Red,Yellow,Green,Blue,Clear,Frost'
          first_color = 'White'
        new_item_markup = telebot.types.InlineKeyboardMarkup()
        color_btn = telebot.types.InlineKeyboardButton(text=first_color ,callback_data='available|changecolor|'+colors_str)
        size_btn = telebot.types.InlineKeyboardButton(text=size_txt, callback_data='available|changesize')
        add_btn = telebot.types.InlineKeyboardButton(text='Add', callback_data='available|add')
        decrease5 = telebot.types.InlineKeyboardButton(text='-5', callback_data='available|update|-5')
        decrease1 = telebot.types.InlineKeyboardButton(text='-1', callback_data='available|update|-1')
        counter = telebot.types.InlineKeyboardButton(text='0', callback_data='available|counter')
        increase1 = telebot.types.InlineKeyboardButton(text='+1', callback_data='available|update|1')
        increase5 = telebot.types.InlineKeyboardButton(text='+5', callback_data='available|update|5')
        cancel_btn = telebot.types.InlineKeyboardButton(text='Cancel', callback_data='cancel')
        if(item_name.upper() in ['MASON JAR', 'MASON-JAR', 'MASONJAR', 'MUG']):
          new_item_markup.row(color_btn)
        else:
          new_item_markup.row(color_btn, size_btn)
        new_item_markup.row(decrease5, decrease1, counter, increase1,increase5)
        new_item_markup.row(add_btn, cancel_btn)
        bot.send_message(user_id, "Item name -"+item_name,reply_markup=new_item_markup)
      elif(message.reply_to_message.text=='New Item Name'):
        if(database.getprice(message.text) is not None):
          bot.send_message(user_id, 'This item type is alredy registered.', reply_markup=markup_admin)
        else:
          addnewitemtype(user_id, message.text)
    else:
      text = message.text
      if text.isdigit():
        item_id = int(text)
        if(database.initems(str(item_id))):
          deleteMessage(user_id, message.message_id)
          senditemtoadmin(user_id, item_id)
        else:
          bot.send_message(user_id, "Cound not find the item with that id.", reply_markup=markup_admin)
      else:
        bot.send_message(user_id, "Please choose an option from the commands available below.", reply_markup=markup_admin)
  except Exception as e:
    return (e)

@bot.message_handler(content_types=['contact'])
def contact_handler(message):
    phone_number = message.contact.phone_number
    userid = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    res = database.updateuser(userid,username, first_name, phone_number)
    if(res is None):
      bot.send_message(userid, "Your contact has been saved.",reply_markup=markup)
    else:
      bot.send_message(userid, "What would you like to do:", reply_markup=markup)
      while(res is not None):
        res = database.updateuser(userid,username, first_name, phone_number)

def addnewitemtype(user_id, itemtype):
  price_markup = telebot.types.InlineKeyboardMarkup()
  item_name = telebot.types.InlineKeyboardButton(text=itemtype, callback_data= 'newitemtype|skip')
  decrease10 = telebot.types.InlineKeyboardButton(text='-10', callback_data='newitemtype|-10')
  decrease5 = telebot.types.InlineKeyboardButton(text='-5', callback_data='newitemtype|-5')
  price = telebot.types.InlineKeyboardButton(text='300', callback_data='newitemtype|skip')
  increase5 = telebot.types.InlineKeyboardButton(text='+5', callback_data='newitemtype|5')
  increase10 = telebot.types.InlineKeyboardButton(text='+10', callback_data='newitemtype|10')
  discountd10 = telebot.types.InlineKeyboardButton(text='-10', callback_data='newitemtype|discount|-10')
  discountd1 = telebot.types.InlineKeyboardButton(text='-1', callback_data='newitemtype|discount|-1')
  discount = telebot.types.InlineKeyboardButton(text='0%', callback_data='newitemtype|discount|0')
  discount1 = telebot.types.InlineKeyboardButton(text='+1', callback_data='newitemtype|discount|1')
  discount10 = telebot.types.InlineKeyboardButton(text='+10', callback_data='newitemtype|discount|10')
  price_markup.row(item_name)
  price_markup.row(decrease10, decrease5, price, increase5, increase10)
  price_markup.row(discountd10, discountd1, discount, discount1, discount10)
  update = telebot.types.InlineKeyboardButton(text='Create', callback_data='defaultprice|create')
  cancel = telebot.types.InlineKeyboardButton(text='Cancel', callback_data='cancel')
  price_markup.row(update, cancel)
  bot.send_message(user_id, "New item type", reply_markup=price_markup)

def senditemtypes(user_id):
  try:
    items = database.getprices()
    price_markup = telebot.types.InlineKeyboardMarkup()
    for item in items:
      itemtype = str(item.itemtype)
      item_name = telebot.types.InlineKeyboardButton(text=item.itemtype, callback_data= 'defaultprice|skip')
      decrease10 = telebot.types.InlineKeyboardButton(text='-10', callback_data='defaultprice|-10|'+itemtype)
      decrease5 = telebot.types.InlineKeyboardButton(text='-5', callback_data='defaultprice|-5|'+itemtype)
      price = telebot.types.InlineKeyboardButton(text=str(item.price), callback_data='defaultprice|skip')
      increase5 = telebot.types.InlineKeyboardButton(text='+5', callback_data='defaultprice|5|'+itemtype)
      increase10 = telebot.types.InlineKeyboardButton(text='+10', callback_data='defaultprice|10|'+itemtype)
      discountd10 = telebot.types.InlineKeyboardButton(text='-10', callback_data='defaultprice|discount|-10|'+itemtype)
      discountd1 = telebot.types.InlineKeyboardButton(text='-1', callback_data='defaultprice|discount|-1|'+itemtype)
      discount = telebot.types.InlineKeyboardButton(text=str(item.discount)+'%', callback_data='defaultprice|discount|0|'+itemtype)
      discount1 = telebot.types.InlineKeyboardButton(text='+1', callback_data='defaultprice|discount|1|'+itemtype)
      discount10 = telebot.types.InlineKeyboardButton(text='+10', callback_data='defaultprice|discount|10|'+itemtype)
      price_markup.row(item_name)
      price_markup.row(decrease10, decrease5, price, increase5, increase10)
      price_markup.row(discountd10, discountd1, discount, discount1, discount10)
    update = telebot.types.InlineKeyboardButton(text='Update', callback_data='defaultprice|update')
    cancel = telebot.types.InlineKeyboardButton(text='Cancel', callback_data='cancel')
    price_markup.row(update, cancel)
    bot.send_message(user_id, "Default price and discounts", reply_markup=price_markup)
  except Exception as e:
    print(e)

def availableitems(userid):
  try:
    availablelist = database.getavailableitems()
    if(len(availablelist) == 0):
      bot.send_message(userid, 'There are no items in stock.', reply_markup=markup_admin)
      return
    items_keyboard = telebot.types.InlineKeyboardMarkup()
    for item in availablelist:
      btn1 = telebot.types.InlineKeyboardButton(text='-5',callback_data='upitem|'+str(item.id)+'|-5')
      btn2 = telebot.types.InlineKeyboardButton(text='-1',callback_data='upitem|'+str(item.id)+'|-1')
      btn3 = telebot.types.InlineKeyboardButton(text='0',callback_data='upitem|'+str(item.id)+'|0')
      text = item.type + ', '+item.color+' - '+str(item.count)
      if(item.size is not None):
        text = item.type + ', ' + item.size+', '+item.color+' : '+str(item.count)
      btn6 = telebot.types.InlineKeyboardButton(text=text,callback_data='upitem|'+str(item.id)+'|skip')
      btn4 = telebot.types.InlineKeyboardButton(text='+1',callback_data='upitem|'+str(item.id)+'|+1')
      btn5 = telebot.types.InlineKeyboardButton(text='+5',callback_data='upitem|'+str(item.id)+'|+5')
      items_keyboard.row(btn6)
      items_keyboard.row(btn1, btn2, btn3, btn4, btn5)
    cancel = telebot.types.InlineKeyboardButton(text = 'Cancel', callback_data='cancel')
    update = telebot.types.InlineKeyboardButton(text = 'Update', callback_data='upitem|update')
    items_keyboard.row(update, cancel)
    
    bot.send_message(userid, 'Items in Stock.', reply_markup=items_keyboard)
  except Exception as e:
    print (e)

def sendpendingorders(userid, messageid = None):
  orders = database.getnotdeliveredorders()
  if(len(orders) == 0):
    if(messageid is not None):
      deleteMessage(userid, messageid)
    bot.send_message(userid, "There are no pending orders.", reply_markup=markup_admin)
  else:
    markup_orders = telebot.types.InlineKeyboardMarkup()
    for order in orders:
      ord_button = telebot.types.InlineKeyboardButton(text=order.itemid, url=main_channel+str(order.itemid))
      date_btn = telebot.types.InlineKeyboardButton(text=order.date, callback_data='skip')
      delivered = telebot.types.InlineKeyboardButton(text='Delivered ✅', callback_data='delivered|'+str(order.id))
      markup_orders.row(ord_button, date_btn, delivered)
    cancel = telebot.types.InlineKeyboardButton(text='Cancel', callback_data='cancel')
    markup_orders.row(cancel)
    if(messageid is None):
      bot.send_message(userid, 'Here are pending orders.', reply_markup=markup_orders)
    else:
      bot.edit_message_reply_markup(userid, messageid,reply_markup=markup_orders)

def senditemtoadmin(userid, itemid, photoid = None, title = None, messageid = None):
  itemtype = 'T-shirt'
  printtypeText = 'DTG'
  whiteText = "⬜"
  blackText = "⬛"
  grayText = "Gray"
  redText = "🟥"
  yellowText = "🟨"
  greenText = "🟩"
  blueText = "🟦"
  orangeText = "🟧"
  magicText = "Magic"
  silverText = "Silver"
  goldText = "Gold"
  frameText = "Full Black"
  frostText = "Frost"
  clearText = "Clear"
  markup_inline = telebot.types.InlineKeyboardMarkup()
  if(database.initems(itemid)):
    item = database.getitem(itemid)
    itemtype = item.itemtype
    photoid = item.imagepath
    title = item.title
    messageid = item.messageid
    if(itemtype == "T-shirt" or itemtype == "Hoodie"):
      printtypeText = item.printtype
      colors = item.color
      if('ALL' in colors):
        colors = "{White, Black, Gray, Red, Yellow, Green, Blue}"
      whi = '0'; bla = '0'; gra = '0'; re = '0'; yel = '0'; gre = '0'; blu = '0'
      if('White' in colors):
        whiteText = '⬜ - ✅'; whi = '1'
      if('Black' in colors):
        blackText = '⬛ - ✅'; bla = '1'
      if('Gray' in colors):
        grayText = 'Gray - ✅'; gra = '1'
      if('Red' in colors):
        redText = '🟥 - ✅'; re = '1'
      if('Yellow' in colors):
        yellowText = '🟨 - ✅'; yel = '1'
      if('Green' in colors):
        greenText = '🟩 - ✅'; gre = '1'
      if('Blue' in colors):
        blueText = '🟦 - ✅'; blu = '1'
        
      itemtype = telebot.types.InlineKeyboardButton(text=itemtype, callback_data="edititem|changetype")
      allcolors = telebot.types.InlineKeyboardButton(text="All", callback_data="edititem|all")
      white = telebot.types.InlineKeyboardButton(text=whiteText, callback_data="edititem|whi|"+whi)
      black = telebot.types.InlineKeyboardButton(text=blackText, callback_data="edititem|bla|"+bla)
      gray = telebot.types.InlineKeyboardButton(text=grayText, callback_data="edititem|gra|"+gra)
      red = telebot.types.InlineKeyboardButton(text=redText, callback_data="edititem|red|"+re)
      yellow = telebot.types.InlineKeyboardButton(text=yellowText, callback_data="edititem|yel|"+yel)
      green = telebot.types.InlineKeyboardButton(text=greenText, callback_data="edititem|gre|"+gre)
      blue = telebot.types.InlineKeyboardButton(text=blueText, callback_data="edititem|blu|"+blu)
      clear = telebot.types.InlineKeyboardButton(text="Clear All", callback_data="edititem|clear")
      printtype = telebot.types.InlineKeyboardButton(text=printtypeText, callback_data="edititem|pty|"+printtypeText)
      
      markup_inline.row(itemtype, allcolors, white, black)
      markup_inline.row(gray, red, yellow, green)
      markup_inline.row(blue, clear, printtype)
    elif(itemtype == "Mug"):
      colors = item.color
      if('ALL' in colors):
        colors = "{Magic, Frame, White, Black, Red, Orange, Green, Blue, Silver, Gold}"
      mag = '0'; fra = '0'; whi = '0'; bla = '0'; ora = '0'; re = '0'; gre = '0'; blu = '0'; sil = '0'; gol = '0'
      if('Magic' in colors):
        magicText = 'Magic - ✅'; mag = '1'
      if('Frame' in colors):
        frameText = 'Frame - ✅'; fra = '1'
      if('White' in colors):
        whiteText = '⬜ - ✅'; whi = '1'
      if('Black' in colors):
        blackText = '⬛ - ✅'; bla = '1'
      if('Orange' in colors):
        orangeText = '🟧 - ✅'; ora = '1'
      if('Red' in colors):
        redText = '🟥 - ✅'; re = '1'
      if('Green' in colors):
        greenText = '🟩 - ✅'; gre = '1'
      if('Blue' in colors):
        blueText = '🟦 - ✅'; blu = '1'
      if('White' in colors):
        silverText = 'Silver - ✅'; sil = '1'
      if('White' in colors):
        goldText = 'Gold - ✅'; gol = '1'
      itemtype = telebot.types.InlineKeyboardButton(text=itemtype, callback_data="edititem|changetype")
      allcolors = telebot.types.InlineKeyboardButton(text="All", callback_data="edititem|all")
      magic = telebot.types.InlineKeyboardButton(text=magicText, callback_data="edititem|mag|"+mag)
      frame = telebot.types.InlineKeyboardButton(text=frameText, callback_data="edititem|fra|"+fra)
      white = telebot.types.InlineKeyboardButton(text=whiteText, callback_data="edititem|whi|"+whi)
      black = telebot.types.InlineKeyboardButton(text=blackText, callback_data="edititem|bla|"+bla)
      red = telebot.types.InlineKeyboardButton(text=redText, callback_data="edititem|red|"+re)
      orange = telebot.types.InlineKeyboardButton(text=orangeText, callback_data="edititem|ora|"+ora)
      green = telebot.types.InlineKeyboardButton(text=greenText, callback_data="edititem|gre|"+gre)
      blue = telebot.types.InlineKeyboardButton(text=blueText, callback_data="edititem|blu|"+blu)
      silver = telebot.types.InlineKeyboardButton(text=silverText, callback_data="edititem|sil|"+sil)
      gold = telebot.types.InlineKeyboardButton(text=goldText, callback_data="edititem|gol|"+gol)
      clear = telebot.types.InlineKeyboardButton(text="Clear All", callback_data="edititem|clear")
      markup_inline.row(itemtype, allcolors, magic, frame)
      markup_inline.row(white, black, red, orange)
      markup_inline.row(green, blue, silver, gold)
      markup_inline.row(clear)
    elif(itemtype == "Mason Jar"):
      colors = item.color
      if('ALL' in colors):
        colors = "{Clear, Frost}"
      cle = '0'; fro = '0'
      if('Clear' in colors):
        clearText = 'Clear - ✅'; cle = '1'
      if('Frame' in colors):
        frostText = 'Frost - ✅'; fro = '1'
      allcolors = telebot.types.InlineKeyboardButton(text="All", callback_data="edititem|all")
      clearcolor = telebot.types.InlineKeyboardButton(text=clearText, callback_data="edititem|cle|"+cle)
      frost = telebot.types.InlineKeyboardButton(text=frostText, callback_data="edititem|fro|"+fro)
      clear = telebot.types.InlineKeyboardButton(text="Clear All", callback_data="edititem|clear")
      markup_inline.row(itemtype, allcolors)
      markup_inline.row(clearcolor, frost)
      markup_inline.row(clear)
  else:
    itemtype = telebot.types.InlineKeyboardButton(text=itemtype, callback_data="edititem|changetype")
    allcolors = telebot.types.InlineKeyboardButton(text="All", callback_data="edititem|all")
    white = telebot.types.InlineKeyboardButton(text=whiteText, callback_data="edititem|whi|0")
    black = telebot.types.InlineKeyboardButton(text=blackText, callback_data="edititem|bla|0")
    gray = telebot.types.InlineKeyboardButton(text=grayText, callback_data="edititem|gra|0")
    red = telebot.types.InlineKeyboardButton(text=redText, callback_data="edititem|red|0")
    yellow = telebot.types.InlineKeyboardButton(text=yellowText, callback_data="edititem|yel|0")
    green = telebot.types.InlineKeyboardButton(text=greenText, callback_data="edititem|gre|0")
    blue = telebot.types.InlineKeyboardButton(text=blueText, callback_data="edititem|blu|0")
    clear = telebot.types.InlineKeyboardButton(text="Clear All", callback_data="edititem|clear")
    printtype = telebot.types.InlineKeyboardButton(text=printtypeText, callback_data="edititem|pty|"+printtypeText)

    markup_inline.row(itemtype, white, black ,gray)
    markup_inline.row(yellow, red, green, blue)
    markup_inline.row(allcolors, clear, printtype)
    
  cap = "Item ID - "+str(itemid)+"\nTitle -"+title+"\nMessage ID - "+str(messageid)
  bot.send_photo(userid,photo=photoid, caption=cap,reply_markup=markup_inline)

@bot.channel_post_handler(content_types=["photo"])
def channelpost(channel_post):
  try:
    channelid = '-1001506505814'
    caption = channel_post.caption
    messageid = channel_post.message_id
    photoid = channel_post.photo[-1].file_id
    if(photoid is None or caption is None):
      return
    caption_list = caption.split("\n")
    if(len(caption_list)>1):
      title = caption_list[0].split(":")[-1]
      tags_list = caption_list[1].split(",")
      item_id = tags_list[-1].replace(" ","")
      if(item_id.isdigit()):
        senditemtoadmin(channelid, item_id, photoid, title, messageid)
  except Exception as e:
    print(e)
    
@bot.message_handler(func=lambda message: message.forward_from_chat, content_types=["photo"])
def posts_from_channels(message):
  try:
    user_id = message.chat.id
    channel_username = message.forward_from_chat.username
    if(channel_username == "aradatshirts" or message.forward_from_chat.title == "ARADA Resources"):
      caption_list = message.caption.split("\n")
      if(len(caption_list)>1):
        tags_list = caption_list[1].split(",")
        item_id = tags_list[-1].replace(" ","")
        if(item_id.isdigit()):
          if(str(user_id) in adminlist):
            senditemtoadmin(user_id,int(item_id))
          else:
            send_item(user_id, int(item_id), message.message_id)
        else:
          print("Could not identify Item ID")
    else:
      bot.send_message(user_id, "This channel is not Arada T-Shirts channel. Please join our channel and forward the message from there.\nChannel link @aradatshirts", reply_markup=markup)
  except Exception as e:
    print(e)

def deleteMessage(user_id, message_id):
  try:
    bot.delete_message(user_id,message_id)
  except Exception as e:
    return e

@bot.callback_query_handler(func = lambda call: True)
def handlecall(call):
  user_id = call.from_user.id
  if(str(user_id) not in adminlist):
    handle(call)
  else:
    handleadmincall(call)

def handle(call):
  try:
    user_id = call.message.chat.id
    if(call.data == "cancel"):
      deleteMessage(user_id, call.message.message_id)
      bot.send_message(user_id, 'What would you like to do:', reply_markup=markup)
    else:
      datas = call.data.split('|')
      param1 = datas[0]
      if(param1 == 'cartlist'):
        param2 = datas[1]
        if(param2 == 'editcart'):
          deleteMessage(user_id, call.message.message_id)
          send_item(user_id, datas[2],None)
        elif(param2 == 'remove'):
          database.removefromcart(user_id, datas[1].replace(' ', ''))
          send_cartlist(user_id, call.message.message_id)
        elif(param2 == 'orderall'):
          cart_markup = call.message.reply_markup.keyboard
          itemidlist = []
          for index, keyboard in enumerate(cart_markup):
            if(index+1 != len(cart_markup)):
              itemid = int(keyboard[0].text.split('-')[1].replace(' ', ''))
              itemidlist.append(itemid)
          itemstoorder = []
          out_of_stock_item = []
          map_counter = {}
          for itemid in itemidlist:
            itemincart = database.getItemInCart(user_id,itemid, True)
            itemtype = database.getitem(itemid).itemtype
            availableitem = database.inavailable(itemtype, itemincart.color, itemincart.size)
            item_type = itemtype +itemincart.color+itemincart.size if(itemincart.size is not None) else itemtype+itemincart.color
            if(availableitem >-1):
              if(item_type in map_counter):
                in_map = map_counter[item_type]
                if(availableitem-in_map>=itemincart.count):
                  itemstoorder.append(itemincart)
                  map_counter[item_type] = map_counter[item_type] +itemincart.count
                else:
                  out_of_stock_item.append(itemincart)
              else:
                if(availableitem>=itemincart.count):
                  itemstoorder.append(itemincart)
                  map_counter[item_type] = itemincart.count
                else:
                  out_of_stock_item.append(itemincart)
            else:
              out_of_stock_item.append(itemincart)
          message = None
          if(len(out_of_stock_item)>0):
            message = 'Some items are out of stock!'
            for item in out_of_stock_item:
              message = message + '\n- ' + item.title
          price = 0
          if(len(itemstoorder)>0):
            if(message is None):
              message = 'Items available from your order'
            else:
              message = message + '\nItems available from your order'
            for item in itemstoorder:
              database_item = database.getitem(item.itemid)
              item_total_price = item.count * database_item.price
              price += item_total_price
              message = message + '\n- ' + item.title + ' - ' + str(item.count) + ' * ' + str(database_item.price) + ' = '+ str(item_total_price)
          if(message is not None):
            message += '\nTotal - '+str(price)+' Birr'
          orderall_markup = telebot.types.InlineKeyboardMarkup()
          order_btn = telebot.types.InlineKeyboardButton('Order', callback_data='orderfromcart')
          cancel_btn = telebot.types.InlineKeyboardButton('Cancel', callback_data='cancel')
          orderall_markup.row(order_btn, cancel_btn)
          bot.send_message(user_id, message, reply_markup= orderall_markup)
      elif (param1 == 'newcart'):
        send_item(user_id, datas[1],None)
      elif (param1 == 'order'):
        param2 = datas[1]
        deleteMessage(user_id, call.message.message_id)
        if(param2 == 'editorder'):
          lines = call.message.caption.split('\n')
          itemid = lines[0].split(':')[-1]
          color = lines[2].split(':')[-1]
          count = None; size = 'NA'
          if(len(lines) == 6):
            size = lines[3].split(':')[-1]
            count = lines[4].split(':')[-1]
          else:
            count = lines[3].split(':')[-1]
          data = color+'|'+size+'|'+count
          send_item(user_id, itemid, None, True, data)
        elif(param2 == 'ordernow'):
          date = datetime.datetime.fromtimestamp(call.message.date).strftime("%d-%m-%Y")
          itemid = int(call.message.caption.split('\n')[0].split(':')[-1].replace(' ',''))
          item = database.getitem(itemid)
          title = item.title
          size = None; color = None; count = None
          lines = call.message.caption.split('\n')
          itemid = lines[0].split(':')[-1]
          color = lines[2].split(':')[-1]
          caption = None
          if(len(lines) == 6):
            size = lines[3].split(':')[-1]
            count = lines[4].split(':')[-1]
            caption = 'Item ID : '+itemid + '\nTitle : '+title + '\nSize : ' +size + '\nColor : '+color + '\nCount : '+count
          else:
            count = lines[3].split(':')[-1]
            caption = 'Item ID : '+itemid + '\nTitle : '+title + '\nColor : '+color + '\nCount : '+count
          res = database.addcart_order(user_id, itemid, title, count, color, size, 'order', date)
          if(res is not None):
            message = "\nPending payment..."
            new_cap = 'Order ID - ' + str(res) +'\n'+ caption + message
            paid_markup = telebot.types.InlineKeyboardMarkup()
            paid_btn = telebot.types.InlineKeyboardButton(text= 'Confirm Payment', callback_data='confirmpayment')
            paid_markup.row(paid_btn)
            bot.send_photo(user_id, item.imagepath, new_cap, reply_markup=paid_markup)
          else:
            bot.send_message(user_id, "Some problem was encountered while saving your order.\nPlease try again.", reply_markup=markup)
      elif (param1 == 'orderdetails'):
        param2 = datas[1]
        inline_keyboard = call.message.reply_markup.keyboard
        if (param2 == 'cart' or param2 == 'order'):
          date = datetime.datetime.fromtimestamp(call.message.date).strftime("%d-%m-%Y")
          itemid = int(call.message.caption.split('\n')[0].split('-')[-1].replace(' ',''))
          title = call.message.caption.split('\n')[2].split('-')[-1]
          itemtype = database.getitem(itemid).itemtype
          size = None; color = None; count = None
          if(itemtype.upper() == 'T-SHIRT' or itemtype.upper() == 'HOODIE'):
            size = inline_keyboard[0][0].text
            color = inline_keyboard[0][1].text
            count = int(inline_keyboard[1][1].text)
          else:
            color = inline_keyboard[0][0].text
            color = 'Frame' if(color == 'Full Black') else color
            count = int(inline_keyboard[1][1].text)
          res = None
          message = None
          if(param2 == 'cart'):
            if(database.incart(user_id,itemid)):
              message = "Your cart has been updated."
              res = database.updatecart(user_id, itemid, count, color, size, date)
            else:
              message = "Item has been added to your cart."
              res = database.addcart_order(user_id, itemid, title, count, color, size, 'cart', date)
            if(res is None):
              bot.delete_message(user_id, call.message.message_id)
              response = bot.send_message(user_id, message, reply_markup=markup)
            else:
              print("Error "+str(res))
          else:
            user = database.getuser(user_id)
            if(user.phone is None):
              keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
              share_contact_btn = telebot.types.KeyboardButton(text="Share", request_contact=True)
              cancel_btn = telebot.types.KeyboardButton(text="Cancel")
              keyboard.row(share_contact_btn, cancel_btn)
              bot.send_message(user_id,"It seems like you have not shared your phone number yet.\nPlease share your number and try again.",reply_markup=keyboard)
            else:
              item = database.getitem(itemid)
              item_type = item.itemtype
              available = database.inavailable(item_type, color, size)
              if(available >= count):
                photoid = database.getitem(itemid).imagepath
                total_price = database.getitem(itemid).price * count
                caption = "Item ID :" + str(itemid) + "\nTitle :" + title + "\nColor :" + color + "\nCount :" + str(count) + '\nTotal Price :' + str(total_price)
                if (size is not None):
                  caption = "Item ID :" + str(itemid) + "\nTitle :" + title + "\nColor :" + color + "\nSize :"+ size + "\nCount :" + str(count) + '\nTotal Price :' + str(total_price)
                order_markup = telebot.types.InlineKeyboardMarkup()
                order_btn = telebot.types.InlineKeyboardButton(text='Order', callback_data='order|ordernow')
                edit_btn = telebot.types.InlineKeyboardButton(text='Edit', callback_data= 'order|editorder')
                cancel = telebot.types.InlineKeyboardButton(text='❌', callback_data='cancel')
                order_markup.row(edit_btn, order_btn, cancel)
                deleteMessage(user_id, call.message.message_id)
                bot.send_photo(user_id, photoid, caption, reply_markup= order_markup)
                
              else:
                bot.send_message(user_id, 'Sorry this items is out of stock.')
        else:
          size_btn = None
          color_btn = None
          if(len(inline_keyboard[0]) == 2):
            size_btn = inline_keyboard[0][0]
            color_btn = inline_keyboard[0][1]
          else:
            color_btn = inline_keyboard[0][0]
          decrease_btn = inline_keyboard[1][0]
          count_btn = inline_keyboard[1][1]
          increase_btn = inline_keyboard[1][2]
          add_to_cart = inline_keyboard[2][0]
          place_an_order = inline_keyboard[2][1]
          cancel = inline_keyboard[2][2]
          
          if(param2 == 'changesize'):
            current_size = inline_keyboard[0][0].text
            size_list = ['M', 'L', 'XL', 'XXL']
            index = size_list.index(current_size)
            next_index = index + 1
            if(index == 3):
              next_index = 0
            size = size_list[next_index]
            size_btn = telebot.types.InlineKeyboardButton(text=size, callback_data = call.data)
          elif (param2 == 'changecolor'):
            current_color = color_btn.text
            current_color = 'Frame' if(current_color == 'Full Black') else current_color
            itemid = int(call.message.caption.split('\n')[0].split('-')[-1].replace(' ',''))
            item = database.getitem(itemid)
            colors = item.color
            if(item.itemtype.upper() == 'T-SHIRT' or item.itemtype.upper() == 'HOODIE'):
              colors = ['White','Black','Gray','Yellow','Red','Green','Blue']
            elif(item.itemtype.upper() == 'MUG'):
              colors = ['Magic','Frame','White','Black','Red','Orange','Green','Blue','Silver','Gold']
            elif(item.itemtype.upper() == 'MASON JAR'):
              colors = ['Clear','Frost']
            current_color_index = colors.index(current_color.replace(' ',''))
            next_color_index = current_color_index + 1
            if(next_color_index == len(colors)):
              next_color_index = 0
            color = colors[next_color_index]
            color = 'Full Black' if(color == 'Frame') else color
            color_btn = telebot.types.InlineKeyboardButton(text=color, callback_data = call.data)
          elif (param2 == 'decrease'):
            cntr = int(inline_keyboard[1][1].text)-1
            if(cntr == 0):
              cntr = 1
              return
            count_btn = telebot.types.InlineKeyboardButton(text=str(cntr), callback_data = 'orderdetails|counter')
          elif (param2 == 'increase'):
            cntr = int(inline_keyboard[1][1].text)+1
            count_btn = telebot.types.InlineKeyboardButton(text=str(cntr), callback_data = 'orderdetails|counter')
          
          markup_inline = telebot.types.InlineKeyboardMarkup()
          if (size_btn is not None):
            markup_inline.row(size_btn, color_btn)
          else:
            markup_inline.row(color_btn)
          markup_inline.row(decrease_btn, count_btn, increase_btn)
          markup_inline.row(add_to_cart, place_an_order, cancel)
          bot.edit_message_reply_markup(user_id,call.message.message_id,reply_markup=markup_inline)
      elif (param1 == 'confirmpayment'):
        print('confirm')
  except Exception as e:
    print(e)

def handleadmincall(call):
  try:
    user_id = call.message.chat.id
    datas = call.data.split('|')
    param1 = datas[0]
    
    if(param1 == 'delivered'):
      database.updateorderdelivered(datas[1])
      sendpendingorders(user_id,messageid = call.message.message_id)
      return
    
    elif(param1 == 'cancel'):
      deleteMessage(user_id, call.message.message_id)
      return
    
    elif (param1 == 'available'):
      param2 = datas[1]
      if(param2 == 'yes'):
        message_text_list = call.message.text.split('\n')
        item_id = int(datas[-1])
        count = int(message_text_list[-1].split('-')[-1])
        res = database.updateitem(item_id, count)
        if(res is None):
          deleteMessage(user_id,call.message.message_id)
          bot.send_message(user_id, 'Update successful.', reply_markup=markup_admin)
        else:
          bot.send_message(user_id, 'Update failed. Try again.')
      else:
        markup_old = call.message.reply_markup.keyboard
        color_btn = markup_old[0][0]
        size_btn = markup_old[0][1] if(len(markup_old[0]) == 2) else None
        decrease5 = markup_old[1][0]
        decrease1 = markup_old[1][1]
        counter = markup_old[1][2]
        increase1 = markup_old[1][3]
        increase5 = markup_old[1][4]
        add_btn = markup_old[2][0]
        cancel_btn = markup_old[2][1]
        if(param2 == 'add'):
          item_name = call.message.text.replace("Item name -", "")
          item_color = color_btn.text
          item_size = size_btn.text if(size_btn is not None or size_btn.text != 'None') else None
          count = int(counter.text)
          if(database.inavailable(item_name,item_color,item_size)):
            text = 'This item is already registerd.\nItem name -'+item_name+'\nItem color -'+item_color+'\nItem size -'+item_size+'\nUpdate count to -'+str(count)
            item = database.getitemcount(item_name, item_size, item_color)
            confirm_markup = telebot.types.InlineKeyboardMarkup()
            yes_btn = telebot.types.InlineKeyboardButton(text='Yes', callback_data='available|yes|'+str(item.id))
            no_btn = telebot.types.InlineKeyboardButton(text='Cancel', callback_data='cancel')
            confirm_markup.row(yes_btn, no_btn)
            deleteMessage(user_id,call.message.message_id)
            bot.send_message(user_id, text, reply_markup=confirm_markup)
          else:
            res = database.addnewitem(item_name,item_color, item_size, count)
            if(res is None):
              deleteMessage(user_id,call.message.message_id)
              bot.send_message(user_id,'New item has been added to stock.',reply_markup=markup_admin)
            else:
              bot.send_message(user_id,'Failed to add item to stock. Try again.')
        else:
          if(param2 == 'changecolor'):
            color_list = datas[-1].split(',')
            next_index = color_list.index(color_btn.text)+1
            if(next_index == len(color_list)):
              next_index = 0
            next_color = color_list[next_index]
            color_btn = telebot.types.InlineKeyboardButton(text=next_color, callback_data= color_btn.callback_data)
          elif(param2 == 'changesize'):
            curr_size = size_btn.text
            size_list = ['M', 'L', 'XL', 'XXL', 'None']
            next_index = size_list.index(curr_size)+1
            if(next_index == len(size_list)):
              next_index = 0
            next_size = size_list[next_index]
            size_btn = telebot.types.InlineKeyboardButton(text=next_size, callback_data=size_btn.callback_data)
          elif(param2 == 'update'):
            num = int(datas[-1])
            new_num = int(counter.text)+num
            if(new_num<0):
              new_num = 0
            counter = telebot.types.InlineKeyboardButton(text=str(new_num), callback_data=counter.callback_data)
          updated_markup = telebot.types.InlineKeyboardMarkup()
          if(size_btn is None):
            updated_markup.row(color_btn)
          else:
            updated_markup.row(color_btn, size_btn)
          updated_markup.row(decrease5,decrease1,counter,increase1, increase5)
          updated_markup.row(add_btn, cancel_btn)
          bot.edit_message_reply_markup(user_id, call.message.message_id, reply_markup=updated_markup)
    
    elif (param1 == 'upitem'):
      if(datas[1] == 'update'):
        inline_keyboard = call.message.reply_markup.keyboard
        for index, keyboard in enumerate(inline_keyboard):
          if(index+1 != len(inline_keyboard)):
            if(len(keyboard) == 1):
              btn1 = keyboard[0]
              callback_data = btn1.callback_data
              itemid = int(callback_data.split('|')[1])
              count = int(btn1.text.split(':')[-1].replace(' ',''))
              database.updateitem(itemid, count)
        deleteMessage(user_id, call.message.message_id)
        bot.send_message(user_id, 'Update successful.' ,reply_markup=markup_admin)
      
      elif(datas[2] != 'skip'):
        itemidnum = int(datas[1])
        increaseby = int(datas[2])
        new_inline_keyboard = telebot.types.InlineKeyboardMarkup()
        inline_keyboard = call.message.reply_markup.keyboard
        for index, keyboard in enumerate(inline_keyboard):
          if(index+1 != len(inline_keyboard)):
            if(len(keyboard) == 1):
              btn1 = keyboard[0]
              callback_data = btn1.callback_data
              itemid = int(callback_data.split('|')[1])
              if(itemid == itemidnum):
                old_count = btn1.text.split(':')[-1].replace(' ','')
                new_count = str(int(old_count)+increaseby) if increaseby !=0 else '0'
                new_count = new_count if int(new_count)>-1 else '0'
                newText = btn1.text.replace(old_count, new_count)
                btn1 = telebot.types.InlineKeyboardButton(text=newText,callback_data = callback_data)
              new_inline_keyboard.row(btn1)
            else:
              btn1 = keyboard[0]
              btn2 = keyboard[1]
              btn3 = keyboard[2]
              btn4 = keyboard[3]
              btn5 = keyboard[4]
              new_inline_keyboard.row(btn1, btn2, btn3, btn4, btn5)
          else:
            cancel = telebot.types.InlineKeyboardButton(text = 'Cancel', callback_data='cancel')
            update = telebot.types.InlineKeyboardButton(text = 'Update', callback_data='upitem|update')
            new_inline_keyboard.row(update, cancel)
        bot.edit_message_reply_markup(user_id,call.message.message_id,reply_markup=new_inline_keyboard)
    
    elif(param1 == 'edititem'):
      printtypeText = 'DTG'
      whiteText = "⬜"; blackText = "⬛"; grayText = "Gray"; redText = "🟥"; yellowText = "🟨"; greenText = "🟩"
      blueText = "🟦"; orangeText = "🟧"; magicText = "Magic"; frameText = "Frame"; silverText = "Silver"
      goldText = "Gold"; frostText = "Frost"; clearText = "Clear"
      
      whiteTextcheck = '⬜ - ✅'; blackTextcheck = '⬛ - ✅'; grayTextcheck = 'Gray - ✅'; redTextcheck = '🟥 - ✅'
      yellowTextcheck = '🟨 - ✅'; greenTextcheck = '🟩 - ✅'; blueTextcheck = '🟦 - ✅'; orangeTextcheck = '🟧 - ✅'
      magicTextcheck = "Magic - ✅"; frameTextcheck = "Frame - ✅"; silverTextcheck = "Silver - ✅"
      goldTextcheck = "Gold - ✅"; frostTextcheck = "Frost - ✅"; clearTextcheck = "Clear - ✅"
      
      item_types = ['T-shirt', 'Hoodie', 'Mug', 'Mason Jar']
      
      markup_inline = telebot.types.InlineKeyboardMarkup()
      inline_keyboard = call.message.reply_markup.keyboard
      param2 = datas[1]
      if(param2 == 'changetype'):
        allcolors = telebot.types.InlineKeyboardButton(text="All", callback_data="edititem|all")
        white = telebot.types.InlineKeyboardButton(text=whiteText, callback_data="edititem|whi|0")
        black = telebot.types.InlineKeyboardButton(text=blackText, callback_data="edititem|bla|0")
        gray = telebot.types.InlineKeyboardButton(text=grayText, callback_data="edititem|gra|0")
        red = telebot.types.InlineKeyboardButton(text=redText, callback_data="edititem|red|0")
        yellow = telebot.types.InlineKeyboardButton(text=yellowText, callback_data="edititem|yel|0")
        green = telebot.types.InlineKeyboardButton(text=greenText, callback_data="edititem|gre|0")
        blue = telebot.types.InlineKeyboardButton(text=blueText, callback_data="edititem|blu|0")
        orange = telebot.types.InlineKeyboardButton(text=orangeText, callback_data="edititem|ora|0")
        magic = telebot.types.InlineKeyboardButton(text=magicText, callback_data="edititem|mag|0")
        frame = telebot.types.InlineKeyboardButton(text=frameText, callback_data="edititem|fra|0")
        silver = telebot.types.InlineKeyboardButton(text=silverText, callback_data="edititem|sil|0")
        gold = telebot.types.InlineKeyboardButton(text=goldText, callback_data="edititem|gol|0")
        clearcolor = telebot.types.InlineKeyboardButton(text=clearText, callback_data="edititem|cle|0")
        frost = telebot.types.InlineKeyboardButton(text=frostText, callback_data="edititem|fro|0")
        clear = telebot.types.InlineKeyboardButton(text="Clear All", callback_data="edititem|clear")
        printtype = telebot.types.InlineKeyboardButton(text=printtypeText, callback_data="edititem|pty|"+printtypeText)
        add = telebot.types.InlineKeyboardButton(text="Done", callback_data="edititem|done")
        
        next_index = item_types.index(inline_keyboard[0][0].text)+1
        if(next_index == len(item_types)):
          next_index = 0
        next_item = item_types[next_index]
        itemtype = telebot.types.InlineKeyboardButton(text=next_item, callback_data="edititem|changetype")
        if(next_item == item_types[0] or next_item == item_types[1]):
          markup_inline.row(itemtype, white, black ,gray)
          markup_inline.row(yellow, red, green, blue)
          markup_inline.row(allcolors, clear, printtype)
        elif(next_item == item_types[2]):
          markup_inline.row(itemtype, allcolors, magic, frame)
          markup_inline.row(white, black, red, orange)
          markup_inline.row(green, blue, silver, gold)
          markup_inline.row(clear)
        elif(next_item == item_types[3]):
          markup_inline.row(itemtype, allcolors)
          markup_inline.row(clearcolor, frost)
          markup_inline.row(clear)
      elif(param2 == 'all'):
        itemtypebtn = inline_keyboard[0][0]
        itemtype = itemtypebtn.text
        allcolors = telebot.types.InlineKeyboardButton(text="All", callback_data="edititem|all")
        white = telebot.types.InlineKeyboardButton(text=whiteTextcheck, callback_data="edititem|whi|1")
        black = telebot.types.InlineKeyboardButton(text=blackTextcheck, callback_data="edititem|bla|1")
        gray = telebot.types.InlineKeyboardButton(text=grayTextcheck, callback_data="edititem|gra|1")
        red = telebot.types.InlineKeyboardButton(text=redTextcheck, callback_data="edititem|red|1")
        yellow = telebot.types.InlineKeyboardButton(text=yellowTextcheck, callback_data="edititem|yel|1")
        green = telebot.types.InlineKeyboardButton(text=greenTextcheck, callback_data="edititem|gre|1")
        blue = telebot.types.InlineKeyboardButton(text=blueTextcheck, callback_data="edititem|blu|1")
        orange = telebot.types.InlineKeyboardButton(text=orangeTextcheck, callback_data="edititem|ora|1")
        magic = telebot.types.InlineKeyboardButton(text=magicTextcheck, callback_data="edititem|mag|1")
        frame = telebot.types.InlineKeyboardButton(text=frameTextcheck, callback_data="edititem|fra|1")
        silver = telebot.types.InlineKeyboardButton(text=silverTextcheck, callback_data="edititem|sil|1")
        gold = telebot.types.InlineKeyboardButton(text=goldTextcheck, callback_data="edititem|gol|1")
        clearcolor = telebot.types.InlineKeyboardButton(text=clearTextcheck, callback_data="edititem|cle|1")
        frost = telebot.types.InlineKeyboardButton(text=frostTextcheck, callback_data="edititem|fro|1")
        clear = telebot.types.InlineKeyboardButton(text="Clear All", callback_data="edititem|clear")
        add = telebot.types.InlineKeyboardButton(text="Done", callback_data="edititem|done")

        if(itemtype == item_types[0] or itemtype == item_types[1]):
          printtype = inline_keyboard[2][1]
          printtype = telebot.types.InlineKeyboardButton(text=printtypeText, callback_data="edititem|pty|"+printtypeText)
          markup_inline.row(itemtypebtn, allcolors, white, black)
          markup_inline.row(gray, red, yellow, green)
          markup_inline.row(blue, clear, printtype, add)
        elif(itemtype == item_types[2]):
          markup_inline.row(itemtypebtn, allcolors, magic, frame)
          markup_inline.row(white, black, red, orange)
          markup_inline.row(green, blue, silver, gold)
          markup_inline.row(clear, add)
        elif(itemtype == item_types[3]):
          markup_inline.row(itemtypebtn, allcolors)
          markup_inline.row(clearcolor, frost)
          markup_inline.row(clear, add)
      elif (param2 == 'clear'):
        itemtypebtn = inline_keyboard[0][0]
        itemtype = itemtypebtn.text
        allcolors = telebot.types.InlineKeyboardButton(text="All", callback_data="edititem|all")
        white = telebot.types.InlineKeyboardButton(text=whiteText, callback_data="edititem|whi|0")
        black = telebot.types.InlineKeyboardButton(text=blackText, callback_data="edititem|bla|0")
        gray = telebot.types.InlineKeyboardButton(text=grayText, callback_data="edititem|gra|0")
        red = telebot.types.InlineKeyboardButton(text=redText, callback_data="edititem|red|0")
        yellow = telebot.types.InlineKeyboardButton(text=yellowText, callback_data="edititem|yel|0")
        green = telebot.types.InlineKeyboardButton(text=greenText, callback_data="edititem|gre|0")
        blue = telebot.types.InlineKeyboardButton(text=blueText, callback_data="edititem|blu|0")
        orange = telebot.types.InlineKeyboardButton(text=orangeText, callback_data="edititem|ora|0")
        magic = telebot.types.InlineKeyboardButton(text=magicText, callback_data="edititem|mag|0")
        frame = telebot.types.InlineKeyboardButton(text=frameText, callback_data="edititem|fra|0")
        silver = telebot.types.InlineKeyboardButton(text=silverText, callback_data="edititem|sil|0")
        gold = telebot.types.InlineKeyboardButton(text=goldText, callback_data="edititem|gol|0")
        clearcolor = telebot.types.InlineKeyboardButton(text=clearText, callback_data="edititem|cle|0")
        frost = telebot.types.InlineKeyboardButton(text=frostText, callback_data="edititem|fro|0")
        clear = telebot.types.InlineKeyboardButton(text="Clear All", callback_data="edititem|clear")

        if(itemtype == item_types[0] or itemtype == item_types[1]):
          printtype = inline_keyboard[2][2]
          printtype = telebot.types.InlineKeyboardButton(text=printtypeText, callback_data="edititem|pty|"+printtypeText)
          markup_inline.row(itemtypebtn, allcolors, white, black)
          markup_inline.row(gray, red, yellow, green)
          markup_inline.row(blue, clear, printtype)
        elif(itemtype == item_types[2]):
          markup_inline.row(itemtypebtn, allcolors, magic, frame)
          markup_inline.row(white, black, red, orange)
          markup_inline.row(green, blue, silver, gold)
          markup_inline.row(clear)
        elif(itemtype == item_types[3]):
          markup_inline.row(itemtypebtn, allcolors)
          markup_inline.row(clearcolor, frost)
          markup_inline.row(clear)    
      elif(param2 == 'done'):
        itemtypebtn = inline_keyboard[0][0]
        itemtype = itemtypebtn.text
        colors = []
        count = 0
        printtype = None
        colors_str = None
        if(itemtype == item_types[0] or itemtype == item_types[1]):
          if(inline_keyboard[0][2].callback_data.split('|')[-1] == '1'):
            count += 1; colors.append('White')
          if(inline_keyboard[0][3].callback_data.split('|')[-1] == '1'):
            count += 1; colors.append('Black')
          if(inline_keyboard[1][0].callback_data.split('|')[-1] == '1'):
            count += 1; colors.append('Gray')
          if(inline_keyboard[1][1].callback_data.split('|')[-1] == '1'):
            count += 1; colors.append('Red')
          if(inline_keyboard[1][2].callback_data.split('|')[-1] == '1'):
            count += 1; colors.append('Yellow')
          if(inline_keyboard[1][3].callback_data.split('|')[-1] == '1'):
            count += 1; colors.append('Green')
          if(inline_keyboard[2][0].callback_data.split('|')[-1] == '1'):
            count += 1; colors.append('Blue')
          printtype = inline_keyboard[2][2].text
          colors_str = str(colors).replace('[', '{').replace(']', '}').replace("'", "")
          if(count == 7):
            colors_str = "{ALL}"
        elif(itemtype == item_types[2]):
          if(inline_keyboard[0][2].callback_data.split('|')[-1] == '1'):
            count += 1; colors.append('Magic')
          if(inline_keyboard[0][3].callback_data.split('|')[-1] == '1'):
            count += 1; colors.append('Frame')
          if(inline_keyboard[1][0].callback_data.split('|')[-1] == '1'):
            count += 1; colors.append('White')
          if(inline_keyboard[1][1].callback_data.split('|')[-1] == '1'):
            count += 1; colors.append('Black')
          if(inline_keyboard[1][2].callback_data.split('|')[-1] == '1'):
            count += 1; colors.append('Red')
          if(inline_keyboard[1][3].callback_data.split('|')[-1] == '1'):
            count += 1; colors.append('Orange')
          if(inline_keyboard[2][0].callback_data.split('|')[-1] == '1'):
            count += 1; colors.append('Green')
          if(inline_keyboard[2][1].callback_data.split('|')[-1] == '1'):
            count += 1; colors.append('Blue')
          if(inline_keyboard[2][2].callback_data.split('|')[-1] == '1'):
            count += 1; colors.append('Silver')
          if(inline_keyboard[2][3].callback_data.split('|')[-1] == '1'):
            count += 1; colors.append('Gold')
          colors_str = str(colors).replace('[', '{').replace(']', '}').replace("'", "")
          if(count == 10):
            colors_str = "{ALL}"
        elif(itemtype == item_types[3]):
          if(inline_keyboard[1][0].callback_data.split('|')[-1] == '1'):
            count += 1; colors.append('Clear')
          if(inline_keyboard[1][1].callback_data.split('|')[-1] == '1'):
            count += 1; colors.append('Frost')
          colors_str = str(colors).replace('[', '{').replace(']', '}').replace("'", "")
          if(count == 2):
            colors_str = "{ALL}"
        
        itemid = int(call.message.caption.split('\n')[0].split('-')[-1].replace(' ',''))
        title = call.message.caption.split('\n')[1].split('-')[-1]
        messageid = int(call.message.caption.split('\n')[2].split('-')[-1].replace(' ',''))
        imagepath = call.message.photo[-1].file_id
        res = None
        message = "Item has been saved."
        if(count>0):
          if(database.initems(itemid)):
            message = "Item has been updated."
            res = database.updateitem(itemid, itemtype, title, colors_str, printtype, imagepath)
          else:
            price = database.getprice(itemtype)
            res = database.additem(itemid, messageid, itemtype, title, colors_str, printtype, imagepath, price)
          if(res is None):
            response = bot.send_message(user_id, message)
            t = Timer(3.0, deleteMessage,[user_id, response.message_id])
            t.start();
            deleteMessage(user_id,call.message.message_id)
            return
          else:
            print(res)
            response = bot.send_message(user_id, "Something went wrong. Try again.")
            t = Timer(3.0, deleteMessage,[user_id, response.message_id])
            t.start();
            return
        else:
          res = bot.send_message(user_id, "Choose atleast one color.")
          t = threading.Timer(3.0, deleteMessage, [user_id, res.message_id])
          t.start()
      else:
        itemtypebtn = inline_keyboard[0][0]
        itemtype = itemtypebtn.text
        if(itemtype == item_types[0] or itemtype == item_types[1]):
          allcolors = inline_keyboard[0][1]
          white = inline_keyboard[0][2]
          black = inline_keyboard[0][3]
          gray = inline_keyboard[1][0]
          red = inline_keyboard[1][1]
          yellow = inline_keyboard[1][2]
          green = inline_keyboard[1][3]
          blue = inline_keyboard[2][0]
          clear = inline_keyboard[2][1]
          printtype = inline_keyboard[2][2]
          add = telebot.types.InlineKeyboardButton(text='Done', callback_data='edititem|done')

          if(param2 == 'pty'):
            ptlist = ['DTG', 'Vinyl', 'Sublimation']
            curr_index = ptlist.index(datas[-1].replace(' ',''))
            next_index = curr_index + 1
            if(next_index == len(ptlist)):
              next_index = 0
            printtypeText = ptlist[next_index]
            new_data = inline_keyboard[2][2].callback_data.replace(datas[-1], printtypeText)
            printtype = telebot.types.InlineKeyboardButton(text=printtypeText, callback_data = new_data)
          else:
            checked = datas[2]
            status = '0' if(checked == '1') else '1'
            if(param2 == 'whi'):
              text_data = whiteTextcheck if (checked == '0') else whiteText
              callback_data_new = "edititem|whi|"+status
              white = telebot.types.InlineKeyboardButton(text=text_data, callback_data = callback_data_new)
            elif(param2 == 'bla'):
              text_data = blackTextcheck if (checked == '0') else blackText
              callback_data_new = "edititem|bla|"+status
              black = telebot.types.InlineKeyboardButton(text=text_data, callback_data = callback_data_new)
            elif(param2 == 'gra'):
              text_data = grayTextcheck if (checked == '0') else grayText
              callback_data_new = "edititem|gra|"+status
              gray = telebot.types.InlineKeyboardButton(text=text_data, callback_data = callback_data_new)
            elif(param2 == 'red'):
              text_data = redTextcheck if (checked == '0') else redText
              callback_data_new = "edititem|red|"+status
              red = telebot.types.InlineKeyboardButton(text=text_data, callback_data = callback_data_new)
            elif(param2 == 'yel'):
              text_data = yellowTextcheck if (checked == '0') else yellowText
              callback_data_new = "edititem|yel|"+status
              yellow = telebot.types.InlineKeyboardButton(text=text_data, callback_data = callback_data_new)
            elif(param2 == 'gre'):
              text_data = greenTextcheck if (checked == '0') else greenText
              callback_data_new = "edititem|gre|"+status
              green = telebot.types.InlineKeyboardButton(text=text_data, callback_data = callback_data_new)
            elif(param2 == 'blu'):
              text_data = blueTextcheck if (checked == '0') else blueText
              callback_data_new = "edititem|blu|"+status
              blue = telebot.types.InlineKeyboardButton(text=text_data, callback_data = callback_data_new)
          markup_inline.row(itemtypebtn, allcolors, white, black)
          markup_inline.row(gray, red, yellow, green)
          markup_inline.row(blue, clear, printtype, add)
        elif(itemtype == item_types[2]):
          allcolors = inline_keyboard[0][1]
          magic = inline_keyboard[0][2]
          frame = inline_keyboard[0][3]
          white = inline_keyboard[1][0]
          black = inline_keyboard[1][1]
          red = inline_keyboard[1][2]
          orange = inline_keyboard[1][3]
          green = inline_keyboard[2][0]
          blue = inline_keyboard[2][1]
          silver = inline_keyboard[2][2]
          gold = inline_keyboard[2][3]
          clear = inline_keyboard[3][0]
          add = telebot.types.InlineKeyboardButton(text='Done', callback_data='edititem|done')

          checked = datas[2]
          status = '0' if(checked == '1') else '1'
          if(param2 == 'mag'):
            text_data = magicTextcheck if (checked == '0') else magicText
            callback_data_new = "edititem|mag|"+status
            magic = telebot.types.InlineKeyboardButton(text=text_data, callback_data = callback_data_new)
          elif(param2 == 'fra'):
            text_data = frameTextcheck if (checked == '0') else frameText
            callback_data_new = "edititem|fra|"+status
            frame = telebot.types.InlineKeyboardButton(text=text_data, callback_data = callback_data_new)
          elif(param2 == 'whi'):
            text_data = whiteTextcheck if (checked == '0') else whiteText
            callback_data_new = "edititem|whi|"+status
            white = telebot.types.InlineKeyboardButton(text=text_data, callback_data = callback_data_new)
          elif(param2 == 'bla'):
            text_data = blackTextcheck if (checked == '0') else blackText
            callback_data_new = "edititem|bla|"+status
            black = telebot.types.InlineKeyboardButton(text=text_data, callback_data = callback_data_new)
          elif(param2 == 'red'):
            text_data = redTextcheck if (checked == '0') else redText
            callback_data_new = "edititem|red|"+status
            red = telebot.types.InlineKeyboardButton(text=text_data, callback_data = callback_data_new)
          elif(param2 == 'ora'):
            text_data = orangeTextcheck if (checked == '0') else orangeText
            callback_data_new = "edititem|ora|"+status
            orange = telebot.types.InlineKeyboardButton(text=text_data, callback_data = callback_data_new)
          elif(param2 == 'gre'):
            text_data = greenTextcheck if (checked == '0') else greenText
            callback_data_new = "edititem|gre|"+status
            green = telebot.types.InlineKeyboardButton(text=text_data, callback_data = callback_data_new)
          elif(param2 == 'blu'):
            text_data = blueTextcheck if (checked == '0') else blueText
            callback_data_new = "edititem|blu|"+status
            blue = telebot.types.InlineKeyboardButton(text=text_data, callback_data = callback_data_new)
          elif(param2 == 'sil'):
            text_data = silverTextcheck if (checked == '0') else silverText
            callback_data_new = "edititem|sil|"+status
            silver = telebot.types.InlineKeyboardButton(text=text_data, callback_data = callback_data_new)
          elif(param2 == 'gol'):
            text_data = goldTextcheck if (checked == '0') else goldText
            callback_data_new = "edititem|gol|"+status
            gold = telebot.types.InlineKeyboardButton(text=text_data, callback_data = callback_data_new)
          markup_inline.row(itemtypebtn, allcolors, magic, frame)
          markup_inline.row(white, black, red, orange)
          markup_inline.row(green, blue, silver, gold)
          markup_inline.row(clear, add)
        elif(itemtype == item_types[3]):
          allcolors = inline_keyboard[0][1]
          clearcolor = inline_keyboard[1][0]
          frost = inline_keyboard[1][1]
          clear = inline_keyboard[2][0]
          add = telebot.types.InlineKeyboardButton(text='Done', callback_data='edititem|done')

          checked = datas[2]
          status = '0' if(checked == '1') else '1'
          if(param2 == 'cle'):
            text_data = clearTextcheck if (checked == '0') else clearText
            callback_data_new = "edititem|cle|"+status
            clearcolor = telebot.types.InlineKeyboardButton(text=text_data, callback_data = callback_data_new)
          elif(param2 == 'fro'):
            text_data = frostTextcheck if (checked == '0') else frostText
            callback_data_new = "edititem|fro|"+status
            frost = telebot.types.InlineKeyboardButton(text=text_data, callback_data = callback_data_new)
          markup_inline.row(itemtypebtn, allcolors)
          markup_inline.row(clearcolor, frost)
          markup_inline.row(clear, add)  
        
      bot.edit_message_reply_markup(user_id, call.message.message_id, reply_markup=markup_inline)

    elif(param1 == 'defaultprice'):
      param2 = datas[1]
      price_markup = call.message.reply_markup.keyboard
      if(param2 == 'update'):
        counter = 0
        while counter+2 < len(price_markup):
          itemtype = price_markup[counter][0].text
          itemprice = float(price_markup[counter+1][2].text)
          discount = int(price_markup[counter+2][2].text.replace('%',''))
          database.updatedefaultprice(itemtype, itemprice, discount)
          counter += 3
        deleteMessage(user_id, call.message.message_id)
        bot.send_message(user_id, 'Default prices have been updated.', reply_markup=markup_admin)
      elif(param2 != 'skip'):
        itemtype = datas[-1]
        new_price_markup = telebot.types.InlineKeyboardMarkup()
        if(param2 == 'discount'):
          updatenum = int(datas[2])
          counter = 0
          while counter+2 < len(price_markup):
            item_name = price_markup[counter][0]
            decrease10 = price_markup[counter+1][0]
            decrease5 = price_markup[counter+1][1]
            price = price_markup[counter+1][2]
            increase5 = price_markup[counter+1][3]
            increase10 = price_markup[counter+1][4]
            discountd10 = price_markup[counter+2][0]
            discountd1 = price_markup[counter+2][1]
            discount = price_markup[counter+2][2]
            discount1 = price_markup[counter+2][3]
            discount10 = price_markup[counter+2][4]
            if(item_name.text == itemtype):
              new_discount = int(discount.text.replace('%', ''))+updatenum
              if(updatenum == 0):
                new_discount = 0
              if(new_discount<0):
                new_discount = 0
              elif(new_discount > 100):
                new_discount = 100
              discount = telebot.types.InlineKeyboardButton(text=str(new_discount)+'%', callback_data='defaultprice|discount|0|'+itemtype)
            new_price_markup.row(item_name)
            new_price_markup.row(decrease10, decrease5, price, increase5, increase10)
            new_price_markup.row(discountd10, discountd1, discount, discount1, discount10)
            counter += 3
        else:
          updatenum = int(datas[1])
          counter = 0
          while counter+2 < len(price_markup):
            item_name = price_markup[counter][0]
            decrease10 = price_markup[counter+1][0]
            decrease5 = price_markup[counter+1][1]
            price = price_markup[counter+1][2]
            increase5 = price_markup[counter+1][3]
            increase10 = price_markup[counter+1][4]
            discountd10 = price_markup[counter+2][0]
            discountd1 = price_markup[counter+2][1]
            discount = price_markup[counter+2][2]
            discount1 = price_markup[counter+2][3]
            discount10 = price_markup[counter+2][4]
            if(item_name.text == itemtype):
              new_price = float(price.text)+updatenum
              if(new_price < 0):
                new_price = 0
              price = telebot.types.InlineKeyboardButton(text=str(new_price), callback_data='defaultprice|skip')
            new_price_markup.row(item_name)
            new_price_markup.row(decrease10, decrease5, price, increase5, increase10)
            new_price_markup.row(discountd10, discountd1, discount, discount1, discount10)
            counter += 3
        update = telebot.types.InlineKeyboardButton(text='Update', callback_data='defaultprice|update')
        cancel = telebot.types.InlineKeyboardButton(text='Cancel', callback_data='cancel')
        new_price_markup.row(update, cancel)
        bot.edit_message_reply_markup(user_id, call.message.message_id,reply_markup= new_price_markup)

    elif(param1 == 'newitemtype'):
      param2 = datas[1]
      price_markup = call.message.reply_markup.keyboard
      if(param2 == 'create'):
        itemtype = price_markup[0][0].text
        itemprice = float(price_markup[1][2].text)
        print(price_markup[2][2].text.replace('%',''))
        discount = int(price_markup[2][2].text.replace('%',''))
        res = database.addnewitemtype(itemtype, itemprice, discount)
        if(res is None):
          deleteMessage(user_id, call.message.message_id)
          bot.send_message(user_id, 'Item type - '+itemtype+' has been created.', reply_markup=markup_admin)
        else:
          bot.send_message(user_id, 'Something went wrong. Try again.', reply_markup=markup_admin)
      elif(param2 != 'skip'):
        itemtype = datas[-1]
        new_price_markup = telebot.types.InlineKeyboardMarkup()
        item_name = price_markup[0][0]
        decrease10 = price_markup[1][0]
        decrease5 = price_markup[1][1]
        price = price_markup[1][2]
        increase5 = price_markup[1][3]
        increase10 = price_markup[1][4]
        discountd10 = price_markup[2][0]
        discountd1 = price_markup[2][1]
        discount = price_markup[2][2]
        discount1 = price_markup[2][3]
        discount10 = price_markup[2][4]
        if(param2 == 'discount'):
          updatenum = int(datas[2])
          new_discount = int(discount.text.replace('%', ''))+updatenum
          if(updatenum == 0):
            new_discount = 0
          if(new_discount<0):
            new_discount = 0
          elif(new_discount > 100):
            new_discount = 100
          discount = telebot.types.InlineKeyboardButton(text=str(new_discount)+'%', callback_data='newitemtype|discount|0')
        else:
          updatenum = int(datas[1])
          new_price = float(price.text)+updatenum
          if(new_price < 0):
            new_price = 0
          price = telebot.types.InlineKeyboardButton(text=str(new_price), callback_data='newitemtype|skip')
        new_price_markup.row(item_name)
        new_price_markup.row(decrease10, decrease5, price, increase5, increase10)
        new_price_markup.row(discountd10, discountd1, discount, discount1, discount10)
        create = telebot.types.InlineKeyboardButton(text='Create', callback_data='newitemtype|create')
        cancel = telebot.types.InlineKeyboardButton(text='Cancel', callback_data='cancel')
        new_price_markup.row(create, cancel)
        bot.edit_message_reply_markup(user_id, call.message.message_id,reply_markup= new_price_markup)

  except Exception as e:
    print(e)

def send_cartlist(user_id, message_id):
  try:
    cart = database.getcart(str(user_id))
    if (len(cart) == 0):
      if(message_id is not None):
        deleteMessage(user_id, message_id)
      bot.send_message(user_id, "Your cart is empty.",reply_markup=markup)
    else:
      markup_inline = telebot.types.InlineKeyboardMarkup()
      for item in cart:
        color = item.color if(item.color != 'Frame') else 'Full Black'
        cart_details = color+' - '+str(item.count)+' ✎'
        if(item.type.upper() == 'T-SHIRT' or item.type.upper() == 'HOODIE'):
          cart_details = color+' - '+item.size+' - '+str(item.count)+' ✎'
        item_detail = database.getitem(str(item.itemid).replace(' ', ''))
        tochannel = telebot.types.InlineKeyboardButton(text='Item ID - '+str(item.itemid), url=main_channel+str(item_detail.messageid))
        editcart = telebot.types.InlineKeyboardButton(text=cart_details, callback_data="cartlist|editcart|"+str(item.itemid))
        removecart = telebot.types.InlineKeyboardButton(text="❌", callback_data="cartlist|remove|"+str(item.itemid))
        markup_inline.row(tochannel, editcart, removecart)
      orderall = telebot.types.InlineKeyboardButton(text='Order All', callback_data='cartlist|orderall')
      cancel = telebot.types.InlineKeyboardButton(text="Cancel", callback_data="cancel")
      markup_inline.row(orderall, cancel)
      if (message_id is None):
        bot.send_message(user_id, "Here is your cart.", reply_markup=markup_inline)
      else:
        bot.edit_message_reply_markup(user_id, message_id, reply_markup=markup_inline)
  except Exception as e:
    print(e)

def send_orderslist(user_id):
  orders = database.getorders(str(user_id))
  if (len(orders) == 0):
    bot.send_message(user_id, "You haven't ordered anything yet.",reply_markup=markup)
  else:
    markup_inline = telebot.types.InlineKeyboardMarkup()
    for item in orders:
      item_detail = database.getitem(str(item.itemid).replace(' ', ''))
      tochannel = telebot.types.InlineKeyboardButton(text='Item ID - '+str(item.itemid), url=main_channel+str(item_detail.messageid))
      order = telebot.types.InlineKeyboardButton(text="✎", callback_data="newcart|"+str(item.itemid))
      markup_inline.row(tochannel, order)
    cancel = telebot.types.InlineKeyboardButton(text="Cancel", callback_data="cancel")
    markup_inline.row(cancel)
    bot.send_message(user_id, "Here are your orders.", reply_markup=markup_inline)

def send_item(user_id, item_id, message_id, edit = False, olddata = None):
  try:  
    item = database.getitem(int(item_id))
    if(item is None):
      bot.send_message(user_id, "Could not find requested item.\n\tPlease try again.")
      return
  
    colors = item.color
    if(colors[0]=="ALL"):
      if(item.itemtype.upper() == 'T-SHIRT' or item.itemtype.upper() == 'HOODIE'):
        colors = ['White','Black','Gray','Yellow','Red','Green','Blue']
      elif(item.itemtype.upper() == 'MUG'):
        colors = ['Magic','Frame','White','Black','Red','Orange','Green','Blue','Silver','Gold']
      elif(item.itemtype.upper() == 'MASON JAR'):
        colors = ['Clear','Frost']
    
    sizeText = 'M'
    countText = '1'
    cartText = 'Add Cart'
    colorText = colors[0]
    colorText = 'Full Black' if(colorText == 'Frame') else colorText
    if(database.incart(user_id, item_id)):
      itemInCart = database.getItemInCart(user_id,item_id,True)
      sizeText = itemInCart.size
      colorText = itemInCart.color.replace(" ","")
      colorText = 'Full Black' if(colorText == 'Frame') else colorText
      countText = str(itemInCart.count)
      cartText = 'Update Cart'
    elif (database.inorders(user_id, item_id)):
      itemInCart = database.getItemInCart(user_id,item_id, False)
      sizeText = itemInCart.size
      colorText = itemInCart.color.replace(" ","")
      colorText = 'Full Black' if(colorText == 'Frame') else colorText
    
    if edit:
      datas = olddata.split('|')
      colorText = datas[0]
      sizeText = datas[1]
      countText = datas[2]
    
    size = None
    if(item.itemtype.upper() == 'T-SHIRT' or item.itemtype.upper() == 'HOODIE'):
      size  = telebot.types.InlineKeyboardButton(text=sizeText, callback_data="orderdetails|changesize")
    color = telebot.types.InlineKeyboardButton(text=colorText,callback_data= "orderdetails|changecolor")
    decreasecount = telebot.types.InlineKeyboardButton(text='-', callback_data="orderdetails|decrease")
    count = telebot.types.InlineKeyboardButton(text=countText,callback_data="orderdetails|counter")
    increasecount = telebot.types.InlineKeyboardButton(text='+', callback_data="orderdetails|increase")
    add_to_cart = telebot.types.InlineKeyboardButton(text=cartText, callback_data="orderdetails|cart")
    place_an_order = telebot.types.InlineKeyboardButton(text='Order Now', callback_data="orderdetails|order")
    cancel = telebot.types.InlineKeyboardButton(text='Cancel', callback_data="cancel")
    
    markup_inline = telebot.types.InlineKeyboardMarkup()
    cap = None
    if(size is not None):
      markup_inline.row(size, color)
      cap = "Item ID - "+item.itemid+"\nItem Type - "+item.itemtype+"\nTitle - "+item.title+"\nPrint Type - "+item.printtype+"\nPrevious Orders - "+str(item.orders)
    else:
      markup_inline.row(color)
      cap = "Item ID - "+item.itemid+"\nItem Type - "+item.itemtype+"\nTitle - "+item.title+"\nPrevious Orders - "+str(item.orders)
    markup_inline.row(decreasecount, count, increasecount)
    markup_inline.row(add_to_cart, place_an_order, cancel)

    if(message_id is not None):
      bot.delete_message(user_id, message_id)
    
    res = bot.send_photo(user_id, item.imagepath, caption=cap, reply_markup=markup_inline)
  except Exception as e:
    print(e)

# Start the server
if (__name__ == "__main__"):
  while True:
    try:
      bot.polling()
    except:
      print('Connection error.')
