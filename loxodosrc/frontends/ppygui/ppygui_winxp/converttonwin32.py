import re 


def convert(path):
    f = open(path)
    FUNCTION_RE = re.compile(r'(\S*?)\s*=\s*\w+dll.\w+.(\S*)')

    import ctypes

    dlls = \
    {
        'user32' : ctypes.windll.user32,
        'shell32' : ctypes.windll.shell32,
        'kernel32' : ctypes.windll.kernel32,
        'gdi32' : ctypes.windll.gdi32,
        'comctl32' : ctypes.windll.comctl32,
    }

    dlls_items = dlls.items()

    buffer = []
    for line in f.readlines():
        match = FUNCTION_RE.match(line)
        if match:
            function_name, function_w32_name = match.groups()
            #print function_name, function_w32_name
            dll_found = False
            for dll_name, dll in dlls_items:
                try:
                    getattr(dll, function_w32_name)
                except AttributeError:
                    continue
                else:
                    line = '%s = windll.%s.%s\n'\
                        %(function_name, dll_name, function_w32_name)
                    dll_found = True
                    break
            if not dll_found:
                line = '#%s' %line
                print '%s ignored' %function_name

        buffer.append(line)

    code= ''.join(buffer)
    open(path, 'w').write(code)

convert('filedlg.py')
