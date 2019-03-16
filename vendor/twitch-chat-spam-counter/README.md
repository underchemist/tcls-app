# twitch-chat-spam-counter

Parse Chatty twitch chat logs into a Pandas dataframe. Example usage below:

``` python
> C = ChattyLog('#moonmoon_ow.log')
> C.df.head()
...             timestamp          username                                                 content
   6  2017-11-28 21:13:25     +Mominthetrap                                      D E A D A S S 🅱️
   7  2017-11-28 21:13:25    %+ACTIONMANXVI     gachiBASS Clap gachiBASS Clap gachiBASS Clap g...
   8  2017-11-28 21:13:25       %$andrewcat                                                moon2W
   9  2017-11-28 21:13:26           %+vsnXD                                       D E A D A S S 🅱
   10 2017-11-28 21:13:26  jaredbruiser2099                                           DEAD ASS B
> counter = C.gen_count()
> counter.most_common(15)
... [('moon2MLEM', 12868),
 ('moon2REE', 9492),
 ('moon2SHRUG', 9331),
 ('Clap', 6576),
 ('Jebaited', 4793),
 ('moon2W', 4502),
 ('me', 4322),
 ('gachiBASS', 4291),
 ('🍷', 4097),
 ('FeelsGoodMan', 3780),
 ('SourPls', 3613),
 ('beats', 3476),
 ('LUL', 3094),
 ('Citto', 3016),
 ('PepePls', 2853)]
```

The functionality is pretty basic, but the entire chat log is parsed into the
dataframe from which more sophisticated massaging can be achieved.

By default Chatty logs timestamps with no date. When the parser reads this
into a python datetime format it will prepend your systems current date into
the timestamp. If you want to select time periods to count it is easiest if
you go into Chatty settings and change date format to include full YYYY-MM-DD
date as well as time.



