from preprocess import PDF_Create
def post(self):
    """
    Creates a pdf file from the json file.
    
    """
    pdf=PDF_Create().create_pdf().move_json_file()
    return pdf
if __name__ == "__main__":
    post()