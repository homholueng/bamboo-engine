# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import copy
import logging
import traceback

from bamboo_engine import states
from bamboo_engine.eri import ProcessInfo, NodeType
from bamboo_engine.handler import register_handler, ExecuteResult

from .empty_end_event import EmptyEndEventHandler

logger = logging.getLogger("bamboo_engine")


@register_handler(NodeType.ExecutableEndEvent)
class ExecutableEndEventHandler(EmptyEndEventHandler):
    def execute(
        self, process_info: ProcessInfo, loop: int, inner_loop: int, version: str
    ) -> ExecuteResult:
        """
        节点的 execute 处理逻辑

        :param runtime: 引擎运行时实例
        :type runtime: EngineRuntimeInterface
        :param process_info: 进程信息
        :type process_id: ProcessInfo
        :return: 执行结果
        :rtype: ExecuteResult
        """

        logger.info(
            "[%s] %s executable end event: %s",
            process_info.root_pipeline_id,
            self.node.id,
            self.node,
        )
        event = self.runtime.get_executable_end_event(code=self.node.code)

        try:
            event.execute(
                pipeline_stack=copy.copy(process_info.pipeline_stack),
                root_pipeline_id=process_info.root_pipeline_id,
            )
        except Exception:
            ex_data = traceback.format_exc()
            logger.warning(
                "[%s] %s executable end event execute raise: %s",
                process_info.root_pipeline_id,
                self.node.id,
                ex_data,
            )

            self.runtime.set_execution_data_outputs(
                node_id=self.node.id, outputs={"ex_data": ex_data}
            )

            self.runtime.set_state(
                node_id=self.node.id, to_state=states.FAILED, set_archive_time=True
            )

            return ExecuteResult(
                should_sleep=True,
                schedule_ready=False,
                schedule_type=None,
                schedule_after=-1,
                dispatch_processes=[],
                next_node_id=None,
            )

        return super().execute(process_info=process_info, loop=loop, inner_loop=inner_loop, version=version)
