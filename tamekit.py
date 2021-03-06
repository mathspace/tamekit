# tamekit.py - Code execution control toolkit for python
# Copyright (C) 2016 Mansour Behabadi <mansour@oxplot.com>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

from __future__ import division

import ctypes
import functools
import inspect
import threading
import time
import timeit

__all__ = ['timeout_after', 'TimeoutError']

try:
  TimeoutError = TimeoutError
except NameError:
  class TimeoutError(Exception):
    pass

def interrupt_thread(tid, exctype):
  """
  Interrupt thread using an instance of exctype

  tid: thread ID as returned by threading.get_ident() or Thread.ident

  Raises ValueError if thread doesn't exist
  """
  res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
    ctypes.c_long(tid), ctypes.py_object(exctype))
  if res == 0:
    raise ValueError('Invalid thread ID')

class timeout_after(object):
  """
  Combined context manager and decorator for timed execution

  As decorator: @timeout_after(dur)
  As context manager: with timeout_after(dur): ...

  Wrapped code is allowed to run for up to dur seconds, after which
  TimeoutError is raised inside that thread. Exception is not raised if
  thread is in middle of a system call, but will be as soon as it's done.
  """

  def __init__(self, dur, exctype = TimeoutError):
    """
    Start timer for the wrapped code

    dur: max. len of time in seconds the wrapped code is allowed to
         execute before interrupted by TimeoutError
    exctype: custom exception type to raise an instance of on timeout
    """
    if not inspect.isclass(exctype):
      raise TypeError('exctype must be a type (not instance)')

    self.exctype = exctype
    self.completed = False
    self.completed_lock = threading.Lock()
    self.dur = dur

  def __call__(self, f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
      # If we don't clone this instance, the decorated function will
      # only be time limited the first time it's called.
      with timeout_after(dur=self.dur, exctype=self.exctype):
        return f(*args, **kwargs)
    return wrapper

  def __enter__(self):
    self.tid = threading.current_thread().ident
    self.start = timeit.default_timer()
    watcher_thread = threading.Thread(target=self.watcher)
    watcher_thread.daemon = True
    watcher_thread.start()
    
  def __exit__(self, typ, value, traceback):
    with self.completed_lock:
      self.completed = True
    return False

  def watcher(self):
    while True:
      with self.completed_lock:
        if self.completed:
          return
        remaining = self.dur - (timeit.default_timer() - self.start)
        if remaining < 0:
          # ValueError could never be raised because __exit__ holds a
          # lock to set completed flag. If the flag was set, we'd never
          # be in this block. If the flag wasn't set, target thread
          # cannot progress until we get out of this block.
          interrupt_thread(self.tid, self.exctype)
          return
      time.sleep(max(0.002, remaining / 2))
