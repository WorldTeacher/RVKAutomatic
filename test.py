class TestBot:
    def __init__(self):
        self.logging = log()
        self.logging.bot_info("TestBot started")   
        self.first_run = True     
        self.signatur = ""
        self.ppn = ""
        self.oldnotation = []
        self.count=['1']
        
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
            pyautogui.moveTo(*pyautogui.center(image_position))
            
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
        pyautogui.write(str(string))
        if confirm:
            pyautogui.press('enter')
 
    def check(self, image, n_tries:int=10, delay:float=1):
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
        return False

    def check_screen(self, image)->bool:
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
        
        pyautogui.screenshot(region=(1480,240,150,30)).save("img/item/thiscount.png")
        this_count = imagerecognition.digits("img/item/thiscount.png")
        if this_count == self.count:
            self.logging.bot_info("count matches")
            print("count matches")
            return True
        else:
            print(this_count)
            self.logging.bot_critical("count does not match, adding to data.csv, continuing with next item")
            with open("manual.csv", "a") as f:
                message = f"PPN: {self.ppn}, signatur:{self.signatur}, this_count: {this_count}"
                f.write(message)
            return False
    def main_screen(self,ppn_number):       
        self.check("img/main_menu/main_menu_btns.png",n_tries=10,delay=0.3)
        self.mti_rel_movement(screenshot=self.screenshot(),image="img/main_menu/ppn.png",rel_coords=(200,10))
        pyautogui.leftClick()
        self.write_string(str(ppn_number), confirm=True) 
        self.check(image="img/count_base.png",n_tries=10,delay=0.3)
        if not self.check_count() == True:
            pyautogui.hotkey('alt', 's')
            return False
        return True
    
    def item_screen(self,signatur):
        if self.check("img/item/gesamtinfoheading.png",n_tries=10,delay=0.3) == False:
            raise Exception("could not find gesamtinfoheading")
        if not self.check_screen(image="img/item/gesamtinfoheading.png"):
            raise Exception("screen does not match")
        self.edit_gesamtinfo(signatur)
        if self.check("img/item/gesamtinfoheading.png",n_tries=10,delay=0.25) == False:
            raise Exception("could not find gesamtinfoheading")
        self.mti_rel_movement(image="img/item/gesamtinfoheading.png",screenshot=self.screenshot(),rel_coords=(0,100))
        self.scroll(direction="down",n=2000)
        # self.move_to_image(image="img/exemplar_exemplare.png",screenshot=self.screenshot())
        pyautogui.moveTo(*EXEMPLAR_POSITION)
        pyautogui.leftClick()
        self.enter_edit_mode(gesamtinfo=True)
        
    
    def exemplar_screen(self,signatur):
        self.logging.bot_info("exemplar screen")
        self.enter_edit_mode()
        pyautogui.moveTo(1093,369)
        if not self.check(image="img/title/exemplar_stuff.png",n_tries=10,delay=0.2):
            Exception("could not find img/title/exemplar_stuff.png in exemplar_screen")
        pyautogui.leftClick()
        pyautogui.write(signatur)
        pyautogui.hotkey("altleft","p")
        self.logging.bot_info("pressed alt+p")
        self.check("img/add_signatur.png",n_tries=10,delay=0.2)
        time.sleep(0.5)
        pyautogui.moveTo(815,96)
        pyautogui.leftClick()
        if not self.check("img/exemplar_anzahlEx1.png",n_tries=10,delay=0.1):
            raise Exception("could not find img/exemplar_anzahlEx1.png in exemplar_screen")
        self.logging.bot_info("alt+r finished")
        self.commit()
    
    def commit(self):
        pyautogui.keyDown("altleft")
        pyautogui.press("b")
        pyautogui.press("l")
        pyautogui.keyUp("altleft")
        if self.check("img/adis_message.png",n_tries=10,delay=0.3) == False:
            raise Exception("could not find adis_message.png")
        if self.commit_success() == True:
            self.logging.bot_info("commit successful")
            time.sleep(0.5)  #! dirty fix, only momentary
            pyautogui.click(1019,561)
            pyautogui.hotkey("altleft","s")
            send_notification(f"Successfully changed PPN:**{self.ppn}**: \n ```-Removed {self.oldnotation}\n -Added {self.signatur}```","PC1","info")
        else:
            send_notification(f"Commit failed for PPN:**{self.ppn}***: \n ```-Removed {self.oldnotation}\n -Added {self.signatur}```","PC1","critical")
            self.logging.bot_critical(f"commit failed, PPN: {self.ppn}")
            raise Exception("commit failed")
        time.sleep(0.2)
        pyautogui.hotkey("altleft","s")
        time.sleep(0.2)
    
    def commit_success(self):
        
        pyautogui.screenshot(region=(854,483,210,50)).save("img/adis_message.png")
        text = imagerecognition.ocrtxt("img/adis_message.png")
        text.replace("\n","")
        if "aDIS/Lokalsatz ist geandert worden" in text:
            print("commiscrollt success")
            send_embedded_message_success(ppn=self.ppn, removed=self.oldnotation, changed=self.signatur)
            return True
        else:
            self.logging.bot_critical("commit failed")
            return False
    
    def enter_edit_mode(self,gesamtinfo=False):
        if gesamtinfo == False:
            pyautogui.moveTo(*EDIT_POSITION)
        # self.move_to_image("img/item/edit.png",self.screenshot())
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
        def check_if_deletion_allowed(image_text):
            if not image_text in imagerecognition.FIELDS_TO_DELETE:
                send_notification(f"not deleting ```*{image_text}*```","desktop","info")
                return False 
            else:
                send_notification(f"deleting ```*{image_text}*```","desktop","info")
                return True
        # time.sleep(.2)
        
        self.screenshot(region=line1).save("img/item/decipher.png")
        self.screenshot(region=line2).save("img/item/decipher1.png")
        
        text_line_1 = imagerecognition.ocrtxt("img/item/decipher.png")
        text_line_2 = imagerecognition.ocrtxt("img/item/decipher1.png")
        if text_line_1 not in self.oldnotation:
            self.oldnotation.append(text_line_1)
        if text_line_2 not in self.oldnotation:
            self.oldnotation.append(text_line_2)
        subject = text_line_1.split(" ")[0]
        subject2 = text_line_2.split(" ")[0]
        if check_if_deletion_allowed(subject) and check_if_deletion_allowed(subject2):
            self.delete_line(line2[:2])
            self.delete_line(line1[:2])
            send_notification("deleted both lines","desktop","info")
        elif check_if_deletion_allowed(subject):
            self.delete_line(line1[:2])
        elif check_if_deletion_allowed(subject2):
            self.delete_line(line2[:2])
        elif (subject and subject2) not in imagerecognition.FIELDS_TO_DELETE:
            return False
        return True

    def edit_gesamtinfo(self,signatur):
        
        self.enter_edit_mode()
        self.check("img/item/sachersch.png",n_tries=10,delay=0.3)
        self.move_to_image("img/item/sachersch.png",self.screenshot())
        pyautogui.leftClick()
        self.move_to_image("img/item/notation.png",self.screenshot())
        pyautogui.leftClick()
        for i in range(5):
            if self.remove_notation() == False:
                break
        pyautogui.moveTo(1160,665)                 
        pyautogui.leftClick()
        pyautogui.hotkey("ctrl","a")
        time.sleep(0.02)
        pyautogui.write(signatur) 
        send_notification("Wrote RVK", "PC1","info")
        pyautogui.hotkey("altleft","p")
        #self.check("img/main_menu/main_menu_btns.png",n_tries=10,delay=0.2)
        
    def locate(self,image):
        if pyautogui.locateOnScreen(image):
            return True
        else:
            self.logging.bot_debug(f"could not locate {image}")
            return False
    def run(self,signatur:str, ppn:str):
        self.logging.bot_info("Run started")
        
        if self.first_run:
            self.startup()
            self.first_run = False
        self.ppn = ppn
        self.signatur = signatur
        if self.main_screen(ppn_number=ppn)==True:#! replace constant with variable later on
            self.item_screen(signatur=signatur)
            self.exemplar_screen(signatur=signatur)
        else:
            # pyautogui.hotkey("altleft","s")
            self.logging.bot_critical("could not find main screen, restarting")
            return False
        
    def start_adis(self,username,password):# TODO: make this work
        pyautogui.hotkey("winleft","d")
        pyautogui.click(67,251,clicks=2)
        if not self.check("img/adis_create_connection.png",n_tries=20,delay=0.3):
            raise Exception("adis not found after doubleclick")
        conn_loc = pyautogui.locateOnScreen("img/adis_create_connection.png")
        pyautogui.click(*pyautogui.center(conn_loc))
        time.sleep(0.5)
        pyautogui.press("enter")
        pyautogui.write(username)
        pyautogui.press("tab")
        pyautogui.write([password,"enter"])
        pyautogui.press("space")        
 
    def startup(self): #* done
        window_name = "PHFR: Katalog"
        if not window_name in pyautogui.getActiveWindow().title:
            self.logging.bot_info("waiting for window, checking if it exists")
            move.change_window("PHFR: Katalog")
            
        elif window_name in pyautogui.getActiveWindow().title:
            self.logging.bot_info("window found, checking if screen matches")
            if not self.check_screen("img/main_menu/main_menu_btns.png"):
                raise Exception("screen does not match, didn't find main menu")    
        pyautogui.moveTo(*START_POSITION)




