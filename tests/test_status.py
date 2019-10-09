#!/usr/bin/env python
#
# test_status.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import time

import mock
import pytest

import fsleyes_widgets.utils.status as status


class MockTarget(object):

    def __init__(self):
        self.msg = None

    def __call__(self, msg):
        self.msg = msg


def test_update():

    # Test without a target
    status.setTarget(None)
    status.update('Status')

    target = MockTarget()

    status.setTarget(target)

    assert target.msg is None
    status.update('Status1', None)
    assert target.msg == 'Status1'
    status.update('Status2', None)
    assert target.msg == 'Status2'


def test_update_timeout():

    status.setTarget(None)
    status.clearStatus()

    target = MockTarget()
    status.setTarget(target)

    # Test that the message gets cleared
    status.update('Status1', 0.25)
    assert target.msg == 'Status1'
    time.sleep(0.5)
    assert target.msg == ''

    # If a timed update is followed by an untimed
    # update, the untimed one should persist
    status.update('Status2', 0.25)
    status.update('Status3', None)
    time.sleep(0.5)
    assert target.msg == 'Status3'


def test_clearStatus():
    target = MockTarget()
    status.setTarget(target)

    status.update('Status1', None)
    assert target.msg == 'Status1'
    status.clearStatus()
    assert target.msg == ''

    status.update('Status1', 0.25)
    assert target.msg == 'Status1'
    status.clearStatus()
    assert target.msg == ''


def test_ClearThread_die():
    target = MockTarget()
    status.setTarget(target)

    # make sure the clearthread is running
    status.update('Status1', 1.0)
    time.sleep(1.1)

    # and can be killed
    status._clearThread.die()
    status._clearThread.clear(0.1)
    status._clearThread.join()
    status._clearThread = None

    # and then gets restarted again
    status.update('Status1', 0.25)
    assert target.msg == 'Status1'
    time.sleep(0.5)
    assert target.msg == ''






def test_reportError():

    class MockWX(object):

        ICON_ERROR = 0
        OK         = 2

        def MessageBox(self, msg, title, flags):
            self.msg   = msg
            self.title = title

    class MyException(Exception):
        def __str__(self):
            return 'MyException'

    wx  = MockWX()
    exc = MyException()

    with mock.patch.dict('sys.modules', {'wx' : wx}):
        status.reportError('Error title',
                           'Error message',
                           exc)

    assert wx.title == 'Error title'
    assert wx.msg.startswith('Error message')
    assert wx.msg.endswith(str(exc))

    with mock.patch.dict('sys.modules', {'wx' : None}), \
         mock.patch('fsleyes_widgets.utils.status.log.error') as log:
        status.reportError('Error title', 'Error message', exc)
        log.assert_called_once()


def test_reportIfError_noError():

    with mock.patch('fsleyes_widgets.utils.status.reportError') as func:
        with status.reportIfError('title', 'message'):
            pass
        func.assert_not_called()


def test_reportIfError_error_noraise():

    title = 'title'
    msg   = 'msg'
    exc   = Exception()

    # report=True
    with mock.patch('fsleyes_widgets.utils.status.reportError') as reperr:
        with status.reportIfError(title, msg, raiseError=False):
            raise exc
        reperr.assert_called_once_with(title, msg, exc)

    # report=False
    with mock.patch('fsleyes_widgets.utils.status.reportError') as reperr, \
         mock.patch('fsleyes_widgets.utils.status.log.error') as log:
        with status.reportIfError(title, msg, raiseError=False, report=False):
            raise exc
        reperr.assert_not_called()
        log.assert_called_once()


def test_reportIfError_error_raise():

    title = 'title'
    msg   = 'msg'
    exc   = Exception()

    # report=True
    with mock.patch('fsleyes_widgets.utils.status.reportError') as reperr:
        with pytest.raises(Exception):
            with status.reportIfError(title, msg):
                raise exc
        reperr.assert_called_once_with(title, msg, exc)

    # report=False
    with mock.patch('fsleyes_widgets.utils.status.reportError') as reperr, \
         mock.patch('fsleyes_widgets.utils.status.log.error') as log:

        with pytest.raises(Exception):
            with status.reportIfError(title, msg, report=False):
                raise exc
        reperr.assert_not_called()
        log.assert_called_once()


def test_reportErrorDecorator():

    title = 'title'
    msg   = 'msg'
    exc   = Exception()

    @status.reportErrorDecorator(title, msg)
    def errfunc():
        raise exc

    @status.reportErrorDecorator(title, msg)
    def noerrfunc():
        pass

    with mock.patch('fsleyes_widgets.utils.status.reportError') as reperr:
        noerrfunc()
        reperr.assert_not_called()

    with mock.patch('fsleyes_widgets.utils.status.reportError') as reperr:
        with pytest.raises(Exception):
            errfunc()
        reperr.assert_called_with(title, msg, exc)
