#!/usr/bin/env python

import unittest
import tamekit
import time

class TimeoutAfterTests(unittest.TestCase):

  def is_2_plus_2_really_4(self):
    for i in range(2 ** 64):
      u = 2 + 2
      if u != 4:
        return False
    return True

  def test_decorator(self):

    @tamekit.timeout_after(1)
    def _fn():
      self.is_2_plus_2_really_4()

    start_ts = time.perf_counter()
    with self.assertRaises(TimeoutError):
      _fn()
    end_ts = time.perf_counter()
    self.assertLess(abs(1 - (end_ts - start_ts)), 0.1)

  def test_context_manager(self):

    start_ts = time.perf_counter()
    with self.assertRaises(TimeoutError):
      with tamekit.timeout_after(1):
        self.is_2_plus_2_really_4()
    end_ts = time.perf_counter()
    self.assertLess(abs(1 - (end_ts - start_ts)), 0.1)

  def test_exc_after_wrapped_code(self):

    with tamekit.timeout_after(1):
      for i in range(50):
        time.sleep(0.01)
    try:
      for i in range(100):
        time.sleep(0.01)
    except TimeoutError:
      self.fail('exc raised outside wrapped block')

  def test_long_system_call(self):

    start_ts = time.perf_counter()
    with self.assertRaises(TimeoutError):
      with tamekit.timeout_after(1):
        time.sleep(1.1)
        time.sleep(1.1)
    end_ts = time.perf_counter()
    self.assertLess(abs(1.1 - (end_ts - start_ts)), 0.1)

  def test_custom_exc(self):

    class CustomError(Exception):
      pass
    custom_error = CustomError()

    with self.assertRaises(CustomError):
      with tamekit.timeout_after(1, exctype=CustomError):
        for i in range(2 ** 64):
          pass

    with self.assertRaises(TypeError):
      with tamekit.timeout_after(1, exctype=custom_error):
        for i in range(2 ** 64):
          pass

  def test_caught_timeout_in_thread(self):

    try:
      with tamekit.timeout_after(0.2):
        try:
          while True:
            time.sleep(0.01)
        except TimeoutError:
          for i in range(13):
            time.sleep(0.01)
    except TimeoutError:
      self.fail('timeout_after must not raise multiple exc')

  def test_delayed_use(self):

    ta = tamekit.timeout_after(1)
    try:
      for i in range(70):
        time.sleep(0.01)
    except TimeoutError:
      self.fail('exc raised without deco or context manager')

    start_ts = time.perf_counter()
    with self.assertRaises(TimeoutError):
      with ta:
        for i in range(120):
          time.sleep(0.01)
    end_ts = time.perf_counter()
    self.assertLess(abs(1 - (end_ts - start_ts)), 0.1)

  def test_delayed_use_decorator(self):

    @tamekit.timeout_after(1)
    def _fn():
      self.is_2_plus_2_really_4()

    time.sleep(1)

    start_ts = time.perf_counter()
    with self.assertRaises(TimeoutError):
      _fn()
    end_ts = time.perf_counter()
    self.assertLess(abs(1 - (end_ts - start_ts)), 0.1)

if __name__ == '__main__':
  unittest.main()
