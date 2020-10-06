from XTBApi.api import Client
import time, threading, requests, json, select, tty, termios,sys,os
from datetime import datetime


loopInterval=0.5
totalProfit=0
client = Client()
cyclesToSendInfo=0
buy=False
sell=False
TP = 10
SL = -20
volumen = 0.02
priceGradient= 0   
x = list(range(0))  
y = list(range(0))    
buyProfit =0
sellProfit = 0
lastProfits={}
passwords=''
secondsForAnalisys=3
tradeEnable=False
info=''
def loadPass() :
    global passwords
    file = open('../../dump.txt', 'r')
    passwords=file.read()
    file.close()


def printXY(message,x=2,y=0):
    #store cursor
    print('\033[s',end='')
    #move to x y and print
    print('\033[%d;%dH%s' % (x, y, message),end='')
    #restore cursor
    print('\033[u\033[1A')

class NonBlockingConsole(object):

    def __enter__(self):
        self.old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())
        return self

    def __exit__(self, type, value, traceback):
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)


    def get_data(self):
        if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
            return sys.stdin.read(1)
        return False
def menageMenu():
    CRED = '\033[91m'
    CGREEN = '\033[92m'
    CEND = '\033[0m'       
    global tradeEnable
    global info
    rows, columns = os.popen('stty size', 'r').read().split()
    if tradeEnable :
        menuTradeColor=CGREEN
    else:
        menuTradeColor=CRED
    menuOptions='| Menu | ' + menuTradeColor+'Trade \033[0m| \033[92mB\033[0muy | \033[92mS\033[0mell | \033[92mQ\033[0muit |'
    printXY(menuOptions,1,1)    
    c=nbc.get_data()
    if c!=False:
        if len(info)>10:
            info=''
        info=info+c
    if c == 'g':
        info=info[:-1]
        if info == 't':
            if not tradeEnable:
                #printXY('>> Trade was enabled  <<',1,int(columns)-24)    
                info='>> Trade was enabled  <<'
                tradeEnable=True
            else:
               # printXY('>> Trade was disabled  <<',1,55)   
                info='>> Trade was disabled  <<'
                tradeEnable=False
        if info == '\x1b' or info == 'q':  # x1b is ESC
           # printXY('>> Quit <<',1,int(columns)-10)
            info=' >> Quit <<'
        #for c in menuOptions:
            #if c.isprintable() :
                #printableChars+=1
    
    print('\033[s',end='')
    printableChars=len(menuOptions+info)-36
    #move to x y and print
    print('\033[%d;%dH%s' % (1, len(menuOptions)-36+1, info),end='')
    for i in range(int(columns)-printableChars):
        print(' ',end='')              
    #move to x y and print
    print('\033[%d;%dH' % (2, 1),end='')
    for i in range(int(columns)):
        print('-',end='')           
#restore cursor  
    print('\033[u\033[1A')  
    if info==' >> Quit <<':    
        time.sleep(3)
        return False  
  
    return True
def pushbullet_message(title, body):
    global passwords
    creds=passwords.split(',')
    msg = {"type": "note", "title": title, "body": body}
    TOKEN = creds[2][:-1]#remove last end line sign
    resp = requests.post('https://api.pushbullet.com/v2/pushes', 
                        data=json.dumps(msg),
                        headers={'Authorization': 'Bearer ' + TOKEN,
                                'Content-Type': 'application/json'})
    if resp.status_code != 200:
        print('blad przy wysylanu notyfikacji')
        raise Exception('Error',resp.status_code)   
    

def connectToXtb() :
    global totalProfit 
    global passwords
    cred=passwords.split(',')
    if str(client.status) == "STATUS.NOT_LOGGED" :
        client.login(cred[0],cred[1])    
        tradeHistory=client.get_trades_history(datetime(datetime.now().year,datetime.now().month , datetime.now().day, 4, 0).timestamp()*1000,0)
        totalProfit = round(sum( [trade['profit'] for trade in tradeHistory]),2)
        pushbullet_message("Trade robot working!",'Start balace: ' + str(totalProfit) +'PLN')



