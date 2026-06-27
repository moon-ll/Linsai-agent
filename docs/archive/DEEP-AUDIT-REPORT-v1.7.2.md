# LinSai-CoPilot 深度评估报告

**版本**: v1.7.2  
**时间**: 2026-05-11 21:59:25  
**评估维度**: 9  
**发现问题**: 150 项（严重 0 / 高 0 / 中 0 / 低 150）  
**风险评分**: 150 / 1000

---

## LLM引擎（3 项）

### 🟢 [LOW] 工具调用降级已就绪

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/copilot_engine.py`
- **详情**: 工具引擎不可用时降级为普通 LLM 调用

### 🟢 [LOW] 超时参数已配置

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/llm_router.py`
- **详情**: urllib.request 和 subprocess 均配置 timeout

### 🟢 [LOW] Provider 降级链已实现

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/llm_router.py`
- **详情**: 支持 priority/round_robin 策略及 failure_count 追踪

---

## 代码质量（137 项）

### 🟢 [LOW] 疑似未使用导入

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/agora_bridge.py`
- **详情**: agora_bridge.py: annotations

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/backup_manager.py:149`
- **详情**: backup_manager.py:149 建议捕获更具体的异常类型

### 🟢 [LOW] 疑似未使用导入

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/backup_manager.py`
- **详情**: backup_manager.py: os

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/chat_archive.py:70`
- **详情**: chat_archive.py:70 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/chat_archive.py:82`
- **详情**: chat_archive.py:82 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/chat_archive.py:196`
- **详情**: chat_archive.py:196 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/chat_archive.py:235`
- **详情**: chat_archive.py:235 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/chat_archive.py:369`
- **详情**: chat_archive.py:369 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/chat_archive.py:150`
- **详情**: chat_archive.py:150 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/chat_archive.py:249`
- **详情**: chat_archive.py:249 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/chat_archive.py:381`
- **详情**: chat_archive.py:381 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/context_builder.py:65`
- **详情**: context_builder.py:65 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/context_builder.py:79`
- **详情**: context_builder.py:79 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/context_builder.py:93`
- **详情**: context_builder.py:93 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/context_builder.py:136`
- **详情**: context_builder.py:136 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/context_builder.py:230`
- **详情**: context_builder.py:230 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/context_builder.py:271`
- **详情**: context_builder.py:271 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/copilot_engine.py:40`
- **详情**: copilot_engine.py:40 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/copilot_engine.py:208`
- **详情**: copilot_engine.py:208 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/copilot_engine.py:290`
- **详情**: copilot_engine.py:290 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/copilot_engine.py:573`
- **详情**: copilot_engine.py:573 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/copilot_engine.py:586`
- **详情**: copilot_engine.py:586 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/copilot_engine.py:451`
- **详情**: copilot_engine.py:451 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/copilot_engine.py:462`
- **详情**: copilot_engine.py:462 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/copilot_engine.py:475`
- **详情**: copilot_engine.py:475 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/copilot_engine.py:488`
- **详情**: copilot_engine.py:488 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/copilot_engine.py:502`
- **详情**: copilot_engine.py:502 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/copilot_engine.py:663`
- **详情**: copilot_engine.py:663 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/copilot_engine.py:367`
- **详情**: copilot_engine.py:367 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/copilot_engine.py:402`
- **详情**: copilot_engine.py:402 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/copilot_engine.py:93`
- **详情**: copilot_engine.py:93 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/copilot_engine.py:361`
- **详情**: copilot_engine.py:361 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/copilot_engine.py:384`
- **详情**: copilot_engine.py:384 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/copilot_engine.py:422`
- **详情**: copilot_engine.py:422 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/copilot_engine.py:448`
- **详情**: copilot_engine.py:448 建议捕获更具体的异常类型

### 🟢 [LOW] 疑似未使用导入

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/copilot_engine.py`
- **详情**: copilot_engine.py: annotations, subprocess

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/deep_audit.py:99`
- **详情**: deep_audit.py:99 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/deep_audit.py:498`
- **详情**: deep_audit.py:498 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/deep_audit.py:509`
- **详情**: deep_audit.py:509 建议捕获更具体的异常类型

