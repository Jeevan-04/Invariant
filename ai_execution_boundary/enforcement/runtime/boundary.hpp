#pragma once
#include "execution_graph.hpp"
#include <memory>
#include <string>

namespace invariant {

class ExecutionBoundary {
public:
  ExecutionBoundary();
  ~ExecutionBoundary();

  // Prevent copying to ensure unique ownership of the execution state
  ExecutionBoundary(const ExecutionBoundary &) = delete;
  ExecutionBoundary &operator=(const ExecutionBoundary &) = delete;

  // Step 2: Load Policy
  void load_policy(const std::string &policy_name);

  // Step 7: Load Model Spec (Freezing configuration)
  void load_model(const ModelSpec &spec);

  // Load context
  void load_context(const ContextSpec &context);

  // Step 5: Admissibility Pre-Check
  // Returns true if admissible, raises exception or returns false otherwise
  bool precheck(const std::string &input_payload);

  // Step 7/9: Controlled Execution
  // Takes the input and returns the output token stream (as string for V0)
  std::string run(const std::string &input_payload);

  // Phase 8: Streaming Interface
  void start(const std::string &input_payload);
  bool step(const std::string &token);
  std::string get_output();

  // Step 8: Seal
  // Returns the cryptographic proof of the execution
  std::string seal();

private:
  struct Impl;
  std::unique_ptr<Impl> pimpl;
};

} // namespace invariant
