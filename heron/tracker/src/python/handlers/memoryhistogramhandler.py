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

import json
import logging
import tornado.gen
import tornado.web
import traceback

from heron.tracker.src.python import constants
from heron.tracker.src.python import utils
from heron.tracker.src.python.handlers import BaseHandler
from heron.tracker.src.python.handlers.pidhandler import getInstancePid

LOG = logging.getLogger(__name__)

class MemoryHistogramHandler(BaseHandler):
  """
  URL - /topologies/histo?cluster=<cluster>&topology=<topology> \
        &environ=<environment>&instance=<instance>
  Parameters:
   - cluster - Name of the cluster.
   - role - (optional) Role used to submit the topology.
   - environ - Running environment.
   - topology - Name of topology (Note: Case sensitive. Can only
                include [a-zA-Z0-9-_]+)
   - instance - Instance Id

  Resturns a histogram of top in memory object.
  The response JSON is a dict with following format:
  {
     'command': Full command executed at server.
     'stdout': Text on stdout of executing the command.
     'stderr': <optional> Text on stderr.
  }
  """

  def initialize(self, tracker):
    self.tracker = tracker

  @tornado.gen.coroutine
  def get(self):
    try:
      cluster = self.get_argument_cluster()
      role = self.get_argument_role()
      environ = self.get_argument_environ()
      topology_name = self.get_argument_topology()
      instance = self.get_argument_instance()
      topology_info = self.tracker.getTopologyInfo(topology_name, cluster, role, environ)
      ret = yield self.getInstanceMemoryHistogram(topology_info, instance)
      self.write_success_response(ret)
    except Exception as e:
      traceback.print_exc()
      self.write_error_response(e)

  @tornado.gen.coroutine
  def getInstanceMemoryHistogram(self, topology_info, instance_id):
    """
    Fetches Instance top memory item as histogram.
    """
    pid_response = yield getInstancePid(topology_info, instance_id)
    try:
      http_client = tornado.httpclient.AsyncHTTPClient()
      component_id = instance_id.split('_')[1] # Format: container_<id>_<instance_id>
      pid_json = json.loads(pid_response)
      pid = pid_json['stdout'].strip()
      if pid == '':
        raise Exception('Failed to get pid')
      endpoint = utils.make_shell_endpoint(topology_info, instance_id)
      url = "%s/histo/%s" % (endpoint, pid)
      response = yield http_client.fetch(url)
      LOG.debug("HTTP call for url: %s" % url)
      raise tornado.gen.Return(response.body)
    except tornado.httpclient.HTTPError as e:
      raise Exception(str(e))

