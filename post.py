from preprocess import PDF_Create
def post(dupes:bool):
    """
    Creates a pdf file from the json file.
    
    """
    pdf=PDF_Create().create_pdf(remove_dupes=dupes).move_json_file()
    return pdf
if __name__ == "__main__":
    dupes=input("Remove duplicates? (y/n) ")
    if dupes=="y":
        post(dupes=True)
    else:
        post(dupes=False)