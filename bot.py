import random
import time
import pyautogui
from logger import log
import discord_notification as dn
import move
import imagerecognition

START_POSITION = (1,1)
EXEMPLAR_POSITION = (498,980)
GESAMTINFO_POSITION = (420,90)
FAILSAFE_LOCATION = (0,0)
EDIT_POSITION = (525,90)
DELAY = 0.5

class Bot:
    """
    Create the bot object. Add debug=True to the constructor to disable the startup sequence.
    
    
    """
    def __init__(self, debug:bool=False):
        self.logging = log()
        self.logging.bot_info("Bot started")   
        self.first_run = True 
        if debug == False:
            if self.first_run ==True:
                self.startup()    
        self.signatur = ""
        self.ppn = ""
        self.oldnotation:list = []
        self.count=['1']
        self.this_count = []

    def screenshot(self, region:tuple=None):
        """
        Take a screenshot of the screen and return it.
        """
        if region == None:
            return pyautogui.screenshot()
        else:
            return pyautogui.screenshot(region=region)
    
    def move_to_image(self, image:str):
        """move mouse to image"""
        image_position = pyautogui.locate(image, self.screenshot(),confidence=0.7)
        if image_position == None:
            message=f"Image {image} not found"
            # Exception(message)
            self.logging.bot_error(Exception(message))
            
            return False
        else:
            pyautogui.moveTo(*pyautogui.center(image_position))
            return True 
         
    def mti_rel(self, image,rel_coords=(0,0)):
        """
        extension of move_to_image, moves relativly after finding the image
        
        Args:
            - image (str): Path to image
            - screenshot (pyautogui.screenshot()): screenshot
            - rel_coords (tuple, optional): Coordinates to move after locating image. Defaults to (0,0)px.
        """
        try:
            if self.move_to_image(image=image)==False:
                dn.send_notification(message="Check PC, manual move needed", computer="PC1",type="warning")
                #pyautogui.confirm(f'Failed to move to {image}, please move to {image} manually and press OK')
                raise Exception(f"could not move to {image}, did not move relativly by {rel_coords}px")
            pyautogui.moveRel(*rel_coords)
            self.logging.bot_debug(f'moved to {image}, moved relativly by {rel_coords}px')
        except Exception as e:
            message = f'could not move to {image}, did not move relativly by {rel_coords}px'
            self.logging.bot_critical(message)
            # dc_msg = f'```{message}\n{e}```' #! uncomment later
            # send_error_notification(dc_msg, "Computer Alexander")
            raise Exception(message)  
            
    
    def scroll(self, direction:str=['up','down'], n:int=1 ):
        """
        scrolls the mouse wheel
        
        Args:
            - direction (str): direction to scroll, can be 'up' or 'down'
            - amount (int): amount of scrolls (px)
        """
        if direction == 'up':
            pyautogui.scroll(n)
        elif direction == 'down':
            pyautogui.scroll(-n)
        else:
            self.logging.bot_critical(f'could not scroll, direction {direction} is not valid')

    def write_string(self, string: str, confirm: bool = True):
        """write a string to the keyboard and confirm with enter if confirm is True (Default is True)"""
        pyautogui.write(str(string))
        if confirm:
            pyautogui.press('enter') 

    def check(self, image, n_tries:int=10, delay:float=DELAY, region:tuple=None):
        """
        checks if the screen contains the image, retries n times with delay in seconds
        
        Args:
            - image (image): a image
            - n_tries (int, optional): How many times to try. Defaults to 10.
            - delay (int, optional): Delay between tries. Defaults to DELAY.
        
        Returns:
            - bool: True if image was found, False if not
        """
        #check if screen contains image, retry n times with delay in seconds
        tries=0
        while tries < n_tries:
        
            if pyautogui.locateOnScreen(image, confidence=0.7, region=region) is not None:
                self.logging.bot_info(f"found {image}")
                return True
            else:
                tries += 1
                self.logging.bot_info(f"could not find {image}, retrying ({tries}/{n_tries})")
                time.sleep(delay)
        return False

    def check_ocr(self, region:tuple, text:str, save_path:str="img/defaults.png", n_tries:int=10, delay:float=DELAY, start_delay:float=0.2):
        """
        checks if the screen contains the text, retries n times with delay in seconds
        
        Args:
            - region (tuple): region to check
            - text (str): text to check
            - n_tries (int, optional): How many times to try. Defaults to 10.
            - delay (int, optional): Delay between tries. Defaults to DELAY.
        
        Returns:
            - bool: True if text was found, False if not
        """
        #check if screen contains text, retry n times with delay in seconds
        tries=0
        if start_delay != 0:
            time.sleep(start_delay)
        while tries < n_tries:
            pyautogui.screenshot(region=region).save(save_path)
            if imagerecognition.ocr_core(save_path).split("\n")[0] == text or text in imagerecognition.ocr_core(save_path):
                self.logging.bot_info(f"found {text}")
                return True
            else:
                tries += 1
                self.logging.bot_info(f"could not find {text}, retrying ({tries}/{n_tries})")
                time.sleep(delay)
        return False

    def check_screen(self, image:str)->bool:
        """
        check if screen matches, if not abort
        
        Args:
            - screenshot (any): PyAutoGUI screenshot
            - image (str): path to image to check
        
        Returns:
            - bool: True if screen matches, False if not
        """
        #check if screen matches
        if pyautogui.locate(image, self.screenshot()) is not None:
            self.logging.bot_info("screen matches")
            return True
        else:         
            self.logging.bot_critical("Screen does not match, aborting")
            return False

    def check_count(self):
        
        pyautogui.screenshot(region=(1450,240,120,30)).save("img/item/thiscount.png")
        this_count = imagerecognition.digits("img/item/thiscount.png")
        self.this_count = this_count
        if this_count == self.count:
            self.logging.bot_info("count matches")
            print("count matches")
            return True
        else:
            self.this_count = this_count
            return False
        
    def commit(self):
        pyautogui.keyDown("alt")
        pyautogui.hotkey("b","l")
        pyautogui.keyUp("alt")
        if self.check("img/adis_message.png",n_tries=10,delay=0.3) == False:
            pyautogui.screenshot(region=(890,150,150,50)).save("checkthis.png")
            if imagerecognition.ocr_core("checkthis.png").split("\n")[0] == "Trefferliste":
                self.logging.bot_info("Trefferliste")
                pyautogui.click(*GESAMTINFO_POSITION)
                time.sleep(DELAY*2)
            pyautogui.keyDown("alt")
            pyautogui.hotkey("b","l")
            pyautogui.keyUp("alt")
            if self.check("img/adis_message.png",n_tries=10,delay=0.3) == False:
                pyautogui.keyDown("alt")
                pyautogui.hotkey("b","l")
                pyautogui.keyUp("alt")
                if self.check("img/adis_message.png",n_tries=10,delay=0.3) == False:
                
                    raise Exception("could not find adis_message.png")
        if self.commit_success() == True:
            self.logging.bot_info("commit successful")
            time.sleep(DELAY)  #! dirty fix, only momentary
            pyautogui.click(1019,561)
            #pyautogui.hotkey("altleft","s")
            #dn.send_notification(f"Successfully changed PPN:**{self.ppn}**: \n ```-Removed {self.oldnotation}\n -Added {self.signatur}```","PC1","info")
        else:
            #dn.send_notification(f"Commit failed for PPN:**{self.ppn}***: \n ```-Removed {self.oldnotation}\n -Added {self.signatur}```","PC1","critical")
            self.logging.bot_critical(f"commit failed, PPN: {self.ppn}")
            return False
                
            
        
    
    def commit_success(self):
        
        pyautogui.screenshot(region=(854,483,210,50)).save("img/adis_message.png")
        text = imagerecognition.ocrtxt("img/adis_message.png")
        text.replace("\n","")
        if "aDIS/Lokalsatz ist geandert worden" in text:
            print("commit success")
            dn.send_embedded_message_success(ppn=self.ppn, removed=self.oldnotation, changed=self.signatur)
            return True
        else:
            self.logging.bot_critical("commit failed")
            dn.send_embedded_message_error(ppn=self.ppn, removed=self.oldnotation, changed=self.signatur)
            return False

    def enter_edit_mode(self,gesamtinfo=False):
        if gesamtinfo == False:
            pyautogui.moveTo(*EDIT_POSITION)
        else:
            pyautogui.moveTo(*GESAMTINFO_POSITION)
        time.sleep(0.2)
        pyautogui.leftClick()
        pyautogui.moveTo(*START_POSITION)

    def delete_line(self, coords=(0,0)):
        if coords!=(0,0):
            pyautogui.moveTo(*coords)
        pyautogui.leftClick()
        pyautogui.hotkey("ctrl","d")

    def remove_notation(self):
        line1=(160,655,100,30)
        line2=(160,685,100,30)
        dellist = []
        no_dellist = []
        def check_if_deletion_allowed(image_text):
            if not image_text in imagerecognition.FIELDS_TO_DELETE:
                return False 
            else:
                return True
        # time.sleep(.2)
        
        self.screenshot(region=line1).save("img/item/decipher.png")
        self.screenshot(region=line2).save("img/item/decipher1.png")
        
        text_line_1 = imagerecognition.ocrtxt("img/item/decipher.png")
        text_line_2 = imagerecognition.ocrtxt("img/item/decipher1.png")
        
        subject = text_line_1.split(" ")[0]
        subject2 = text_line_2.split(" ")[0]
        if check_if_deletion_allowed(subject) and check_if_deletion_allowed(subject2):
            self.delete_line(line2[:2])
            self.delete_line(line1[:2])
            self.oldnotation.append(subject)
            self.oldnotation.append(subject2)
            dellist.append(subject)
            dellist.append(subject2)
        elif check_if_deletion_allowed(subject):
            self.oldnotation.append(subject)
            if subject not in dellist:
                dellist.append(subject) 
            self.delete_line(line1[:2])
        elif check_if_deletion_allowed(subject2):
            self.oldnotation.append(subject2)
            if subject2 not in dellist:
                dellist.append(subject2)
            self.delete_line(line2[:2])
        elif (subject and subject2) not in imagerecognition.FIELDS_TO_DELETE:
            no_dellist.append(subject)
            no_dellist.append(subject2)
            dn.send_notification(f"Did not delete {no_dellist} for PPN:**{self.ppn}**","PC1","control")
            return False
        dn.send_notification(f"Deleted {dellist} for PPN:**{self.ppn}**","PC1","info")
        dellist.clear()
        no_dellist.clear()
        return True

    def edit_gesamtinfo(self,signatur):
        
        self.enter_edit_mode()
        time.sleep(3)
        #self.check("img/item/sachersch.png",n_tries=10,delay=0.3,region=(340,120,250,50))
        edit_y_n=self.check_ocr(region=(410,145,200,30),text="SacherschlieRung",n_tries=10,delay=DELAY,save_path="img/item/sachersch.png")
        if edit_y_n==True:
            self.move_to_image("img/item/sachersch.png")
            pyautogui.leftClick()
            pyautogui.moveTo(384,570)
            pyautogui.leftClick()
            for i in range(5):
                if self.remove_notation() == False:
                    break
            pyautogui.moveTo(1160,665)                 
            pyautogui.leftClick()
            pyautogui.hotkey("ctrl","a")
            time.sleep(0.02)
            pyautogui.write(signatur) 
            pyautogui.hotkey("altleft","p")
            time.sleep(0.2)
            if self.check("img/testresult.png",n_tries=3,delay=0.2):
                pyautogui.click(1385, 964,clicks=3, interval=0.25)
                dn.send_embedded_message_control(ppn=self.ppn,signatur=signatur,message="Got a ResultError, clicked save, but best to check manually")
        
    def startup(self): #* done
        window_name = "PHFR: Katalog"
        if not window_name in pyautogui.getActiveWindow().title:
            self.logging.bot_info("waiting for window, checking if it exists")
            move.change_window("PHFR: Katalog")
            pyautogui.click(10,1) #set focus manually, in some cases the window is not focused
            
        elif window_name in pyautogui.getActiveWindow().title:
            self.logging.bot_info("window found, checking if screen matches")
            if not self.check_ocr(region=(0,100,150,30),text="Suche starten"):
                raise Exception("screen does not match, didn't find main menu")    
        pyautogui.moveTo(*START_POSITION)

    def main_screen(self,ppn_number):       
        
        pyautogui.leftClick()
        self.write_string(str(ppn_number), confirm=True) 
        #self.check(image="img/count_base.png",n_tries=10,delay=0.3)
        if self.check_ocr(region=(1400,230,450,40),save_path="img/item/THIScount.png",text="Anzahl Ex. 1",n_tries=10,delay=0.3)==False:
            dn.send_notification(f"Got a count mismatch, expected {self.count} got {self.this_count}","PC1","warning")
            pyautogui.hotkey('alt', 's')
            return False
        
        return True
    
    def item_screen(self,signatur):
        if self.check_ocr(region=(900,150,130,40),text="Gesamtinfo",save_path="img/item/gesamtinfo.png")==False: #("img/item/gesamtinfoheading.png",n_tries=10,delay=0.3) == False:
            raise Exception("could not find gesamtinfoheading")
        self.edit_gesamtinfo(signatur)
        # if self.check("img/item/gesamtinfoheading.png",n_tries=20,delay=0.2) == False:

        if self.check_ocr(region=(900,150,130,40),text="Gesamtinfo",save_path="img/item/gesamtinfo.png")==False: #("img/item/gesamtinfoheading.png",n_tries=10,delay=0.3) == False:
            raise Exception("could not find gesamtinfoheading")
        #self.mti_rel(image="img/item/gesamtinfoheading.png",rel_coords=(0,100))
        self.scroll(n=2000, direction="down")
        #! detect if scroll was executed
        if self.check(region=(1805,215,30,70),image="img/item/scrollbar_present.png",n_tries=2,delay=0.1)==True:
            self.scroll(n=2000, direction="down")
        #pyautogui.moveTo(*EXEMPLAR_POSITION)
        self.locate_and_click_checkbox()
        #self.check_if_clicked()
        self.enter_edit_mode(gesamtinfo=True)
    
    def locate_and_click_checkbox(self,region=(EXEMPLAR_POSITION[0]-30,EXEMPLAR_POSITION[1]-30,50,50)):
        #if pyautogui.locate("img/empty.png","img/exemplar_clicked.png")==True:
        location=pyautogui.locateOnScreen("img/empty_checkbox.png",region=region)
        pyautogui.click(location)
        screenshot = pyautogui.screenshot(region=region)
        screenshot.save("img/exemplar_clicked.png")
        if pyautogui.locate("img/clicked_checkbox.png","img/exemplar_clicked.png") ==True:
            print("exemplar checkbox clicked")
        else:
            print("exemplar checkbox not clicked, attempting to locate and click")

        
    def check_if_clicked(self):
        screenshot = pyautogui.screenshot(region=(EXEMPLAR_POSITION[0]-30,EXEMPLAR_POSITION[1]-30,50,50))
        screenshot.save("img/exemplar_clicked.png")
        
        location=pyautogui.locateOnScreen("img/empty_checkbox.png",region=(EXEMPLAR_POSITION[0]-50,EXEMPLAR_POSITION[1]-50,50,50))
       # print(location)
        pyautogui.moveTo(location)
        pyautogui.leftClick()
        screenshot = pyautogui.screenshot(region=(EXEMPLAR_POSITION[0]-30,EXEMPLAR_POSITION[1]-30,50,50))
        screenshot.save("img/exemplar_clicked.png")
            
            
    def exemplar_screen(self,signatur):
        self.logging.bot_info("exemplar screen")
        self.enter_edit_mode()
        pyautogui.moveTo(1093,369)
        if not self.check_ocr(region=(0,130,245,40),text="Bearbeiten Exemplar",delay=0.2):
            Exception("could not find img/title/exemplar_stuff.png in exemplar_screen")
            #return to try again
        pyautogui.leftClick()
        pyautogui.hotkey("ctrl","a")
        pyautogui.press("backspace")
        pyautogui.write(signatur)
        pyautogui.hotkey("altleft","p")
        self.logging.bot_info("pressed alt+p")
        time.sleep(DELAY*3)
        pyautogui.moveTo(815,96)
        pyautogui.leftClick()
        pyautogui.moveTo(*START_POSITION)
        if self.check_ocr(region=(1400,230,130,40), save_path="img/item/confirm_thiscount.png",text="Anzahl Ex. 1",n_tries=10,delay=0.3)==False: #("img/item/thiscount.png",n_tries=10,delay=0.3) == False:
            print("not at location, trying an additional time")
            if self.check_ocr(region=(886,150,155,50),save_path="img/error_img.png",text="Trefferliste"):
                dn.send_notification(f"Got lost in 'Trefferliste', moved to title annd commited, please check {signatur}","PC1","warning")
                pyautogui.leftClick(*GESAMTINFO_POSITION)
            
        self.logging.bot_info("alt+r finished")
        time.sleep(0.1)
        if self.commit() ==False:
            return False
        time.sleep(0.2)
        pyautogui.hotkey("altleft","s")
        time.sleep(DELAY)
    
    def run(self,signatur:str, ppn:str):
        time.sleep(DELAY*2)
        self.logging.bot_info("Run started")
        self.ppn = ppn
        self.signatur = signatur
        # pyautogui.screenshot(region=(1218,785,60,30)).save("tmpimg.png")
        #while imagerecognition.ocr_core("tmpimg.png").split("\n")[0] != "PPN":
        while self.check_ocr(region=(1218,785,60,30),text="PPN",delay=0.2)==False:
            #dn.send_notification("Could not find main screen","PC1","error")
            print("could not find main screen, restarting")
            pyautogui.hotkey("altleft","s")
            sleep_time = random.randint(1,5)
            time.sleep(DELAY*sleep_time)
            #pyautogui.screenshot(region=(1218,785,60,30)).save("tmpimg.png")
        # self.mti_rel(image="img/main_menu/ppn.png",rel_coords=(200,10)) #using image to find the location
        pyautogui.moveTo(1400,800)
        if self.main_screen(ppn_number=ppn)==True:
            self.item_screen(signatur=signatur)
            if self.exemplar_screen(signatur=signatur)==False:
                return False
            # time.sleep(0.2)
            # pyautogui.hotkey("altleft","s")
            # time.sleep(0.2)
        else:
            # pyautogui.hotkey("altleft","s")
            self.logging.bot_critical("could not find main screen, restarting")
            return False
 
    def testrun(self,signatur:str, ppn:str):
        self.ppn = ppn
        self.signatur = signatur
        pyautogui.screenshot(region=(1218,785,60,30)).save("tmpimg.png")
        while imagerecognition.ocr_core("tmpimg.png").split("\n")[0] != "PPN":
            dn.send_notification("Could not find main screen","PC1","error")
            print("could not find main screen, restarting")
            pyautogui.hotkey("altleft","s")
            sleep_time = random.randint(1,5)
            time.sleep(DELAY*sleep_time)
            pyautogui.screenshot(region=(1218,785,60,30)).save("tmpimg.png")
        
        if self.main_screen(ppn_number=ppn)==True:
            self.item_screen(signatur=signatur)
            if self.exemplar_screen(signatur=signatur)==False:
                return False
            # time.sleep(0.2)
            # pyautogui.hotkey("altleft","s")
            # time.sleep(0.2)
        else:
            # pyautogui.hotkey("altleft","s")
            self.logging.bot_critical("could not find main screen, restarting")
            return False
        
