import os
import pytz
import imghdr
import pdftotext
import pytesseract
import textract
from PIL import Image
import tempfile
from pdf2image import convert_from_path, convert_from_bytes
from pdfminer.pdfpage import PDFPage
from werkzeug.utils import secure_filename
from flask import Flask

app = Flask(__name__)

UPLOAD_FOLDER = '/home/Flask/count_words/files'
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc',  'xls', 'xlsx', 'txt'}
FILE_OUTPUT = '/home/Flask/count_words/files/output.txt'


class CountWordsDocument():
    
    def allowed_file(self, filename):
        return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def _doc_text(self, path_file):
        self._clear_file_output()
        text = textract.process(path_file)
        text = str(text).replace('\\n', ' ').replace(
            '\r', '').replace('\\', '').replace('xc3', '')

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

        output = {
            'success': True,
            'words': len(words),
            'numbers': numbers,
            'text': str(data),
            'spaces': str(spaces),
            'others': str(others)
        }

        print(output)
        app.logger.info('Procesado Ok !')
        return output


    def _clear_file_output(self):
        fileVariable = open(FILE_OUTPUT, 'r+')
        fileVariable.truncate(0)
        fileVariable.close()
        print('fileVariable')
        print(fileVariable)

    def _pdf_to_Text(self, file):
        print('Start Proccess Documento escaneado')
        
        try:
            self._clear_file_output()

            print('inicio convert_from_path')
            with tempfile.TemporaryDirectory() as path:
                pages = convert_from_path(file, output_folder=path)
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
                    f.write(text.encode().decode('ascii', 'ignore'))
                f.close()

                file = open(FILE_OUTPUT, "rt")
                data = file.read()
                print(data)

                return self._output_data(data)
        
        except Exception as e:
            print("ERROR : "+str(e)) 
            return {}



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

        return data
    
    def on_start_count(self, file):
        print('onStartCount')
        filename = secure_filename(file.filename)
        print(filename)

        if filename != '' and self.allowed_file(file.filename):
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

                else:
                    print('Documento escaneado')
                    print('Procesando...')

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
