import os
import sys
import imghdr
import pdftotext
import pytesseract
import textract
from flask import jsonify
from PIL import Image
from pdf2image import convert_from_path
from pdfminer.pdfpage import PDFPage
from werkzeug.utils import secure_filename

from flask import (
    Flask, render_template,
    request, redirect, url_for, abort,
    send_from_directory)


app = Flask(__name__)
app.config['DEBUG'] = True

UPLOAD_FOLDER = '/home/count_words/files'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc',  'xls', 'xlsx', 'txt'}
FILE_OUTPUT = '/home/count_words/files/output.txt'


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class CountWordsDocument():

    def __init__(self):
        pass


    def _doc_text(self, path_file):
        self._clear_file_output()
        text = textract.process(path_file)
        text = str(text).replace('\\n', ' ').replace('\r', '').replace('\\', '').replace('xc3', '')
        
        with open(FILE_OUTPUT, 'w') as f:
            f.write(str(text))

        file = open(FILE_OUTPUT, "rt")
        data = file.read()
        
        return self._output_data(data)
        
    
    def _output_data(self, data):
        words = data.split()
        numbers = sum(c.isdigit() for c in data)
        letters = sum(c.isalpha() for c in data)
        spaces = sum(c.isspace() for c in data)
        others = len(data) - numbers - letters - spaces

        print('TOTAL PALABRAS :', len(words))
        print('TOTAL NUMEROS :', numbers)

        output = {
            'success': True,
            'words': len(words),
            'numbers': numbers,
            'text': str(data), 
            'spaces': str(spaces),
            'others': str(others)
        }
        
        print(output)

        return jsonify(output)


    def _clear_file_output(self):
        fileVariable = open(FILE_OUTPUT, 'r+')
        fileVariable.truncate(0)
        fileVariable.close()

    
    def _count_word_from_pdf(self, path_file):
        print('countWordFromPdf')

        with open(path_file, "rb") as f:
            pdf = pdftotext.PDF(f)
        
        self._clear_file_output()


        with open(FILE_OUTPUT, 'w') as f:
            f.write("\n\n".join(pdf))

        file = open(FILE_OUTPUT, "rt")
        data = file.read()

        return self._output_data(data)


    def _pdf_to_Text(self, file):
        print('Start Proccess Documento escaneado')
        
        self._clear_file_output()

        pages = convert_from_path(file, 500)
        image_counter = 1

        for page in pages:
            filename = "page_"+str(image_counter)+".jpg"
            page.save(filename, 'JPEG')
            image_counter = image_counter + 1

        filelimit = image_counter-1
        f = open(FILE_OUTPUT, "a")

        for i in range(1, filelimit + 1):
            filename = "page_"+str(i)+".jpg"
            text = str(((pytesseract.image_to_string(Image.open(filename)))))
            text = text.replace('-\n', '')
            f.write(text)

        f.close()

        file = open(FILE_OUTPUT, "rt")
        data = file.read()

        return self._output_data(data)


    def _get_pdf_searchable_pages(self, fname):
        print('get_pdf_searchable_pages')

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
                print(
                    f"Document '{fname}' has {page_num} page(s). " f"Complete document is non-searchable")

                return False

            elif len(non_searchable_pages) == 0:
                print(
                    f"Document '{fname}' has {page_num} page(s). " f"Complete document is searchable")

                return True
            else:
                print(f"searchable_pages : {searchable_pages}")
                print(f"non_searchable_pages : {non_searchable_pages}")

                return False
        else:
            print(f"Not a valid document")

            return False

    def _file_not_allowed(self):
        data = {'success': False, 'message': 'Archivo no permitido'}

        return jsonify(data)
    
    
    def on_start_count(self, file):
        print('onStartCount')
        filename = secure_filename(file.filename)
        print(filename)

        if filename != '' and allowed_file(file.filename):
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            os.chdir(app.config['UPLOAD_FOLDER'])

            path_file = os.path.abspath(filename)
            print(os.path.abspath(filename))

            file_name, file_extension = os.path.splitext(path_file)
            print(f"file_extension: {file_extension}")

            if(file_extension == '.pdf'):
                print('Documento pdf')
                print('Saber si el documento es escaneado')

                if self._get_pdf_searchable_pages(os.path.abspath(filename)):
                    print('Documento digital')
                    
                    return self._doc_text(path_file=os.path.abspath(filename))
                    #return self._count_word_from_pdf(filename)
                else:
                    print('Documento escaneado')

                    return self._pdf_to_Text(os.path.abspath(filename))

            elif(file_extension == '.docx' or file_extension == '.doc' or file_extension == '.xlsx' or file_extension == '.xls' or file_extension == '.txt'):
                print('Es tipo doc o docx, .xlsx')
                return self._doc_text(path_file=os.path.abspath(filename))

            else:
                print('No es un formato valido')
                
                return self._file_not_allowed()

        else:
            print('Formato no permitido')
            
            return self._file_not_allowed()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/uploader', methods=['POST'])
def upload_file():
    file = request.files['file']
    return CountWordsDocument().on_start_count(file=file)


if __name__ == '__main__':
    app.run(host="0.0.0.0")
