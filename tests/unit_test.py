# vim: set fileencoding=utf8 :
import binascii
import datetime
import decimal
import struct
import unittest
import uuid
import pytest

import OpenSSL.crypto

import pytds
from pytds.collate import raw_collation
from pytds.tds import (
    _TdsSocket, _TdsSession, Collation,
    )
from pytds import _TdsLogin
from pytds.tds_base import (
    TDS_ENCRYPTION_REQUIRE, Column, TDS70, TDS73, TDS71, TDS72, TDS73, TDS74,
    TDS_ENCRYPTION_OFF, PreLoginEnc)
from pytds.tds_types import DateTimeSerializer, DateTime, DateTime2Type, DateType, TimeType, DateTimeOffsetType, IntType, \
    BigIntType, TinyIntType, SmallIntType, VarChar72Serializer, XmlSerializer, Text72Serializer, NText72Serializer, \
    Image72Serializer, MoneyNSerializer, VariantSerializer, BitType, DeclarationsParser, SmallDateTimeType, DateTimeType, \
    ImageType, VarBinaryType, VarBinaryMaxType, SmallMoneyType, MoneyType, DecimalType, UniqueIdentifierType, \
    VariantType, BinaryType, RealType, FloatType, CharType, VarCharType, VarCharMaxType, NCharType, NVarCharType, \
    NVarCharMaxType, TextType, NTextType
from pytds.tds_types import (
    BitNSerializer,
    TdsTypeInferrer, SerializerFactory, NVarChar72Serializer, IntNSerializer, MsDecimalSerializer, FloatNSerializer, VarBinarySerializerMax, NVarCharMaxSerializer, VarCharMaxSerializer, DateTime2Serializer,
    DateTimeOffsetSerializer, MsDateSerializer, MsTimeSerializer, MsUniqueSerializer, NVarChar71Serializer, Image70Serializer, NText71Serializer, Text71Serializer, DateTimeNSerializer, NVarChar70Serializer,
    NText70Serializer, Text70Serializer, VarBinarySerializer, VarBinarySerializer72,
    )

tzoffset = pytds.tz.FixedOffsetTimezone


class _FakeSock(object):
    def __init__(self, messages):
        self._stream = b''.join(messages)

    def recv(self, size):
        if not self._stream:
            return b''
        res = self._stream[:size]
        self._stream = self._stream[size:]
        return res

    def send(self, buf, flags):
        self._sent = buf
        return len(buf)

    def sendall(self, buf, flags):
        self._sent = buf

    def setsockopt(self, *args):
        pass

    def close(self):
        self._stream = b''


