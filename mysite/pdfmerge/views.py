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
import glob

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


@csrf_exempt
def purge_pdf(request):
    response={}
    if request.method == 'POST':
        #clear the pdf files in the path: /files
        base_files_path =  os.path.join(os.path.dirname(settings.BASE_DIR),'files')
        number_removed = 0
        file_name_list = []
        try:
            pdf_files = [f for f in glob.glob(base_files_path + '/*.pdf',recursive=True)]
            for f in pdf_files:
                file_name = os.path.basename(f)
                os.remove(f)
                number_removed += 1
                file_name_list.append(file_name)
            response['code']=errCodes.OK_CODE_BASE.value
            data={}
            data['number_removed'] = number_removed
            data['file_names'] = file_name_list
            response['data']=data
            return HttpResponse(json.dumps(response),content_type="application/json",status=200)

        except Exception as e:
            response['code']=errCodes.ERROR_INTERNAL.value
            response['reason']=str(e)
            return HttpResponse(json.dumps(response),content_type="application/json",status=400)
    
    else:
        response['code']=errCodes.ERROR_METHOD_NOT_ALLOWED.value
        response['reason']='method only support post'
        return HttpResponse(json.dumps(response),content_type="application/json", status=405)