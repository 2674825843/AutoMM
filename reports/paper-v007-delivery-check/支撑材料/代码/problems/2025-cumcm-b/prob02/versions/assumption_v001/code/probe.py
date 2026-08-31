"""prob02 实现阶段接口探针（秒级小计算，不涉及完整数据集/完整反演）。

用途：implementation 阶段静态检查入口之一；核验 model.py 对 formulation_v003 公式的
数值实现（Sellmeier/Fischer 色散、带内 N-SE/N-SE-delta/N-const、正模型物理边界、
**v003 变量投影往返反演（shared/indep）**、基线阶数稳健、n_sub 幅度弱辨识、轮廓似然 CI、
两角嵌套 F 检验、以及 v002 复用项：P2 联合往返、t–n_sub 解耦、解析 CI、预处理机制）。

用法：
    python code/probe.py
"""

from __future__ import annotations

import model


def main() -> int:
    results = model.run_probes()
    for name, passed in sorted(results.items()):
        print(f"{'PASS' if passed else 'FAIL'}  {name}")
    total = len(results)
    passed_count = sum(1 for passed in results.values() if passed)
    print(f"probe 汇总：{passed_count}/{total} 通过")
    return 0 if passed_count == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
