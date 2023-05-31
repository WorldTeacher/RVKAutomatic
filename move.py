import pyautogui
import win32gui
import win32con
import regex as re
#pyautogui.moveTo(1920,1080, duration=0.25)

import win32gui
import re


class WindowMgr:
    """Encapsulates some calls to the winapi for window management"""

    def __init__ (self):
        """Constructor"""
        self._handle = None

    def find_window(self, class_name, window_name=None):
        """find a window by its class_name"""
        self._handle = win32gui.FindWindow(class_name, window_name)

    def _window_enum_callback(self, hwnd, wildcard):
        """Pass to win32gui.EnumWindows() to check all the opened windows"""
        if re.match(wildcard, str(win32gui.GetWindowText(hwnd))) is not None:
            self._handle = hwnd

    def find_window_wildcard(self, wildcard):
        """find a window whose title matches the wildcard regex"""
        self._handle = None
        wildcard = ".*{}.*".format(wildcard)
        win32gui.EnumWindows(self._window_enum_callback, wildcard)
        return self
    def set_foreground(self):
        """put the window in the foreground"""
        win32gui.SetForegroundWindow(self._handle)
        return self
    
    def maximize(self):
        win32gui.ShowWindow(self._handle, win32con.SW_MAXIMIZE)
        return self

def change_window(window_name):
    try:
        window_titles = pyautogui.getAllTitles()
        #print(window_titles)
        for title in window_titles:
            #print(title)
            if window_name in title:
                
                window_pid = win32gui.FindWindowEx(None, None, None, title)
                #set focus
                win32gui.SetForegroundWindow(window_pid)
                break
    except Exception as e:
        print(e)    
        raise Exception("Error occured, aborting")
   
def change_focus(window):
    try:
        window_pid = win32gui.FindWindowEx(None, None, None, window)
        #set focus
        win32gui.SetForegroundWindow(window_pid)
    except Exception as e:
        print(e)    
        raise Exception("Error occured, aborting") 



    
if __name__ == '__main__':
    w = WindowMgr()
    w.find_window_wildcard("PHFR:")
    w.set_foreground().maximize()
    # change_window("PHFR: Katalog")