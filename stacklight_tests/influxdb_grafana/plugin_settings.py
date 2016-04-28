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

from stacklight_tests import settings


name = 'influxdb_grafana'
version = '0.9.0'
role_name = ['influxdb_grafana']
vip_name = 'influxdb'
plugin_path = settings.INFLUXDB_GRAFANA_PLUGIN_PATH

influxdb_db_name = "lma"
influxdb_user = 'influxdb'
influxdb_pass = 'influxdbpass'
influxdb_rootuser = 'root'
influxdb_rootpass = 'r00tme'
influxdb_url = "http://{0}:8086/query"

grafana_user = 'grafana'
grafana_pass = 'grafanapass'
grafana_url = "http://{0}:{1}@{2}:8000/api/org"

mysql_mode = 'local'
mysql_dbname = 'grafanalma'
mysql_user = 'grafanalma'
mysql_pass = 'mysqlpass'
