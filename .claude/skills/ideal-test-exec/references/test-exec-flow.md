# 测试执行流程图

```dot
digraph testexec_workflow {
    rankdir=TB;

    start [label="读取 P7-测试用例.md"];
    prepare [label="准备测试环境"];
    loop_start [label="获取下一个用例"];
    execute [label="执行测试"];
    record [label="记录结果"];
    defect [label="发现缺陷?"];
    log [label="记录缺陷"];
    more [label="还有用例?"];
    report [label="生成测试报告"];
    update [label="更新流程状态"];
    end [label="完成"];

    start -> prepare -> loop_start;
    loop_start -> execute -> record;
    record -> defect;
    defect -> log [label="是"];
    defect -> more [label="否"];
    log -> more;
    more -> loop_start [label="是"];
    more -> report [label="否"];
    report -> update -> end;
}
```

## 调试流程

测试失败时的处理：

```
测试失败
    │
    ▼
暂停测试
    │
    ▼
调用 debug 子代理
    │
    ├── Phase 1: 根因调查
    ├── Phase 2: 模式分析
    ├── Phase 3: 假设测试
    └── Phase 4: TDD 修复
    │
    ▼
修复成功？
    ├── 是 → 重新执行测试
    └── 否 → 记录缺陷，等待人工介入
```
