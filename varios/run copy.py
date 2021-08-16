import imghdr
from flask import jsonify
import os
import pdftotext
from PIL import Image 
import pytesseract 
import sys 
from pdf2image import convert_from_path 

from flask import Flask, render_template, request, redirect, url_for, abort, \
    send_from_directory

from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['DEBUG'] = True


UPLOAD_FOLDER = '/home/count_words/files'

app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def countWordFromPdf(path_file):
    with open(path_file, "rb") as f:
        pdf = pdftotext.PDF(f)

    fileVariable = open('/home/count_words/output.txt', 'r+')
    fileVariable.truncate(0)
    fileVariable.close()

    # Save all text to a txt file.
    with open('/home/count_words/output.txt', 'w') as f:
        f.write("\n\n".join(pdf))
    
    file = open("/home/count_words/output.txt", "rt")
    data = file.read()
    words = data.split()

    numbers = sum(c.isdigit() for c in data)
    letters = sum(c.isalpha() for c in data)
    spaces  = sum(c.isspace() for c in data)
    others  = len(data) - numbers - letters - spaces
    
    print('TOTAL PALABRAS :', len(words))
    print('TOTAL NUMEROS :', numbers)

    return {
        'success': True,
        'words': len(words),
        'numbers': numbers,
        'text': str(data)
    }


def pdftoText(file):
    fileVariable = open('/home/count_words/out_text.txt', 'r+')
    fileVariable.truncate(0)
    fileVariable.close()    
    # Store all the pages of the PDF in a variable 
    pages = convert_from_path(file, 500) 

    # Counter to store images of each page of PDF to image 
    image_counter = 1

    # Iterate through all the pages stored above 
    for page in pages: 
        filename = "page_"+str(image_counter)+".jpg"
        page.save(filename, 'JPEG') 
        image_counter = image_counter + 1

    ''' 
    Part #2 - Recognizing text from the images using OCR 
    '''
    # Variable to get count of total number of pages 
    filelimit = image_counter-1

    # Creating a text file to write the output 
    outfile = "out_text.txt"

    # Open the file in append mode so that 
    # All contents of all images are added to the same file 
    f = open(outfile, "a") 

    # Iterate from 1 to total number of pages 
    for i in range(1, filelimit + 1): 
        filename = "page_"+str(i)+".jpg"
        text = str(((pytesseract.image_to_string(Image.open(filename))))) 
        text = text.replace('-\n', '')	 
        f.write(text) 

    # Close the file after writing all the text. 
    f.close() 

    file = open("out_text.txt", "rt")
    data = file.read()
    words = data.split()

    numbers = sum(c.isdigit() for c in data)
    letters = sum(c.isalpha() for c in data)
    spaces  = sum(c.isspace() for c in data)
    others  = len(data) - numbers - letters - spaces

    print('TOTAL PALABRAS :', len(words))
    print('TOTAL NUMEROS :', numbers)
    return {
        'success': True,
        'words': len(words),
        'numbers': numbers,
        'text': str(data)
    }



def get_pdf_searchable_pages(fname):
    # pip install pdfminer
    from pdfminer.pdfpage import PDFPage
    searchable_pages = []
    non_searchable_pages = []
    page_num = 0
    with open(fname, 'rb') as infile:

        for page in PDFPage.get_pages(infile):
            page_num += 1
            if 'Font' in page.resources.keys():
                searchable_pages.append(page_num)
            else:
                non_searchable_pages.append(page_num)
    if page_num > 0:
        if len(searchable_pages) == 0:
            print(f"Document '{fname}' has {page_num} page(s). " f"Complete document is non-searchable")
            return False

        elif len(non_searchable_pages) == 0:
            print(f"Document '{fname}' has {page_num} page(s). " f"Complete document is searchable")
            return True
        else:
            print(f"searchable_pages : {searchable_pages}")
            print(f"non_searchable_pages : {non_searchable_pages}")
            return False
    else:
        print(f"Not a valid document")
        return False



@app.route('/')
def index():
    #files = os.listdir(app.config['UPLOAD_PATH'])
    return render_template('index.html')



@app.route('/', methods=['POST'])
def upload_files():
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
    return '', 204


@app.route('/send', methods=['POST'])
def send():
    data = {'name': 'nabin khadka'}
    return jsonify(data)
    

@app.route('/uploads/<filename>')
def upload(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)


@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
      f = request.files['file']
      filename = secure_filename(f.filename)
      print(filename)
      if filename != '' and allowed_file(f.filename):
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
      
        os.chdir(app.config['UPLOAD_FOLDER'])
        path_file = os.path.abspath(filename)
        print(os.path.abspath(filename))
        
        file_name, file_extension = os.path.splitext(path_file)
        print(file_extension)

        if(file_extension=='.pdf'):
            print('Es pdf')
            # Saber si el documento es escaneado
            if get_pdf_searchable_pages(os.path.abspath(filename)):
                count_ = countWordFromPdf(filename)
                return jsonify(count_)
            else:
                count_ = pdftoText(os.path.abspath(filename))
                # data = {'success': False, 'message': 'Archivo no permitido'}
                return jsonify(count_)                

        elif(file_extension=='.docx' or file_extension=='.doc'):
            print('Es tipo doc o docx')
        else:
            print('No es un formato valido')
    
      else:
        print('Formato no permitido')
        data = {'success': False, 'message': 'Archivo no permitido'}
        return jsonify(data)

      # get_pdf_searchable_pages(os.path.abspath(filename))
      return 'file uploaded successfully'
      # acá hcaer la logica, validar que el archivo tenga extension, doc, pdf
      # llamara la funcion que chekea si es un archivo escaneado
      # si hacer ocr
      # no conteo normal
      # reponder el json con el conteo.

if __name__ == '__main__':
    app.run(host="0.0.0.0")