### 🟢 [LOW] 疑似未使用导入

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/deep_audit.py`
- **详情**: deep_audit.py: Tuple, annotations, os, subprocess

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/document_handler.py:48`
- **详情**: document_handler.py:48 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/document_handler.py:87`
- **详情**: document_handler.py:87 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/document_handler.py:152`
- **详情**: document_handler.py:152 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/document_handler.py:279`
- **详情**: document_handler.py:279 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/document_handler.py:315`
- **详情**: document_handler.py:315 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/document_handler.py:330`
- **详情**: document_handler.py:330 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/document_handler.py:347`
- **详情**: document_handler.py:347 建议捕获更具体的异常类型

### 🟢 [LOW] 疑似未使用导入

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/document_handler.py`
- **详情**: document_handler.py: annotations

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/kb_capture.py:111`
- **详情**: kb_capture.py:111 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/kb_capture.py:289`
- **详情**: kb_capture.py:289 建议捕获更具体的异常类型

### 🟢 [LOW] 疑似未使用导入

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/kb_capture.py`
- **详情**: kb_capture.py: Optional

### 🟢 [LOW] 疑似未使用导入

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/kb_maintenance.py`
- **详情**: kb_maintenance.py: Any, Dict, List, Optional, json

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/knowledge_base.py:87`
- **详情**: knowledge_base.py:87 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/knowledge_base.py:127`
- **详情**: knowledge_base.py:127 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/knowledge_base.py:329`
- **详情**: knowledge_base.py:329 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/knowledge_base.py:414`
- **详情**: knowledge_base.py:414 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/knowledge_base.py:429`
- **详情**: knowledge_base.py:429 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/knowledge_base.py:542`
- **详情**: knowledge_base.py:542 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/knowledge_base.py:689`
- **详情**: knowledge_base.py:689 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/knowledge_base.py:1141`
- **详情**: knowledge_base.py:1141 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/knowledge_base.py:1276`
- **详情**: knowledge_base.py:1276 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/knowledge_base.py:1343`
- **详情**: knowledge_base.py:1343 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/knowledge_base.py:999`
- **详情**: knowledge_base.py:999 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/knowledge_base.py:1037`
- **详情**: knowledge_base.py:1037 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/knowledge_base.py:1389`
- **详情**: knowledge_base.py:1389 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/knowledge_base.py:354`
- **详情**: knowledge_base.py:354 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/knowledge_base.py:1057`
- **详情**: knowledge_base.py:1057 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/knowledge_base.py:1274`
- **详情**: knowledge_base.py:1274 建议捕获更具体的异常类型

### 🟢 [LOW] 疑似未使用导入

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/knowledge_base.py`
- **详情**: knowledge_base.py: os

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/llm_router.py:37`
- **详情**: llm_router.py:37 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/llm_router.py:130`
- **详情**: llm_router.py:130 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/llm_router.py:526`
- **详情**: llm_router.py:526 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/llm_router.py:501`
- **详情**: llm_router.py:501 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/llm_router.py:422`
- **详情**: llm_router.py:422 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/llm_router.py:576`
- **详情**: llm_router.py:576 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/llm_router.py:371`
- **详情**: llm_router.py:371 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/logger.py:137`
- **详情**: logger.py:137 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/memory_manager.py:80`
- **详情**: memory_manager.py:80 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/memory_manager.py:179`
- **详情**: memory_manager.py:179 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/memory_manager.py:62`
- **详情**: memory_manager.py:62 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/memory_manager.py:341`
- **详情**: memory_manager.py:341 建议捕获更具体的异常类型

### 🟢 [LOW] 疑似未使用导入

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/memory_manager.py`
- **详情**: memory_manager.py: annotations

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/proactive_engine.py:139`
- **详情**: proactive_engine.py:139 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/proactive_engine.py:81`
- **详情**: proactive_engine.py:81 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/proactive_engine.py:327`
- **详情**: proactive_engine.py:327 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/proactive_engine.py:341`
- **详情**: proactive_engine.py:341 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/proactive_engine.py:159`
- **详情**: proactive_engine.py:159 建议捕获更具体的异常类型

