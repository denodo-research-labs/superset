# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy.engine.url import URL
from superset.databases.utils import make_url_safe
from superset.db_engine_specs.base import BaseEngineSpec


class DenodoEngineSpec(BaseEngineSpec):

    engine = "denodo"
    engine_name = "denodo"

    _time_grain_expressions = {
        None: "{col}",
        "PT1M": "TRUNC({col},'MI')",
        "PT1H": "TRUNC({col},'HH')",
        "P1D": "TRUNC({col},'DDD')",
        "P1W": "TRUNC({col},'W')",
        "P1M": "TRUNC({col},'MONTH')",
        "P3M": "TRUNC({col},'Q')",
        "P1Y": "TRUNC({col},'YEAR')",
    }

    @classmethod
    def update_impersonation_config(
        cls,
        connect_args: Dict[str, Any],
        uri: str,
        username: Optional[str],
    ) -> None:
        """
        Update a configuration dictionary
        that can set the correct properties for impersonating users
        :param connect_args: config to be updated
        :param uri: URI string
        :param username: Effective username
        :return: None
        """
        url = make_url_safe(uri)
        backend_name = url.get_backend_name()

        # Must be Trino connection, enable impersonation, and set optional param
        # auth=LDAP|KERBEROS
        # Set principal_username=$effective_username
        if backend_name == "denodo" and username is not None:
            connect_args["user"] = username

    @classmethod
    def get_url_for_impersonation(
        cls, url: URL, impersonate_user: bool, username: Optional[str]
    ) -> URL:
        """
        Return a modified URL with the username set.

        :param url: SQLAlchemy URL object
        :param impersonate_user: Flag indicating if impersonation is enabled
        :param username: Effective username
        """
        # Do nothing and let update_impersonation_config take care of impersonation
        return url
