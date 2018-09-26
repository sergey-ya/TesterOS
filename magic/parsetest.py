# coding: utf_8


import os
import re


class parseTestFile():
    name = None
    prere = None
    expected = None
    procedure = None
    result = None
    # file1_url = None
    auto = None
    def parseText(self, text=None):
        if text:
            lines = text[0].strip('\n').split('\n')

            for i, line in enumerate(lines):
                res = line + '<br>'
                res = re.sub(r'\[code\]', '<div class="code">', res)
                res = re.sub(r'\[/code\]', '</div>', res)
                res = re.sub(r'</div><br>', '</div>', res)
                lines[i] = res

            return ''.join(lines)
        else:
            return None

    def parseFileUrl(self, text=None):
        return text[0].strip('\n')


    def __init__(self, file_path):
        try:
            f = open(file_path, 'r')
            data = f.read()
            f.close()

            text = re.findall(r'\[NAME\](.*?)\[/NAME\]', data, re.DOTALL)
            self.name = self.parseText(text)
            text = re.findall(r'\[PRERE\](.*?)\[/PRERE\]', data, re.DOTALL)
            self.prere = self.parseText(text)
            text = re.findall(r'\[EXPECTED\](.*?)\[/EXPECTED\]', data, re.DOTALL)
            self.expected = self.parseText(text)
            text = re.findall(r'\[PROCEDURE\](.*?)\[/PROCEDURE\]', data, re.DOTALL)
            self.procedure = self.parseText(text)
            text = re.findall(r'\[RESULT\](.*?)\[/RESULT\]', data, re.DOTALL)
            self.result = self.parseText(text)
            text = re.findall(r'\[AUTO\](.*?)\[/AUTO\]', data, re.DOTALL)
            self.auto = self.parseText(text)

            # text = re.findall(r'\[FILE1\](.*?)\[/FILE1\]', data, re.DOTALL)
            # self.file1_url = self.parseFileUrl(text)
        except Exception as e:
            raise Exception(e)





# file = parseTestFile('/home/yarikov/web/testeros/apps/tests/test009.txt')
# print('PRERE')
# print(file.prere)
# print('EXPECTED')
# print(file.expected)
# print('PROCEDURE')
# print(file.procedure)
# print('RESULT')
# print(file.result)
# print('file')
# print(file.file1_url)


