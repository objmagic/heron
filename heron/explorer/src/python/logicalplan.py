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

import heron.explorer.src.python.args as args
from collections import defaultdict
from heron.common.src.python.color import Log
from heron.explorer.src.python.utils import get_logical_plan, get_topology_info
from tabulate import tabulate


def create_parser(subparsers):
  components_parser = subparsers.add_parser(
    'components',
    help='display information of a topology in a logical plan',
    usage="%(prog)s [options]",
    add_help=False)
  args.add_cluster_role_env(components_parser)
  args.add_topology_name(components_parser)
  args.add_verbose(components_parser)
  args.add_tracker_url(components_parser)
  args.add_config(components_parser)
  components_parser.set_defaults(subcommand='components')

  spouts_parser = subparsers.add_parser(
    'spouts',
    help='display information of spouts of a topology in a logical plan',
    usage="%(prog)s [options]",
    add_help=False)
  args.add_cluster_role_env(spouts_parser)
  args.add_topology_name(spouts_parser)
  args.add_verbose(spouts_parser)
  args.add_tracker_url(spouts_parser)
  args.add_config(spouts_parser)
  spouts_parser.set_defaults(subcommand='spouts')

  bolts_parser = subparsers.add_parser(
    'bolts',
    help='display information of bolts of a topology in a logical plan',
    usage="%(prog)s [options]",
    add_help=False)
  args.add_cluster_role_env(bolts_parser)
  args.add_topology_name(bolts_parser)
  args.add_verbose(bolts_parser)
  args.add_tracker_url(bolts_parser)
  args.add_config(bolts_parser)
  bolts_parser.set_defaults(subcommand='bolts')

  return subparsers


def parse_topo_loc(cl_args):
  try:
    topo_loc = cl_args['cluster/[role]/[env]'].split('/')
    topo_loc.append(cl_args['topology-name'])
    if len(topo_loc) != 4:
      raise
    return topo_loc
  except Exception:
    Log.error('Error: invalid topology location')
    raise


def dump_components(components, topo_info):
  inputs, outputs = defaultdict(list), defaultdict(list)
  for ctype, component in components.iteritems():
    if ctype == 'bolts':
      for component_name, component_info in component.iteritems():
        for input_stream in component_info['inputs']:
          input_name = input_stream['component_name']
          inputs[component_name].append(input_name)
          outputs[input_name].append(component_name)
  info = []
  spouts_instance = topo_info['physical_plan']['spouts']
  bolts_instance = topo_info['physical_plan']['bolts']
  for ctype, component in components.iteritems():
    for component_name, component_info in component.iteritems():
      row = [ctype, component_name]
      if ctype == 'spouts':
        row.append(len(spouts_instance[component_name]))
      else:
        row.append(len(bolts_instance[component_name]))
      row.append(','.join(inputs.get(component_name, ['-'])))
      row.append(','.join(outputs.get(component_name, ['-'])))
      info.append(row)
  header = ['type', 'name', '#instances', 'input', 'output']
  print(tabulate(info, headers=header))
  return True


def dump_bolts(bolts, topo_loc):
  print('Bolts under topology \'%s\'' % '/'.join(topo_loc))
  for bolt in bolts.keys():
    print('  %s' % bolt)
  return True


def dump_spouts(spouts, topo_loc):
  print('Spouts under topology \'%s\'' % '/'.join(topo_loc))
  for spout in spouts.keys():
    print('  %s' % spout)
  return True


def run(cl_args, compo_type):
  cluster, role, env = cl_args['cluster'], cl_args['role'], cl_args['environ']
  topology = cl_args['topology-name']
  topo_loc = [cluster, role, env, topology]
  try:
    components = get_logical_plan(cluster, env, topology, role)
    bolts, spouts = components["bolts"], components["spouts"]
    if compo_type == 'bolts':
      return dump_bolts(bolts, topo_loc)
    if compo_type == 'spouts':
      return dump_spouts(spouts, topo_loc)
    else:
      topo_info = get_topology_info(cluster, env, topology, role)
      return dump_components(components, topo_info)
  except:
    return False


def run_components(command, parser, cl_args, unknown_args):
  return run(cl_args, 'all')


def run_spouts(command, parser, cl_args, unknown_args):
  return run(cl_args, 'spouts')


def run_bolts(command, parser, cl_args, unknown_args):
  return run(cl_args, 'bolts')
