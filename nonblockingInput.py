import sys
import select
import tty
import termios
import time

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

CRED = '\033[91m'
CGREEN = '\033[92m'
CEND = '\033[0m'   
print('\033[2J')
menuOptions='| Menu | \033[92mT\033[0mrade Enable | \033[92mB\033[0muy strop | \033[92mS\033[0mell Stop | \033[92mQ\033[0muit |'
printXY(menuOptions,1,1)
with NonBlockingConsole() as nbc:
    i = 0
    while 1:
        i += 1
        c=nbc.get_data()
        if c == 't':
            printXY(' >> Trade was enabled  <<',1,55)
        if c == 'b':
            printXY(' >> Buy was stopped <<   ',1,55)
        if c == '\x1b' or c == 'q':  # x1b is ESC
            printXY(' >> Quit <<              ',1,55)
            time.sleep(3)
            break
    time.sleep(0.1)