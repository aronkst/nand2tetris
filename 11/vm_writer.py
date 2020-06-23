class VmWriter():
    def __init__(self, vm_file):
        self._vm_file = vm_file
        self._vm_text = ''

    def write_push(self, segment, index):
        self._write('push %s %d' % (segment, index))

    def write_pop(self, segment, index):
        self._write('pop %s %d' % (segment, index))

    def write_arithmetic(self, command):
        self._write(command)

    def write_label(self, label):
        self._write('label %s' % label)

    def write_goto(self, label):
        self._write('goto %s' % label)

    def write_if(self, label):
        self._write('if-goto %s' % label)

    def write_call(self, name, n_args):
        self._write('call %s %d' % (name, n_args))

    def write_function(self, name, n_locals):
        self._write('function %s %d' % (name, n_locals))

    def write_return(self):
        self._write('return')

    def save(self):
        self._vm_file.write(self._vm_text)

    def _write(self, value):
        self._vm_text += '%s\n' % value