class TestMessages(unittest.TestCase):
    def _make_login(self):
        from pytds.tds_base import TDS74
        login = _TdsLogin()
        login.blocksize = 4096
        login.use_tz = None
        login.query_timeout = login.connect_timeout = 60
        login.tds_version = TDS74
        login.instance_name = None
        login.enc_flag = PreLoginEnc.ENCRYPT_NOT_SUP
        login.use_mars = False
        login.option_flag2 = 0
        login.user_name = 'testname'
        login.password = 'password'
        login.app_name = 'appname'
        login.server_name = 'servername'
        login.library = 'library'
        login.language = 'EN'
        login.database = 'database'
        login.auth = None
        login.bulk_copy = False
        login.readonly = False
        login.client_lcid = 100
        login.attach_db_file = ''
        login.text_size = 0
        login.client_host_name = 'clienthost'
        login.pid = 100
        login.change_password = ''
        login.client_tz = tzoffset(5)
        login.client_id = 0xabcd
        login.bytes_to_unicode = True
        return login

    def test_login(self):
        sock = _FakeSock([
            b'\x04\x01\x00+\x00\x00\x01\x00\x00\x00\x1a\x00\x06\x01\x00 \x00\x01\x02\x00!\x00\x01\x03\x00"\x00\x00\x04\x00"\x00\x01\xff\n\x00\x15\x88\x00\x00\x02\x00\x00',
            b"\x04\x01\x01\xad\x00Z\x01\x00\xe3/\x00\x01\x10S\x00u\x00b\x00m\x00i\x00s\x00s\x00i\x00o\x00n\x00P\x00o\x00r\x00t\x00a\x00l\x00\x06m\x00a\x00s\x00t\x00e\x00r\x00\xab~\x00E\x16\x00\x00\x02\x00/\x00C\x00h\x00a\x00n\x00g\x00e\x00d\x00 \x00d\x00a\x00t\x00a\x00b\x00a\x00s\x00e\x00 \x00c\x00o\x00n\x00t\x00e\x00x\x00t\x00 \x00t\x00o\x00 \x00'\x00S\x00u\x00b\x00m\x00i\x00s\x00s\x00i\x00o\x00n\x00P\x00o\x00r\x00t\x00a\x00l\x00'\x00.\x00\tM\x00S\x00S\x00Q\x00L\x00H\x00V\x003\x000\x00\x00\x01\x00\x00\x00\xe3\x08\x00\x07\x05\t\x04\x00\x01\x00\x00\xe3\x17\x00\x02\nu\x00s\x00_\x00e\x00n\x00g\x00l\x00i\x00s\x00h\x00\x00\xabn\x00G\x16\x00\x00\x01\x00'\x00C\x00h\x00a\x00n\x00g\x00e\x00d\x00 \x00l\x00a\x00n\x00g\x00u\x00a\x00g\x00e\x00 \x00s\x00e\x00t\x00t\x00i\x00n\x00g\x00 \x00t\x00o\x00 \x00u\x00s\x00_\x00e\x00n\x00g\x00l\x00i\x00s\x00h\x00.\x00\tM\x00S\x00S\x00Q\x00L\x00H\x00V\x003\x000\x00\x00\x01\x00\x00\x00\xad6\x00\x01s\x0b\x00\x03\x16M\x00i\x00c\x00r\x00o\x00s\x00o\x00f\x00t\x00 \x00S\x00Q\x00L\x00 \x00S\x00e\x00r\x00v\x00e\x00r\x00\x00\x00\x00\x00\n\x00\x15\x88\xe3\x13\x00\x04\x044\x000\x009\x006\x00\x044\x000\x009\x006\x00\xfd\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
            b'\x04\x01\x00#\x00Z\x01\x00\xe3\x0b\x00\x08\x08\x01\x00\x00\x00Z\x00\x00\x00\x00\xfd\x00\x00\xfd\x00\x00\x00\x00\x00\x00\x00\x00\x00',
        ])
        _TdsSocket().login(self._make_login(), sock, None)

        # test connection close on first message
        sock = _FakeSock([
            b'\x04\x01\x00+\x00',
        ])
        with self.assertRaises(pytds.Error):
            _TdsSocket().login(self._make_login(), sock, None)

        # test connection close on second message
        sock = _FakeSock([
            b'\x04\x01\x00+\x00\x00\x01\x00\x00\x00\x1a\x00\x06\x01\x00 \x00\x01\x02\x00!\x00\x01\x03\x00"\x00\x00\x04\x00"\x00\x01\xff\n\x00\x15\x88\x00\x00\x02\x00\x00',
            b"\x04\x01\x01\xad\x00Z\x01\x00\xe3/\x00\x01\x10S",
        ])
        with self.assertRaises(pytds.Error):
            _TdsSocket().login(self._make_login(), sock, None)

        # test connection close on third message
        sock = _FakeSock([
            b'\x04\x01\x00+\x00\x00\x01\x00\x00\x00\x1a\x00\x06\x01\x00 \x00\x01\x02\x00!\x00\x01\x03\x00"\x00\x00\x04\x00"\x00\x01\xff\n\x00\x15\x88\x00\x00\x02\x00\x00',
            b"\x04\x01\x01\xad\x00Z\x01\x00\xe3/\x00\x01\x10S\x00u\x00b\x00m\x00i\x00s\x00s\x00i\x00o\x00n\x00P\x00o\x00r\x00t\x00a\x00l\x00\x06m\x00a\x00s\x00t\x00e\x00r\x00\xab~\x00E\x16\x00\x00\x02\x00/\x00C\x00h\x00a\x00n\x00g\x00e\x00d\x00 \x00d\x00a\x00t\x00a\x00b\x00a\x00s\x00e\x00 \x00c\x00o\x00n\x00t\x00e\x00x\x00t\x00 \x00t\x00o\x00 \x00'\x00S\x00u\x00b\x00m\x00i\x00s\x00s\x00i\x00o\x00n\x00P\x00o\x00r\x00t\x00a\x00l\x00'\x00.\x00\tM\x00S\x00S\x00Q\x00L\x00H\x00V\x003\x000\x00\x00\x01\x00\x00\x00\xe3\x08\x00\x07\x05\t\x04\x00\x01\x00\x00\xe3\x17\x00\x02\nu\x00s\x00_\x00e\x00n\x00g\x00l\x00i\x00s\x00h\x00\x00\xabn\x00G\x16\x00\x00\x01\x00'\x00C\x00h\x00a\x00n\x00g\x00e\x00d\x00 \x00l\x00a\x00n\x00g\x00u\x00a\x00g\x00e\x00 \x00s\x00e\x00t\x00t\x00i\x00n\x00g\x00 \x00t\x00o\x00 \x00u\x00s\x00_\x00e\x00n\x00g\x00l\x00i\x00s\x00h\x00.\x00\tM\x00S\x00S\x00Q\x00L\x00H\x00V\x003\x000\x00\x00\x01\x00\x00\x00\xad6\x00\x01s\x0b\x00\x03\x16M\x00i\x00c\x00r\x00o\x00s\x00o\x00f\x00t\x00 \x00S\x00Q\x00L\x00 \x00S\x00e\x00r\x00v\x00e\x00r\x00\x00\x00\x00\x00\n\x00\x15\x88\xe3\x13\x00\x04\x044\x000\x009\x006\x00\x044\x000\x009\x006\x00\xfd\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
            b'\x04\x01\x00#\x00Z\x01\x00\xe3\x0b\x00\x08\x08\x01\x00\x00\x00Z\x00\x00\x00\x00\xfd\x00\x00\xfd\x00\x00',
        ])
        with self.assertRaises(pytds.Error):
            _TdsSocket().login(self._make_login(), sock, None)

    def test_prelogin_parsing(self):
        # test good packet
        sock = _FakeSock([
            b'\x04\x01\x00+\x00\x00\x01\x00\x00\x00\x1a\x00\x06\x01\x00 \x00\x01\x02\x00!\x00\x01\x03\x00"\x00\x00\x04\x00"\x00\x01\xff\n\x00\x15\x88\x00\x00\x02\x00\x00',
        ])
        tds = _TdsSocket()
        tds._main_session = _TdsSession(tds, tds, None)
        tds.sock = sock
        login = _TdsLogin()
        login.enc_flag = PreLoginEnc.ENCRYPT_NOT_SUP
        tds._main_session.process_prelogin(login)
        self.assertFalse(tds._mars_enabled)
        self.assertTupleEqual(tds.server_library_version, (0xa001588, 0))

        # test bad packet type
        sock = _FakeSock([
            b'\x03\x01\x00+\x00\x00\x01\x00\x00\x00\x1a\x00\x06\x01\x00 \x00\x01\x02\x00!\x00\x01\x03\x00"\x00\x00\x04\x00"\x00\x01\xff\n\x00\x15\x88\x00\x00\x02\x00\x00',
        ])
        tds = _TdsSocket()
        tds._main_session = _TdsSession(tds, tds, None)
        tds.sock = sock
        with self.assertRaises(pytds.InterfaceError):
            login = self._make_login()
            tds._main_session.process_prelogin(login)

        # test bad offset 1
        sock = _FakeSock([
            b'\x04\x01\x00+\x00\x00\x01\x00\x00\x00\x1a\x00\x06\x01\x00 \x00\x01\x02\x00!\x00\x01\x03\x00"\x00\x00\x04\x00"\x00\x01\x00\n\x00\x15\x88\x00\x00\x02\x00\x00',
        ])
        tds = _TdsSocket()
        tds._main_session = _TdsSession(tds, tds, None)
        tds.sock = sock
        with self.assertRaises(pytds.InterfaceError):
            login = self._make_login()
            tds._main_session.process_prelogin(login)

        # test bad offset 2
        sock = _FakeSock([
            b'\x04\x01\x00+\x00\x00\x01\x00\x00\x00\x1a\x00\x06\x01\x00 \x00\x01\x02\x00!\x00\x01\x03\x00"\x00\x00\x04\x00"\x00\x01\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00',
        ])
        tds = _TdsSocket()
        tds._main_session = _TdsSession(tds, tds, None)
        tds.sock = sock
        with self.assertRaises(pytds.InterfaceError):
            login = self._make_login()
            tds._main_session.process_prelogin(login)

    def test_prelogin_generation(self):
        sock = _FakeSock('')
        tds = _TdsSocket()
        tds._main_session = _TdsSession(tds, tds, None)
        tds.sock = sock
        login = _TdsLogin()
        login.instance_name = 'MSSQLServer'
        login.enc_flag = PreLoginEnc.ENCRYPT_NOT_SUP
        login.use_mars = False
        tds._main_session.send_prelogin(login)
        template = (b'\x12\x01\x00:\x00\x00\x00\x00\x00\x00' +
                    b'\x1a\x00\x06\x01\x00 \x00\x01\x02\x00!\x00\x0c\x03' +
                    b'\x00-\x00\x04\x04\x001\x00\x01\xff' + struct.pack('>l', pytds.intversion) +
                    b'\x00\x00\x02MSSQLServer\x00\x00\x00\x00\x00\x00')
        self.assertEqual(sock._sent, template)

        login.instance_name = 'x' * 65499
        sock._sent = b''
        with self.assertRaisesRegexp(ValueError, 'Instance name is too long'):
            tds._main_session.send_prelogin(login)
        self.assertEqual(sock._sent, b'')

        login.instance_name = u'тест'
        with self.assertRaises(UnicodeEncodeError):
            tds._main_session.send_prelogin(login)
        self.assertEqual(sock._sent, b'')

    def test_login_parsing(self):
        sock = _FakeSock([
            b"\x04\x01\x01\xad\x00Z\x01\x00\xe3/\x00\x01\x10S\x00u\x00b\x00m\x00i\x00s\x00s\x00i\x00o\x00n\x00P\x00o\x00r\x00t\x00a\x00l\x00\x06m\x00a\x00s\x00t\x00e\x00r\x00\xab~\x00E\x16\x00\x00\x02\x00/\x00C\x00h\x00a\x00n\x00g\x00e\x00d\x00 \x00d\x00a\x00t\x00a\x00b\x00a\x00s\x00e\x00 \x00c\x00o\x00n\x00t\x00e\x00x\x00t\x00 \x00t\x00o\x00 \x00'\x00S\x00u\x00b\x00m\x00i\x00s\x00s\x00i\x00o\x00n\x00P\x00o\x00r\x00t\x00a\x00l\x00'\x00.\x00\tM\x00S\x00S\x00Q\x00L\x00H\x00V\x003\x000\x00\x00\x01\x00\x00\x00\xe3\x08\x00\x07\x05\t\x04\x00\x01\x00\x00\xe3\x17\x00\x02\nu\x00s\x00_\x00e\x00n\x00g\x00l\x00i\x00s\x00h\x00\x00\xabn\x00G\x16\x00\x00\x01\x00'\x00C\x00h\x00a\x00n\x00g\x00e\x00d\x00 \x00l\x00a\x00n\x00g\x00u\x00a\x00g\x00e\x00 \x00s\x00e\x00t\x00t\x00i\x00n\x00g\x00 \x00t\x00o\x00 \x00u\x00s\x00_\x00e\x00n\x00g\x00l\x00i\x00s\x00h\x00.\x00\tM\x00S\x00S\x00Q\x00L\x00H\x00V\x003\x000\x00\x00\x01\x00\x00\x00\xad6\x00\x01s\x0b\x00\x03\x16M\x00i\x00c\x00r\x00o\x00s\x00o\x00f\x00t\x00 \x00S\x00Q\x00L\x00 \x00S\x00e\x00r\x00v\x00e\x00r\x00\x00\x00\x00\x00\n\x00\x15\x88\xe3\x13\x00\x04\x044\x000\x009\x006\x00\x044\x000\x009\x006\x00\xfd\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
        ])
        tds = _TdsSocket()
        tds._main_session = _TdsSession(tds, tds, None)
        tds.sock = sock
        tds._main_session.process_login_tokens()

        # test invalid tds version
        sock = _FakeSock([
            b"\x04\x01\x01\xad\x00Z\x01\x00\xe3/\x00\x01\x10S\x00u\x00b\x00m\x00i\x00s\x00s\x00i\x00o\x00n\x00P\x00o\x00r\x00t\x00a\x00l\x00\x06m\x00a\x00s\x00t\x00e\x00r\x00\xab~\x00E\x16\x00\x00\x02\x00/\x00C\x00h\x00a\x00n\x00g\x00e\x00d\x00 \x00d\x00a\x00t\x00a\x00b\x00a\x00s\x00e\x00 \x00c\x00o\x00n\x00t\x00e\x00x\x00t\x00 \x00t\x00o\x00 \x00'\x00S\x00u\x00b\x00m\x00i\x00s\x00s\x00i\x00o\x00n\x00P\x00o\x00r\x00t\x00a\x00l\x00'\x00.\x00\tM\x00S\x00S\x00Q\x00L\x00H\x00V\x003\x000\x00\x00\x01\x00\x00\x00\xe3\x08\x00\x07\x05\t\x04\x00\x01\x00\x00\xe3\x17\x00\x02\nu\x00s\x00_\x00e\x00n\x00g\x00l\x00i\x00s\x00h\x00\x00\xabn\x00G\x16\x00\x00\x01\x00'\x00C\x00h\x00a\x00n\x00g\x00e\x00d\x00 \x00l\x00a\x00n\x00g\x00u\x00a\x00g\x00e\x00 \x00s\x00e\x00t\x00t\x00i\x00n\x00g\x00 \x00t\x00o\x00 \x00u\x00s\x00_\x00e\x00n\x00g\x00l\x00i\x00s\x00h\x00.\x00\tM\x00S\x00S\x00Q\x00L\x00H\x00V\x003\x000\x00\x00\x01\x00\x00\x00\xad6\x00\x01\x65\x0b\x00\x03\x16M\x00i\x00c\x00r\x00o\x00s\x00o\x00f\x00t\x00 \x00S\x00Q\x00L\x00 \x00S\x00e\x00r\x00v\x00e\x00r\x00\x00\x00\x00\x00\n\x00\x15\x88\xe3\x13\x00\x04\x044\x000\x009\x006\x00\x044\x000\x009\x006\x00\xfd\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
        ])
        tds = _TdsSocket()
        tds._main_session = _TdsSession(tds, tds, None)
        tds.sock = sock
        with self.assertRaises(pytds.InterfaceError):
            tds._main_session.process_login_tokens()

        # test for invalid env type
        sock = _FakeSock([
            b"\x04\x01\x01\xad\x00Z\x01\x00\xe3/\x00\x01\x10S\x00u\x00b\x00m\x00i\x00s\x00s\x00i\x00o\x00n\x00P\x00o\x00r\x00t\x00a\x00l\x00\x06m\x00a\x00s\x00t\x00e\x00r\x00\xab~\x00E\x16\x00\x00\x02\x00/\x00C\x00h\x00a\x00n\x00g\x00e\x00d\x00 \x00d\x00a\x00t\x00a\x00b\x00a\x00s\x00e\x00 \x00c\x00o\x00n\x00t\x00e\x00x\x00t\x00 \x00t\x00o\x00 \x00'\x00S\x00u\x00b\x00m\x00i\x00s\x00s\x00i\x00o\x00n\x00P\x00o\x00r\x00t\x00a\x00l\x00'\x00.\x00\tM\x00S\x00S\x00Q\x00L\x00H\x00V\x003\x000\x00\x00\x01\x00\x00\x00\xe3\x08\x00\xab\x05\t\x04\x00\x01\x00\x00\xe3\x17\x00\x02\nu\x00s\x00_\x00e\x00n\x00g\x00l\x00i\x00s\x00h\x00\x00\xabn\x00G\x16\x00\x00\x01\x00'\x00C\x00h\x00a\x00n\x00g\x00e\x00d\x00 \x00l\x00a\x00n\x00g\x00u\x00a\x00g\x00e\x00 \x00s\x00e\x00t\x00t\x00i\x00n\x00g\x00 \x00t\x00o\x00 \x00u\x00s\x00_\x00e\x00n\x00g\x00l\x00i\x00s\x00h\x00.\x00\tM\x00S\x00S\x00Q\x00L\x00H\x00V\x003\x000\x00\x00\x01\x00\x00\x00\xad6\x00\x01s\x0b\x00\x03\x16M\x00i\x00c\x00r\x00o\x00s\x00o\x00f\x00t\x00 \x00S\x00Q\x00L\x00 \x00S\x00e\x00r\x00v\x00e\x00r\x00\x00\x00\x00\x00\n\x00\x15\x88\xe3\x13\x00\x04\x044\x000\x009\x006\x00\x044\x000\x009\x006\x00\xfd\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
        ])
        tds = _TdsSocket()
        tds._main_session = _TdsSession(tds, tds, None)
        tds.sock = sock
        tds._main_session.process_login_tokens()

    def test_login_generation(self):
        sock = _FakeSock(b'')
        tds = _TdsSocket()
        tds._main_session = _TdsSession(tds, tds, None)
        tds.sock = sock
        login = _TdsLogin()
        login.option_flag2 = 0
        login.user_name = 'test'
        login.password = 'testpwd'
        login.app_name = 'appname'
        login.server_name = 'servername'
        login.library = 'library'
        login.language = 'en'
        login.database = 'database'
        login.auth = None
        login.tds_version = TDS73
        login.bulk_copy = True
        login.client_lcid = 0x204
        login.attach_db_file = 'filepath'
        login.readonly = False
        login.client_host_name = 'subdev1'
        login.pid = 100
        login.change_password = ''
        login.client_tz = tzoffset(-4 * 60)
        login.client_id = 0x1234567890ab
        tds._main_session.tds7_send_login(login)
        self.assertEqual(
            sock._sent,
            b'\x10\x01\x00\xde\x00\x00\x00\x00' +  # header
            b'\xc6\x00\x00\x00' +  # size
            b'\x03\x00\ns' +  # tds version
            b'\x00\x10\x00\x00' +  # buf size
            struct.pack('<l', pytds.intversion) +
            b'd\x00\x00\x00' +  # pid
            b'\x00\x00\x00\x00' +  # connection id of primary server (whatever that means)
            b'\xe0\x00\x00\x08' +  # flags
            b'\x10\xff\xff\xff' +  # client tz
            b'\x04\x02\x00\x00' +  # client lcid
            b'^\x00\x07\x00l\x00\x04\x00t\x00\x07\x00\x82\x00\x07\x00\x90\x00\n\x00\x00\x00\x00\x00\xa4\x00\x07' +
            b'\x00\xb2\x00\x02\x00\xb6\x00\x08\x00' +
            b'\x12\x34\x56\x78\x90\xab' +
            b'\xc6\x00\x00' +
            b'\x00\xc6\x00\x08\x00\xd6\x00\x00\x00\x00\x00\x00\x00' +
            b's\x00u\x00b\x00d\x00e\x00v\x001\x00' +
            b't\x00e\x00s\x00t\x00' +
            b'\xe2\xa5\xf3\xa5\x92\xa5\xe2\xa5\xa2\xa5\xd2\xa5\xe3\xa5' +
            b'a\x00p\x00p\x00n\x00a\x00m\x00e\x00' +
            b's\x00e\x00r\x00v\x00e\x00r\x00n\x00a\x00m\x00e\x00' +
            b'l\x00i\x00b\x00r\x00a\x00r\x00y\x00' +
            b'e\x00n\x00' +
            b'd\x00a\x00t\x00a\x00b\x00a\x00s\x00e\x00' +
            b'f\x00i\x00l\x00e\x00p\x00a\x00t\x00h\x00')

        login.tds_version = TDS71
        tds._main_session.tds7_send_login(login)
        self.assertEqual(
            binascii.hexlify(bytes(sock._sent)),
            b'100100de00000100' +
            b'c6000000' +
            b'00000071' +
            b'00100000' +
            binascii.hexlify(struct.pack('<l', pytds.intversion)) +
            b'6400000000000000e000000810ffffff040200005e0007006c000400740007008200070090000a0000000000a4000700b' +
            b'2000200b60008001234567890abc6000000c6000800d60000000000000073007500620064006500760031007400650073' +
            b'007400e2a5f3a592a5e2a5a2a5d2a5e3a56100700070006e0061006d0065007300650072007600650072006e0061006d0' +
            b'065006c0069006200720061007200790065006e0064006100740061006200610073006500660069006c00650070006100' +
            b'74006800')
        sock._sent = b''
        login.user_name = 'x' * 129
        with self.assertRaisesRegexp(ValueError, 'User name should be no longer that 128 characters'):
            tds._main_session.tds7_send_login(login)
        self.assertEqual(sock._sent, b'')

        login.user_name = 'username'
        login.password = 'x' * 129
        with self.assertRaisesRegexp(ValueError, 'Password should be not longer than 128 characters'):
            tds._main_session.tds7_send_login(login)
        self.assertEqual(sock._sent, b'')

        login.password = 'password'
        login.client_host_name = 'x' * 129
        with self.assertRaisesRegexp(ValueError, 'Host name should be not longer than 128 characters'):
            tds._main_session.tds7_send_login(login)
        self.assertEqual(sock._sent, b'')

        login.client_host_name = 'clienthost'
        login.app_name = 'x' * 129
        with self.assertRaisesRegexp(ValueError, 'App name should be not longer than 128 characters'):
            tds._main_session.tds7_send_login(login)
        self.assertEqual(sock._sent, b'')

        login.app_name = 'appname'
        login.server_name = 'x' * 129
        with self.assertRaisesRegexp(ValueError, 'Server name should be not longer than 128 characters'):
            tds._main_session.tds7_send_login(login)
        self.assertEqual(sock._sent, b'')

        login.server_name = 'servername'
        login.database = 'x' * 129
        with self.assertRaisesRegexp(ValueError, 'Database name should be not longer than 128 characters'):
            tds._main_session.tds7_send_login(login)
        self.assertEqual(sock._sent, b'')

        login.database = 'database'
        login.language = 'x' * 129
        with self.assertRaisesRegexp(ValueError, 'Language should be not longer than 128 characters'):
            tds._main_session.tds7_send_login(login)
        self.assertEqual(sock._sent, b'')

        login.language = 'en'
        login.change_password = 'x' * 129
        with self.assertRaisesRegexp(ValueError, 'Password should be not longer than 128 characters'):
            tds._main_session.tds7_send_login(login)
        self.assertEqual(sock._sent, b'')

        login.change_password = ''
        login.attach_db_file = 'x' * 261
        with self.assertRaisesRegexp(ValueError, 'File path should be not longer than 260 characters'):
            tds._main_session.tds7_send_login(login)
        self.assertEqual(sock._sent, b'')

    def test_submit_plain_query(self):
        tds = _TdsSocket()
        tds.tds_version = TDS72
        tds._main_session = _TdsSession(tds, tds, None)
        sock = _FakeSock(b'')
        tds.sock = sock
        tds._main_session.submit_plain_query('select 5*6')
        self.assertEqual(
            sock._sent,
            b'\x01\x01\x002\x00\x00\x00\x00' +
            b'\x16\x00\x00\x00\x12\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00' +
            b's\x00e\x00l\x00e\x00c\x00t\x00 \x005\x00*\x006\x00')

        # test pre TDS7.2 query
        tds = _TdsSocket()
        tds.tds_version = TDS71
        tds._main_session = _TdsSession(tds, tds, None)
        tds.sock = sock
        tds._main_session.submit_plain_query('select 5*6')
        self.assertEqual(
            sock._sent,
            b'\x01\x01\x00\x1c\x00\x00\x00\x00' +
            b's\x00e\x00l\x00e\x00c\x00t\x00 \x005\x00*\x006\x00')

    def test_bulk_insert(self):
        tds = _TdsSocket()
        tds.tds_version = TDS72
        tds._main_session = _TdsSession(tds, tds, None)
        sock = _FakeSock(b'')
        tds.sock = sock
        col1 = Column()
        col1.column_name = 'c1'
        col1.type = BitType()
        col1.flags = Column.fNullable | Column.fReadWrite
        metadata = [col1]
        tds._main_session.submit_bulk(metadata, [(False,)])
        self.assertEqual(
            binascii.hexlify(bytes(sock._sent)),
            binascii.hexlify(
                b'\x07'  # type - TDS_BULK
                b'\x01'  # status - 1 = EOM (end of message)
                b'\x00\x28'  # size (big endian)
                b'\x00\x00'  # spid, should be 0 when sent from client (big endian)
                b'\x00'  # packetid, currently ignored
                b'\x00'  # window, should be 0
                b'\x81'  # RESULT TOKEN
                b'\x01\x00'  # num columns (little endian)
                b'\x00\x00\x00\x00'  # column user type
                b'\x09\x00'  # column flags
                b'\x68'  # column type - SYBBITN
                b'\x01'  # type size
                b'\x02'  # column name len in chars
                b'c\x001\x00'  # utf16 column name
                b'\xd1'  # TDS_ROW_TOKEN
                b'\x01'  # type size
                b'\x00'  # value 0 - false
                b'\xfd'  # tokey type: TDS_DONE_TOKEN
                b'\x00\x00'  # status: TDS_DONE_FINAL
                b'\x00\x00'  # curcmd
                b'\x00\x00\x00\x00\x00\x00\x00\x00'  # row count
            ),
        )

    def test_types(self):
        tds = _TdsSocket()
        tds.tds_version = TDS72
        tds._main_session = _TdsSession(tds, tds, None)
        sock = _FakeSock(b'')
        tds.sock = sock
        w = tds._main_session._writer

        t = pytds.tds_types.NVarCharMaxSerializer(
            Collation(lcid=1033, sort_id=0, ignore_case=False, ignore_accent=False, ignore_width=False,
                      ignore_kana=False, binary=True, binary2=False, version=0),
        )
        t.write_info(w)
        self.assertEqual(w._buf[:w._pos], b'\xff\xff\t\x04\x00\x01\x00')

        w._pos = 0
        t.write(w, 'test')
        self.assertEqual(w._buf[:w._pos],
                         b'\x08\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00t\x00e\x00s\x00t\x00\x00\x00\x00\x00')

    def test_get_instances(self):
        data = b'\x05[\x00ServerName;MISHA-PC;InstanceName;SQLEXPRESS;IsClustered;No;Version;10.0.1600.22;tcp;49849;;'
        ref = {'SQLEXPRESS': {'ServerName': 'MISHA-PC',
                              'InstanceName': 'SQLEXPRESS',
                              'IsClustered': 'No',
                              'Version': '10.0.1600.22',
                              'tcp': '49849',
                              },
               }
        instances = pytds.tds._parse_instances(data)
        self.assertDictEqual(ref, instances)