class TestBot:
    def __init__(self):
        self.logging = log()
        self.logging.bot_info("TestBot started")   
        self.first_run = True     
        self.signatur = ""
        self.ppn = ""
        self.oldnotation = []
        self.count=['1']
        
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
            pyautogui.moveTo(*pyautogui.center(image_position))
            
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
        pyautogui.write(str(string))
        if confirm:
            pyautogui.press('enter')
 
    def check(self, image, n_tries:int=10, delay:float=1):
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
        return False

    def check_screen(self, image)->bool:
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
        
        pyautogui.screenshot(region=(1480,240,150,30)).save("img/item/thiscount.png")
        this_count = imagerecognition.digits("img/item/thiscount.png")
        if this_count == self.count:
            self.logging.bot_info("count matches")
            print("count matches")
            return True
        else:
            print(this_count)
            self.logging.bot_critical("count does not match, adding to data.csv, continuing with next item")
            with open("manual.csv", "a") as f:
                message = f"PPN: {self.ppn}, signatur:{self.signatur}, this_count: {this_count}"
                f.write(message)
            return False
    def main_screen(self,ppn_number):       
        self.check("img/main_menu/main_menu_btns.png",n_tries=10,delay=0.3)
        self.mti_rel_movement(image="img/main_menu/ppn.png",rel_coords=(200,10))
        pyautogui.leftClick()
        self.write_string(str(ppn_number), confirm=True) 
        self.check(image="img/count_base.png",n_tries=10,delay=0.3)
        if not self.check_count() == True:
            pyautogui.hotkey('alt', 's')
            return False
        return True
    
    def item_screen(self,signatur):
        if self.check("img/item/gesamtinfoheading.png",n_tries=10,delay=0.3) == False:
            raise Exception("could not find gesamtinfoheading")
        if not self.check_screen(image="img/item/gesamtinfoheading.png"):
            raise Exception("screen does not match")
        self.edit_gesamtinfo(signatur)
        if self.check("img/item/gesamtinfoheading.png",n_tries=10,delay=0.25) == False:
            raise Exception("could not find gesamtinfoheading")
        self.mti_rel_movement(image="img/item/gesamtinfoheading.png",screenshot=self.screenshot(),rel_coords=(0,100))
        self.scroll(direction="down",n=2000)
        # self.move_to_image(image="img/exemplar_exemplare.png",screenshot=self.screenshot())
        pyautogui.moveTo(*EXEMPLAR_POSITION)
        pyautogui.leftClick()
        self.enter_edit_mode(gesamtinfo=True)
        
    
    def exemplar_screen(self,signatur):
        self.logging.bot_info("exemplar screen")
        self.enter_edit_mode()
        pyautogui.moveTo(1093,369)
        if not self.check(image="img/title/exemplar_stuff.png",n_tries=10,delay=0.2):
            Exception("could not find img/title/exemplar_stuff.png in exemplar_screen")
        pyautogui.leftClick()
        pyautogui.write(signatur)
        pyautogui.hotkey("altleft","p")
        self.logging.bot_info("pressed alt+p")
        self.check("img/add_signatur.png",n_tries=10,delay=0.2)
        time.sleep(DELAY)
        pyautogui.moveTo(815,96)
        pyautogui.leftClick()
        if not self.check("img/exemplar_anzahlEx1.png",n_tries=10,delay=0.1):
            raise Exception("could not find img/exemplar_anzahlEx1.png in exemplar_screen")
        self.logging.bot_info("alt+r finished")
        self.commit()
    
    def commit(self):
        pyautogui.keyDown("altleft")
        pyautogui.press("b")
        pyautogui.press("l")
        pyautogui.keyUp("altleft")
        if self.check("img/adis_message.png",n_tries=10,delay=0.3) == False:
            raise Exception("could not find adis_message.png")
        if self.commit_success() == True:
            self.logging.bot_info("commit successful")
            time.sleep(DELAY)  #! dirty fix, only momentary
            pyautogui.click(1019,561)
            pyautogui.hotkey("altleft","s")
            send_notification(f"Successfully changed PPN:**{self.ppn}**: \n ```-Removed {self.oldnotation}\n -Added {self.signatur}```","PC1","info")
        else:
            send_notification(f"Commit failed for PPN:**{self.ppn}***: \n ```-Removed {self.oldnotation}\n -Added {self.signatur}```","PC1","critical")
            self.logging.bot_critical(f"commit failed, PPN: {self.ppn}")
            raise Exception("commit failed")
        time.sleep(0.2)
        pyautogui.hotkey("altleft","s")
        time.sleep(0.2)
    
    def commit_success(self):
        
        pyautogui.screenshot(region=(854,483,210,50)).save("img/adis_message.png")
        text = imagerecognition.ocrtxt("img/adis_message.png")
        text.replace("\n","")
        if "aDIS/Lokalsatz ist geandert worden" in text:
            print("commit success")
            send_embedded_message_success(ppn=self.ppn, removed=self.oldnotation, changed=self.signatur)
            return True
        else:
            self.logging.bot_critical("commit failed")
            return False
    
    def enter_edit_mode(self,gesamtinfo=False):
        if gesamtinfo == False:
            pyautogui.moveTo(*EDIT_POSITION)
        # self.move_to_image("img/item/edit.png",self.screenshot())
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
        def check_if_deletion_allowed(image_text):
            if not image_text in imagerecognition.FIELDS_TO_DELETE:
                send_notification(f"not deleting ```*{image_text}*```","desktop","info")
                return False 
            else:
                send_notification(f"deleting ```*{image_text}*```","desktop","info")
                return True
        # time.sleep(.2)
        
        self.screenshot(region=line1).save("img/item/decipher.png")
        self.screenshot(region=line2).save("img/item/decipher1.png")
        
        text_line_1 = imagerecognition.ocrtxt("img/item/decipher.png")
        text_line_2 = imagerecognition.ocrtxt("img/item/decipher1.png")
        if text_line_1 not in self.oldnotation:
            self.oldnotation.append(text_line_1)
        if text_line_2 not in self.oldnotation:
            self.oldnotation.append(text_line_2)
        subject = text_line_1.split(" ")[0]
        subject2 = text_line_2.split(" ")[0]
        if check_if_deletion_allowed(subject) and check_if_deletion_allowed(subject2):
            self.delete_line(line2[:2])
            self.delete_line(line1[:2])
            send_notification("deleted both lines","desktop","info")
        elif check_if_deletion_allowed(subject):
            self.delete_line(line1[:2])
        elif check_if_deletion_allowed(subject2):
            self.delete_line(line2[:2])
        elif (subject and subject2) not in imagerecognition.FIELDS_TO_DELETE:
            return False
        return True

    def edit_gesamtinfo(self,signatur):
        
        self.enter_edit_mode()
        self.check("img/item/sachersch.png",n_tries=10,delay=0.3)
        self.move_to_image("img/item/sachersch.png",self.screenshot())
        pyautogui.leftClick()
        self.move_to_image("img/item/notation.png",self.screenshot())
        pyautogui.leftClick()
        for i in range(5):
            if self.remove_notation() == False:
                break
        pyautogui.moveTo(1160,665)                 
        pyautogui.leftClick()
        pyautogui.hotkey("ctrl","a")
        time.sleep(0.02)
        pyautogui.write(signatur) 
        send_notification("Wrote RVK", "PC1","info")
        pyautogui.hotkey("altleft","p")
        #self.check("img/main_menu/main_menu_btns.png",n_tries=10,delay=0.2)
        
    def locate(self,image):
        if pyautogui.locateOnScreen(image):
            return True
        else:
            self.logging.bot_debug(f"could not locate {image}")
            return False
    def run(self,signatur:str, ppn:str):
        self.logging.bot_info("Run started")
        
        if self.first_run:
            self.startup()
            self.first_run = False
        self.ppn = ppn
        self.signatur = signatur
        if self.main_screen(ppn_number=ppn)==True:#! replace constant with variable later on
            self.item_screen(signatur=signatur)
            self.exemplar_screen(signatur=signatur)
        else:
            # pyautogui.hotkey("altleft","s")
            self.logging.bot_critical("could not find main screen, restarting")
            return False
        
    def start_adis(self,username,password):# TODO: make this work
        pyautogui.hotkey("winleft","d")
        pyautogui.click(67,251,clicks=2)
        if not self.check("img/adis_create_connection.png",n_tries=20,delay=0.3):
            raise Exception("adis not found after doubleclick")
        conn_loc = pyautogui.locateOnScreen("img/adis_create_connection.png")
        pyautogui.click(*pyautogui.center(conn_loc))
        time.sleep(DELAY)
        pyautogui.press("enter")
        pyautogui.write(username)
        pyautogui.press("tab")
        pyautogui.write([password,"enter"])
        pyautogui.press("space")        
 
    def startup(self): #* done
        window_name = "PHFR: Katalog"
        if not window_name in pyautogui.getActiveWindow().title:
            self.logging.bot_info("waiting for window, checking if it exists")
            move.change_window("PHFR: Katalog")
            
        elif window_name in pyautogui.getActiveWindow().title:
            self.logging.bot_info("window found, checking if screen matches")
            if not self.check_screen("img/main_menu/main_menu_btns.png"):
                raise Exception("screen does not match, didn't find main menu")    
        pyautogui.moveTo(*START_POSITION)

























import json
import time, pyautogui
import imagerecognition
import asyncio
# # time.sleep(5)
# # print(pyautogui.position())
# # pyautogui.screenshot(region=(854,483,210,50)).save("current.png")
# text = imagerecognition.ocr_core("img/adis_message.png")
# #remove \n and \r
# text = text.replace("\n","")
# print(text)

# # this_count = imagerecognition.count("img/item/thiscount.png")
# # print(this_count)


# with open("data/test.json","r",encoding="utf-8") as f:
#     jsonfile = json.load(f)
    
# print(len(jsonfile))


DELAY = 0.5

print(DELAY+0.5)