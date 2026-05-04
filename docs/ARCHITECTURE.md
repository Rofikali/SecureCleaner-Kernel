# System Architecture - SecureCleaner Kernel

## 1. Overview

The SecureCleaner is built on a **Modular Micro-Kernel** architecture. It decouples system events, business logic, and the user interface to ensure high availability and security.

## 2. Design Patterns

### A. Facade Pattern (`main.py` & `core/app.py`)

We use the **Facade Pattern** to wrap the complexity of multiple background threads (Observer, Heartbeat, and Tray UI).

- **Intent:** Provide a simplified interface to the complex subsystems.
- **Implementation:** The `CleanerApp` class acts as the Orchestrator. The entry point (`main.py`) only needs to call `app.bootstrap()`, hiding the manual thread management and OS-level process handling.

### B. Strategy Pattern (`core/strategy.py`)

The categorization logic is decoupled using the **Strategy Pattern**.

- **Intent:** Define a family of algorithms (sorting rules), encapsulate each one, and make them interchangeable.
- **Implementation:** `ExtensionStrategy` allows the kernel to change how files are sorted (via JSON mappings) without modifying the execution logic in `CleanHandler`. This makes the system extensible for future "MIME-type" or "ML-based" sorting strategies.

### C. Observer Pattern (`watchdog`)

The system utilizes the **Observer Pattern** to react to OS-level signals.

- **Implementation:** The `CleanHandler` observes `FileSystemEvents`. This ensures zero CPU waste, as the code only executes when the OS signals a file change.

## 3. Core Algorithms

- **Exponential Backoff:** Used in `move_with_retry` to handle file-lock contention during browser downloads.
- **Recursive Directory Cleanup:** A depth-first search algorithm to prune empty directory trees post-cleanup.

## mermaid ( Very Important )

    graph TD
        A[main.py] -->|Initializes| B[CleanerApp Kernel]
        B --> C[Tray UI Manager]
        B --> D[File Observer]
        D -->|Triggers| E[CleanHandler Engine]
        E -->|Consults| F[Extension Strategy]
        E -->|Audits to| G[Security Guard]
        G -->|Atomic Sync| H[(Physical Disk)]
