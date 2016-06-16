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

from devops.helpers import helpers
from fuelweb_test import logger
from proboscis import asserts

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from stacklight_tests import base_test
from stacklight_tests.lma_infrastructure_alerting import(
    plugin_settings as infra_alerting_plugin_settings)


class InfraAlertingPluginApi(base_test.PluginApi):
    def get_plugin_settings(self):
        return infra_alerting_plugin_settings

    def prepare_plugin(self):
        self.helpers.prepare_plugin(self.settings.plugin_path)

    def activate_plugin(self, options=None):
        if options is None:
            options = self.settings.default_options
        self.helpers.activate_plugin(
            self.settings.name, self.settings.version, options)

    def get_plugin_vip(self):
        try:
            return self.helpers.get_plugin_vip(self.settings.vip_name)
        except Exception:
            return self.helpers.get_plugin_vip(
                'infrastructure_alerting_mgmt_vip')

    def check_plugin_online(self):
        nagios_url = self.get_nagios_url()
        logger.info("Nagios UI is at {}".format(nagios_url))
        logger.info("Check that the '{}' user is authorized".format(
            self.settings.nagios_user))
        self.checkers.check_http_get_response(
            nagios_url,
            auth=(self.settings.nagios_user, self.settings.nagios_password)
        )
        logger.info("Check that the Nagios UI requires authentication")
        self.checkers.check_http_get_response(
            nagios_url, expected_code=401,
            auth=(self.settings.nagios_user, 'rogue')
        )

    def get_authenticated_nagios_url(self):
        return "http://{0}:{1}@{2}:8001".format(self.settings.nagios_user,
                                                self.settings.nagios_password,
                                                self.get_plugin_vip())

    def get_nagios_url(self):
        return "http://{}:8001/".format(self.get_plugin_vip())

    def open_nagios_page(self, driver, link_text, anchor):
        driver.switch_to.default_content()
        driver.switch_to.frame(driver.find_element_by_name("side"))
        link = driver.find_element_by_link_text(link_text)
        link.click()
        driver.switch_to.default_content()
        driver.switch_to.frame(driver.find_element_by_name("main"))
        WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.XPATH, anchor)))
        return driver

    def check_node_in_nagios(self, changed_node, state):
        with self.ui_tester.ui_driver(
                self.get_authenticated_nagios_url(),
                "//frame[2]", "Nagios Core") as driver:
            driver = self.open_nagios_page(
                driver, 'Hosts', "//table[@class='headertable']")
            asserts.assert_equal(state, self.node_is_present(
                driver, changed_node), "Failed to find node '{0}' "
                                       "on nagios!".format(changed_node))

    def node_is_present(self, driver, name):
        table = self.ui_tester.get_table(driver,
                                         "/html/body/div[2]/table/tbody")
        for ind in xrange(2, self.ui_tester.get_table_size(table) + 1):
            node_name = self.ui_tester.get_table_cell(
                table, ind, 1).text.rstrip()
            if name == node_name:
                return True

        return False

    def uninstall_plugin(self):
        return self.helpers.uninstall_plugin(self.settings.name,
                                             self.settings.version)

    def check_uninstall_failure(self):
        return self.helpers.check_plugin_cannot_be_uninstalled(
            self.settings.name, self.settings.version)

    def get_services_for_node(self, table, node_name):
        services = {}
        node_start, node_end = '', ''
        for ind in xrange(2, self.ui_tester.get_table_size(table) + 1):
            if not self.ui_tester.get_table_row(table, ind).text:
                if node_start:
                    node_end = ind
                    break
                else:
                    continue
            if self.ui_tester.get_table_cell(table, ind, 1).text == node_name:
                node_start = ind

        for ind in xrange(node_start, node_end):
            services[self.ui_tester.get_table_cell(table, ind, 2).text] = \
                self.ui_tester.get_table_cell(table, ind, 3).text
        return services

    def check_service_state_on_nagios(self, driver, service_state=None,
                                      node_names=None):
        self.open_nagios_page(
            driver, 'Services', "//table[@class='headertable']")
        table = self.ui_tester.get_table(driver, "/html/body/table[3]/tbody")
        if not node_names:
            node_names = [self.ui_tester.get_table_cell(table, 2, 1).text]
        for node in node_names:
            node_services = self.get_services_for_node(table, node)
            if service_state:
                for service in service_state:
                    if service_state[service] != node_services[service]:
                        return False
            else:
                for service in node_services:
                    if 'OK' != node_services[service]:
                        return False
        return True

    def wait_service_state_on_nagios(self, driver, service_state=None,
                                     node_names=None):
        msg = "Fail to get expected service states for services: {0} " \
              "on nodes: {1}"

        if not service_state or not node_names:
            self.open_nagios_page(
                driver, 'Services', "//table[@class='headertable']")
            table = self.ui_tester.get_table(driver,
                                             "/html/body/table[3]/tbody")
            if not node_names:
                node_names = [self.ui_tester.get_table_cell(table, 2, 1).text]
            if not service_state:
                service_state = dict((key, 'OK') for key in
                                     self.get_services_for_node(table,
                                                                node_names[0]))

        msg = msg.format([key for key in service_state], node_names)

        helpers.wait(lambda: self.check_service_state_on_nagios(
            driver, service_state, node_names), timeout=60 * 5,
            timeout_msg=msg)
