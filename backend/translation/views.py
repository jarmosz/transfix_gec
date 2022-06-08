from tracemalloc import start
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from websocket import create_connection
from django.conf import settings
import subprocess
from .serializers import TranslationSerializer
from rest_framework import status
from pathlib import Path
import regex as re
import uuid
import os
from langdetect import detect

BASE_DIR = Path(__file__).resolve().parent

from rest_framework.decorators import api_view, renderer_classes, parser_classes
from .renderers import MyXMLRenderer

def filter_dummy_errors(original, error):

    if '//' in error:
        return (False, "")
    elif error.split(" ") > 2:
        return (False, "")
    # Check if is not english
    elif detect(error) != 'pl':
        return (False, "")
    
    return (True, error)

def get_context(line, start_index, end_index):

    start_index = start_index - 20
    end_index = end_index + 20

    if start_index >=0 and end_index <= len(line) -1:
        return '...' + line[start_index:end_index] + '...'
    else:
        if start_index < 0 and end_index <= len(line) -1:
            return line[0:end_index] + '...'
        elif start_index >= 0 and end_index > len(line) -1:
            return '...'+line[start_index:len(line)-1]
        else:
            return line

def diff_text(original, corrected):
    lines = corrected.splitlines(1)
    output = []
    for idx, line in enumerate(lines):
        groups_found = re.findall('\[-([^\[]*?)\+}', line)
        new_line = re.sub('\[-([^\[]*?)\+}', '', line)

        for group in groups_found:
            removed = re.findall('^(.*?)\-]', group)
            added = re.findall('{\+(.*?)$', group)

            start_position = re.search('\[-([^\[]*?)\+}', line).start()
            end_position = re.search('\[-([^\[]*?)\+}', line).end()

            is_error, error = filter_dummy_errors(removed, added)
            
            if is_error:
                output.append({'id': 'grammar-error', 'type': 'grammar', 'correction': added[0], 'context': f'{get_context(lines[idx], start_position, end_position)}', 'msg': f"Zamiana '{removed[0]}' na '{added[0]}'"})
        
        removed = re.findall('\[\-(.*?)\-]', new_line)
        added = re.findall('{\+(.*?)\+}', new_line)
        if removed is list:
            for remove in removed:
                output.append({'id': 'grammar-error', 'type': 'grammar', 'correction': "", 'context': f'{lines[idx]}', 'msg': f"Usunięcie '{remove}"})
        if added is list:
            for add in added:
                output.append({'id': 'grammar-error', 'type': 'grammar', 'correction': "", 'context': f'{lines[idx]}', 'msg': f"Dodanie '{add}"})
    return output
        

@api_view(['POST'])
@parser_classes([MultiPartParser])
@renderer_classes([MyXMLRenderer])
def xml_translate(request, format=None):

    uploaded_file = request.FILES['file']

    original_text = str(uploaded_file.read().decode('utf-8'))
    # Save raw txt file
    raw_filename = uuid.uuid1()
    with open(f'./translation/files/{raw_filename}.txt', 'w') as file:
        file.write(original_text)

    proc = subprocess.Popen(f'cat {BASE_DIR}/files/{raw_filename}.txt | sh {BASE_DIR}/preprocess_text.sh', stdout=subprocess.PIPE, shell=True)
    output, err = proc.communicate()
    ws = create_connection(settings.TRANSLATION_WEBSOCKET)
    text = output.decode('utf-8')
    ws.send(text)
    result = ws.recv()
    result_filename = uuid.uuid1()
    with open(f'./translation/files/{result_filename}.txt', 'w') as file:
        file.write(result)

    sec_proc = subprocess.Popen(f'cat {BASE_DIR}/files/{result_filename}.txt | sh {BASE_DIR}/postprocess_text.sh', stdout=subprocess.PIPE, shell=True)
    sec_output, err = sec_proc.communicate()
    sec_output_filename = uuid.uuid1()
    with open(f'./translation/files/{sec_output_filename}.txt', 'w') as file:
        file.write(sec_output.decode("utf-8"))

    third_proc = subprocess.Popen(f'git diff $(cat {BASE_DIR}/files/{raw_filename}.txt | git hash-object -w --stdin) $(cat {BASE_DIR}/files/{sec_output_filename}.txt  | git hash-object -w --stdin)  --word-diff | tail -n +6', stdout=subprocess.PIPE, shell=True)
    third_output, err = third_proc.communicate()
    marked_errors = third_output.decode('utf-8').rstrip()

    os.remove(f"./translation/files/{raw_filename}.txt")
    os.remove(f"./translation/files/{result_filename}.txt")
    os.remove(f"./translation/files/{sec_output_filename}.txt")

    return Response(diff_text(original_text, marked_errors), status=status.HTTP_200_OK)

class TranslationAPIView(APIView):
    def post(self, request):

        serializer = TranslationSerializer(data=request.data)

        if serializer.is_valid():
            # Encode to BPE.
            proc = subprocess.Popen(f'echo "{request.data["text"]}" | sh {BASE_DIR}/preprocess_text.sh', stdout=subprocess.PIPE, shell=True)
            output, err = proc.communicate()
            ws = create_connection(settings.TRANSLATION_WEBSOCKET)
            text = output.decode('utf-8')
            ws.send(text)
            result = ws.recv()
            # Decode from BPE.
            sec_proc = subprocess.Popen(f'echo "{result.rstrip()}" | sh {BASE_DIR}/postprocess_text.sh', stdout=subprocess.PIPE, shell=True)
            sec_output, err = sec_proc.communicate()
            # Decode from BPE.
            third_proc = subprocess.Popen(f'git diff $(echo "{request.data["text"]}" | git hash-object -w --stdin) $(echo "{sec_output.decode("utf-8").rstrip()}" | git hash-object -w --stdin)  --word-diff | tail -n +6', stdout=subprocess.PIPE, shell=True)
            third_output, err = third_proc.communicate()
            marked_errors = third_output.decode('utf-8').rstrip()
            return Response({'corrected_text': sec_output.decode('utf-8').rstrip(), "errors": marked_errors}, status=status.HTTP_200_OK)
        else:
            return Response("Bad request", status=status.HTTP_400_BAD_REQUEST)