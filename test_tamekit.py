#!/usr/bin/env python

import tamekit
import time
import timeit
import unittest

TimeoutError = tamekit.TimeoutError

class TimeoutAfterTests(unittest.TestCase):

  def compute_for(self, dur):
    start = timeit.default_timer()
    u = 0
    while timeit.default_timer() - start < dur:
      pass

  def test_decorator(self):

    @tamekit.timeout_after(1)
    def _fn():
      self.compute_for(2)

    start_ts = timeit.default_timer()
    with self.assertRaises(TimeoutError):
      _fn()
    end_ts = timeit.default_timer()
    self.assertLess(abs(1 - (end_ts - start_ts)), 0.1)

  def test_context_manager(self):

    start_ts = timeit.default_timer()
    with self.assertRaises(TimeoutError):
      with tamekit.timeout_after(1):
        self.compute_for(2)
    end_ts = timeit.default_timer()
    self.assertLess(abs(1 - (end_ts - start_ts)), 0.1)

  def test_exc_after_wrapped_code(self):

    with tamekit.timeout_after(1):
      self.compute_for(0.5)
    try:
      self.compute_for(1)
    except TimeoutError:
      self.fail('exc raised outside wrapped block')

  def test_long_system_call(self):

    start_ts = timeit.default_timer()
    with self.assertRaises(TimeoutError):
      with tamekit.timeout_after(1):
        time.sleep(1.3)
        self.compute_for(1)
    end_ts = timeit.default_timer()
    self.assertLess(abs(1.3 - (end_ts - start_ts)), 0.1)

  def test_custom_exc(self):

    class CustomError(Exception):
      pass
    custom_error = CustomError()

    with self.assertRaises(CustomError):
      with tamekit.timeout_after(1, exctype=CustomError):
        self.compute_for(2)

    with self.assertRaises(TypeError):
      with tamekit.timeout_after(1, exctype=custom_error):
        self.compute_for(2)

  def test_caught_timeout_in_thread(self):

    try:
      with tamekit.timeout_after(1):
        try:
          self.compute_for(0.5)
        except TimeoutError:
          self.compute_for(1)
    except TimeoutError:
      self.fail('timeout_after must not raise multiple exc')

  def test_delayed_use(self):

    ta = tamekit.timeout_after(1)
    try:
      self.compute_for(1.5)
    except TimeoutError:
      self.fail('exc raised without deco or context manager')

    start_ts = timeit.default_timer()
    with self.assertRaises(TimeoutError):
      with ta:
        self.compute_for(2)
    end_ts = timeit.default_timer()
    self.assertLess(abs(1 - (end_ts - start_ts)), 0.1)

  def test_delayed_use_decorator(self):

    @tamekit.timeout_after(1)
    def _fn():
      self.compute_for(2)

    time.sleep(1)

    start_ts = timeit.default_timer()
    with self.assertRaises(TimeoutError):
      _fn()
    end_ts = timeit.default_timer()
    self.assertLess(abs(1 - (end_ts - start_ts)), 0.1)

  def test_no_timeout(self):

    try:
      with tamekit.timeout_after(2):
        self.compute_for(0.7)
    except TimeoutError:
      self.fail('exc raised before timeout')

if __name__ == '__main__':
  unittest.main()
