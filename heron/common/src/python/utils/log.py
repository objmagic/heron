# Copyright 2016 Twitter. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
''' log.py '''
import logging
from logging.handlers import RotatingFileHandler
import colorlog

# initialize default handler for all use cases
logging.basicConfig()

# Create logger
# pylint: disable=invalid-name
Log = logging.getLogger()

# time formatter formats time as `date - time - UTC offset`
# e.g. "08/16/1988 21:30:00 +1030"
# see Python's time formatter documentation for more
#
# Timezone information is necessary since user
# can start process on a remote machine which is
# different time zone. In such cases, time info
# without UTC offest is useless.
#
# This customized date_format should be added
# when each log entry needs to be associated with time
# For example, `heron-ui` and `heron-tracker` need to
# display log with time info
date_format = "%m/%d/%Y %H:%M:%S %z"

def configure(level, logfile=None, with_time=False):
  """ Configure logger which dumps log on terminal

  :param level: logging level: info, warning, verbose...
  :type level: logging level
  :param logfile: log file name, default to None
  :type logfile: string
  :return: None
  :rtype: None
  """

  root_logger = logging.getLogger()
  root_logger.setLevel(level)
  # if logfile is specified, FileHandler is used and
  # there is no need to enable colored output
  if logfile is not None:
    if with_time:
      log_format = "%(asctime)s:%(levelname)s: %(message)s"
    else:
      log_format = "%(levelname)s: %(message)s"
    formatter = logging.Formatter(fmt=log_format, datefmt=date_format)
    file_handler = logging.FileHandler(logfile)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
  # otherwise, use StreamHandler to output to stream (stdout, stderr...)
  else:
    if with_time:
      log_format = "%(log_color)s%(levelname)s:%(reset)s %(asctime)s %(message)s"
    else:
      log_format = "%(log_color)s%(levelname)s:%(reset)s %(message)s"
    # pylint: disable=redefined-variable-type
    formatter = colorlog.ColoredFormatter(fmt=log_format, datefmt=date_format)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)


def init_rotating_logger(level, logfile, max_files, max_bytes):
  """Initializes a rotating logger

  It also makes sure that any StreamHandler is removed, so as to avoid stdout/stderr
  constipation issues
  """

  root_logger = logging.getLogger()
  log_format = "%(asctime)s:%(levelname)s:%(filename)s: %(message)s"

  root_logger.setLevel(level)
  handler = RotatingFileHandler(logfile, maxBytes=max_bytes, backupCount=max_files)
  handler.setFormatter(logging.Formatter(fmt=log_format, datefmt=date_format))
  root_logger.addHandler(handler)

  for handler in root_logger.handlers:
    root_logger.debug("Associated handlers - " + str(handler))
    if isinstance(handler, logging.StreamHandler):
      root_logger.debug("Removing StreamHandler: " + str(handler))
      root_logger.handlers.remove(handler)

def set_logging_level(cl_args, with_time=False):
  """simply set verbose level based on command-line args

  :param cl_args: CLI arguments
  :type cl_args: dict
  :return: None
  :rtype: None
  """
  if 'verbose' in cl_args and cl_args['verbose']:
    configure(logging.DEBUG, with_time=with_time)
  else:
    configure(logging.INFO, with_time=with_time)
