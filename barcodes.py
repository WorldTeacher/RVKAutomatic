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
    
    
    
    
if __name__ == "__main__":
    import json
    with open("completed.json","r",encoding="utf-8") as f:
        data=json.load(f)
    for entry in data:
        ppn=data[entry]["PPN"]
        sig=data[entry]["SIG"]
        notice=data[entry]["NOT"]
        edition=data[entry]["EDI"]
        BarcodeGenerator(ppn=ppn,signatur=sig).create_barcodes()
    # ImageWriter().save("test", "PNG")