"""Incomplete implementation of a thread function for consuming a
 multiprocessing Queue.

 Blockers: storing self.terminate flag
 Options: a. pass as a reference to func
          b. make consumer an object with that state
Recommendations: b. make consumer an object

Duplicate implementations already exist in dds.py and debug.py
"""

# from queue import Empty
# from time import sleep


# def consumer(self, q: Queue, action: Callable, sleep_time: int):
#     """A method to be run by a thread for consuming the contents of a
#      queue asynchronously
#     """
#     # Loop
#     while not self.terminate_flag:
#         try:
#             page = q.get_nowait()
#             if page is not None:
#                 action(page)
#                 page = q.get_nowait()
#         except Empty:
#             pass
#         sleep(sleep_time)

#     # Remaining lines
#     try:
#         page = q.get_nowait()
#         while page is not None:
#             action(page)
#             page = q.get()
#     except Exception as e:
#         print(f"{e}")
#     return
