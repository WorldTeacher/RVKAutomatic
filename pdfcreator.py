from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.pdfgen import canvas
from reportlab.graphics import renderPDF, renderPM
from reportlab.platypus import SimpleDocTemplate
from svglib.svglib import svg2rlg
import barcode



class BarcodeGenerator:

    def __init__(self, ppn, signatur):
        self.ppn = ppn
        self.signatur = signatur
       
        
    
    def create_barcode_ppn(self):
        # Create barcode
        ean = barcode.get_barcode_class('code128')
        ean = ean(self.ppn)
        fullname = ean.save(f"barcodes/ppn/{self.ppn}")
        return fullname
    def create_barcode_sig(self):
        # Create barcode
        ean = barcode.get_barcode_class('code128')
        ean = ean(self.signatur)
        fullname = ean.save(f"barcodes/signatur/{self.signatur}")
        return fullname
    def create_barcodes(self):
        ppn_name=self.create_barcode_ppn()
        signatur_name=self.create_barcode_sig()
        return ppn_name,signatur_name
 
 
class PDFCreator:
    #create a pdf document using platypus with the barcodes, the pdf should be saved in the folder "pdfs", create a save function that creates the pdf after the add_data function has added all the data
    def __init__(self):
        self.template = SimpleDocTemplate("pdfs/manual.pdf", pagesize=letter)
        self.flowables = []
        self.canvas = canvas.Canvas("pdfs/manual.pdf")
    def add_data(self,ppn,signatur):
        #add the barcode svg images for the ppn and the signatur to the pdf using canvas
        
        self.flowables.append(Paragraph("PPN",getSampleStyleSheet()["Normal"]))
        self.canvas.drawImage(ppn, 0, 0, width=100, height=100)
        
        
        
    def save(self):
        self.template.build(self.flowables)
if __name__ == "__main__":
    import json
    pdf=PDFCreator()
    with open("completed.json","r",encoding="utf-8") as f:
        data=json.load(f)
    for entry in data:
        ppn=data[entry]["PPN"]
        sig=data[entry]["SIG"]
        notice=data[entry]["NOT"]
        edition=data[entry]["EDI"]
        ppn_name, signatur_name=BarcodeGenerator(ppn=ppn,signatur=sig).create_barcodes()
        pdf.add_data(ppn_name,signatur_name)
        
    pdf.save()
    # ppn_name, signatur_name=BarcodeGenerator(ppn="848427939",signatur="ZC 51100 K92 (27)").create_barcodes()
    # create_document()