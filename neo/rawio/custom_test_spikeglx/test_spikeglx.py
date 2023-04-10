import spikeinterface.extractors as se
import pandas as pd
import numpy as np
from spikeinterface.core import order_channels_by_depth

spikeglx_path = r"D:\data\spike-interface\testing\steve\test_data\spikeglx"
bin_filename = "1110925_test_shank1_g0_t0.imec0.ap.bin"
csv_test_file = r"D:\data\spike-interface\testing\steve\test_data\sec_1_to_5\1110925_test_shank1_g0_t0.exported.imec0.ap.csv"

recording = se.read_spikeglx(spikeglx_path)
test_data = pd.read_csv(csv_test_file, header=None)  # this data is 1 second to 5 seconds of spikeglx data exported as csv from spikeglx
test_data = np.array(test_data, dtype=np.float32) * 1000000
test_data = test_data[:, :384]

fs = recording.get_sampling_frequency()
traces = recording.get_traces(return_scaled=True, start_frame=int(1*fs), end_frame=int(5*fs), order="C")

assert np.allclose(traces,test_data), "spikeglx reader broken"

"""
python-neo>python -m unittest neo/test/rawiotest/test_spikeglxrawio.py
"""

"""
FAILED neo/test/iotest/test_asciisignalio.py::TestAsciiSignalIO::test_csv_expect_success - ValueError: setting an array element with a sequence. The requested array has an inhomogeneous shape after 1 dimensi
ons. The detected shape was (8,) + inhomogeneous part.
FAILED neo/test/utils/test_datasets.py::TestDownloadDataset::test_download_dataset - ModuleNotFoundError: No module named 'datalad'
"""

# https://neo.readthedocs.io/en/stable/developers_guide.html docs are out of date, is .[tests] NOT .[test]
# out of date https://neo-python.readthedocs.io/en/latest/tests.html other docs say use pytest