def trade():
    global loopInterval
    global totalProfit
    global client   
    global cyclesToSendInfo
    global buy
    global sell
    global TP 
    global SL 
    global volumen 
    global priceGradient
    global x 
    global y         
    global buyProfit
    global sellProfit 
    global lastProfits
    global secondsForAnalisys
    global tradeEnable
    CRED = '\033[91m'
    CGREEN = '\033[92m'
    CEND = '\033[0m'    
    if str(client.status) != "STATUS.NOT_LOGGED" :   
        data=client.get_symbol("US100")     
    
        if len(x) == 200:
            x = x[1:]  # Remove the first y element.
        if len(x) > 0:    
            x.append(x[-1] + 1)  # Add a new value 1 higher than the last.
        else:
            x.append(1)

        if len(y) == 200:
            y = y[1:]  # Remove the first 
        y.append( data['ask']) #randint(0,100))  # Add a new random value.
            
        # get trades and analize them
        if len(y) > secondsForAnalisys:
            priceGradient= sum([price-y[-secondsForAnalisys] for price in y[-(secondsForAnalisys-1):]  ]   )
            #priceGradient=priceGradient/(secondsForAnalisys/2)
        trades=client.update_trades()
        trade_ids = [trade_id for trade_id in trades.keys()]
        buy= False
        sell= False     
        for trade in trade_ids:
            try:
                actual_profit =  client.get_trade_profit(trade) # CHECK PROFIT
                transaktionMode = client.trade_rec[trade].mode
            except:
                actual_profit=0
                transaktionMode=''
            buy= transaktionMode == "buy" or buy
            sell= transaktionMode == "sell" or sell 
            #buy display
            if transaktionMode == 'buy':
                buyProfit = actual_profit
                #if actual_profit >=0:
                 #   print(CGREEN+"Buy profit: "+ str(actual_profit)+CEND)
                #else:
                #    print(CRED+"Buy profit: "+ str(actual_profit)+CEND)'''
                

            # sell display
            if transaktionMode == 'sell':
                sellProfit = actual_profit
                #'''if actual_profit >=0:
                #    print(CGREEN+"Sell profit: "+ str(actual_profit)+CEND)
                #else:
                #    print(CRED+"Sell profit: "+ str(actual_profit)+CEND)'''
                         
            ##close transaction 
            #if trade in lastProfits.keys():
                #if ((actual_profit >= TP) and (actual_profit < lastProfits[trade])) or actual_profit <= SL :
                    #client.close_trade(trade) # CLOSE TRADE    
                    #cyclesToSendInfo=5
                    #lastProfits
            
            lastProfits[trade]=actual_profit    

        # otwieranie tranzakcji  
        if (not buy) and  (len(trade_ids) <1 and tradeEnable):
            if priceGradient > (8.0*(data['ask']-data['bid'])):
                client.open_trade('buy', "US100", volumen,data['ask']-20,data['ask']+10)  
        if (not sell) and  (len(trade_ids) <1 and tradeEnable):            
            if priceGradient < ((-8.0)*(data['ask']-data['bid'])):
                client.open_trade('sell', "US100", volumen,data['bid']+20,data['bid']-10)
         
    ########### display menu and info  
        if priceGradient > 8*(data['ask']-data['bid']):
            print('%s|% 6.2f  / % 6.2f %s' %( CGREEN, float(round(priceGradient,2)), round(8*(data['ask']-data['bid']),2) ,CEND),end='')  
        elif priceGradient < (-8*(data['ask']-data['bid'])):
            print('%s|% 6.2f  / % 6.2f %s' %( CRED, float(round(priceGradient,2)), round(8*(data['ask']-data['bid']),2) ,CEND),end='')  
        else:
            print('|% 6.2f  / % 6.2f ' %( float(round(priceGradient,2)), round(8*(data['ask']-data['bid']),2) ),end='')  
            
        if buy:
            if buyProfit>=0:
                print("%s| Buy: % 6.2f %s" % (CGREEN,float(buyProfit),CEND),end='')
            else:
                print("%s| Buy: % 6.2f %s" %(CRED,buyProfit,CEND),end='')    
        else:
                print("| Buy: % 6.2f " % (float(buyProfit)),end='')
            
        if sell:    
            if sellProfit >=0:
                print("%s| Sell: % 6.2f %s" % (CGREEN,sellProfit,CEND),end='')
            else:
                print("%s| Sell: % 6.2f %s" % (CRED ,sellProfit, CEND),end='')
        else:
                print("| Sell: % 6.2f " % (sellProfit),end='')
                
        if totalProfit >=0:
            print("| %sDay: % 6.2f %s" % (CGREEN, totalProfit, CEND))
        else:
            print("| %sDay: % 6.2f  %s" % (CRED, totalProfit, CEND))   
        if not menageMenu():
            return False

    #send push notification
    if cyclesToSendInfo > 0:
        cyclesToSendInfo=cyclesToSendInfo-1
        if cyclesToSendInfo ==0:     
            tradeHistory=client.get_trades_history(datetime(datetime.now().year,datetime.now().month , datetime.now().day, 4, 0).timestamp()*1000,0)     
            totalProfit= round(sum( [trade['profit'] for trade in tradeHistory]),2)
           # print("Total Profit: "+ str(totalProfit))  
            title="Wynik: "+str(tradeHistory[0]['profit']) + " PLN"
            message="Dzienny zysk: " + str(totalProfit) + " PLN"
            pushbullet_message(title,message)    
    return True

    
#def loop():

loadPass()
connectToXtb()
while 1:    
    with NonBlockingConsole() as nbc:
        if not trade():
            break




    #threading.Timer(loopInterval, loop).start() 
#loop()
#client.logout()