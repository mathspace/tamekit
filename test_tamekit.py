#!/usr/bin/env python

import unittest
import tamekit
import time

class TimeoutAfterTests(unittest.TestCase):

  def test_decorator(self):

    @tamekit.timeout_after(1)
    def is_2_plus_2_really_4():
      for i in range(2 ** 64):
        u = 2 + 2
        if u != 4:
          return False
      return True

    timed_out = False
    start_ts = time.perf_counter()
    try:
      is_2_plus_2_really_4()
    except TimeoutError:
      timed_out = True
    end_ts = time.perf_counter()

    self.assertTrue(timed_out)
    self.assertLess(abs(1 - (end_ts - start_ts)), 0.1)

  def test_context_manager(self):

    timed_out = False
    start_ts = time.perf_counter()
    try:
      with tamekit.timeout_after(1):
        for i in range(2 ** 64):
          u = 2 + 2
          if u != 4:
            break
    except TimeoutError:
      timed_out = True
    end_ts = time.perf_counter()

    self.assertTrue(timed_out)
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

    timed_out = False
    start_ts = time.perf_counter()
    try:
      with tamekit.timeout_after(1):
        while True:
          time.sleep(0.08)
    except TimeoutError:
      timed_out = True
    end_ts = time.perf_counter()

    self.assertTrue(timed_out)
    self.assertLess(abs(1 - (end_ts - start_ts)), 0.1)

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

if __name__ == '__main__':
  unittest.main()