class ControlBot(Bot):
    def __init__(self,debug=False):
        super().__init__(debug= debug)
        
    def check_item_screen(self):
        pyautogui.click(*EXEMPLAR_POSITION)
        self.enter_edit_mode(gesamtinfo=True)
        if not self.check("img/control/signaturen.png"):
            self.logging.bot_critical("could not find signaturen.png in item screen")
            return False
        self.logging.bot_info("found signaturen.png in item screen")
        return True
        
    def run(self, ppn, signatur):
        self.main_screen(ppn_number=ppn)
        self.mti_rel("img/control/katalogsignatur.png",(355,-10))
        pyautogui.screenshot(region=(481,330,200,25)).save("img/control/katalogsignatur.png")        #(481,330)
        text = imagerecognition.ocr_core("img/control/katalogsignatur.png")
        text=text.split("\n")[0]
        if not signatur == text:
            return False
            # raise Exception(f"signatures do not match, '{signatur}' got '{text}'")
        else:
            self.logging.bot_info(f"signatures match, '{signatur}' got '{text}'")
        self.scroll(n=2000,direction="down")
        if not self.check_item_screen():
            return False
        pyautogui.hotkey("altleft","s")
        time.sleep(DELAY*2)
        return True
        

        #pyautogui.screenshot()

    def check_exemplar_count(self,ppn):
        self.main_screen(ppn_number=ppn)
        self.ex
    
    
if __name__ == '__main__':
   
    bot=Bot()
    
    #bot.startup()
    
    #bot.run(ppn="86011225X",signatur="ZA 55300 N397")
    # bot.item_screen("ZA 55300 N397")
    #bot.locate_and_click_checkbox(region=(0,0,1920,1080))
    bot.run(ppn="025240935",signatur="ZC 28000 K92")
    # for i in range(25):
    #     print(i)
    #     if bot.run(ppn="025240935",signatur="ZC 28000 K92")==False:
    #         print(f"failed on run {i}")
    #bot.exemplar_screen("ZC 50000 L433")
    #bot.edit_gesamtinfo("ZC 50000 L433")
    # bot.locate_and_click_checkbox()
    # bot.item_screen("ZC 10000 V916")
    # for i in range(200):
    #     if bot.run(ppn="1685293034",signatur="UB 4053 S594") == False:
    #         break
    #     dn.send_notification(f"finished {i+1}/200","PC1","info")
    # cb = ControlBot()
    # cb.run(ppn="840060254",signatur="ZC 50000 F399")
    