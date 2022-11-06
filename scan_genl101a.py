
# BIG todo: modularize ocr_tools.py and what I use here 
# to flexibly... enough? make the same tools useable between 
# (e.g.) Rochester pdf files, and Williamstown files.


# my local scripts
import stab
import parse

####################

import numpy as np
import pandas

import cv2 # for denoising and thresholding


import pdf2image # convert pdf file to 3D array

import deskew # for estimating an angle the document may be rotated by
import skimage # for rotating the image by a pre-determined angle.

import pytesseract # for main OCR step (image to text dataframe)

#################

#
matchy = {
    'defendant' :           {'op': parse.defendant, 'value':''},
    'utt_number' :          {'op': parse.utt_number, 'value':''},
    'officer' :             {'op': parse.officer, 'value':''},
    'law' :                 {'op': parse.law, 'value':''},
    'description' :         {'op': parse.description, 'value':''},
    'date' :                {'op': parse.null, 'value':''},
    'time' :                {'op': parse.null, 'value':''},
    'C/T/V' :               {'op': parse.null, 'value':''},
    'vehicle_year' :        {'op': parse.null, 'value':''},
    'vehicle_make' :        {'op': parse.null, 'value':''},
    'direction_travel' :    {'op': parse.direction, 'value':''},
    'highway_type/name' :   {'op': parse.highway, 'value':''},
    'charge_base' :         {'op': parse.charge_base, 'value':''},
    'officer_narrative' :   {'op': parse.officer_narrative, 'value':''}
}



def row_ize(arr):
    import numpy as np
    rows = []
    row = []
    for t in arr:
        if not type(t)==str:
#        if np.isnan(t):
            rows.append(' '.join(row))
            row = []
        else:
            row.append(t)
    return rows

def process_genl101a(df_tess):
    '''
    Purpose: process the output of tesseract on the Rochester Genl101A forms.
    Inputs: 
        df_tess: pandas.DataFrame
    Outputs: 
        info: cleaned dataframe with the following columns. Note these are 
        directly based on the form's top fields as well as items 1. through 8.
            "field" - 
                defendant
                utt_number
                officer
                law
                description
                date
                time
                C/T/V
                vehicle_year
                vehicle_make
                direction_travel
                highway_type/name
                charge_base
                officer_narrative
            "value" -
                string associated with each of the above.
    Items 1 through 8 in the form are inferred from the dataframe 
    based on the regularity of the form (string numbers 1. through 8. 
    immediately followed by their values.)
    '''
    import re
    
    
    df_tess.sort_values(['top', 'left'], inplace=True) # row-order sorting if not already
    for row in df_tess.iloc:
        
        match 


#########################################################
TESS_BLACKLIST = ";{}&£~=%¥€@" # characters we want to specifically exclude from the OCR

DPI = 300

#Pyesseract config string
TESS_CONFIG = '-c tessedit_char_blacklist={} \
        --psm 1 \
        --dpi {} \
        --user-patterns eng.my-patterns \
        --user-words eng.my-words'.format(TESS_BLACKLIST,DPI)
###############

pdfpath = stab.df.iloc[20]['filename']

pages = pdf2image.convert_from_path(pdfpath,
                              dpi = DPI,
                              first_page = 1,
                              last_page = 1,
                              thread_count = 4)

pp = pages[0]

# cast to numpy array
img = np.array(pp)
# rotate
angle = deskew.determine_skew(img)
img = skimage.transform.rotate(img, angle, resize=True)*255
# cast back to uint8
img = img.astype(np.uint8)
# denoise
img = cv2.fastNlMeansDenoising(img, h = 50)
# threshold
_ ,img  = cv2.threshold(img,150,255, cv2.THRESH_BINARY)

df_ocr = pytesseract.image_to_data(
    img, 
    output_type=pytesseract.Output.DATAFRAME, 
    lang='eng', 
    config=TESS_CONFIG
)


######################

text_rows = row_ize(df_ocr['text'].values)

for k in matchy.keys():
    matchy[k]['value'] = matchy[k]['op'](text_rows)
    print(k, matchy[k]['value'])


############################

if False:
    from matplotlib import pyplot
    fig,ax = pyplot.subplots()
    ax.imshow(img, cmap=pyplot.cm.Greys_r)
    fig.show()


