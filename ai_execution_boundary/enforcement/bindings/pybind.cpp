#include "../runtime/boundary.hpp"
#include "../runtime/crypto_utils.hpp"
#include "../runtime/execution_graph.hpp"
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;
using namespace invariant;

PYBIND11_MODULE(invariant_enforcement, m) {
  m.doc() = "Invariant C++ Enforcement Plane Bindings";

  // Bind structs
  py::class_<Identity>(m, "Identity")
      .def(py::init<>())
      .def_readwrite("user_id", &Identity::user_id)
      .def_readwrite("role", &Identity::role)
      .def_readwrite("org", &Identity::org)
      .def_readwrite("env", &Identity::env);

  py::class_<ModelSpec>(m, "ModelSpec")
      .def(py::init<>())
      .def_readwrite("provider", &ModelSpec::provider)
      .def_readwrite("name", &ModelSpec::name)
      .def_readwrite("version", &ModelSpec::version)
      .def_readwrite("seed", &ModelSpec::seed)
      .def_readwrite("decoding_strategy", &ModelSpec::decoding_strategy);

  py::class_<ContextSource>(m, "ContextSource")
      .def(py::init<>())
      .def_readwrite("type", &ContextSource::type)
      .def_readwrite("sensitivity", &ContextSource::sensitivity)
      .def_readwrite("identifier", &ContextSource::identifier)
      .def_readwrite("content_hash", &ContextSource::content_hash);

  py::class_<ContextSpec>(m, "ContextSpec")
      .def(py::init<>())
      .def_readwrite("sources", &ContextSpec::sources);

  // Bind ExecutionBoundary
  py::class_<ExecutionBoundary>(m, "ExecutionBoundary")
      .def(py::init<>())
      .def("load_policy", &ExecutionBoundary::load_policy,
           "Load a compiled policy by name")
      .def("load_model", &ExecutionBoundary::load_model,
           "Freeze model configuration")
      .def("load_context", &ExecutionBoundary::load_context,
           "Load context sources")
      .def("precheck", &ExecutionBoundary::precheck,
           "Run admissibility pre-check")
      .def("run", &ExecutionBoundary::run, "Execute the model proxy")
      .def("start", &ExecutionBoundary::start, "Start streaming execution")
      .def("step", &ExecutionBoundary::step, "Process one token")
      .def("get_output", &ExecutionBoundary::get_output,
           "Get accumulated output")
      .def("seal", &ExecutionBoundary::seal, "Seal and produce proof");

  // Expose Crypto Utils
  m.def("crypto_hash_file", &invariant::crypto::SHA256::hash_file,
        "Compute hash of a file efficiently");
}