class ConnectionStringTestCase(unittest.TestCase):
    def test_parsing(self):
        res = pytds._parse_connection_string(
            'Server=myServerAddress;Database=myDataBase;User Id=myUsername; Password=myPassword;')
        self.assertEqual({'server': 'myServerAddress',
                          'database': 'myDataBase',
                          'user_id': 'myUsername',
                          'password': 'myPassword'},
                         res)

        res = pytds._parse_connection_string('Server=myServerAddress;Database=myDataBase;Trusted_Connection=True;')
        self.assertEqual({'server': 'myServerAddress',
                          'database': 'myDataBase',
                          'trusted_connection': 'True',
                          },
                         res)

        res = pytds._parse_connection_string(
            'Server=myServerName\\myInstanceName;Database=myDataBase;User Id=myUsername; Password=myPassword;')
        self.assertEqual({'server': 'myServerName\\myInstanceName',
                          'database': 'myDataBase',
                          'user_id': 'myUsername',
                          'password': 'myPassword',
                          },
                         res)


def infer_tds_serializer(value, serializer_factory, collation=None, bytes_to_unicode=True, allow_tz=True):
    inferrer = TdsTypeInferrer(
        type_factory=serializer_factory,
        collation=collation,
        bytes_to_unicode=bytes_to_unicode,
        allow_tz=allow_tz,
    )
    sql_type = inferrer.from_value(value)
    return serializer_factory.serializer_by_type(sql_type)


