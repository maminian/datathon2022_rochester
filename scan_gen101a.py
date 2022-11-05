

'''
# via https://pypi.org/project/PyPDF2/
reader = pp2.PdfReader(DATA_FILES[0])
number_of_pages = len(reader.pages)
for page in reader.pages:
    text = page.extract_text()
    print(text)
'''
