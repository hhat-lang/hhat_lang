# from hhat_lang import types
from .protocols import protocols_list, Protocols, BiggestValue, WeightedAverage


# def use_protocol(f):
#     def inner_func(itself, other):
#         if isinstance(itself, types.ArrayCircuit):
#             from hhat_lang import grammar
#
#             if isinstance(
#                 other,
#                 (
#                     types.Gate,
#                     types.GateArray,
#                     types.ArrayCircuit,
#                     types.SingleHashmap,
#                     types.ArrayHashmap,
#                     grammar.AST,
#                 ),
#             ):
#                 return f(itself, other)
#             if isinstance(
#                 other,
#                 (
#                     types.SingleInt,
#                     types.ArrayInt,
#                     types.SingleStr,
#                     types.ArrayStr,
#                     types.SingleBool,
#                     types.ArrayBool,
#                 ),
#             ):
#                 protocol = protocols_list.get(itself.protocol, None)
#                 if protocol is not None:
#                     pass
#                 raise ValueError(f"{itself.name}: trying to use invalid protocol for circuit type.")
#         if isinstance(
#             other,
#             (
#                 types.SingleInt,
#                 types.ArrayInt,
#                 types.SingleStr,
#                 types.ArrayStr,
#                 types.SingleBool,
#                 types.ArrayBool,
#                 types.SingleHashmap,
#                 types.ArrayHashmap,
#             ),
#         ):
#             return f(itself, other)
#         if isinstance(other, (types.Gate, types.GateArray, types.ArrayCircuit)):
#             protocol = protocols_list.get(itself.protocol, None)
#             if protocol is not None:
#                 pass
#             raise ValueError(f"{itself.name}: trying to use invalid protocol for circuit type.")
#         raise ValueError(f"{itself.name}: invalid operation with {other.__class__.__name__}.")
#
#     return inner_func
