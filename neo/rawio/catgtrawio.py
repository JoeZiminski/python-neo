from .spikeglxrawio import SpikeGLXRawIO, extract_stream_info, read_meta_file, parse_spikeglx_fname

from .baserawio import (BaseRawIO, _signal_channel_dtype, _signal_stream_dtype,
                _spike_channel_dtype, _event_channel_dtype)
import numpy as np
from pathlib import Path


class CatGTRawIO(SpikeGLXRawIO, BaseRawIO):  # SpikeGLXRawIO
    """
    """
    def __init__(self, filename="", load_sync_channel=False, load_channel_location=False):
        BaseRawIO.__init__(self)

        self.filename = Path(filename)  # TODO: presumably this is entire path
        self.load_sync_channel = load_sync_channel
        self.load_channel_location = load_channel_location

    def _source_name(self):
        return self.filename

    def _parse_header(self):
        """
        TODO:
            1) understand how spikeglx handles the time array. In particular, firstSample. Understand how
               SI handles this problem, in particular _segment_t_start() and _segment_t_stop().
               Determine "deal with nb_segment and t_start/t_stop per segment" and how to implement this here.

            2) understand the scaling logic. Check that the scape per channel are taken correctly as per
               the documentation in spikeglx

           3) determine what filename to get (e.g. .meta, .bin, or both, or filename prior, or all three (all three)

           4) Think how to handle segments. Would we ever want more than 1 segment? Specifically think of
              use cases in the building and the downstream counting uses.

            5) think hard, with reference to new insights on the time axis, as to whether the gates / triggers
               and segments are the same across SI and CatGT. Understand how their input is passed to KS (raw).

        NOTES:

        1) extract_stream_info
            return an object containng, fname, the whole original meta as well as key info extracted (renamed to SI names)
            dict_keys(['fname', 'meta', 'sampling_rate', 'num_chan', 'sample_length', 'gate_num', 'trigger_num', 'device',
                'stream_kind', 'stream_name', 'units', 'channel_names', 'channel_gains', 'channel_offsets',
                'meta_file', 'bin_file', 'seg_index'])
            fname = parse_spikeglx_fname(self.filename)  # just for inspection

        2) gates and triggers are converted to segments in order
            In spikeglxrawio, the segment index are ordered by the gate / trigger number. So
            gate / trigger are not handled explicitly but all gate, trigger are ordered
            as (gate, trigger) and then indexed based on this.  (line ~268)


        """
        self.filename = Path(self.filename)  # TODO: why is this not been converted...

        # read the whole meta file
        meta = read_meta_file(self.filename)  # TODO: dont forget CatGT meta, handle all other filenames

        info = extract_stream_info(self.filename, meta)  # note parse_spikeglx_fname() is called from here.

        info["seg_index"] = 0  # TODO: handle multiple segments
        nb_segment = 1
        info["bin_file"] = self.filename.with_suffix(".bin")

        # create memmap
        self._memmaps = {}
        key = (info['seg_index'], info['stream_name'])  # TODO: only 1 segment at the moment
        data = np.memmap(info['bin_file'], dtype='int16', mode='r', offset=0, order='C')
        # this should be (info['sample_length'], info['num_chan'])
        # be some file are shorten (TODO: check this out)
        data = data.reshape(-1, info['num_chan'])
        assert data.shape == (info['sample_length'], info['num_chan'])  # see above

        self._memmaps[key] = data

        # create channel header
        signal_streams = []
        stream_name = info["stream_name"]
        stream_id = stream_name
        signal_streams.append((stream_name, stream_id))  # TODO: why this?

        # direct copy
        signal_channels = []
        # add channels to global list
        for local_chan in range(info['num_chan']):
            chan_name = info['channel_names'][local_chan]
            chan_id = f'{stream_name}#{chan_name}'
            signal_channels.append((chan_name, chan_id, info['sampling_rate'], 'int16',
                                    info['units'], info['channel_gains'][local_chan],
                                    info['channel_offsets'][local_chan], stream_id))

        if not self.load_sync_channel:
            signal_channels = signal_channels[:-1]

        signal_streams = np.array(signal_streams, dtype=_signal_stream_dtype)
        signal_channels = np.array(signal_channels, dtype=_signal_channel_dtype)

        # No events
        event_channels = []
        event_channels = np.array(event_channels, dtype=_event_channel_dtype)

        # No spikes
        spike_channels = []
        spike_channels = np.array(spike_channels, dtype=_spike_channel_dtype)

        # no need to deal with trigger start / stop here? ##############################

        self.fill_header_dict(nb_segment, signal_streams, signal_channels,
                              spike_channels, event_channels)

# TODO:
# check fname handling [NOT LOADED CORRECTLY
# check how to handle gate/ trigger (new segment?)
# how to handle mutliple segments
# test all metadata entries...
# TODO: check channel gains applied correctly
# really need to understand how spikegldx handles the time axis vs. spikeinterface