class TypeInferenceTestCase(unittest.TestCase):
    def test_tds74(self):
        factory = SerializerFactory(TDS74)

        # None should infer as NVarChar72
        res = infer_tds_serializer(None, serializer_factory=factory)
        self.assertIsInstance(res, NVarChar72Serializer)

        # bool should infer as Bit
        res = infer_tds_serializer(True, serializer_factory=factory)
        self.assertIsInstance(res, BitNSerializer)

        # small integers inferred as IntN(4)
        res = infer_tds_serializer(100, serializer_factory=factory)
        self.assertEqual(res, IntNSerializer(IntType()))

        # big integers inferred as IntN(8)
        res = infer_tds_serializer(6000000000, serializer_factory=factory)
        self.assertEqual(res, IntNSerializer(BigIntType()))

        # even bigger integers inferred as MsDecimal
        res = infer_tds_serializer(600000000000000000000, serializer_factory=factory)
        self.assertEqual(res, MsDecimalSerializer(scale=0, precision=38))

        res = infer_tds_serializer(0.25, serializer_factory=factory)
        self.assertEqual(res, FloatNSerializer(8))

        res = infer_tds_serializer(pytds.Binary(b'abc'), serializer_factory=factory)
        self.assertEqual(res, VarBinarySerializer72(8000))

        res = infer_tds_serializer(pytds.Binary(b'a' * 8001), serializer_factory=factory)
        self.assertEqual(res, VarBinarySerializerMax())

        res = infer_tds_serializer(b'abc', serializer_factory=factory, bytes_to_unicode=True, collation=raw_collation)
        self.assertEqual(res, NVarCharMaxSerializer(collation=raw_collation))

        res = infer_tds_serializer(b'abc', serializer_factory=factory, bytes_to_unicode=False, collation=raw_collation)
        self.assertEqual(res, VarCharMaxSerializer(collation=raw_collation))

        res = infer_tds_serializer(u'abc', serializer_factory=factory, collation=raw_collation)
        self.assertEqual(res, NVarCharMaxSerializer(collation=raw_collation))

        dt = datetime.datetime.now()
        dt = dt.replace(tzinfo=tzoffset(0))
        res = infer_tds_serializer(dt, serializer_factory=factory, allow_tz=False)
        self.assertEqual(res, DateTime2Serializer(DateTime2Type(precision=6)))

        dt = datetime.datetime.now()
        dt = dt.replace(tzinfo=tzoffset(0))
        res = infer_tds_serializer(dt, serializer_factory=factory, allow_tz=True)
        self.assertEqual(res, DateTimeOffsetSerializer(DateTimeOffsetType(precision=6)))

        d = datetime.date.today()
        res = infer_tds_serializer(d, serializer_factory=factory)
        self.assertEqual(res, MsDateSerializer(DateType()))

        t = datetime.time()
        res = infer_tds_serializer(t, serializer_factory=factory)
        self.assertEqual(res, MsTimeSerializer(TimeType(precision=6)))

        dec = decimal.Decimal()
        res = infer_tds_serializer(dec, serializer_factory=factory)
        self.assertEqual(res, MsDecimalSerializer(scale=0, precision=1))

        res = infer_tds_serializer(uuid.uuid4(), serializer_factory=factory)
        self.assertEqual(res, MsUniqueSerializer())

    def test_tds73(self):
        factory = SerializerFactory(TDS73)

        # None should infer as NVarChar72
        res = infer_tds_serializer(None, serializer_factory=factory)
        self.assertIsInstance(res, NVarChar72Serializer)

        # bool should infer as Bit
        res = infer_tds_serializer(True, serializer_factory=factory)
        self.assertIsInstance(res, BitNSerializer)

        # small integers inferred as IntN(4)
        res = infer_tds_serializer(100, serializer_factory=factory)
        self.assertEqual(res, IntNSerializer(IntType()))

        # big integers inferred as IntN(8)
        res = infer_tds_serializer(6000000000, serializer_factory=factory)
        self.assertEqual(res, IntNSerializer(BigIntType()))

        # even bigger integers inferred as MsDecimal
        res = infer_tds_serializer(600000000000000000000, serializer_factory=factory)
        self.assertEqual(res, MsDecimalSerializer(scale=0, precision=38))

        res = infer_tds_serializer(0.25, serializer_factory=factory)
        self.assertEqual(res, FloatNSerializer(8))

        res = infer_tds_serializer(pytds.Binary(b'abc'), serializer_factory=factory)
        self.assertEqual(res, VarBinarySerializer72(8000))

        res = infer_tds_serializer(pytds.Binary(b'a' * 8001), serializer_factory=factory)
        self.assertEqual(res, VarBinarySerializerMax())

        res = infer_tds_serializer(b'abc', serializer_factory=factory, bytes_to_unicode=True, collation=raw_collation)
        self.assertEqual(res, NVarCharMaxSerializer())

        res = infer_tds_serializer(b'abc', serializer_factory=factory, bytes_to_unicode=False, collation=raw_collation)
        self.assertEqual(res, VarCharMaxSerializer(collation=raw_collation))

        res = infer_tds_serializer(u'abc', serializer_factory=factory, collation=raw_collation)
        self.assertEqual(res, NVarCharMaxSerializer())

        dt = datetime.datetime.now()
        dt = dt.replace(tzinfo=tzoffset(0))
        res = infer_tds_serializer(dt, serializer_factory=factory, allow_tz=False)
        self.assertEqual(res, DateTime2Serializer(DateTime2Type(precision=6)))

        dt = datetime.datetime.now()
        dt = dt.replace(tzinfo=tzoffset(0))
        res = infer_tds_serializer(dt, serializer_factory=factory, allow_tz=True)
        self.assertEqual(res, DateTimeOffsetSerializer(DateTimeOffsetType(precision=6)))

        d = datetime.date.today()
        res = infer_tds_serializer(d, serializer_factory=factory)
        self.assertEqual(res, MsDateSerializer(DateType()))

        t = datetime.time()
        res = infer_tds_serializer(t, serializer_factory=factory)
        self.assertEqual(res, MsTimeSerializer(TimeType(precision=6)))

        dec = decimal.Decimal()
        res = infer_tds_serializer(dec, serializer_factory=factory)
        self.assertEqual(res, MsDecimalSerializer(scale=0, precision=1))

        res = infer_tds_serializer(uuid.uuid4(), serializer_factory=factory)
        self.assertEqual(res, MsUniqueSerializer())

    def test_tds72(self):
        factory = SerializerFactory(TDS72)

        # None should infer as NVarChar72
        res = infer_tds_serializer(None, serializer_factory=factory)
        self.assertIsInstance(res, NVarChar72Serializer)

        # bool should infer as Bit
        res = infer_tds_serializer(True, serializer_factory=factory)
        self.assertIsInstance(res, BitNSerializer)

        # small integers inferred as IntN(4)
        res = infer_tds_serializer(100, serializer_factory=factory)
        self.assertEqual(res, IntNSerializer(IntType()))

        # big integers inferred as IntN(8)
        res = infer_tds_serializer(6000000000, serializer_factory=factory)
        self.assertEqual(res, IntNSerializer(BigIntType()))

        # even bigger integers inferred as MsDecimal
        res = infer_tds_serializer(600000000000000000000, serializer_factory=factory)
        self.assertEqual(res, MsDecimalSerializer(scale=0, precision=38))

        res = infer_tds_serializer(0.25, serializer_factory=factory)
        self.assertEqual(res, FloatNSerializer(8))

        res = infer_tds_serializer(pytds.Binary(b'abc'), serializer_factory=factory)
        self.assertEqual(res, VarBinarySerializer72(8000))

        res = infer_tds_serializer(pytds.Binary(b'a' * 8001), serializer_factory=factory)
        self.assertEqual(res, VarBinarySerializerMax())

        res = infer_tds_serializer(b'abc', serializer_factory=factory, bytes_to_unicode=True, collation=raw_collation)
        self.assertEqual(res, NVarCharMaxSerializer())

        res = infer_tds_serializer(b'abc', serializer_factory=factory, bytes_to_unicode=False, collation=raw_collation)
        self.assertEqual(res, VarCharMaxSerializer())

        res = infer_tds_serializer(u'abc', serializer_factory=factory, collation=raw_collation)
        self.assertEqual(res, NVarCharMaxSerializer())

        dt = datetime.datetime.now()
        dt = dt.replace(tzinfo=tzoffset(0))
        res = infer_tds_serializer(dt, serializer_factory=factory, allow_tz=False)
        self.assertEqual(res, DateTime2Serializer(DateTime2Type(precision=6)))

        dt = datetime.datetime.now()
        dt = dt.replace(tzinfo=tzoffset(0))
        res = infer_tds_serializer(dt, serializer_factory=factory, allow_tz=True)
        self.assertEqual(res, DateTimeOffsetSerializer(DateTimeOffsetType(precision=6)))

        d = datetime.date.today()
        res = infer_tds_serializer(d, serializer_factory=factory)
        self.assertEqual(res, MsDateSerializer(DateType()))

        t = datetime.time()
        res = infer_tds_serializer(t, serializer_factory=factory)
        self.assertEqual(res, MsTimeSerializer(TimeType(precision=6)))

        dec = decimal.Decimal()
        res = infer_tds_serializer(dec, serializer_factory=factory)
        self.assertEqual(res, MsDecimalSerializer(scale=0, precision=1))

        res = infer_tds_serializer(uuid.uuid4(), serializer_factory=factory)
        self.assertEqual(res, MsUniqueSerializer())

    def test_tds71(self):
        factory = SerializerFactory(TDS71)

        # None should infer as NVarChar72
        res = infer_tds_serializer(None, serializer_factory=factory)
        self.assertIsInstance(res, NVarChar71Serializer)

        # bool should infer as Bit
        res = infer_tds_serializer(True, serializer_factory=factory)
        self.assertIsInstance(res, BitNSerializer)

        # small integers inferred as IntN(4)
        res = infer_tds_serializer(100, serializer_factory=factory)
        self.assertEqual(res, IntNSerializer(IntType()))

        # big integers inferred as IntN(8)
        res = infer_tds_serializer(6000000000, serializer_factory=factory)
        self.assertEqual(res, IntNSerializer(BigIntType()))

        # even bigger integers inferred as MsDecimal
        res = infer_tds_serializer(600000000000000000000, serializer_factory=factory)
        self.assertEqual(res, MsDecimalSerializer(scale=0, precision=38))

        res = infer_tds_serializer(0.25, serializer_factory=factory)
        self.assertEqual(res, FloatNSerializer(8))

        res = infer_tds_serializer(pytds.Binary(b'abc'), serializer_factory=factory)
        self.assertEqual(res, VarBinarySerializer(8000))

        res = infer_tds_serializer(pytds.Binary(b'a' * 8001), serializer_factory=factory)
        self.assertEqual(res, Image70Serializer())

        res = infer_tds_serializer(b'abc', serializer_factory=factory, bytes_to_unicode=True, collation=raw_collation)
        self.assertEqual(res, NText71Serializer(collation=raw_collation))

        res = infer_tds_serializer(b'abc', serializer_factory=factory, bytes_to_unicode=False, collation=raw_collation)
        self.assertEqual(res, Text71Serializer(collation=raw_collation))

        res = infer_tds_serializer(u'abc', serializer_factory=factory, collation=raw_collation)
        self.assertEqual(res, NText71Serializer(collation=raw_collation))

        dt = datetime.datetime.now()
        dt = dt.replace(tzinfo=tzoffset(0))
        res = infer_tds_serializer(dt, serializer_factory=factory, allow_tz=False)
        self.assertEqual(res, DateTimeNSerializer(8))

        dt = datetime.datetime.now()
        dt = dt.replace(tzinfo=tzoffset(0))
        with self.assertRaises(pytds.DataError):
            infer_tds_serializer(dt, serializer_factory=factory, allow_tz=True)

        d = datetime.date.today()
        res = infer_tds_serializer(d, serializer_factory=factory)
        self.assertEqual(res, DateTimeNSerializer(8))

        t = datetime.time()
        with self.assertRaises(pytds.DataError):
            infer_tds_serializer(t, serializer_factory=factory)

        dec = decimal.Decimal()
        res = infer_tds_serializer(dec, serializer_factory=factory)
        self.assertEqual(res, MsDecimalSerializer(scale=0, precision=1))

        res = infer_tds_serializer(uuid.uuid4(), serializer_factory=factory)
        self.assertEqual(res, MsUniqueSerializer())

    def test_tds70(self):
        factory = SerializerFactory(TDS70)

        # None should infer as NVarChar70
        res = infer_tds_serializer(None, serializer_factory=factory)
        self.assertIsInstance(res, NVarChar70Serializer)

        # bool should infer as Bit
        res = infer_tds_serializer(True, serializer_factory=factory)
        self.assertIsInstance(res, BitNSerializer)

        # small integers inferred as IntN(4)
        res = infer_tds_serializer(100, serializer_factory=factory)
        self.assertEqual(res, IntNSerializer(IntType()))

        # big integers inferred as IntN(8)
        res = infer_tds_serializer(6000000000, serializer_factory=factory)
        self.assertEqual(res, IntNSerializer(BigIntType()))

        # even bigger integers inferred as MsDecimal
        res = infer_tds_serializer(600000000000000000000, serializer_factory=factory)
        self.assertEqual(res, MsDecimalSerializer(scale=0, precision=38))

        res = infer_tds_serializer(0.25, serializer_factory=factory)
        self.assertEqual(res, FloatNSerializer(8))

        res = infer_tds_serializer(pytds.Binary(b'abc'), serializer_factory=factory)
        self.assertEqual(res, VarBinarySerializer(8000))

        res = infer_tds_serializer(pytds.Binary(b'a' * 8001), serializer_factory=factory)
        self.assertEqual(res, Image70Serializer())

        res = infer_tds_serializer(b'abc', serializer_factory=factory, bytes_to_unicode=True, collation=raw_collation)
        self.assertEqual(res, NText70Serializer())

        res = infer_tds_serializer(b'abc', serializer_factory=factory, bytes_to_unicode=False, collation=raw_collation)
        self.assertEqual(res, Text70Serializer())

        res = infer_tds_serializer(u'abc', serializer_factory=factory, collation=raw_collation)
        self.assertEqual(res, NText70Serializer())

        dt = datetime.datetime.now()
        dt = dt.replace(tzinfo=tzoffset(0))
        res = infer_tds_serializer(dt, serializer_factory=factory, allow_tz=False)
        self.assertEqual(res, DateTimeNSerializer(8))

        dt = datetime.datetime.now()
        dt = dt.replace(tzinfo=tzoffset(0))
        with self.assertRaises(pytds.DataError):
            infer_tds_serializer(dt, serializer_factory=factory, allow_tz=True)

        d = datetime.date.today()
        res = infer_tds_serializer(d, serializer_factory=factory)
        self.assertEqual(res, DateTimeNSerializer(8))

        t = datetime.time()
        with self.assertRaises(pytds.DataError):
            infer_tds_serializer(t, serializer_factory=factory)

        dec = decimal.Decimal()
        res = infer_tds_serializer(dec, serializer_factory=factory)
        self.assertEqual(res, MsDecimalSerializer(scale=0, precision=1))

        res = infer_tds_serializer(uuid.uuid4(), serializer_factory=factory)
        self.assertEqual(res, MsUniqueSerializer())

    def test_tvp(self):
        def rows_gen():
            yield (1, 'test1')
            yield (2, 'test2')

        factory = SerializerFactory(TDS74)
        tvp = pytds.TableValuedParam(type_name='dbo.CategoryTableType', rows=rows_gen())
        res = infer_tds_serializer(tvp, serializer_factory=factory, collation=raw_collation)
        self.assertEqual(res.table_type.typ_schema, 'dbo')
        self.assertEqual(res.table_type.typ_name, 'CategoryTableType')
        self.assertEqual(list(tvp.rows), list(rows_gen()))
        self.assertEqual(res.table_type.columns, [Column(type=IntType()),
                                                  Column(type=NVarCharMaxType())])

    def test_null_tvp(self):
        factory = SerializerFactory(TDS74)
        tvp = pytds.TableValuedParam(type_name='dbo.CategoryTableType')
        self.assertTrue(tvp.is_null())
        res = infer_tds_serializer(tvp, serializer_factory=factory, collation=raw_collation)
        self.assertEqual(res.table_type.typ_schema, 'dbo')
        self.assertEqual(res.table_type.typ_name, 'CategoryTableType')
        self.assertEqual(tvp.rows, None)
        self.assertEqual(res.table_type.columns, None)
        self.assertTrue(tvp.is_null())

    def test_nested_tvp(self):
        """
        Nested TVPs are not allowed by TDS
        """
        factory = SerializerFactory(TDS74)
        inner_tvp = pytds.TableValuedParam(type_name='dbo.InnerTVP', rows=[(1,)])
        tvp = pytds.TableValuedParam(type_name='dbo.OuterTVP', rows=[(inner_tvp,)])
        with self.assertRaisesRegexp(pytds.DataError, 'TVP type cannot have nested TVP types'):
            infer_tds_serializer(tvp, serializer_factory=factory)

    def test_invalid_tvp(self):
        factory = SerializerFactory(TDS74)
        tvp = pytds.TableValuedParam(type_name='dbo.OuterTVP', rows=[])
        with self.assertRaisesRegexp(pytds.DataError, 'Cannot infer columns from rows for TVP because there are no rows'):
            infer_tds_serializer(tvp, serializer_factory=factory)

        tvp = pytds.TableValuedParam(type_name='dbo.OuterTVP', rows=5)
        with self.assertRaisesRegexp(pytds.DataError, 'rows should be iterable'):
            infer_tds_serializer(tvp, serializer_factory=factory)

        tvp = pytds.TableValuedParam(type_name='dbo.OuterTVP', rows=[None])
        with self.assertRaisesRegexp(pytds.DataError, 'Each row in table should be an iterable'):
            infer_tds_serializer(tvp, serializer_factory=factory)

        # too many columns
        tvp = pytds.TableValuedParam(type_name='dbo.OuterTVP', rows=[[1] * 1025])
        with self.assertRaisesRegexp(ValueError, 'TVP cannot have more than 1024 columns'):
            infer_tds_serializer(tvp, serializer_factory=factory)

        # too few columns
        tvp = pytds.TableValuedParam(type_name='dbo.OuterTVP', rows=[[]])
        with self.assertRaisesRegexp(ValueError, 'TVP must have at least one column'):
            infer_tds_serializer(tvp, serializer_factory=factory)

        with self.assertRaisesRegexp(ValueError, 'Schema part of TVP name should be no longer than 128 characters'):
            tvp = pytds.TableValuedParam(type_name=('x' * 129) + '.OuterTVP', rows=[[]])
            infer_tds_serializer(tvp, serializer_factory=factory)

        with self.assertRaisesRegexp(ValueError, 'Name part of TVP name should be no longer than 128 characters'):
            tvp = pytds.TableValuedParam(type_name='dbo.' + ('x' * 129), rows=[[]])
            infer_tds_serializer(tvp, serializer_factory=factory)


