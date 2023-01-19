import time
import pyautogui
import asyncio
import json
import pandas as pd
from logger import log
from data.source.tsvReader import TsvReader
from discord_notification import send_notification
import move
from pynput.keyboard import Controller
import imagerecognition

START_POSITION = (1,1)
EXEMPLAR_POSITION = (498,980)

FAILSAFE_LOCATION = (0,0)

PPN = 234490160
RVK_SIGNATUR = "WI 5870 O12"

class Bot:
    def __init__(self, config):
        self.logging = log()
        self.config = config
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.main())

    async def main(self):
        pyautogui.moveTo(*START_POSITION)
        self.find_img('img/item/test.png')

    async def click(self):
        # await 
        pass        
    def image_detect(self, image, image_to_detect):
        image_position = pyautogui.locate(image_to_detect, image)

        # If the image is present, move the mouse cursor to its position and click
        if image_position is not None:
            pyautogui.moveTo(image_position)
            
        else:
            print("Image not found")
            raise Exception("Location not found")
    def find_img(self, image):
        img = pyautogui.locateOnScreen(image)
        if img is not None:
            pyautogui.moveTo(img)            
        else:
            print("Image not found")
            raise Exception("Location not found")
        
        
        
class TestBot:
    def __init__(self):
        self.logging = log()
        self.keyboard = Controller()
        self.logging.bot_info("TestBot started")        
        #self.config = config
        # self.loop = asyncio.get_event_loop()
        # self.loop.run_until_complete(self.main())
        pass
    
    def load_data(self,data_path):
        #read csv, save as dataframe
        data= pd.read_csv(data_path, sep='\t')
        #convert to json
        with open('data.json', 'w') as f:
            json.dump(data, f, indent=4)
        for entry in data:
            print(entry[0]['PPN:'])
            time.sleep(2)
    def screenshot(self,region:tuple=None):
        """
        Take a screenshot of the screen and return it.
        
        Args:
            - region (Tuple(x1,y1,x2,y2), optional): Region to capture x2,y2 are relative to x1.y1. Defaults to None.
        
        Returns:
            - huh: screenshot
        """
        screenshot = pyautogui.screenshot(region=region)
        return screenshot
    def move_to_image(self,image:str, screenshot):
        """
        moves the mouse cursor to the position of the image
        
        Args:
            - image (str[path to img]): path to image
            - screenshot (pyautogui.screenshot()): screnshot of the screen
        
        Raises:
            - Exception: Location not found
        """
        image_position = pyautogui.locate(image, screenshot)

        # If the image is present, move the mouse cursor to its position and click
        if image_position is not None:
            pyautogui.moveTo(image_position)
            
        else:
            print("Image not found")
            raise Exception("Location not found")
    
    def mti_rel_movement(self, image,screenshot,rel_coords=(0,0)):
        """
        extension of move_to_image, moves relativly after finding the image
        
        
        
        Args:
            - image (_type_): _description_
            - screenshot (_type_): _description_
            - rel_coords (tuple, optional): _description_. Defaults to (0,0)px.
        """
        try:
            self.move_to_image(image,screenshot)
            pyautogui.moveRel(*rel_coords)
            self.logging.bot_debug(f'moved to {image}, moved relativly by {rel_coords}px')
        except Exception as e:
            message = f'could not move to {image}, moved relativly by {rel_coords}px'
            self.logging.bot_critical(message)
            # dc_msg = f'```{message}\n{e}```' #! uncomment later
            # send_error_notification(dc_msg, "Computer Alexander")
            self.error()
    
    def scroll(self, direction:str, n:int):
        """
        scrolls the mouse wheel
        
        Args:
            - direction (str): direction to scroll, can be 'up' or 'down'
            - amount (int): amount of scrolls
        """
        if direction == 'up':
            pyautogui.scroll(n)
        elif direction == 'down':
            pyautogui.scroll(-n)
        else:
            self.logging.bot_critical(f'could not scroll, direction {direction} is not valid')
            self.error()
    
    def write_number(self, number: int, confirm: bool = True):
        pyautogui.write(str(PPN)) #! change to number later
        if confirm:
            pyautogui.press('enter')
    def write_string(self, string: str, confirm: bool = True):
        pyautogui.write(str(string))
        if confirm:
            pyautogui.press('enter')
    def check(self, image, n_tries=10, delay=1):
        """
        checks if the screen contains the image, retries n times with delay in seconds
        
        
        
        Args:
            - image (image): a image
            - n_tries (int, optional): How many times to try. Defaults to 10.
            - delay (int, optional): Delay between tries. Defaults to 1.
        
        Returns:
            - bool: True if image was found, False if not
        """
        #check if screen contains image, retry n times with delay in seconds
        tries=0
        while tries < n_tries:
            if pyautogui.locateOnScreen(image) is not None:
                self.logging.bot_info(f"found {image}")
                return True
            else:
                tries += 1
                self.logging.bot_info(f"could not find {image}, retrying ({tries}/{n_tries})")
                time.sleep(delay)
        
    def check_screen(self, screenshot, image)->bool:
        """
        check if screen matches, if not abort
        
        
        
        Args:
            - screenshot (any): PyAutoGUI screenshot
            - image (str): path to image to check
        
        Returns:
            - bool: True if screen matches, False if not
        """
        #check if screen matches
        if pyautogui.locate(image, screenshot) is not None:
            self.logging.bot_info("screen matches")
            return True
        else:         
            self.logging.bot_critical("Screen does not match, aborting")
            return False

    def check_count(self):
        
        if pyautogui.locate("img/item/count.png",self.screenshot()) is not None:
            self.logging.bot_info("count matches")
            pyautogui.moveTo(*FAILSAFE_LOCATION)
            return True
        else:         
            self.logging.bot_critical("Count does not match, aborting")
            return False

    def main_screen(self,ppn_number):       
        self.check("img/main_menu/main_menu_btns.png",n_tries=10,delay=0.3)
        self.mti_rel_movement(screenshot=self.screenshot(),image="img/main_menu/numbers.png",rel_coords=(400,0))
        pyautogui.leftClick()
        self.write_number(PPN, confirm=False) #! change to ppn_number later
        pyautogui.press('ä')
        #await self.loading_check()
        self.check(image="img/item/count.png",n_tries=10,delay=0.3)
        # self.check(screenshot=self.screenshot(),image="img/item/count.png")
        # self.mti_rel_movement(image="img/item/count.png",screenshot=self.screenshot(),rel_coords=(0,100))
    
    def item_screen(self):
        self.check("img/item/gesamtinfoheading.png",n_tries=10,delay=0.3)
        if not self.check_screen(image="img/item/gesamtinfoheading.png",screenshot=self.screenshot()):
            self.error()
            
        # screenshot = pyautogui.screenshot()
        self.edit_gesamtinfo()
        
        self.mti_rel_movement(image="img/item/gesamtinfoheading.png",screenshot=self.screenshot(),rel_coords=(0,100))
        self.scroll(direction="down",n=1000)
        # self.move_to_image(image="img/exemplar_exemplare.png",screenshot=self.screenshot())
        pyautogui.moveTo(*EXEMPLAR_POSITION)
        pyautogui.leftClick()
        # pyautogui.hold("leftAlt")
        # pyautogui.KEYBOARD_KEYS
        # self.keyboard.press("ä")
    def enter_edit_mode(self):
        self.move_to_image("img/item/edit.png",self.screenshot())
        pyautogui.leftClick()
    def delete_line(self, coords=(0,0)):
        if coords!=(0,0):
            pyautogui.moveTo(*coords)
        pyautogui.leftClick()
        pyautogui.hotkey("ctrl","d")
    def remove_notation(self):
        line1=(160,655,100,30)
        line2=(160,685,100,30)
        def check_if_deletion_allowed(image_text):
            if not image_text in imagerecognition.FIELDS_TO_DELETE:
                send_notification(f"not deleting {image_text}","desktop","info")
                return False 
            else:
                send_notification(f"deleting {image_text}","desktop","info")
                return True
        # time.sleep(.2)
        self.screenshot(region=line1).save("img/item/decipher.png")
        self.screenshot(region=line2).save("img/item/decipher1.png")
        text_line_1 = imagerecognition.ocrtxt("img/item/decipher.png").split(" ")[0]
        text_line_2 = imagerecognition.ocrtxt("img/item/decipher1.png").split(" ")[0]
        if check_if_deletion_allowed(text_line_2):
            self.delete_line(line2[:2])
        if check_if_deletion_allowed(text_line_1):
            self.delete_line(line1[:2])
    def edit_gesamtinfo(self):
        self.enter_edit_mode()
        self.check("img/item/sachersch.png",n_tries=10,delay=0.3)
        self.move_to_image("img/item/sachersch.png",self.screenshot())
        send_notification("Sacherschließung", "PC1","info")
        pyautogui.leftClick()
        self.move_to_image("img/item/notation.png",self.screenshot())
        pyautogui.leftClick()
        send_notification("Moved to Notation", "PC1","info")
        self.remove_notation()
        pyautogui.moveTo(1160,665)                 
        send_notification("Moved to RVK", "PC1","info")
        pyautogui.leftClick()
        pyautogui.hotkey("ctrl","a")
        time.sleep(0.02)
        pyautogui.write(RVK_SIGNATUR)
        send_notification("Wrote RVK", "PC1","info")
        pyautogui.hotkey("altleft","p")
        send_notification("done", "PC1","info")
        # self.remove_notation()
        
    def run(self):
        self.logging.bot_info("Run started")
        self.startup()
        self.main_screen()
        self.item_screen()
    def startup(self): #* done
        window_name = "PHFR: "
        #detect window name
        if not window_name in pyautogui.getActiveWindow().title:
            self.logging.bot_info("waiting for window, checking if it exists")
            move.change_window("PHFR: Katalog")
            
        elif window_name in pyautogui.getActiveWindow().title:
            print(pyautogui.getActiveWindow().title)
            self.logging.bot_info("window found, checking if screen matches")
            if not self.check_screen(self.screenshot(), "img/main_menu/main_menu_btns.png"):
                self.error()    
        pyautogui.moveTo(*START_POSITION)
    def error(self): #* done
        import traceback
        trace=traceback.format_exc()
        self.logging.bot_critical("Error occured, aborting")
        send_notification(f"Error, {trace}", "PC1","error")
        raise Exception("Error occured, aborting")   
if __name__ == '__main__':
    # b = Bot(json.load(open('./data/positions/config.json')))
    tb= TestBot()
    tb.item_screen()
    # mti_rel_movement(image="img/item/count.png",screenshot=tb.screenshot(),rel_coords=(0,100))