### 🟢 [LOW] 疑似未使用导入

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/proactive_engine.py`
- **详情**: proactive_engine.py: annotations, get_relevant_memories

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/self_test.py:63`
- **详情**: self_test.py:63 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/self_test.py:78`
- **详情**: self_test.py:78 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/self_test.py:124`
- **详情**: self_test.py:124 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/self_test.py:138`
- **详情**: self_test.py:138 建议捕获更具体的异常类型

### 🟢 [LOW] 疑似未使用导入

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/self_test.py`
- **详情**: self_test.py: test_runner

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/session_manager.py:71`
- **详情**: session_manager.py:71 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/session_manager.py:80`
- **详情**: session_manager.py:80 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/session_manager.py:127`
- **详情**: session_manager.py:127 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/session_manager.py:202`
- **详情**: session_manager.py:202 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/session_manager.py:303`
- **详情**: session_manager.py:303 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/session_manager.py:249`
- **详情**: session_manager.py:249 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/session_manager.py:237`
- **详情**: session_manager.py:237 建议捕获更具体的异常类型

### 🟢 [LOW] 疑似未使用导入

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/session_manager.py`
- **详情**: session_manager.py: annotations

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/skill_manager.py:43`
- **详情**: skill_manager.py:43 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/tool_engine.py:112`
- **详情**: tool_engine.py:112 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/tool_engine.py:123`
- **详情**: tool_engine.py:123 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/tool_engine.py:132`
- **详情**: tool_engine.py:132 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/tool_engine.py:146`
- **详情**: tool_engine.py:146 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/tool_engine.py:165`
- **详情**: tool_engine.py:165 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/tool_engine.py:241`
- **详情**: tool_engine.py:241 建议捕获更具体的异常类型

### 🟢 [LOW] 疑似未使用导入

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/tool_engine.py`
- **详情**: tool_engine.py: Optional, os

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/upgrade.py:115`
- **详情**: upgrade.py:115 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/upgrade.py:289`
- **详情**: upgrade.py:289 建议捕获更具体的异常类型

### 🟢 [LOW] 疑似未使用导入

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/upgrade.py`
- **详情**: upgrade.py: datetime, json, os, timezone

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/usage_tracker.py:52`
- **详情**: usage_tracker.py:52 建议捕获更具体的异常类型

### 🟢 [LOW] 疑似未使用导入

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/usage_tracker.py`
- **详情**: usage_tracker.py: List, os

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/web_server.py:36`
- **详情**: web_server.py:36 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/web_server.py:812`
- **详情**: web_server.py:812 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/web_server.py:839`
- **详情**: web_server.py:839 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/web_server.py:860`
- **详情**: web_server.py:860 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/web_server.py:921`
- **详情**: web_server.py:921 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/web_server.py:911`
- **详情**: web_server.py:911 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/web_server.py:934`
- **详情**: web_server.py:934 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/web_server.py:421`
- **详情**: web_server.py:421 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/web_server.py:428`
- **详情**: web_server.py:428 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/web_server.py:457`
- **详情**: web_server.py:457 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/web_server.py:568`
- **详情**: web_server.py:568 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/web_server.py:599`
- **详情**: web_server.py:599 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/web_server.py:626`
- **详情**: web_server.py:626 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/web_server.py:659`
- **详情**: web_server.py:659 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/web_server.py:695`
- **详情**: web_server.py:695 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/web_server.py:725`
- **详情**: web_server.py:725 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/web_server.py:760`
- **详情**: web_server.py:760 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/web_server.py:772`
- **详情**: web_server.py:772 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/web_server.py:901`
- **详情**: web_server.py:901 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/web_server.py:404`
- **详情**: web_server.py:404 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/web_server.py:513`
- **详情**: web_server.py:513 建议捕获更具体的异常类型

### 🟢 [LOW] 过于宽泛的 except Exception

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/scripts/web_server.py:501`
- **详情**: web_server.py:501 建议捕获更具体的异常类型

### 🟢 [LOW] call_llm 返回值已正确解包

- **位置**: `scripts/copilot_engine.py`
- **详情**: chat_loop 中已修复 3 元组解包问题

---

## 前端（1 项）

### 🟢 [LOW] 前后端 API 路由一致

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/web/js/app.js`
- **详情**: app.js 中的主要 API 调用在 web_server.py 中均有处理

---

## 安全（1 项）

### 🟢 [LOW] os.system 已移除