class DeclarationParsingTestCase(unittest.TestCase):
    def test_serializer_by_declaration(self):
        test_data = [
            ('bit', BitNSerializer(BitType())),
            ('tinyint', IntNSerializer(TinyIntType())),
            ('smallint', IntNSerializer(SmallIntType())),
            ('int', IntNSerializer(IntType())),
            ('bigint', IntNSerializer(BigIntType())),
            ('varchar(10)', VarChar72Serializer(size=10, collation=raw_collation)),
            ('varchar(max)', VarCharMaxSerializer(collation=raw_collation)),
            ('nvarchar(10)', NVarChar72Serializer(size=10, collation=raw_collation)),
            ('nvarchar(max)', NVarCharMaxSerializer(collation=raw_collation)),
            ('xml', XmlSerializer()),
            ('text', Text72Serializer()),
            ('ntext', NText72Serializer()),
            ('varbinary(10)', VarBinarySerializer72(10)),
            ('varbinary(max)', VarBinarySerializerMax()),
            ('image', Image72Serializer()),
            ('smalldatetime', DateTimeNSerializer(size=4)),
            ('datetime', DateTimeNSerializer(size=8)),
            ('date', MsDateSerializer(DateType())),
            #('time', MsTimeSerializer(TimeType(precision=7))),
            ('time(7)', MsTimeSerializer(TimeType(precision=7))),
            ('datetime2', DateTime2Serializer(DateTime2Type(precision=7))),
            ('datetime2(7)', DateTime2Serializer(DateTime2Type(precision=7))),
            ('datetimeoffset', DateTimeOffsetSerializer(DateTimeOffsetType(precision=7))),
            ('datetimeoffset(7)', DateTimeOffsetSerializer(DateTimeOffsetType(precision=7))),
            ('decimal', MsDecimalSerializer()),
            ('decimal(10, 2)', MsDecimalSerializer(scale=2, precision=10)),
            ('smallmoney', MoneyNSerializer(size=4)),
            ('money', MoneyNSerializer(size=8)),
            ('uniqueidentifier', MsUniqueSerializer()),
            ('sql_variant', VariantSerializer(size=0)),
        ]
        p = SerializerFactory(TDS74)

        class FakeConn(object):
            def __init__(self):
                self.collation = raw_collation

        fake_conn = FakeConn()

        for decl, expected_res in test_data:
            ser = p.serializer_by_declaration(decl, fake_conn)
            msg = 'Test for declaration {} failed, expected {} actual {}'.format(decl, expected_res, ser)
            self.assertEqual(ser, expected_res, msg)

    def test_declaration_parser(self):
        test_data = [
            ('bit', BitType()),
            ('\n BIT\t ', BitType()),

            ('tinyint', TinyIntType()),
            ('smallint', SmallIntType()),
            ('int', IntType()),
            ('integer', IntType()),
            ('bigint', BigIntType()),

            ('real', RealType()),
            ('float', FloatType()),
            ('double precision', FloatType()),

            ('char', CharType(size=30)),
            ('character', CharType(size=30)),
            ('char(10)', CharType(size=10)),
            ('character(10)', CharType(size=10)),

            ('varchar', VarCharType(size=30)),
            ('varchar(10)', VarCharType(size=10)),
            ('char varying(10)', VarCharType(size=10)),
            ('character varying(10)', VarCharType(size=10)),
            ('varchar(max)', VarCharMaxType()),

            ('nchar', NCharType(size=30)),
            ('nchar(10)', NCharType(size=10)),
            ('national char(10)', NCharType(size=10)),
            ('national character(10)', NCharType(size=10)),

            ('nvarchar', NVarCharType(size=30)),
            ('nvarchar(10)', NVarCharType(size=10)),
            ('national char varying(10)', NVarCharType(size=10)),
            ('national character varying(10)', NVarCharType(size=10)),

            ('nvarchar(max)', NVarCharMaxType()),

            #('xml', XmlSerializer()),

            ('text', TextType()),
            ('ntext', NTextType()),
            ('national text', NTextType()),

            ('binary', BinaryType(30)),
            ('binary(10)', BinaryType(10)),
            ('varbinary', VarBinaryType(30)),
            ('binary varying', VarBinaryType(30)),
            ('varbinary(10)', VarBinaryType(10)),
            ('binary varying(10)', VarBinaryType(10)),
            ('varbinary(max)', VarBinaryMaxType()),
            ('image', ImageType()),
            ('smalldatetime', SmallDateTimeType()),
            ('datetime', DateTimeType()),
            ('date', DateType()),
            ('time', TimeType(precision=7)),
            ('time(6)', TimeType(precision=6)),
            ('datetime2', DateTime2Type(precision=7)),
            ('datetime2(5)', DateTime2Type(precision=5)),
            ('datetimeoffset', DateTimeOffsetType(precision=7)),
            ('datetimeoffset(4)', DateTimeOffsetType(precision=4)),
            ('dec', DecimalType(precision=18, scale=0)),
            ('decimal', DecimalType(precision=18, scale=0)),
            ('decimal(10)', DecimalType(precision=10, scale=0)),
            ('decimal(10, 2)', DecimalType(precision=10, scale=2)),
            ('dec(10, 2)', DecimalType(precision=10, scale=2)),
            ('numeric', DecimalType(precision=18, scale=0)),
            ('numeric(10, 2)', DecimalType(precision=10, scale=2)),
            ('smallmoney', SmallMoneyType()),
            ('money', MoneyType()),
            ('uniqueidentifier', UniqueIdentifierType()),
            ('sql_variant', VariantType()),
        ]
        parser = DeclarationsParser()
        for decl, expected_res in test_data:
            actual_res = parser.parse(decl)
            msg = 'Incorrect result for declaration {} expected {} got {}'.format(decl, expected_res, actual_res)
            self.assertEqual(actual_res,
                             expected_res,
                             msg)


