from ctypes import windll
import win32gui
import win32ui
from PIL import Image

def getScreenShot(window_name):
    try:
        hwnd = win32gui.FindWindow(None, window_name)
        # Change the line below depending on whether you want the whole window
        # or just the client area.

        left, top, right, bot = win32gui.GetClientRect(hwnd)
        # left, top, right, bot = win32gui.GetWindowRect(hwnd)
        width = right - left
        height = bot - top

        hwndDC = win32gui.GetWindowDC(hwnd)
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)
        saveDC = mfcDC.CreateCompatibleDC()

        saveBitMap = win32ui.CreateBitmap()
        saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)

        saveDC.SelectObject(saveBitMap)

        PW_RENDERFULLCONTENT = 2

        # Change the line below depending on whether you want the whole window
        # or just the client area.
        result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 3)
        # result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 0)

        bmpinfo = saveBitMap.GetInfo()
        bmpstr = saveBitMap.GetBitmapBits(True)

        im = Image.frombuffer(
            'RGB',
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            bmpstr, 'raw', 'BGRX', 0, 1)

        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwndDC)

        return (result == 1), im
    except:
        print("Window %s not found!" % str(window_name))
        return False, None