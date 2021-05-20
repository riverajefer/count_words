import os
import imghdr
from flask import jsonify
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

def allowedfile(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class CountWordsDocument():

    def __init__(self):
        pass
    
    def countWordFromPdf(self, path_file):
        print('countWordFromPdf')
        
        with open(path_file, "rb") as f:
            pdf = pdftotext.PDF(f)

        fileVariable = open('/home/count_words/output.txt', 'r+')
        fileVariable.truncate(0)
        fileVariable.close()

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


    def pdftoText(self, file):
        print('pdftoText')
        
        fileVariable = open('/home/count_words/out_text.txt', 'r+')
        fileVariable.truncate(0)
        fileVariable.close()

        pages = convert_from_path(file, 500) 
        image_counter = 1

        for page in pages: 
            filename = "page_"+str(image_counter)+".jpg"
            page.save(filename, 'JPEG') 
            image_counter = image_counter + 1

        filelimit = image_counter-1
        outfile = "out_text.txt"
        f = open(outfile, "a") 

        for i in range(1, filelimit + 1): 
            filename = "page_"+str(i)+".jpg"
            text = str(((pytesseract.image_to_string(Image.open(filename))))) 
            text = text.replace('-\n', '')	 
            f.write(text) 

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


    def get_pdf_searchable_pages(self, fname):
        print('get_pdf_searchable_pages')
        
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
    
    
    def onStartCount(self, file):
        print('onStartCount')
        filename = secure_filename(file.filename)    
        print(filename)
        
        if filename != '' and allowedfile(file.filename):
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            os.chdir(app.config['UPLOAD_FOLDER'])
            path_file = os.path.abspath(filename)
            print(os.path.abspath(filename))
            
            file_name, file_extension = os.path.splitext(path_file)
            print(file_extension)

            if(file_extension=='.pdf'):
                print('Es pdf')
                # Saber si el documento es escaneado
                print('Saber si el documento es escaneado')
                if self.get_pdf_searchable_pages(os.path.abspath(filename)):
                    result = self.countWordFromPdf(filename)
                    return jsonify(result)
                else:
                    print('Documento digital')
                    result = pdftoText(os.path.abspath(filename))
                    return jsonify(result)                

            elif(file_extension=='.docx' or file_extension=='.doc'):
                print('Es tipo doc o docx')
            else:
                print('No es un formato valido')

        else:
            print('Formato no permitido')
            data = {'success': False, 'message': 'Archivo no permitido'}
            return jsonify(data)




@app.route('/')
def index():
    return render_template('index.html')


@app.route('/uploader', methods = ['POST'])
def upload_file():
    file = request.files['file']
    CountWordsDocument().onStartCount(file=file)

    
if __name__ == '__main__':
    app.run(host="0.0.0.0")