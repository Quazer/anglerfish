#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Anglerfish."""


import atexit
import logging
import os
import sys
import signal
import zipfile

from logging.handlers import TimedRotatingFileHandler
from copy import copy
from datetime import datetime
from tempfile import gettempdir

try:
    import resource
except ImportError:
    resource = None  # MS Window dont have resource


__version__ = '0.5.0'
__license__ = ' GPLv3+ LGPLv3+ '
__author__ = ' Juan Carlos '
__email__ = ' juancarlospaco@gmail.com '
__url__ = 'https://github.com/juancarlospaco/anglerfish'
__all__ = [
    "make_logger", "check_encoding", "check_folder", "get_clipboard",
    "get_sanitized_string", "beep", "json_pretty", "log_exception",
    "multiprocessed", "threads", "make_post_exec_msg", "retry",
    "typecheck", "walk2list", "watch", "set_desktop_launcher",
    "set_process_name", "set_single_instance", "get_temp_folder",
    "set_terminal_title", "bytes2human", "walk2dict", "seconds2human",
    "env2globals", "html2ebook", "TemplatePython", "pdb_on_exception",
    "ipdb_on_exception", "about_python", "about_self", "view_code",
    "report_bug", "get_config_folder", "make_config", "view_config",
    "save_config", "delete_config", "backup_config", "CONFIG",
    "start_time"
]


sys.dont_write_bytecode = True
CONFIG, start_time = None, datetime.now()
signal.signal(signal.SIGINT, signal.SIG_DFL)


def __zip_old_logs(log_file, single_zip):
    zip_file, filename = log_file + "s-old.zip", os.path.basename(log_file)
    log.debug("ZIP Compressing Unused Old Rotated Logs.")
    comment = "Compressed Unused Old Rotated Logs since ~{}.".format(
        datetime.now().isoformat()[:-7])
    logs = [os.path.join(os.path.dirname(log_file), _)
            for _ in os.listdir(os.path.dirname(log_file))
            if ".log." in _ and not _.endswith(".zip") and filename in _]
    if single_zip:  # If 1 ZIP for all Logs, put all *.log inside 1 *.zip
        with zipfile.ZipFile(zip_file, 'a', zipfile.ZIP_DEFLATED) as log_zip:
            log_zip.debug = 3  # Log ZIP inner working,and comment with time
            log_zip.comment = bytes(comment, encoding="utf-8")  # add a comment
            for fyle in logs:
                try:
                    log_zip.write(fyle, os.path.basename(fyle))
                    os.remove(fyle)
                except:
                    pass
            log_zip.printdir()
    else:  # If not 1 ZIP, put 1 *.log inside 1 *.zip, multiple zips
        for fyle in logs:
            newzip = fyle + ".zip"
            with zipfile.ZipFile(newzip, 'w', zipfile.ZIP_DEFLATED) as log_zip:
                log_zip.debug = 3  # Log ZIP inner working
                log_zip.comment = bytes(comment, encoding="utf-8")
                try:
                    log_zip.write(fyle, os.path.basename(fyle))
                    os.remove(fyle)
                except:
                    pass
                # log_zip.printdir()
    result = zip_file if single_zip else tuple([_ + ".zip" for _ in logs])
    log.debug(result)
    return result


