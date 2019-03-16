import pandas as pd
import os
from collections import Counter
import warnings


class ChatLog:

    """
    Parser and basic manipulator class for reading plaintext twitch chat log
    files.

    Supported file formats: utf-8 encoded, space-delimited csv files. Files
    must have a timestamp, username, and message field in that order.
        - timestamp: Doesn't have to include an absolute date, whatever the
          current date is will be pre-pended to the time. Optional to be
          enclosed by  [ ] characters.
        - username: The username must be enclosed by < > characters.
        - message: No special formatting required for message content, as long
          as it is utf-8 encoded or can be easily converted.

    Attributes
    ----------
    chat : pandas.DataFrame
        Pandas.DataFrame Parsed logfile with 3 column names: timestamp,
        username, and message. NaN values are replaced with empty strings,
        extraneous chat info is stripped as well (log open and close lines,
        mod announcements and bans).
    fname : str
        Filename of chat log.
    raw : list
        Unprocessed log file, read into a list of str.

    """

    def __init__(self, logfile, rechat_flag=False):
        self.fname = os.path.basename(logfile)
        with open(logfile, 'r', encoding='utf-8-sig') as f:
            raw_contents = f.readlines()
        self.raw = raw_contents
        try:
            if rechat_flag:
                self.chat = self._rechattool_output_to_dataframe(raw_contents)
            else:
                self.chat = self.to_dataframe(self.raw)
        except:
            raise InvalidFileFormat(f'{self.fname} is not a valid chat log format. See ChatLog docstring for supported file formats')

    def _rechattool_output_to_dataframe(self, raw_contents):
        s = pd.Series(raw_contents)
        df = s.str.split(' ', n=2, expand=True)
        df.columns = ['timestamp', 'username', 'message']
        df['timestamp'] = pd.to_datetime(df['timestamp'].str.strip('[]'))
        df['username'] = df['username'].str.strip(':')
        df['message'] = df['message'].str.strip('\n').fillna('')

        return df

    def to_dataframe(self, raw_contents):
        """
        Parse file buffer into pandas DataFrame

        Parameters
        ----------
        raw_contents : list
            Raw output of logfile file buffer. No processing has been done at
            this point. Read in with utf-8 encoding to best deal with variety
            of characters.

        Returns
        -------
        df : pandas.DataFrame Parsed logfile with 3 column names: timestamp,
            username, and content. NaN values are replaced with empty strings,
            extraneous chat info is stripped as well (log open and close
            lines, mod announcements and bans.)
        """
        warnings.filterwarnings("ignore", 'This pattern has match groups')

        s = pd.Series(raw_contents)
        s2 = s[s.str.contains('<(.*?)>')]
        df = s2.str.split('\s<(.*?)>.?\s', n=1, expand=True)
        df.columns = ['timestamp', 'username', 'message']
        df['timestamp'] = df['timestamp'].str.strip('[]')
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['message'] = df['message'].str.strip('\n')
        df['message'] = df['message'].fillna('')  # strip NaN values if exist

        return df

    def gen_counter(self, df=None, split_words=False):
        """
        Generate Counter object from pandas series of twitch chat messages.

        Parameters
        ----------
        df : {None, pandas.Series}, optional
            Series containing chat messages. If parameter is left blank will
            default to the 'content' column of the instances dataframe (i.e.
            df['content']).

        split_words : Boolean, optional
            If true, will split each chat message into single words using
            whitespace as delimiter. Can be useful if you're only interested
            in single word spam like emotes. Default value is False.

        Returns
        -------
        out : collections.Counter
            Counter object from python collections module, using your
            dataframe input.
        """
        if df is None:
            words = self.chat['message']
        else:
            words = df

        if split_words:
            words = words.str.split()
            words = [w for sublist in words for w in sublist]

        return Counter(words)

    def poglul_ratio(self):
        C = self.gen_counter(split_words=True)
        pog = C.get('PogChamp')
        lul = C.get('LUL')
        return (pog, lul, pog / lul)

    def top_spam(self, n=10):
        C = self.gen_counter()
        return C.most_common(n)


class InvalidFileFormat(Exception):
    pass
