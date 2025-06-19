import struct
import crc
import numpy as np


class HDLC(object):
    FRAME_BOUNDARY_MARKER = 0x7E
    ESCAPE_MARKER = 0x7D

    STATE_WAITING_FOR_FRAME_MARKER = 0
    STATE_CONSUMING_PAYLOAD = 1

    def __init__(self, max_len=1024):
        self._max_len = max_len

        self._escape_next = False
        self._state = HDLC.STATE_WAITING_FOR_FRAME_MARKER
        self._pending_payload = []

    def parse(self, data: bytes) -> list[bytes]:
        resulting_frames = []

        for c in data:
            if c == HDLC.FRAME_BOUNDARY_MARKER:
                # end frame, check crc
                if len(self._pending_payload) >= 2:
                    computed_crc = self._crcframe(bytes(self._pending_payload[:-2]))
                    packet_crc = struct.unpack(b'<H', bytes(self._pending_payload[-2:]))[0]
                    if computed_crc == packet_crc:
                        # print('valid CRC!')
                        # valid CRC
                        resulting_frames.append(bytes(self._pending_payload[:-2]))
                        self._reset()
                    else:
                        # print('invalid CRC!')
                        # invalid CRC
                        self._reset()
                else:
                    # frame not long enough to contain crc
                    # print('not long enough')
                    self._reset()
            elif c == HDLC.ESCAPE_MARKER:
                self._escape_next = True

            else:
                if self._escape_next:
                    c ^= (1 << 5)
                    self._escape_next = False

                if self._state == self.STATE_CONSUMING_PAYLOAD:
                    self._pending_payload.append(c)

                if len(self._pending_payload) > self._max_len:
                    print('max length exceeded')
                    self._overrun()

        return resulting_frames

    @classmethod
    def encode(cls, payload: bytes) -> bytes:
        if len(payload) > 65536:
            raise ValueError("Maximum length of payload is 65536")

        checksum = HDLC._crcframe(payload)
        checksum = struct.pack(b'<H', checksum)

        replacechars = {
            HDLC.FRAME_BOUNDARY_MARKER: [HDLC.ESCAPE_MARKER, (HDLC.FRAME_BOUNDARY_MARKER ^ 0x20)],
            HDLC.ESCAPE_MARKER:         [HDLC.ESCAPE_MARKER, (HDLC.ESCAPE_MARKER ^ 0x20)],
        }

        def escape(s: bytes):
            out = []
            for c in s:
                if c in replacechars.keys():
                    out.append(HDLC.ESCAPE_MARKER)
                    out.append(c ^ 0x20)
                else:
                    out.append(c)
            return out

        output = [HDLC.FRAME_BOUNDARY_MARKER] + \
            escape(payload) + \
            escape(checksum) + \
            [HDLC.FRAME_BOUNDARY_MARKER]

        return bytes(output)

    def _reset(self):
        self._escape_next = False
        self._pending_payload.clear()
        self._state = HDLC.STATE_CONSUMING_PAYLOAD

    def _overrun(self):
        self._escape_next = False
        self._pending_payload.clear()
        self._state = HDLC.STATE_WAITING_FOR_FRAME_MARKER

    @classmethod
    def _crcframe(self, payload: bytes):
        return crc.Calculator(crc.Crc16.X25).checksum(payload)

