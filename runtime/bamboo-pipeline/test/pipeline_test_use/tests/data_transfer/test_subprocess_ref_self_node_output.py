# -*- coding: utf-8 -*-

from ..base import *  # noqa


class TestSubprocessRefSelfNodeOutput(EngineTestCase):
    def test_ref_self_node_constant(self):
        sub_start = EmptyStartEvent()
        sub_act_1 = ServiceActivity(component_code="debug_node")
        sub_act_1.component.inputs.param_1 = Var(type=Var.SPLICE, value="${sub_constant_1}")
        sub_act_1.component.inputs.param_2 = Var(type=Var.PLAIN, value="sub_var2")
        sub_act_2 = ServiceActivity(component_code="debug_node")
        sub_act_2.component.inputs.param_1 = Var(type=Var.SPLICE, value="${ref_sub_act_1_outputs}")
        sub_end = EmptyEndEvent()

        sub_start.extend(sub_act_1).extend(sub_act_2).extend(sub_end)

        sub_pipeline_data = Data()
        sub_pipeline_data.inputs["${sub_constant_1}"] = DataInput(type=Var.PLAIN, value="value_1")
        sub_pipeline_data.inputs["${sub_act_1_outputs}"] = NodeOutput(
            source_act=sub_act_1.id, source_key="param_2", type=Var.SPLICE, value=""
        )
        sub_pipeline_data.inputs["${ref_sub_act_1_outputs}"] = Var(type=Var.SPLICE, value="${sub_act_1_outputs}")

        start = EmptyStartEvent()
        act_1 = ServiceActivity(component_code="debug_node")
        act_1.component.inputs.param_1 = Var(type=Var.PLAIN, value="output_value_1")
        params = Params({"${sub_constant_1}": Var(type=Var.SPLICE, value="${act_1_output}")})
        subprocess = SubProcess(start=sub_start, data=sub_pipeline_data, params=params)
        end = EmptyEndEvent()

        start.extend(act_1).extend(subprocess).extend(end)

        pipeline_data = Data()
        pipeline_data.inputs["${act_1_output}"] = NodeOutput(
            source_act=act_1.id, source_key="param_1", type=Var.SPLICE, value=""
        )

        pipeline = self.create_pipeline_and_run(start, data=pipeline_data)

        self.join_or_fail(pipeline)
        self.assert_pipeline_finished(pipeline)

        self.assert_inputs_equals(sub_act_1, "param_1", "output_value_1")
        self.assert_outputs_equals(sub_act_1, "param_1", "output_value_1")
        self.assert_outputs_equals(sub_act_1, "param_2", "sub_var2")
        self.assert_inputs_equals(sub_act_2, "param_1", "sub_var2")

        self.test_pass()
