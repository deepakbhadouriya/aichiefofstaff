from libs.langgraph_flows.bill_payment import BillPaymentFlow
from libs.schemas.workflow import WorkflowRunRequest, WorkflowRunView

_FLOW = BillPaymentFlow()


def run_bill_payment_flow(
    tenant_id: str,
    profile_id: str,
    request_id: str,
    request: WorkflowRunRequest,
) -> WorkflowRunView:
    return _FLOW.run(
        tenant_id=tenant_id,
        profile_id=profile_id,
        x_request_id=request_id,
        request=request,
    )
