#include "boundary.hpp"
#include "crypto_utils.hpp"
#include <fstream>
#include <iostream>
#include <regex>
#include <sstream>
#include <stdexcept>

namespace invariant {

struct PolicyRule {
  std::string id;
  std::string type;
  std::string pattern;
};

std::string unescape_json(const std::string &input) {
  std::string res;
  for (size_t i = 0; i < input.length(); ++i) {
    if (input[i] == '\\' && i + 1 < input.length()) {
      char next = input[i + 1];
      if (next == '\\')
        res += '\\';
      else if (next == 'n')
        res += '\n';
      else if (next == 't')
        res += '\t';
      else if (next == '"')
        res += '"';
      else
        res += next;
      i++;
    } else {
      res += input[i];
    }
  }
  return res;
}

std::vector<PolicyRule> parse_simple_rules(const std::string &content) {
  std::vector<PolicyRule> rules;
  // VERY Basic manual parser for V0
  // searches for "pattern": "VALUE"
  std::size_t pos = 0;
  while ((pos = content.find("\"pattern\":", pos)) != std::string::npos) {
    std::size_t start_quote = content.find("\"", pos + 10);
    if (start_quote == std::string::npos)
      break;
    std::size_t end_quote = content.find("\"", start_quote + 1);
    if (end_quote == std::string::npos)
      break;

    std::string raw_pat =
        content.substr(start_quote + 1, end_quote - start_quote - 1);
    std::string pat = unescape_json(raw_pat);

    // Simple unescape for spaces if needed, but for now take raw
    rules.push_back({"auto_id", "deny_regex", pat});
    pos = end_quote;
  }
  return rules;
}

struct ExecutionBoundary::Impl {
  std::string current_policy_name;
  std::vector<PolicyRule> active_rules;
  ModelSpec model_spec;
  ContextSpec context_spec;
  std::string last_input_payload;
  std::string last_output;
  bool model_loaded = false;
  bool policy_loaded = false;
};

ExecutionBoundary::ExecutionBoundary() : pimpl(std::make_unique<Impl>()) {
  std::cout << "[Invariant] Enforcement Boundary Initialized" << std::endl;
}

ExecutionBoundary::~ExecutionBoundary() = default;

void ExecutionBoundary::load_policy(const std::string &policy_name) {
  pimpl->current_policy_name = policy_name;

  // Try to read file if it looks like a path or just use name
  std::string path = policy_name;
  if (policy_name.find("/") == std::string::npos &&
      policy_name.find(".json") == std::string::npos) {
    // It's just a name, assume default or ignore for now
  } else {
    std::ifstream f(path);
    if (f.good()) {
      std::stringstream buffer;
      buffer << f.rdbuf();
      pimpl->active_rules = parse_simple_rules(buffer.str());
      std::cout << "[Invariant] Loaded " << pimpl->active_rules.size()
                << " rules from " << path << std::endl;
    } else {
      std::cout << "[Invariant] Warning: Could not open policy file: " << path
                << std::endl;
    }
  }

  pimpl->policy_loaded = true;
  std::cout << "[Invariant] Policy Loaded: " << policy_name << std::endl;
}

void ExecutionBoundary::load_model(const ModelSpec &spec) {
  pimpl->model_spec = spec;
  pimpl->model_loaded = true;
  std::cout << "[Invariant] Model Configuration Frozen: " << spec.name
            << " (Seed: " << spec.seed << ")" << std::endl;
}

void ExecutionBoundary::load_context(const ContextSpec &context) {
  pimpl->context_spec = context;
  std::cout << "[Invariant] Context Loaded: " << context.sources.size()
            << " sources" << std::endl;
}

bool ExecutionBoundary::precheck(const std::string &input_payload) {
  std::cout << "[Invariant] Running Admissibility Pre-Check..." << std::endl;
  // Check invariants
  if (!pimpl->policy_loaded)
    throw std::runtime_error("No policy loaded");
  if (!pimpl->model_loaded)
    throw std::runtime_error("No model specification loaded");

  // Placeholder logic: fail if input contains "ILLEGAL"
  // NOW: Check active rules
  if (input_payload.find("ILLEGAL") != std::string::npos) {
    // Legacy check, keep for safety
    std::cout << "[Invariant] Pre-Check FAILED: Legacy ILLEGAL check."
              << std::endl;
    return false;
  }

  for (const auto &rule : pimpl->active_rules) {
    if (rule.type == "deny_regex") {
      // Basic regex check
      try {
        // Note: C++ regex might be slow or strict, for V0 basic find or regex
        // We'll use std::regex for "realness" with case-insensitive flag
        std::regex re(rule.pattern, std::regex_constants::icase);
        if (std::regex_search(input_payload, re)) {
          std::cout
              << "[Invariant] Pre-Check FAILED: Input matched deny_regex '"
              << rule.pattern << "'" << std::endl;
          return false;
        }
      } catch (...) {
        // Fallback if bad regex
        if (input_payload.find(rule.pattern) != std::string::npos) {
          std::cout << "[Invariant] Pre-Check FAILED: Input matched pattern "
                       "(fallback) '"
                    << rule.pattern << "'" << std::endl;
          return false;
        }
      }
    }
  }

  std::cout << "[Invariant] Pre-Check PASSED." << std::endl;
  return true;
}

std::string ExecutionBoundary::run(const std::string &input_payload) {
  if (!precheck(input_payload)) {
    throw std::runtime_error(
        "Execution Aborted: Policy Violation in Pre-Check");
  }

  pimpl->last_input_payload = input_payload;
  std::cout << "[Invariant] Execution Started (Proxied)..." << std::endl;
  // Real implementation would invoke model adapter here
  pimpl->last_output = "Simulated Output: Execution Allowed";
  return pimpl->last_output;
}

void ExecutionBoundary::start(const std::string &input_payload) {
  if (!precheck(input_payload)) {
    throw std::runtime_error(
        "Execution Aborted: Policy Violation in Pre-Check");
  }
  pimpl->last_input_payload = input_payload;
  pimpl->last_output = "";
  std::cout << "[Invariant] Execution Started (Streaming Mode)..." << std::endl;
}

bool ExecutionBoundary::step(const std::string &token) {
  // V0: Append token. Future: Check token against policy (e.g. pattern matching
  // on buffer)
  pimpl->last_output += token;
  return true;
}

std::string ExecutionBoundary::get_output() { return pimpl->last_output; }

std::string ExecutionBoundary::seal() {
  std::cout << "[Invariant] Sealing Execution Proof..." << std::endl;

  std::stringstream proof_data;
  proof_data << "POLICY:" << pimpl->current_policy_name << "|";
  proof_data << "MODEL:" << pimpl->model_spec.name << ":"
             << pimpl->model_spec.seed << "|";

  // Include Context Attribution
  if (!pimpl->context_spec.sources.empty()) {
    proof_data << "CONTEXT:";

    // Create a local copy of pointers to sort deterministically
    std::vector<const ContextSource *> sorted_sources;
    for (const auto &src : pimpl->context_spec.sources) {
      sorted_sources.push_back(&src);
    }

    // Canonical Sort: By Identifier
    std::sort(sorted_sources.begin(), sorted_sources.end(),
              [](const ContextSource *a, const ContextSource *b) {
                return a->identifier < b->identifier;
              });

    for (const auto *src : sorted_sources) {
      proof_data << src->identifier << ":" << src->content_hash << ";";
    }
    proof_data << "|";
  }

  proof_data << "INPUT:" << pimpl->last_input_payload << "|";
  proof_data << "OUTPUT:" << pimpl->last_output << "|";

  return crypto::SHA256::hash(proof_data.str());
}

} // namespace invariant
