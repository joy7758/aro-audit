# VPML A/B Evidence — Physical Anchor Uplift Lowers SCI  
# VPML A/B 证据页——物理锚点增强使 SCI 下降

---

## 1) Scope / 范围

**EN**  
This page documents a controlled A/B experiment showing that strengthening **physical anchoring** fields (fingerprint strength ↑, side-channel exposure ↓) reduces the **Sovereignty Collapse Index (SCI)** under an unchanged RTP topology.

**中文**  
本页记录一个严格控制变量的 A/B 实验：在 **RTP 拓扑不变** 的前提下，仅增强“物理锚点”字段（指纹强度 ↑、侧信道暴露 ↓），即可降低 **主权坍塌指数（SCI）**。

---

## 2) Experiment Design / 实验设计（控制变量）

### Fixed (Control Variables) / 固定项（控制变量）
**EN**
- Graph topology: identical nodes/edges structure
- Edge attributes: identical (`edge.assurance`, `edge.mediation`, `edge.observability`, `edge.latency`)
- All non-physical node attributes: identical (`trust.*`, `priv.*`, `obs.*`, `asset.*`)

**中文**
- 图拓扑：节点/边结构完全一致
- 边属性：完全一致（`edge.assurance`, `edge.mediation`, `edge.observability`, `edge.latency`）
- 除物理字段外的节点属性：完全一致（`trust.*`, `priv.*`, `obs.*`, `asset.*`）

### Changed (Single Treatment Variable) / 变化项（唯一处理变量）
**EN**  
Only the following fields on the same identity node are modified:

- Node: `DEV_PUF_WEAK`
- Fields:
  - `phy.fingerprint_strength`: **0.15 → 0.85**
  - `phy.sidechannel_exposure`: **0.75 → 0.15**

**中文**  
仅修改同一身份节点上的以下字段：

- 节点：`DEV_PUF_WEAK`
- 字段：
  - `phy.fingerprint_strength`：**0.15 → 0.85**
  - `phy.sidechannel_exposure`：**0.75 → 0.15**

**EN**  
This isolates the causal impact of physical anchoring in the VPML susceptibility term.

**中文**  
这保证了 SCI 的变化可被明确归因于 VPML 易损性项中的“物理锚点”调制。

---

## 3) Inputs / 输入

**EN**
- Baseline (Case A): `examples/pFDO_controlplane_case.yaml`
- Strong Anchor (Case B): `examples/pFDO_strong_anchor.yaml`

**中文**
- 基线（A 案例）：`examples/pFDO_controlplane_case.yaml`
- 强锚点（B 案例）：`examples/pFDO_strong_anchor.yaml`

---

## 4) How to Reproduce / 一键复现

**EN (recommended: virtual environment)**
```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .

examples/run_ab_compare.sh
```

**中文（推荐：使用虚拟环境）**

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .

examples/run_ab_compare.sh
```

---

## 5) Results / 结果（记录值）

**EN (recorded on current dev machine)**

* `SCI_A = 0.37129861687805465`
* `SCI_B = 0.301704044308845`
* `DELTA = -0.06959457256920965`
* Relative reduction ≈ **18.75%**

**中文（当前开发机记录值）**

* `SCI_A = 0.37129861687805465`
* `SCI_B = 0.301704044308845`
* `DELTA = -0.06959457256920965`
* 相对降幅 ≈ **18.75%**

**EN**
Interpretation: Under an identical RTP structure, improving physical anchoring reduces susceptibility-driven propagation and therefore lowers SCI.

**中文**
解释：在拓扑与其他参数一致时，物理锚点增强会降低易损性驱动的风险传播，从而使 SCI 下降。

---

## 6) Why This Matters / 为什么重要（产品叙事）

**EN**
VPML quantifies structure-driven risk propagation without requiring exploit details.
This A/B evidence shows that physical anchoring can be audited as a measurable risk-reduction control.

**中文**
VPML 在不依赖漏洞细节的情况下度量“结构性风险传播”。
本 A/B 证据证明：物理锚点可以被审计为“可量化的风险降低控制项”。

---
