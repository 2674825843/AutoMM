"""prob03 实现阶段接口探针（秒级小计算，不涉及完整数据集/完整反演）。

用途：implementation 阶段静态检查入口之一；核验 model.py 对 formulation_v002 公式的
数值实现（硅/碳化硅 Sellmeier、Airy↔两光束极限、极值位置不变性 L17、多光束必要条件 N1–N4、
finesse=π√R̄/(1−R̄)（R2 修正）、变量投影往返反演（shared/indep）、基线阶数稳健、
n_sub 幅度弱辨识、轮廓似然 CI、两角嵌套 F 检验、多光束改善率 η_mb 量级、SiC 重新判定 R̄ 量级）。

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
