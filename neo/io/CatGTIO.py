from neo.io.basefromrawio import BaseFromRaw
from neo.rawio.catgtrawio import CatGTRawIO
from pathlib import Path

class CatGTIO(CatGTRawIO, BaseFromRaw):
    __doc__ = CatGTRawIO.__doc__
    mode = 'dir'

    def __init__(self, filename, load_sync_channel=False, load_channel_location=False):
        filename = Path(filename)  # TODO: better
        CatGTRawIO.__init__(self, filename=filename,
            load_sync_channel=load_sync_channel,
            load_channel_location=load_channel_location)
        BaseFromRaw.__init__(self, filename)
