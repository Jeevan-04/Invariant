# Invariant: The AI Execution Kernel

> "What if we could prove exactly why an AI did what it did?"

## The Problem
We treat AI models like magic black boxes. We feed them inputs, cross our fingers, and hope for the best. When they fail—when they hallucinate, leak data, or break rules—we have no way to prove *why*. We just add more "safety prompts" and hope again.

I wasn't satisfied with hope. I wanted **proof**.

## The Idea
**Invariant** is an answer to a simple question: **Can we build a kernel for AI?**

Operating systems have kernels to stop programs from accessing memory they shouldn't. AI needs a similar boundary—a layer of mandatory enforcement that sits between the model and the world. 

This isn't just an "LLM Wrapper". It's a **C++ Enforcement Plane**. It treats the AI as untrusted compute.

## The Journey

### Phase 1: The Boundary
I started by building a wall. I separated the system into two planes:
1.  **Python Control Plane**: The "User Space". It asks for things.
2.  **C++ Enforcement Plane**: The "Kernel". It decides if those things are allowed.
There is no bypass. If the C++ layer says no, the execution dies.

### Phase 2: Causality & Proofs
Blocking bad outputs wasn't enough. I needed to *prove* that an execution was valid. 
I implemented a cryptographic proof engine. It hashes the Model ID, the Policy, the Context, and the Code. If any of these change—even by a single bit—the Proof ID changes. 
Now, we have **Causality-Bound Execution**.

### Phase 8: The Kernel (Token-Level Control)
The breakthrough. I moved from checking "Text Blobs" to checking "Streams".
The Invariant Kernel now intercepts the Model's generation **token by token**.
If a model starts to say something forbidden, the kernel kills the process mid-sentence. 
It’s like a neurological filter for AI.

## Features

*   **🛡️ Mandatory Policy**: Policies are enforced in C++ (Regex/Logic). 
*   **🇮🇳 The Patriot Policy Demo**: A demo configuration that strictly allows only pro-India content and blocks mentions of other geopolitical entities. It proves how precise the control can be.
*   **📜 Epistemic Receipts**: Every execution generates a `receipt.v1` JSON file. It’s a mathematical guarantee of what happened.
*   **⏪ Replay Verification**: You can take a receipt from last week and "replay" it. If the context files have changed (drift), the replay fails. It’s a closed loop.

## How to Run

1.  **Install**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **The UI (Streamlit)**:
    ```bash
    streamlit run app.py
    ```
    *Experience the Patriot Policy in action.*

3.  **The CLI**:
    ```bash
    python3 cli.py
    ```

## Philosophy
We are moving from "Probabilistic Safety" (it *probably* won't do that) to "Deterministic Invariance" (it *cannot* do that).

Invariant is the first step towards an **Epistemic System**—where AI execution is not just observed, but proven.
