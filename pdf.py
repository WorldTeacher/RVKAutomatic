from barcodes import BarcodeGenerator
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate
import json
import cv2
import io
class PDFGenerator:
    def __init__(self, filename):
        self.filename = filename
        self.doc = SimpleDocTemplate(filename, pagesize=letter)
        self.elements = []
        self.styles = getSampleStyleSheet()

    def add_page(self, image_file, description):
        # image=cv2.imread(image_file,cv2.IMREAD_UNCHANGED)
        # img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # img_io = io.BytesIO()
        image = Image(image_file)
        self.elements.append(image)
        self.elements.append(Paragraph(description, self.styles["Normal"]))

    def build(self):
        self.doc.build(self.elements)

    # def save(self):
    #     self.doc.save()



if __name__ == "__main__":
    import os

    image_path = 'barcodes/ppn/1643424831.svg'
    print(os.path.exists(image_path))

    pdf = PDFGenerator("output.pdf")
    # pdf.add_page("image_1.svg", "description_1")
    # pdf.add_page("image_2.svg", "description_2")
    # pdf.build()
    # pdf.save()
    with open("completed.json","r",encoding="utf-8") as f:
        data=json.load(f)
    for entry in data:
        ppn=data[entry]["PPN"]
        sig=data[entry]["SIG"]
        notice=data[entry]["NOT"]
        edition=data[entry]["EDI"]
        ppn_name, signatur_name=BarcodeGenerator(ppn=ppn,signatur=sig).create_barcodes()
        ppn_nr=ppn_name.split("/")[2].split(".")[0]
        signatur_nr=signatur_name.split("/")[2].split(".")[0]
        print(ppn_nr,signatur_nr)
        pdf.add_page(ppn_name,ppn_nr)
        pdf.add_page(signatur_name,signatur_nr)
    pdf.build()
    # # pdf.save()