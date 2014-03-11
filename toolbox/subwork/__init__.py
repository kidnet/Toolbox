#-*- coding: UTF-8 -*-

from toolbox import exceptions
import os
import sys
import time
import signal
import shlex
import traceback
import subprocess

class SubWork(object):
    """
    add timeout support!
    if timeout, we SIGTERM to child process, and not to cause zombie process
    safe!
    """
    #trace_back
    def _trace_back(self):
        try:
            type, value, tb = sys.exc_info()
            return str(''.join(traceback.format_exception(type, value, tb)))
        except:
            return ''

    def __init__(self, 
                 stdin=None, 
                 stdout=None, 
                 stderr=None, 
                 cmd=None, 
                 cwd=None, 
                 timeout=5*60*60):
        """
        default None
        """
        self._cmd = cmd
        self._Popen = None
        self._pid = None
        self._returncode = None
        self._stdin = None
        self._stdout = stdout
        self._stderr = stderr
        self._cwd = cwd
        self._timeout = int(timeout)
        self._start_time = None
        self._msg = ''

    def _send_signal(self, pid, sig):
        """
        Send a signal to the process
        """
        os.kill(pid, sig)

    def _terminate(self, pid):
        """
        Terminate the process with SIGTERM
        """
        self._send_signal(pid, signal.SIGTERM)

    def _kill(self, pid):
        """
        Kill the process with SIGKILL
        """
        self._send_signal(pid, signal.SIGKILL)

    def _wait(self, _Popen):
        """
        Wait child exit signal
        """
        _Popen.wait()

    def _free_child(self, pid, _Popen):
        """
        Kill process by pid
        """
        try:
            self._terminate(pid)
            self._kill(pid)
            self._wait(_Popen)
        except:
            pass

    def run(self):
        #Run cmd
        cmd = shlex.split(self._cmd)
        code = True
        try:
            self._Popen = subprocess.Popen(args=cmd, 
                                          stdout=self.__stdout, 
                                          stderr=self.__stderr, 
                                          cwd=self.__cwd)
            self._pid = self.__Popen.pid
            self._start_time = time.time()
            while (self._Popen.poll() == None and 
                    (time.time() - self._start_time) < self._timeout):
                time.sleep(1)
        except:
            self._msg += self._trace_back()
            self._returncode = -9998
            code = False

        # Check returncode
        # Child is not exit yet
        if self._Popen.poll() == None: 
            self._free_child(self._pid, self._Popen)
            self._returncode = -9999
        else:
            self._returncode = self._Popen.poll()

        return {"code":code,
                "msg":self._msg,
                "reg":{"returncode":self._returncode}
                }

    def _run_without_timeout(self):
        #Run cmd
        cmd = shlex.split(self._cmd)
        code = True
        try:
            self._Popen = subprocess.Popen(args=cmd, 
                                          stdout=self._stdout, 
                                          stderr=self._stderr, 
                                          cwd=self._cwd)
        except:
            self._msg += self._trace_back()
            self._returncode = -9998
            code = False

        return {"code":code,
                "msg":self._msg,
                "reg":{"returncode":self._returncode}
                }

def get_cur_path():
    try:
        return os.path.normpath(os.path.join(os.getcwdu(), 
                                os.path.dirname(__file__)))
    except:
        return

def check_returncode(dic=None):
    #Check returncode
    if not isinstance(dic, dict):
        raise TypeError, "dist must be a Distribution instance"
    returncode = dic["reg"]["returncode"]
    if returncode is None or int(returncode) == 0:
        return True, dic["msg"]
    else:
        return False, dic["msg"]

def shell_to_tty(_cmd=None, _cwd=None, _timeout=5*60*60): 
    """
    Execute CMD and output result to tty
    """
    try:
        shell = SubWork(cmd=_cmd, 
                        stdout=None, 
                        stderr=None, 
                        cwd=_cwd, 
                        timeout=_timeout)
        if _timeout == 0:
            return check_returncode(shell.run_without_timeout())
        else:
            return check_returncode(shell.run())
    except:
        return False, trace_back()

def shell_to_file(_cmd=None, _cwd=None, _timeout=5*60*60, outtype=0): 
    """
    Execute CMD and output result to file
    """
    try:
        try:
            if outtype == 0:
                fout = tempfile.TemporaryFile()
                ferr = tempfile.TemporaryFile()
            elif outtype == 1:
                out_path = os.path.join(get_cur_path(), 
                                        "%s__tmp_out" % str(time.time()))
                err_path = os.path.join(get_cur_path(), 
                                        "%s__tmp_out" % str(time.time()))
                fout = open(out_path, 'a+')
                ferr = open(err_path, 'a+')
            shell = SubWork(cmd=_cmd, 
                            stdout=fout, 
                            stderr=ferr, 
                            cwd=_cwd, 
                            timeout=_timeout)
            if _timeout == 0:
                req = check_returncode(shell.run_without_timeout())
            else:
                req = check_returncode(shell.run())
            fout.seek(0)
            out = fout.read()
            ferr.seek(0)
            err = "\n====Error Log Start====\n%s\n====Error Log End====" % ferr.read()
            out = out + err
            return req[0], _cmd + "\n" + str(out)
        finally:
            fout.close()
            ferr.close()
    except:
        return False, trace_back()
