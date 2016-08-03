#    Copyright 2016 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from stacklight_tests import base_test
from fuelweb_test import logger
from proboscis import asserts

from stacklight_tests.kafka import plugin_settings


class KafkaPluginApi(base_test.PluginApi):
    def __init__(self):
        super(KafkaPluginApi, self).__init__()

    def get_plugin_settings(self):
        return plugin_settings

    def prepare_plugin(self):
        self.helpers.prepare_plugin(self.settings.plugin_path)

    def activate_plugin(self, options=None):
        if options is None:
            options = self.settings.default_options
        self.helpers.activate_plugin(
            self.settings.name, self.settings.version, options)

    def check_plugin_online(self):
        nodes = []
        for node in self.helpers.get_all_ready_nodes():
            if "kafka" in node["roles"]:
                nodes.append({"name":node["name"], "ip": node["ip"]})

        for port in [
            {"name":"zookeeper_client", "number":2181},
            {"name":"kafka_client",     "number":9092},
            {"name":"kafka_jmx",        "number":9990}]:
            for node in nodes:
                result=self.checkers.check_port(node["ip"],port["number"])
                status = "online" if result else "offline"
                msg = "Port {} ({}) is {} on node {}".format(port['name'],port['number'],status,node['name'])
                logger.info(msg)
                asserts.assert_true(result==True, msg)

    def uninstall_plugin(self):
        return self.helpers.uninstall_plugin(self.settings.name,
                                             self.settings.version)

    def check_uninstall_failure(self):
        return self.helpers.check_plugin_cannot_be_uninstalled(
            self.settings.name, self.settings.version)

