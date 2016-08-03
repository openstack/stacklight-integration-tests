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

from fuelweb_test.helpers.decorators import log_snapshot_after_test
from proboscis import test

from stacklight_tests.kafka import api


@test(groups=["plugins"])
class TestKafkaPlugin(api.KafkaPluginApi):
    """Class for smoke testing the Kafka plugin."""

    @test(depends_on_groups=["prepare_slaves_5"],
          groups=["deploy_kafka", "deploy",
                  "kafka", "smoke"])
    @log_snapshot_after_test
    def deploy_kafka(self):
        """Deploy a cluster with the Kafka plugin

        Scenario:
            1. Upload the Kafka plugin to the master node
            2. Install the plugin
            3. Create the cluster
            4. Add 3 nodes with controller and kafka roles
            5. Add 1 node with compute and cinder roles
            7. Deploy the cluster
            8. Check that Kafka is running
            9. Run OSTF

        Duration 60m
        Snapshot deploy_kafka
        """
        self.check_run("deploy_kafka")
        self.env.revert_snapshot("ready_with_5_slaves")

        self.prepare_plugin()

        self.helpers.create_cluster(name=self.__class__.__name__)

        self.activate_plugin()

        self.helpers.deploy_cluster({
            'slave-01': ['controller', self.settings.role_name],
            'slave-02': ['controller', self.settings.role_name],
            'slave-03': ['controller', self.settings.role_name],
            'slave-04': ['compute', 'cinder'],
        })

        self.check_plugin_online()

        self.helpers.run_ostf()

        self.env.make_snapshot("deploy_kafka", is_make=True)
