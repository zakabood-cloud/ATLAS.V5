"""Bounded fixture dispatch, cancellation and durable failure receipts; no model launcher."""
import asyncio
from .access import AccessBlocked
from .io import AtlasError, confined, atomic_json
from .demo import handoff_fixture


class FixtureWorker:
    async def execute(self,task,context):
        return dict(handoff_fixture(task["id"],"Fixture completed "+task["objective"]),
                    worker="fixture",warning="Synthetic test only, NOT a research result")


async def run_ready(project,worker,max_workers=2,max_tasks=100,timeout_per_task=120):
    if type(max_workers) is not int or not 1<=max_workers<=8 or type(max_tasks) is not int or not 1<=max_tasks<=1000:
        raise AtlasError("Invalid work bounds")
    if type(timeout_per_task) not in (int,float) or not 0<timeout_per_task<=3600:
        raise AtlasError("Invalid task timeout")
    status=project.status()
    if status["state"]!="RESEARCH" or status.get("hold"): raise AtlasError("Project must be active RESEARCH")
    mandate=project.artifact("mandate.json"); count=0; completed=[]; failed=[]

    async def one(task):
        accepted=False
        try:
            project.task(task["id"],"running")
            result=await asyncio.wait_for(worker.execute(task,{"cwd":str(project.root),"mandate":mandate}),timeout_per_task)
            if not isinstance(result,dict) or result.get("task_id")!=task["id"]:
                raise AtlasError("Worker returned wrong task ID or malformed output")
            if result.get("blocked_access"):
                block=result["blocked_access"]
                raise AccessBlocked(block["resource"],block["operation"],block["reason"],block["quality_impact"],block.get("need_id"))
            if project.status().get("hold"): raise AtlasError("Output not accepted after project was held")
            path=f"branches/{task['id']}.json"
            atomic_json(confined(project.path,path),result)
            project.task(task["id"],"done",path); completed.append(task["id"]); accepted=True
        except AccessBlocked as error:
            if not getattr(error,"recorded",False):
                project.block_access(error.resource,error.operation,error.reason,error.quality_impact,error.need_id,task["id"])
            failed.append({"id":task["id"],"error":str(error),"access_block":True})
            raise
        except (OSError,asyncio.TimeoutError) as error:
            reason=type(error).__name__+": "+str(error)
            impact="Worker could not complete its operation; access or execution may be incomplete. No retry or fallback is authorized."
            project.block_access("task:"+task["id"],"worker-execute",reason,impact,task_id=task["id"])
            failed.append({"id":task["id"],"error":reason,"access_block":True})
            raise AccessBlocked("task:"+task["id"],"worker-execute",reason,impact) from error
        except asyncio.CancelledError:
            failed.append({"id":task["id"],"error":"Canceled when dispatch stopped"})
            raise
        except (AtlasError,ValueError,TypeError,KeyError) as error:
            message=type(error).__name__+": "+str(error)
            project.interrupt_task(task["id"],message)
            failed.append({"id":task["id"],"error":message})
        finally:
            if not accepted: project.interrupt_task(task["id"],"Worker interrupted before an output was accepted")

    while count<max_tasks:
        status=project.status()
        if status.get("hold"): break
        done={t["id"] for t in status["tasks"] if t["status"]=="done"}
        ready=[t for t in status["tasks"] if t["status"]=="pending" and all(dep in done for dep in t["depends_on"])]
        if not ready: break
        batch=ready[:min(max_workers,max_tasks-count)]
        futures=[asyncio.create_task(one(t)) for t in batch]
        try:
            finished,pending=await asyncio.wait(futures,return_when=asyncio.FIRST_EXCEPTION)
            exceptions=[f.exception() for f in finished if not f.cancelled() and f.exception() is not None]
            if exceptions:
                for future in pending: future.cancel()
                await asyncio.gather(*pending,return_exceptions=True)
                unexpected=next((e for e in exceptions if not isinstance(e,AccessBlocked)),None)
                if unexpected: raise unexpected
            count+=len(batch)
        finally:
            for future in futures:
                if not future.done(): future.cancel()
            await asyncio.gather(*futures,return_exceptions=True)
    last=project.status()
    remaining=[t["id"] for t in last["tasks"] if t["status"]!="done"]
    return {"ok":not failed and not remaining and not last.get("hold"),"completed":completed,"failed":failed,
            "remaining":remaining,"state":last["state"],"hold":last.get("hold"),
            "note":"Fixture runner only. No automatic retries. External Copilot jobs require the client's own cancellation controls."}
