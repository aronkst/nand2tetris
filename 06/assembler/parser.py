class Parser:
    def __init__(self, text):
        self.text = self._clear_asm(text)

    def _clear_asm(self, text):
        new_text = ''
        for line in text.splitlines():
            if line == '' or line[0:2] == '//':
                continue
            line = line.replace(' ', '')
            if '//' in line:
                line = line.split('//')[0]
            new_text += line + '\n'
        return new_text[0:-1]
