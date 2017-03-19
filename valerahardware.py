#!/usr/bin/env python
""" Script used to read data from Valera's hardware and send it ti RRD """

from __future__ import print_function

import os
import logging
import time
import json
import requests


def get_hardware_filename():
    """ Get filename for Valera's hardware """
    files = [x for x in os.listdir("/dev") if x.startswith("ttyUSB")]
    if len(files) > 1:
        raise Exception("more than one USB hardware detected")
    return "/dev/"+files[0]

def main():

    logging.basicConfig(level=logging.INFO)
    counter = 0

    while True:
        try:
            filename = get_hardware_filename()
            logging.info("opening %s", filename)

            with open(filename) as filep:
                while True:
                    line = filep.readline().strip()
                    if line == "":
                        continue

                    if counter == 0:
                        logging.info("skipping first line in %s", filename)
                        counter += 1
                        continue  # first line in output was known to be buggy

                    counter += 1

                    payload = json.loads(line)
                    logging.info("read payload %s", payload)

                    send_data_to_rrd(payload)

        except Exception:
            logging.exception("exception")
            time.sleep(1.0)


def send_data_to_rrd(payload):
    """ Sending data to RRD. Payload should be in JSON """

    try:
        requests.post("http://rrd2.mlan/update/PlatformTemperature",
                      data=payload, timeout=5.0)
        print("{}: sent {}".format(time.asctime(), payload))
    except Exception:
        logging.exception("%s: error while sending %s", time.asctime(),
                          payload)

if __name__ == "__main__":
    main()
