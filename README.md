# Invariant: The AI Execution Kernel

> "We built a kernel for AI. And it works."

## The Core Concept
**Invariant** is not a moderation tool. It is an **Execution Kernel**.
It intercepts the model's generation **token by token** in C++. If the model attempts to generate a forbidden sequence, the kernel terminates the process mid-stream.

## The Active Policy: Reality-Only AI
Currently, the kernel is configured with the **"No Hypotheticals" Protocol**.
The AI is allowed to discuss:
*   What exists
*   What has happened
*   What is documented

It is **HARD-BLOCKED** if it attempts to:
*   "Imagine if..."
*   "What if..."
*   "Suppose that..."

### Why Regex? (The "Hello World" of Compliance)
We use regular expressions in this demo because they are **transparent**. You can see exactly *why* a token was blocked.
**Do not confuse the configuration with the machinery.**
The Invariant Kernel is agnostic. In production, policies can be:
- Formal verification specifications
- Neural classifier decisions
- Complex RBAC logic

Regex is simply the clearest way to demonstrate the **Enforcement Boundary** without ambiguity.

**Why?**
This demonstrates that the **AI reasoning space itself can be bounded.**
It is not ideological. It is structural. The kernel forces the model to remain in reality.

---

## Development Phases (V0 -> V1)

We built this system in 12 distinct phases to ensure architectural rigor.

**Phase 1: The Boundary**
*   Separated the system into `Control Plane` (Python) and `Enforcement Plane` (C++).
*   Established the `ExecutionGraph` as the source of truth.

**Phase 2: Causality & Proofs**
*   Implemented `invariant.receipt.v0`.
*   Every execution is hashed (Model + Policy + Context + Code).

**Phase 3: The Model Adapter (Mock)**
*   Created `MockAdapter` to simulate token streams for deterministic testing.

**Phase 4: Policy Engine v0**
*   Implemented basic strict string matching in C++.

**Phase 5: Context Injection**
*   Added `ContextSpec` to load external files into the graph.

**Phase 6: Replayability**
*   Built `replay.py` to verify past receipts against current kernel code.
*   "Time-Travel Debugging" for AI.

**Phase 7: The Orchestrator**
*   Unified the components into a single `orchestrator.py` engine.

**Phase 8: Token-Level Control (The Breakthrough)**
*   Moved from checking "blobs" to checking "streams".
*   Kernel now intercepts execution at the byte level.

**Phase 9: UI & Publication**
*   Built the Streamlit interface for real-time inspection.

**Phase 10: Active Kernel Logic**
*   Implemented rolling-buffer regex in C++.
*   Enabled mid-stream abortion of violations.

**Phase 11: Scalable Native Hashing**
*   Implemented `crypto::hash_file` in C++ for GB-scale context integrity.

**Phase 12: Cryptographic Signatures**
*   Integrated **Ed25519** signing.
*   Every receipt is now cryptographically attributable to the node.

---

## Usage

1.  **Run the Kernel**:
    ```bash
    streamlit run app.py
    ```
2.  **Verify a Receipt**:
    ```bash
    python3 replay.py demo_receipt.json
    ```

**Status**: V1 Release Stable.
