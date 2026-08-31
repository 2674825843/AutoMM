"""prob01 实现阶段接口探针（秒级小计算，不涉及完整数据集/完整反演）。

用途：implementation 阶段静态检查入口之一；核验 model.py 对 formulation_v001 公式的
数值实现是否与 formula_validation.md 的探针值一致（Sellmeier、光程差等价性、
理论间隔数量级、正模型物理边界、小型往返反演）。

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
