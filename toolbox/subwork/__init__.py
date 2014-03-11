#-*- coding: UTF-8 -*-

from toolbox.exceptions import CommandExecutionFiled
from toolbox.exceptions import CommandExecutionTimeout
import os
import time
import tempfile
import signal
import shlex
import subprocess

class SubWork(object):
    """
    add timeout support!
    if timeout, we SIGTERM to child process, and not to cause zombie process
    safe!
    """
    def __init__(self, 
                 cmd, 
                 timeout=5*60*60,
                 stdin=None,
                 stdout=None,
                 stderr=None):
        """
        default None
        """
        self._cmd = cmd
        self._Popen = None
        self._pid = None
        self._return_code = None
        self._stdin = stdin
        self._stdout = stdout
        self._stderr = stderr
        self._cwd = None
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

    def _wait(self, Popen):
        """
        Wait child exit signal
        """
        Popen.wait()

    def _free_child(self, pid, Popen):
        """
        Kill process by pid
        """
        try:
            self._terminate(pid)
            self._kill(pid)
            self._wait(Popen)
        except:
            pass

    def _run(self):
        #Run cmd.
        cmd = shlex.split(self._cmd)
        try:
            self._Popen = subprocess.Popen(args=cmd, 
                                          stdout=self._stdout, 
                                          stderr=self._stderr, 
                                          cwd=self._cwd)
            self._pid = self._Popen.pid
            self._start_time = time.time()
            while (self._Popen.poll() == None and 
                    (time.time() - self._start_time) < self._timeout):
                time.sleep(1)
        except (OSError, ValueError), e:
            raise CommandExecutionFiled("Execute Commonand Filed.", e)
            
        # Child is not exit yet.
        if self._Popen.poll() == None: 
            self._free_child(self._pid, self._Popen)
            raise CommandExecutionTimeout("Command Execution Timeout %ds." % self._timeout)
        else:
            self._return_code = self._Popen.poll()

    def execute(self):
        if self._stdout == None or self._stderr():
            self._stdout = tempfile.TemporaryFile()
            self._stderr = tempfile.TemporaryFile()
            use_tempfile = True

        try:
            self._run()
        except:
            raise

        if use_tempfile:
            try:
                self._stdout.seek(0)
                stdout = self._stdout.read()
                self._stderr.seek(0)
                stderr = self._stderr.read()
            finally:
                self._stdout.close()
                self._stderr.close()
        else:
            stdout = self._stdout
            stderr = self._stderr

        return {"code":self._return_code,
                "stdout":stdout,
                "stderr":stderr
                }
