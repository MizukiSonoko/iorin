from  twitter import *

from saiorin import Generate

import daemon.runner
from datetime import datetime
import os
import sys
import time
import random

import key

class IorinDaemon:

    def __init__(self):

        self.tws = TwitterStream(auth=OAuth(
            key.api_key,
            key.api_sec,
            key.auth_key,
            key.auth_sec,
        ),domain='userstream.twitter.com')
        self.tw = Twitter(auth=OAuth(
            key.api_key,
            key.api_sec,
            key.auth_key,
            key.auth_sec,
	    ))

        self.g = Generate()

        print("[start] Set up Iorin! Hello!")


    def run(self):
        print("[log] Running")
        interval = 60
        time_start = time_old = time_new = int(time.time() / interval)        
        
        while True:
            time_new = int(time.time() / interval)
            if time_old != time_new:
                time_old = time_new
                
                say = self.g.say()
                print("[say] "+say)
                self.tw.statuses.update(status= say + "  ")
                
                i = random.randint(0, 4)
                if i == 0:
                    time.sleep(253)
                elif i == 1:
                    time.sleep(327)
                elif i == 2:
                    time.sleep(426)
                else:
                    time.sleep(120)


    def update_name(self, name):
        self.tw.account.update_profile(name=name)


def main():
    d = IorinDaemon()
    d.run()

if __name__ == '__main__':
	main()


