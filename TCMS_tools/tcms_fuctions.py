import TCMS_tools.tcms_maps as tcms_maps

def _get_case_id_in_run(rpc, run_id: int, case_summary: str) -> int:
    cases = rpc.TestRun.get_cases(run_id)
    for c in cases:
        if c.get("summary") == case_summary:
            return c["id"]
    raise RuntimeError(f"TestCase '{case_summary}' not found in run {run_id}")

def set_exec_status(rpc , runner_id ,case_summary: str, ok: bool):
    """Update execution status for a case in the active run."""
    case_id = _get_case_id_in_run(rpc , runner_id, case_summary)
    executions = rpc.TestExecution.filter({"run_id": runner_id, "case": case_id})
    if not executions:
        raise RuntimeError(f"No executions for case_id={case_id} in run_id={runner_id}")

    status_key = "PASSED" if ok else "FAILED"
    status_id = tcms_maps.EXECUTION_STATUSES[status_key]

    for e in executions:
        rpc.TestExecution.update(e["id"], {"status": status_id})
        print(f"[TCMS] {case_summary} -> Execution {e['id']} set to {status_key} ({status_id})")

def set_exec_status_manualy(rpc , runner_id ,case_summary: str, status: str):
    """Update manualy execution status for a case in the active run."""
    case_id = _get_case_id_in_run(rpc , runner_id, case_summary)
    executions = rpc.TestExecution.filter({"run_id": runner_id, "case": case_id})
    if not executions:
        raise RuntimeError(f"No executions for case_id={case_id} in run_id={runner_id}")

    status_id = tcms_maps.EXECUTION_STATUSES[status]

    for e in executions:
        rpc.TestExecution.update(e["id"], {"status": status_id})
        print(f"[TCMS] {case_summary} -> Execution {e['id']} set to {status} ({status_id})")