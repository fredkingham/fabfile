#!/usr/bin/python
import standalone_utils
standalone_utils.setup()

from notifications import queue_reader

queue_reader.process_queue()