class MiscTestCase(unittest.TestCase):
    def test_datetime_serializer(self):
        self.assertEqual(DateTimeSerializer.decode(*DateTimeSerializer._struct.unpack(b'\xf2\x9c\x00\x00}uO\x01')),
                         pytds.Timestamp(2010, 1, 2, 20, 21, 22, 123000))
        self.assertEqual(DateTimeSerializer.decode(*DateTimeSerializer._struct.unpack(b'\x7f$-\x00\xff\x81\x8b\x01')),
                         DateTime.MAX_PYDATETIME)
        self.assertEqual(b'\xf2\x9c\x00\x00}uO\x01', DateTimeSerializer.encode(
            pytds.Timestamp(2010, 1, 2, 20, 21, 22, 123000)))
        self.assertEqual(b'\x7f$-\x00\xff\x81\x8b\x01', DateTimeSerializer.encode(DateTime.MAX_PYDATETIME))


def test_with_simple_server():
    import sys
    if sys.version_info[0:2] < (3, 6):
        # only works on Python 3.6 and newer
        return

    import simple_server
    import utils
    import threading
    from cryptography import x509
    address = ('127.0.0.1', 1433)
    test_ca = utils.TestCA()
    server_key = test_ca.key('server')
    subject = x509.Name(
        [x509.NameAttribute(
            x509.oid.NameOID.COMMON_NAME, address[0]
        )]
    )
    builder = x509.CertificateBuilder()
    server_cert = test_ca.sign(name='server', cb=builder.subject_name(subject)
        .not_valid_before(datetime.datetime.utcnow())
        .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=1))
        .serial_number(x509.random_serial_number())
        .public_key(server_key.public_key()))
    root_ca_path = test_ca.cert_path('root')
    server = simple_server.SimpleServer(
        address,
        enc=PreLoginEnc.ENCRYPT_ON,
        cert=OpenSSL.crypto.X509.from_cryptography(server_cert),
        pkey=OpenSSL.crypto.PKey.from_cryptography_key(server_key)
    )
    server_thread = threading.Thread(target=lambda: server.serve_forever())
    server_thread.start()
    try:
        # test with both server and client configured for encryption
        #with pytds.connect(
        #        dsn=address[0],
        #        port=address[1],
        #        user="sa",
        #        password='password',
        #        cafile=root_ca_path,
        #        disable_connect_retry=True,
        #) as conn:
        #    pass

        # test with server having encrypt on but client has it off
        # should throw exception in this case
        with pytest.raises(pytds.Error) as excinfo:
            pytds.connect(
                dsn=address[0],
                port=address[1],
                user="sa",
                password='password',
                disable_connect_retry=True,
                )
        assert 'not have encryption enabled but it is required by server' in str(excinfo.value)
    finally:
        server.shutdown()
        server_thread.join()