- **位置**: `scripts/web_server.py`
- **详情**: web_server.py 中的 os.system 已替换为 subprocess.run

---

## 性能（2 项）

### 🟢 [LOW] 上下文构建基线

- **位置**: `scripts/context_builder.py`
- **详情**: 空会话上下文构建耗时 4.3ms，总字符 553

### 🟢 [LOW] Web 服务器导入耗时

- **位置**: `scripts/web_server.py`
- **详情**: web_server.py 导入耗时 29.3ms

---

## 数据完整性（2 项）

### 🟢 [LOW] session state 缺少 session_id

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/sessions/20260508-测试/state.json`
- **详情**: sessions/20260508-测试/state.json

### 🟢 [LOW] session state 缺少 session_id

- **位置**: `/Users/ll/Desktop/LinSai-CoPilot/sessions/20260508-测试任务系统/state.json`
- **详情**: sessions/20260508-测试任务系统/state.json

---

## 架构（1 项）

### 🟢 [LOW] 动态导入使用统计

- **位置**: ``
- **详情**: 7 个文件使用 importlib.util 动态导入（共 58 处）: context_builder.py, copilot_engine.py, deep_audit.py, kb_maintenance.py, tool_engine.py, upgrade.py, web_server.py

---

## 边界条件（3 项）

### 🟢 [LOW] 空 JSON 数组解析正常

- **位置**: `/var/folders/ky/29bynnbj7ss_4bkwbhm8rlnw0000gn/T/linsai_audit_i9trh6nu/empty.json`
- **详情**: 空 [] 正确解析为 Python 空列表

### 🟢 [LOW] 损坏 JSON 优雅失败

- **位置**: `/var/folders/ky/29bynnbj7ss_4bkwbhm8rlnw0000gn/T/linsai_audit_i9trh6nu/broken.json`
- **详情**: _read_json 对损坏 JSON 返回 None 而非抛异常

### 🟢 [LOW] 超大 JSON 值解析正常

- **位置**: `/var/folders/ky/29bynnbj7ss_4bkwbhm8rlnw0000gn/T/linsai_audit_i9trh6nu/huge.json`
- **详情**: 100KB 字符串值正确解析

---

## 修复优先级建议

### 建议修复（中/低）

- [ ] **疑似未使用导入** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/agora_bridge.py`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/backup_manager.py:149`
- [ ] **疑似未使用导入** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/backup_manager.py`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/chat_archive.py:70`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/chat_archive.py:82`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/chat_archive.py:196`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/chat_archive.py:235`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/chat_archive.py:369`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/chat_archive.py:150`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/chat_archive.py:249`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/chat_archive.py:381`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/context_builder.py:65`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/context_builder.py:79`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/context_builder.py:93`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/context_builder.py:136`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/context_builder.py:230`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/context_builder.py:271`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/copilot_engine.py:40`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/copilot_engine.py:208`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/copilot_engine.py:290`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/copilot_engine.py:573`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/copilot_engine.py:586`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/copilot_engine.py:451`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/copilot_engine.py:462`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/copilot_engine.py:475`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/copilot_engine.py:488`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/copilot_engine.py:502`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/copilot_engine.py:663`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/copilot_engine.py:367`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/copilot_engine.py:402`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/copilot_engine.py:93`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/copilot_engine.py:361`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/copilot_engine.py:384`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/copilot_engine.py:422`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/copilot_engine.py:448`
- [ ] **疑似未使用导入** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/copilot_engine.py`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/deep_audit.py:99`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/deep_audit.py:498`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/deep_audit.py:509`
- [ ] **疑似未使用导入** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/deep_audit.py`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/document_handler.py:48`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/document_handler.py:87`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/document_handler.py:152`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/document_handler.py:279`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/document_handler.py:315`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/document_handler.py:330`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/document_handler.py:347`
- [ ] **疑似未使用导入** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/document_handler.py`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/kb_capture.py:111`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/kb_capture.py:289`
- [ ] **疑似未使用导入** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/kb_capture.py`
- [ ] **疑似未使用导入** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/kb_maintenance.py`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/knowledge_base.py:87`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/knowledge_base.py:127`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/knowledge_base.py:329`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/knowledge_base.py:414`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/knowledge_base.py:429`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/knowledge_base.py:542`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/knowledge_base.py:689`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/knowledge_base.py:1141`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/knowledge_base.py:1276`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/knowledge_base.py:1343`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/knowledge_base.py:999`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/knowledge_base.py:1037`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/knowledge_base.py:1389`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/knowledge_base.py:354`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/knowledge_base.py:1057`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/knowledge_base.py:1274`
- [ ] **疑似未使用导入** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/knowledge_base.py`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/llm_router.py:37`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/llm_router.py:130`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/llm_router.py:526`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/llm_router.py:501`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/llm_router.py:422`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/llm_router.py:576`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/llm_router.py:371`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/logger.py:137`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/memory_manager.py:80`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/memory_manager.py:179`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/memory_manager.py:62`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/memory_manager.py:341`
- [ ] **疑似未使用导入** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/memory_manager.py`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/proactive_engine.py:139`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/proactive_engine.py:81`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/proactive_engine.py:327`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/proactive_engine.py:341`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/proactive_engine.py:159`
- [ ] **疑似未使用导入** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/proactive_engine.py`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/self_test.py:63`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/self_test.py:78`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/self_test.py:124`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/self_test.py:138`
- [ ] **疑似未使用导入** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/self_test.py`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/session_manager.py:71`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/session_manager.py:80`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/session_manager.py:127`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/session_manager.py:202`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/session_manager.py:303`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/session_manager.py:249`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/session_manager.py:237`
- [ ] **疑似未使用导入** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/session_manager.py`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/skill_manager.py:43`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/tool_engine.py:112`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/tool_engine.py:123`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/tool_engine.py:132`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/tool_engine.py:146`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/tool_engine.py:165`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/tool_engine.py:241`
- [ ] **疑似未使用导入** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/tool_engine.py`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/upgrade.py:115`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/upgrade.py:289`
- [ ] **疑似未使用导入** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/upgrade.py`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/usage_tracker.py:52`
- [ ] **疑似未使用导入** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/usage_tracker.py`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/web_server.py:36`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/web_server.py:812`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/web_server.py:839`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/web_server.py:860`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/web_server.py:921`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/web_server.py:911`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/web_server.py:934`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/web_server.py:421`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/web_server.py:428`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/web_server.py:457`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/web_server.py:568`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/web_server.py:599`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/web_server.py:626`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/web_server.py:659`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/web_server.py:695`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/web_server.py:725`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/web_server.py:760`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/web_server.py:772`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/web_server.py:901`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/web_server.py:404`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/web_server.py:513`
- [ ] **过于宽泛的 except Exception** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/web_server.py:501`
- [ ] **call_llm 返回值已正确解包** — `scripts/copilot_engine.py`
- [ ] **动态导入使用统计** — ``
- [ ] **session state 缺少 session_id** — `/Users/ll/Desktop/LinSai-CoPilot/sessions/20260508-测试/state.json`
- [ ] **session state 缺少 session_id** — `/Users/ll/Desktop/LinSai-CoPilot/sessions/20260508-测试任务系统/state.json`
- [ ] **空 JSON 数组解析正常** — `/var/folders/ky/29bynnbj7ss_4bkwbhm8rlnw0000gn/T/linsai_audit_i9trh6nu/empty.json`
- [ ] **损坏 JSON 优雅失败** — `/var/folders/ky/29bynnbj7ss_4bkwbhm8rlnw0000gn/T/linsai_audit_i9trh6nu/broken.json`
- [ ] **超大 JSON 值解析正常** — `/var/folders/ky/29bynnbj7ss_4bkwbhm8rlnw0000gn/T/linsai_audit_i9trh6nu/huge.json`
- [ ] **前后端 API 路由一致** — `/Users/ll/Desktop/LinSai-CoPilot/web/js/app.js`
- [ ] **工具调用降级已就绪** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/copilot_engine.py`
- [ ] **超时参数已配置** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/llm_router.py`
- [ ] **Provider 降级链已实现** — `/Users/ll/Desktop/LinSai-CoPilot/scripts/llm_router.py`
- [ ] **os.system 已移除** — `scripts/web_server.py`
- [ ] **上下文构建基线** — `scripts/context_builder.py`
- [ ] **Web 服务器导入耗时** — `scripts/web_server.py`
