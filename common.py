from telegram import ParseMode
import config

centrale_checksum = lambda barr : bytes([sum([int(x) for x in barr]) % 256])
centrale_append_checksum = lambda barr : barr + centrale_checksum(barr)
centrale_verify_checksum = lambda barr : len(barr) > 0 and barr[-1:] == bytes([sum([int(x) for x in barr[:-1]]) % 256])
increment_byte_array = lambda barr, n : bytearray((int.from_bytes(barr, 'big') + n).to_bytes(7, 'big'))
ck = centrale_append_checksum
code_to_hex = lambda x : b''.join([ bytes([int(x)]) for x in f"{x:05d}" ])

centrale_commands = {
   "auth": b"pass",
   "postauth": ck(b"\x00\x00\x00\xfe\xd2\x00\x02"),
   "getver": ck(b"\x00\x00\x00\x40\x00\x00\x0c"),
   "getstatus": ck(b"\x00\x03\x00\x1f\xfb\xff\x01\x1d"),
   "preactivate": b"\x00\x00\x00\x1f\xf9\x82\x0d\xa7",
   "activate": b"\x01\x00\x00\x20\x0a\x00\x07\x32" + code_to_hex(config.CODE) + b"\xff\x00",
   "predeactivate": b"\x00\x00\x00\x1f\xf9\x80\x0d\xa5",
   "deactivate": b"\x01\x00\x00\x20\x0a\x00\x07\x32" + code_to_hex(config.CODE) + b"\xff\x02",
   "getloggerpos": ck(b"\x00\x00\x00\x1f\xfe\x00\x04"),
   "getevent": lambda n : ck(increment_byte_array(b"\x00\x00\x00\x1f\xff\x00\x00", n))
}

# This is a time offset hardcoded in the SmartLiving firmware
CENTRALE_TIMEOFFSET = 946684800

PMD = ParseMode.MARKDOWN