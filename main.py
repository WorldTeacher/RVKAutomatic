import time
import pyautogui
import asyncio
import json
import polars as pl
import pandas as pd
from logger import log
from data.source.tsvReader import TsvReader
import move
logging = log()

START_POSITION = (1,1)
EXEMPLAR_POSITION = (498,980)
FAILSAFE_LOCATION = (0,0)

PPN = 1735603120
class Bot:
    def __init__(self, config):
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
        logging.bot_info("TestBot started")        
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
    def screenshot(self):
        screenshot = pyautogui.screenshot()
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
            logging.bot_debug(f'moved to {image}, moved relativly by {rel_coords}px')
        except Exception as e:
            logging.bot_critical(f'could not move to {image}, did not move relativly by {rel_coords}px')
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
            logging.bot_critical(f'could not scroll, direction {direction} is not valid')
            self.error()
    
    def write_number(self, number: int, confirm: bool = True):
        pyautogui.write(str(PPN)) #! change to number later
        if confirm:
            pyautogui.press('enter')
    
    async def loading_check(self):
        #check if mouse icon is in the loading circle
        if pyautogui.locateOnScreen("img/main_menu/loading.png") is not None:
            logging.bot_info("loading")
            while pyautogui.locateOnScreen("img/main_menu/loading.png") is not None:
                time.sleep(1)
                logging.bot_info("still loading")
            logging.bot_info("loading done") 
    def check(self, image, n_tries=10, delay=1):
        #check if screen contains image, retry n times with delay in seconds
        tries=0
        while tries < n_tries:
            if pyautogui.locateOnScreen(image) is not None:
                logging.bot_info(f"found {image}")
                return True
            else:
                tries += 1
                logging.bot_info(f"could not find {image}, retrying ({tries}/{n_tries})")
                time.sleep(delay)
        pyautogui.locateOnScreen(image)
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
            logging.bot_info("screen matches")
            return True
        else:         
            logging.bot_critical("Screen does not match, aborting")
            return False
    def check_count(self):
        
        if pyautogui.locate("img/item/count.png",self.screenshot()) is not None:
            logging.bot_info("count matches")
            pyautogui.moveTo(*FAILSAFE_LOCATION)
            return True
        else:         
            logging.bot_critical("Count does not match, aborting")
            return False
    def main_screen(self):       
    
        self.mti_rel_movement(screenshot=self.screenshot(),image="img/main_menu/numbers.png",rel_coords=(400,0))
        pyautogui.leftClick()
        self.write_number(PPN)
        #await self.loading_check()
        self.check(image="img/item/count.png",n_tries=10,delay=0.3)
        self.check_screen(screenshot=self.screenshot(),image="img/item/count.png")
        self.mti_rel_movement(image="img/item/count.png",screenshot=self.screenshot(),rel_coords=(0,100))
    
    def item_screen(self):
        self.check("img/item/exemplar_gesamtinfoheading.png",n_tries=10,delay=0.3)
        if not self.check_screen(image="img/item/exemplar_gesamtinfoheading.png",screenshot=self.screenshot()):
            self.error()
        # screenshot = pyautogui.screenshot()
        self.mti_rel_movement(image="img/item/exemplar_gesamtinfoheading.png",screenshot=self.screenshot(),rel_coords=(0,100))
        self.scroll(direction="down",n=1000)
        self.move_to_image(image="img/exemplar_exemplare.png",screenshot=self.screenshot())
        pyautogui.moveTo(*EXEMPLAR_POSITION)
        pyautogui.leftClick()
    def run(self):
        logging.bot_info("Run started")
        # self.startup()
        # self.main_screen()
        self.item_screen()
    def startup(self): #* done
        window_name = "PHFR: "
        #detect window name
        if not window_name in pyautogui.getActiveWindow().title:
            logging.bot_info("waiting for window, checking if it exists")
            move.change_window("PHFR: Katalog")
            
        elif window_name in pyautogui.getActiveWindow().title:
            print(pyautogui.getActiveWindow().title)
            logging.bot_info("window found, checking if screen matches")
            if not self.check_screen(self.screenshot(), "img/main_menu/main_menu_btns.png"):
                self.error()    
        pyautogui.moveTo(*START_POSITION)
    def error(self): #* done
        logging.bot_critical("Error occured, aborting")
        raise Exception("Error occured, aborting")   
if __name__ == '__main__':
    # b = Bot(json.load(open('./data/positions/config.json')))
    tb= TestBot()
    tb.item_screen()
    