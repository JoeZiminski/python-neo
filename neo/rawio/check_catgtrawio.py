from neo.rawio import SpikeGLXRawIO
from neo.io import SpikeGLXIO

from neo.io import CatGTIO
from neo.rawio.catgtrawio import CatGTRawIO
import numpy as np

file_path = r"D:\data\catgt_1110925_test_shank1_g0\1110925_test_shank1_g0_tcat.imec0.ap.meta"
test_class = CatGTIO(file_path)
data = test_class.get_analogsignal_chunk(
            block_index=0,
            seg_index=0,
            i_start=0,
            i_stop=1000,
            stream_index=0,
            channel_indexes=None,
        )
assert all([ele[4] == "uV" for ele in test_class.header["signal_channels"]])
gains = np.array([ele[5] for ele in test_class.header["signal_channels"]])
offsets = np.array([ele[6] for ele in test_class.header["signal_channels"]])

scaled_data = data * gains[np.newaxis, :] + offsets[np.newaxis, :]
breakpoint()