from twitter import * 
from iorin import Analysis

import re
import key


if __name__ == "__main__":

    tws = TwitterStream(auth=OAuth(
        key.api_key,
        key.api_sec,
        key.auth_key,
        key.auth_sec,
    ),domain='userstream.twitter.com')
    tw = Twitter(auth=OAuth(
        key.api_key,
        key.api_sec,
        key.auth_key,
        key.auth_sec,
    ))

    
    name = re.compile(r"@\w*")
    url  = re.compile(r"https?://[\w/:%#\$&\?\(\)~\.=\+\-]+")
    for msg in tw.statuses.home_timeline(count=200):#screen_name="chino_0x0", count=10):
        text = msg["text"]

        text = text.replace("\n", u"")
        text = name.sub("", text)
        text =  url.sub("", text)
        print(text)

    #a = Analysis()
    #a.analysis()
    #a.finish()