def make_logger(name, when='midnight', single_zip=False):
    """Build and return a Logging Logger."""
    global log
    log_file = os.path.join(gettempdir(), str(name).lower().strip() + ".log")
    atexit.register(__zip_old_logs, log_file, single_zip)  # ZIP Old Logs
    hand = TimedRotatingFileHandler(log_file, when=when,
                                    backupCount=999, encoding="utf-8")
    hand.setLevel(-1)
    _fmt = ("%(asctime)s %(levelname)s: "
            "%(processName)s (%(process)d) %(threadName)s (%(thread)d) "
            "%(name)s.%(funcName)s: %(message)s %(pathname)s:%(lineno)d")
    hand.setFormatter(logging.Formatter(fmt=_fmt, datefmt="%Y-%m-%d %H:%M:%S"))
    log = logging.getLogger()
    log.addHandler(hand)
    log.setLevel(-1)
    if not sys.platform.startswith("win") and sys.stderr.isatty():
        log.debug("Enabled Colored Logs on current Terminal.")

        def add_color_emit_ansi(fn):
            """Add methods we need to the class."""
            def new(*args):
                """Method overload."""
                if len(args) == 2:
                    new_args = (args[0], copy(args[1]))
                else:
                    new_args = (args[0], copy(args[1]), args[2:])
                if hasattr(args[0], 'baseFilename'):
                    return fn(*args)
                levelno = new_args[1].levelno
                if levelno >= 50:
                    color = '\x1b[31;5;7m\n '  # blinking red with black
                elif levelno >= 40:
                    color = '\x1b[31m'  # red
                elif levelno >= 30:
                    color = '\x1b[33m'  # yellow
                elif levelno >= 20:
                    color = '\x1b[32m'  # green
                elif levelno >= 10:
                    color = '\x1b[35m'  # pink
                else:
                    color = '\x1b[0m'  # normal
                try:
                    new_args[1].msg = color + str(new_args[1].msg) + ' \x1b[0m'
                except Exception as reason:
                    print(reason)  # Do not use log here.
                return fn(*new_args)
            return new
        logging.StreamHandler.emit = add_color_emit_ansi(
            logging.StreamHandler.emit)

    log.addHandler(logging.StreamHandler(sys.stderr))
    if os.path.exists("/dev/log") or os.path.exists("/var/run/syslog"):
        is_linux = sys.platform.startswith("linux")
        adrs = "/dev/log" if is_linux else "/var/run/syslog"
        try:
            handler = logging.handlers.SysLogHandler(address=adrs)
        except Exception:
            log.debug("Unix SysLog Server not found,ignore Logging to SysLog")
        else:
            log.addHandler(handler)
            log.debug("Unix SysLog Server trying to Log to SysLog: " + adrs)
    log.debug("Logger created with Log file at: {0}.".format(log_file))
    return log


from anglerfish.check_encoding import check_encoding  # noqa
from anglerfish.check_folder import check_folder  # noqa
from anglerfish.get_clipboard import get_clipboard  # noqa
from anglerfish.get_sanitized_string import get_sanitized_string  # noqa
from anglerfish.make_beep import beep  # noqa
from anglerfish.make_json_pretty import json_pretty  # noqa
from anglerfish.make_log_exception import log_exception  # noqa
from anglerfish.make_multiprocess import multiprocessed  # noqa
from anglerfish.make_multithread import threads  # noqa
from anglerfish.make_postexec_message import make_post_exec_msg  # noqa
from anglerfish.make_retry import retry  # noqa
from anglerfish.make_typecheck import typecheck  # noqa
from anglerfish.walk2list import walk2list  # noqa
from anglerfish.make_watch import watch  # noqa
from anglerfish.set_desktop_launcher import set_desktop_launcher  # noqa
from anglerfish.set_process_name import set_process_name  # noqa
from anglerfish.set_single_instance import set_single_instance  # noqa
from anglerfish.get_temp_folder import get_temp_folder  # noqa
from anglerfish.set_terminal_title import set_terminal_title  # noqa
from anglerfish.bytes2human import bytes2human  # noqa
from anglerfish.walk2dict import walk2dict  # noqa
from anglerfish.seconds2human import seconds2human  # noqa
from anglerfish.env2globals import env2globals  # noqa
from anglerfish.html2ebook import html2ebook  # noqa
from anglerfish.make_template_python import TemplatePython  # noqa
from anglerfish.get_pdb_on_exception import (pdb_on_exception,  # noqa
                                             ipdb_on_exception)  # noqa
from anglerfish.make_info import (about_python, about_self,  # noqa
                                  view_code, report_bug)  # noqa
from anglerfish.make_config import (get_config_folder, make_config,  # noqa
                                    view_config, save_config,  # noqa
                                    delete_config, backup_config)  # noqa
