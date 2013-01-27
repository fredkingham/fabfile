from hotqueue import HotQueue
import settings, sys, traceback
queue = HotQueue(settings.QUEUE_NAME)
from notifications import queue_writer, mail_calculation
import logging
logger = logging.getLogger(__name__)

def process_queue():
    for item in queue.consume():
        try:
            args = item.get("args", [])
            kwargs = item.get("kwargs", {})

            if item["obj_type"] == queue_writer.NOTIFICATION:
                mail_calculation.notify(item["args"])
        except:
            level = 6
            error_type, error_value, trbk = sys.exc_info()
            tb_list = traceback.format_tb(trbk, level)    
            s = "Error: %s \nDescription: %s \nTraceback:" % (error_type.__name__, error_value)
            for i in tb_list:
                s += "\n" + i
            logger.error('the error is: %s with %s from %s' % (error_type, error_value, s))

