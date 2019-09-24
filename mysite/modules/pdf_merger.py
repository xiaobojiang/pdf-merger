import os
try:
    from PyPDF4 import PdfFileReader, PdfFileWriter
except ImportError:
    from pyPdf import PdfFileReader, PdfFileWriter
from modules.data_model import general_response 

import logging

logger = logging.getLogger('scripts')

class pdf_merger:
    def merge(self,input_files,output_file):
        input_streams = []
        resp = general_response()
        try:
            # First open all the files, then produce the output file, and
            # finally close the input files. This is necessary because
            # the data isn't read from the input files until the write
            # operation. Thanks to
            # https://stackoverflow.com/questions/6773631/problem-with-closing-python-pypdf-writing-getting-a-valueerror-i-o-operation/6773733#6773733
            # for input_file in input_files:
                # input_streams.append(open(input_file, 'rb'))
            # writer = PdfFileWriter()
            # for reader in map(PdfFileReader, input_streams):
                # for n in range(reader.getNumPages()):
                    # writer.addPage(reader.getPage(n))
            writer = PdfFileWriter()        
            for input_file in input_files:
                input_stream = open(input_file, 'rb')
                reader = PdfFileReader(input_stream)
                
                if reader.isEncrypted:
                    try:
                        reader.decrypt('')
                        print('File Decrypted (PyPDF2)')
                    except:
                        command = ("cp "+ input_file +
                            " temp.pdf")
                        os.system(command)
                        command = ("qpdf --password='' --decrypt temp.pdf " + input_file)
                        os.system(command)
                        command = ("rm temp.pdf")
                        os.system(command)
                        print('File Decrypted (qpdf)')
                        fp = open(input_file,'rb')
                        reader = PdfFileReader(fp)
                else:
                    print('File Not Encrypted')
                for n in range(reader.getNumPages()):
                    writer.addPage(reader.getPage(n))
            with open(output_file, "wb") as fout:
                writer.write(fout)
                fout.close()
            resp.set_success(True)
            resp.set_payload(output_file)
        except Exception as e:
            resp.set_success(False)
            resp.set_payload(e.message)
            logger.error(e, exc_info=True)
        finally:
            for f in input_streams:
                f.close()
        return resp