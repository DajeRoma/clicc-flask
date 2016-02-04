from ctypes import *

PIPE_ACCESS_DUPLEX = 0x3
PIPE_TYPE_MESSAGE = 0x4
PIPE_READMODE_MESSAGE = 0x2
PIPE_WAIT = 0
PIPE_UNLIMITED_INSTANCES = 255
BUFSIZE = 4096
NMPWAIT_USE_DEFAULT_WAIT = 0
INVALID_HANDLE_VALUE = -1
ERROR_PIPE_CONNECTED = 535

MESSAGE = "Default answer from server\0"

class PipeIn:
    def __init__(self, name):
        self.szPipename = "\\\\.\\pipe\\" + name
        self.name = name
        self.callback = False
        THREADFUNC = CFUNCTYPE(c_int, c_int)
        thread_func = THREADFUNC(self.ReadWrite_ClientPipe_Thread)
        while 1:
            hPipe = windll.kernel32.CreateNamedPipeA(self.szPipename,
                                                     PIPE_ACCESS_DUPLEX,
                                                     PIPE_TYPE_MESSAGE |
                                                     PIPE_READMODE_MESSAGE |
                                                     PIPE_WAIT,
                                                     PIPE_UNLIMITED_INSTANCES,
                                                     BUFSIZE, BUFSIZE,
                                                     NMPWAIT_USE_DEFAULT_WAIT,
                                                     None
                                                    )
            if (hPipe == INVALID_HANDLE_VALUE):
                print "Error in creating Named Pipe"
                return 0

            fConnected = windll.kernel32.ConnectNamedPipe(hPipe, None)
            if ((fConnected == 0) and (windll.kernel32.GetLastError() == ERROR_PIPE_CONNECTED)):
                fConnected = 1
            if (fConnected == 1):
                dwThreadId = c_ulong(0)
                hThread = windll.kernel32.CreateThread(None, 0, thread_func, hPipe, 0, byref(dwThreadId))
                if (hThread == -1):
                    print "Create Thread failed"
                    return 0
                else:
                    windll.kernel32.CloseHandle(hThread)
            else:
                print "Could not connect to the Named Pipe"
                windll.kernel32.CloseHandle(hPipe)
        return 0

    def set_callback(self, callback):
        print callback
        self.callback = callback

    def ReadWrite_ClientPipe_Thread(self, hPipe):
        chBuf = create_string_buffer(BUFSIZE)
        cbRead = c_ulong(0)
        while 1:
            fSuccess = windll.kernel32.ReadFile(hPipe, chBuf, BUFSIZE, byref(cbRead), None)
            if ((fSuccess ==1) or (cbRead.value != 0)):
                print chBuf.value
                cbWritten = c_ulong(0)
                fSuccess = windll.kernel32.WriteFile(hPipe,
                                                     c_char_p(MESSAGE),
                                                     len(MESSAGE),
                                                     byref(cbWritten),
                                                     None
                                                    )
                if self.callback:
                    self.callback(chBuf.value)
            else:
                break
            if ( (not fSuccess) or (len(MESSAGE) != cbWritten.value)):
                print "Could not reply to the client's request from the pipe"
                break
            else:
                print "Number of bytes written:", cbWritten.value

        windll.kernel32.FlushFileBuffers(hPipe)
        windll.kernel32.DisconnectNamedPipe(hPipe)
        windll.kernel32.CloseHandle(hPipe)
        return 0
