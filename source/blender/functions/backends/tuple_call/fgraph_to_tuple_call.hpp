#pragma once

#include "tuple_call.hpp"

namespace FN {

	TupleCallBody *fgraph_to_tuple_call(
		const FunctionGraph &function_graph);

} /* namespace FN */