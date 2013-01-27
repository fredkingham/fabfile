#!/usr/bin/python
import sys, os
import logging
from datetime import datetime, date
logger = logging.getLogger(__name__)
import standalone_utils
standalone_utils.setup()
from web_crawler import event_extract

from twitter import twitter_calculation
import time

load_ids = twitter_calculation.get_unprocessed_tweet_ids()

print 'found unprocessed load_ids %s' % load_ids

for load_id in load_ids:
    twitter_calculation.process_tweets()

counter = 0

start_date = date.today()
loaded_for_today = False


while(True):
    logger.info('%s started tweet import' % datetime.utcnow())
    batch_id = twitter_calculation.extract_tweets()
    twitter_calculation.process_tweets()
    logger.info('%s sleeping' % datetime.utcnow())
    time.sleep(300)
    counter += 1

    if start_date != date.today() and not loaded_for_today:
        logger.info("starting pcc load")
        event_extract.pcc_extract()
        logger.info("finished pcc load")

        logger.info("starting national theatre load")
        #event_extract.national_theatre_extract()
        logger.info("finished national theatre load")

        start_date = date.today()
        loaded_for_today = True

