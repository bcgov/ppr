# Copyright © 2025 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""This module is the entry point to initialize the job."""
import json
import os
import sys

from assets_payment.services.payment_client import get_sa_token
from assets_payment.utils.logging import logger, setup_logging

from .config import Config
from .job import job

# Retrieve Job-defined env vars
TASK_INDEX = os.getenv("CLOUD_RUN_TASK_INDEX", "0")
TASK_ATTEMPT = os.getenv("CLOUD_RUN_TASK_ATTEMPT", "0")


# Start script
if __name__ == "__main__":
    sa_token: str = None
    try:
        config = Config()
        setup_logging(os.path.join(os.path.abspath(os.path.dirname(__file__)), "logging.yaml"))
        sa_token = get_sa_token(config)
        logger.info(f"Assets Payment job starting sa token={sa_token}")
        job(config, sa_token)
    except Exception as err:
        message = f"Task #{TASK_INDEX}, " + f"Attempt #{TASK_ATTEMPT} failed: {str(err)}"
        print(json.dumps({"message": message, "severity": "ERROR"}))
        logger.error(f"Job failed: {str(err)}")
        sys.exit(1)  # Retry Job Task by exiting the process
