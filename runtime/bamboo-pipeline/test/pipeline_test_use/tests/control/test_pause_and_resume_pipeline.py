# -*- coding: utf-8 -*-

from ..base import *  # noqa


class TestPauseAndResumePipeline(EngineTestCase):
    def test_pause_and_resume_pipeline_with_nest_parallel(self):
        parallel_count = 5
        start = EmptyStartEvent()
        pg_1 = ParallelGateway()
        pg_2 = ParallelGateway()
        sleep_group_1 = []

        for _ in range(parallel_count):
            act = ServiceActivity(component_code="sleep_timer")
            act.component.inputs.bk_timing = Var(type=Var.PLAIN, value=3)
            sleep_group_1.append(act)

        sleep_group_2 = []
        for _ in range(parallel_count):
            act = ServiceActivity(component_code="sleep_timer")
            act.component.inputs.bk_timing = Var(type=Var.PLAIN, value=3)
            sleep_group_2.append(act)

        acts_group_1 = [ServiceActivity(component_code="debug_node") for _ in range(parallel_count)]
        acts_group_2 = [ServiceActivity(component_code="debug_node") for _ in range(parallel_count)]
        cg_1 = ConvergeGateway()
        cg_2 = ConvergeGateway()
        end = EmptyEndEvent()

        for i in range(parallel_count):
            sleep_group_1[i].connect(acts_group_1[i])
            sleep_group_2[i].connect(acts_group_2[i])

        start.extend(pg_1).connect(pg_2, *sleep_group_1).to(pg_2).connect(*sleep_group_2).converge(cg_1).to(
            pg_1
        ).converge(cg_2).extend(end)

        pipeline = self.create_pipeline_and_run(start)

        finished = [start, pg_1, pg_2]
        finished.extend(sleep_group_1)
        finished.extend(sleep_group_2)

        self.wait_to(pg_1, pg_2, state=states.FINISHED)

        self.pause_pipeline(pipeline)

        self.wait_to(*finished, state=states.FINISHED)

        self.assert_state(pipeline, state=states.SUSPENDED)

        self.assert_finished(*finished)

        not_execute = [cg_1, cg_2, end]
        not_execute.extend(acts_group_1)
        not_execute.extend(acts_group_2)
        self.assert_not_execute(*not_execute)

        self.resume_pipeline(pipeline)

        self.join_or_fail(pipeline)
        self.assert_pipeline_finished(pipeline)

        self.test_pass()

    def test_pause_and_resume_pipeline_with_subprocess(self):
        subproc_start = EmptyStartEvent()
        subproc_act = ServiceActivity(component_code="sleep_timer")
        subproc_act.component.inputs.bk_timing = Var(type=Var.PLAIN, value=3)
        subproc_end = EmptyEndEvent()

        subproc_start.extend(subproc_act).extend(subproc_end)

        start = EmptyStartEvent()
        subproc = SubProcess(start=subproc_start)
        end = EmptyEndEvent()

        start.extend(subproc).extend(end)

        pipeline = self.create_pipeline_and_run(start)

        self.wait_to(start, state=states.FINISHED)

        self.pause_pipeline(pipeline)

        self.wait_to(subproc_act, state=states.FINISHED)

        self.assert_finished(start, subproc_start, subproc_act)

        self.assert_not_execute(subproc_end, end)

        self.assert_state(subproc, state=states.RUNNING)

        self.resume_pipeline(pipeline)

        self.join_or_fail(pipeline)
        self.assert_pipeline_finished(pipeline)

        self.test_pass()

    def test_pause_and_resume_pipeline_with_subprocess_has_parallel(self):
        parallel_count = 5
        start = EmptyStartEvent()
        pg_1 = ParallelGateway()
        pg_2 = ParallelGateway()
        sleep_group_1 = []

        for _ in range(parallel_count):
            act = ServiceActivity(component_code="sleep_timer")
            act.component.inputs.bk_timing = Var(type=Var.PLAIN, value=3)
            sleep_group_1.append(act)

        sleep_group_2 = []
        for _ in range(parallel_count):
            act = ServiceActivity(component_code="sleep_timer")
            act.component.inputs.bk_timing = Var(type=Var.PLAIN, value=3)
            sleep_group_2.append(act)

        acts_group_1 = [ServiceActivity(component_code="debug_node") for _ in range(parallel_count)]
        acts_group_2 = [ServiceActivity(component_code="debug_node") for _ in range(parallel_count)]
        cg_1 = ConvergeGateway()
        cg_2 = ConvergeGateway()
        end = EmptyEndEvent()

        for i in range(parallel_count):
            sleep_group_1[i].connect(acts_group_1[i])
            sleep_group_2[i].connect(acts_group_2[i])

        start.extend(pg_1).connect(pg_2, *sleep_group_1).to(pg_2).connect(*sleep_group_2).converge(cg_1).to(
            pg_1
        ).converge(cg_2).extend(end)

        parent_start = EmptyStartEvent()
        subproc = SubProcess(start=start)
        parent_end = EmptyEndEvent()

        parent_start.extend(subproc).extend(parent_end)

        pipeline = self.create_pipeline_and_run(parent_start)

        finished = [parent_start, start, pg_1, pg_2]
        finished.extend(sleep_group_1)
        finished.extend(sleep_group_2)

        self.wait_to(pg_1, pg_2, state=states.FINISHED)

        self.pause_pipeline(pipeline)

        self.wait_to(*finished, state=states.FINISHED)

        self.assert_state(pipeline, state=states.SUSPENDED)

        self.assert_finished(*finished)

        self.assert_state(subproc, state=states.RUNNING)

        not_execute = [cg_1, cg_2, end, parent_end]
        not_execute.extend(acts_group_1)
        not_execute.extend(acts_group_2)
        self.assert_not_execute(*not_execute)

        self.resume_pipeline(pipeline)

        self.join_or_fail(pipeline)
        self.assert_pipeline_finished(pipeline)

        self.test_pass()
