#pragma once
#include <map>
#include <sstream>
#include <string>
#include <vector>

namespace invariant {

struct Identity {
  std::string user_id;
  std::string role;
  std::string org;
  std::string env;
};

struct ModelSpec {
  std::string provider;
  std::string name;
  std::string version;
  int seed;
  std::string decoding_strategy;
};

struct ContextSource {
  std::string type;
  std::string sensitivity;
  std::string identifier;
  std::string content_hash;
};

struct ContextSpec {
  std::vector<ContextSource> sources;
};

// The execution graph structure that must be frozen before execution
struct ExecutionGraph {
  std::string id;
  Identity identity;
  std::string input_payload;
  std::string policy_name;
  ModelSpec model;
  ContextSpec context;

  // Compute a deterministic hash of the frozen graph
  std::string compute_hash() const {
    std::stringstream ss;
    ss << id << "|";
    ss << identity.user_id << ":" << identity.role << ":" << identity.org << ":"
       << identity.env << "|";
    ss << input_payload << "|";
    ss << policy_name << "|";
    ss << model.provider << ":" << model.name << ":" << model.version << ":"
       << model.seed << ":" << model.decoding_strategy << "|";

    for (const auto &src : context.sources) {
      ss << src.type << ":" << src.sensitivity << ":" << src.identifier << ":"
         << src.content_hash << ";";
    }
    return ss.str();
  }
};

} // namespace invariant
