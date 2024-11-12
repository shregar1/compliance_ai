from fastapi import APIRouter

from controllers.apis.compliance_check import ComplianceCheckController

from start_utils import logger

router = APIRouter(prefix="/apis")

logger.debug(f"Registering {ComplianceCheckController.__name__} route.")
router.add_api_route(
    path="/compliance_check",
    endpoint=ComplianceCheckController().post,
    methods=["POST"]
)
logger.debug(f"Registered {ComplianceCheckController.__name__} route.")