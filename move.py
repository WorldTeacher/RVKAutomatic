import pyautogui
import win32gui
import regex as re
#pyautogui.moveTo(1920,1080, duration=0.25)


def change_window(window_name):
    try:
        window_titles = pyautogui.getAllTitles()
        # print(window_titles)
        for title in window_titles:
            if window_name in title:
                
                window_pid = win32gui.FindWindowEx(None, None, None, title)
                #set focus
                win32gui.SetForegroundWindow(window_pid)
                break
    except Exception as e:
        print(e)    
        raise Exception("Error occured, aborting")
    
    
if __name__ == '__main__':
    change_window("PHFR: Katalog")