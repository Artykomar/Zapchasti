import logging

from rest_framework.throttling import ScopedRateThrottle

logger = logging.getLogger(__name__)


class CustomerRequestRateThrottle(ScopedRateThrottle):
    scope = "customer_requests"

    def throttle_failure(self) -> bool:
        logger.warning("Customer request throttle limit reached.")
        return super().throttle_failure()
