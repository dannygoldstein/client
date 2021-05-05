#
# -*- coding: utf-8 -*-
"""Internal utility routines.

Collection of classes to support the internal process.

"""

from __future__ import print_function

import logging
import sys
import threading
import time

from six.moves import queue
import wandb


if wandb.TYPE_CHECKING:
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from typing import Tuple, Type, Optional, Union
        from six.moves.queue import Queue
        from wandb.proto.wandb_internal_pb2 import Record, Result
        from threading import Event
        from types import TracebackType

        ExceptionType = Union[
            Tuple[Type[BaseException], BaseException, TracebackType],
            Tuple[None, None, None],
        ]


logger = logging.getLogger(__name__)


class ExceptionThread(threading.Thread):
    """Class to catch exceptions when running a thread."""

    __stopped: "Event"
    __exception: "Optional[ExceptionType]"

    def __init__(self, stopped: "Event") -> None:
        threading.Thread.__init__(self)
        self.__stopped = stopped
        self.__exception = None

    def _run(self) -> None:
        raise NotImplementedError

    def run(self) -> None:
        try:
            self._run()
        except Exception:
            self.__exception = sys.exc_info()
        finally:
            if self.__exception and self.__stopped:
                self.__stopped.set()

    def get_exception(self) -> "Optional[ExceptionType]":
        return self.__exception


class RecordLoopThread(ExceptionThread):
    """Class to manage reading from queues safely."""

    def __init__(
        self,
        input_record_q: "Queue[Record]",
        result_q: "Queue[Result]",
        stopped: "Event",
        debounce_interval_ms: "float" = 1000,
    ) -> None:
        ExceptionThread.__init__(self, stopped=stopped)
        self._input_record_q = input_record_q
        self._result_q = result_q
        self._stopped = stopped
        self._debounce_interval_ms = debounce_interval_ms

    def _setup(self) -> None:
        raise NotImplementedError

    def _process(self, record: "Record") -> None:
        raise NotImplementedError

    def _finish(self) -> None:
        raise NotImplementedError

    def _debounce(self) -> None:
        raise NotImplementedError

    def _run(self) -> None:
        self._setup()
        start = time.time()
        while not self._stopped.is_set():
            if time.time() - start >= self._debounce_interval_ms / 1000.0:
                self._debounce()
            try:
                record = self._input_record_q.get(timeout=1)
            except queue.Empty:
                continue
            self._process(record)
        self._finish()
