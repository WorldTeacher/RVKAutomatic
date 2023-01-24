import regex as re
import pytesseract,cv2



pytesseract.pytesseract.tesseract_cmd = r'C:\Users\aky547\Desktop\tesseract\tesseract.exe'
FIELDS_TO_DELETE=[
    "Allg",
    "Arch",
    "Bad",
    "Bio",
    "Che",
    "Deu",
    "DFF",
    "EDV",
    "Fre",
    "Geo",
    "His",
    "HTW",
    "JuLi",
    "Komm",
    "Kun",
    "Math", 
    "Mus",
    "Nat",
    "Paed",
    "Phil",
    "Phy",
    "Pol",
    "Psy",
    "Jur",
    "Soz",
    "Spo",
    "Spra",
    "Tech",
    "Theo", 
    "Volk",
    "Wir",
    "Oeko"
]
def ocr_core(filename):
    """
    This function will handle the core OCR processing of images.
    """
    text = pytesseract.image_to_string(filename)  # We'll use Pillow's Image class to open the image and pytesseract to detect the string in the image
    return text
def ocrtxt(filename):
    img = cv2.imread(filename)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))
    
    # Applying dilation on the threshold image
    dilation = cv2.dilate(thresh1, rect_kernel, iterations = 1)
    
    # Finding contours
    contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    
    # Creating a copy of image
    im2 = img.copy()
    
    # A text file is created and flushed
    file = open("recognized.txt", "w+")
    file.write("")
    file.close()
    
    # Looping through the identified contours
    # Then rectangular part is cropped and passed on
    # to pytesseract for extracting text from it
    # Extracted text is then written into the text file
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        
        # Drawing a rectangle on copied image
        rect = cv2.rectangle(im2, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Cropping the text block for giving input to OCR
        cropped = im2[y:y + h, x:x + w]
        
        # Open the file in append mode
        
        
        # Apply OCR on the cropped image
        text = pytesseract.image_to_string(cropped)
        with open("recognized.txt", "a") as file:
            file.write(text)
            
    return text

def digits(filename):
    text = pytesseract.image_to_string(filename)
    digit=re.findall(r'\d+', text)
    return digit

if __name__ == '__main__':
    digit = ocr_core("C:/Users/aky547/Desktop/img/item/gesamtinfoheading.png")
    print(digit)
    # if lesson in txt:
    #     if lesson in FIELDS_TO_DELETE:
    #         print("found")