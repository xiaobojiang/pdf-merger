from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse,HttpResponseServerError
from django.http import StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
import uuid
import os
import json
import logging
from modules.pdf_merger import pdf_merger
from modules.data_model import general_response
from errorcodes.errCodes import errCodes

logger = logging.getLogger('scripts')



def file_iterator(download_file, chunk_size=1024):
    with open(download_file,'rb') as f:
        while True:
            c = f.read(chunk_size)
            if c:
                yield c
            else:
                break

# Create your views here.
@csrf_exempt
def merge_pdf(request):
    response={}
    if request.method == 'POST':
        if 'files' in request.FILES:
            #print (request.FILES)
                
            input_files=[]
            output_file = os.path.join(os.path.dirname(settings.BASE_DIR),'files','merged'+str(uuid.uuid4())+'.pdf')
            for f in request.FILES.getlist('files'):
                try:
                    retFile = f
                    fileName = retFile.name
                    logger.info(fileName)
                    
                    newFileName = str(uuid.uuid4())+'_'+fileName
                    
                    tempFilePath = os.path.join(os.path.dirname(settings.BASE_DIR),'files',newFileName)
                    with open(tempFilePath,'wb+') as destination:
                        for chunk in f.chunks():
                            destination.write(chunk)
                    input_files.append(tempFilePath)
                except Exception as e:
                    logger.error(e, exc_info=True) 
            pdf_merger_tasker = pdf_merger()
            resp = pdf_merger_tasker.merge(input_files,output_file)

            for f in input_files:
                try:
                    os.remove(f)
                except Exception as e:
                    logger.error(e, exc_info=True) 
                
            if resp.get_success() == True:
                ouput_file = resp.get_payload()
                response = StreamingHttpResponse(file_iterator(output_file))
                response["Content-Type"] = "application/octet-stream"
                response["Content-Disposition"] = "attachment;filename={}".format(output_file)                
                return response

            else:
                response['code']=errCodes.ERROR_INTERNAL.value
                response['reason']=resp.get_payload()
                return HttpResponse(json.dumps(response),content_type="application/json",status=400)

        else:    
            response['code']=errCodes.ERROR_CONTENT_EMPTY.value
            response['reason']='user multi-form and file key shall be files'
            return HttpResponse(json.dumps(response),content_type="application/json",status=400)
    else:
        response['code']=errCodes.ERROR_METHOD_NOT_ALLOWED.value
        response['reason']='method only support post'
        return HttpResponse(json.dumps(response),content_type="application/json", status=405)