---
date:
  created: 2025-09-24

authors:
  - dooms

categories:
  - Roadmap

tags:
  - v0.3
  - roadmap
  - announcement

slug: followup-v0.3-roadmap
---


# Follow up on the roadmap for version 0.3


As discussed [previously](2025-09-09_roadmap_v0.3.md), I will give a little bit more information on the actual roadmap.

<!-- more -->

Considering I am focusing on studying, designing and writing code for H-hat in the coming weeks/months with part-time dedication and eventually some people will be helping here and there, the goals and timelines are:

## Codebase

> [!NOTE]
>
> The order of the items does not reflect their priority or implementation order.
>

### September

#### Finish minimal function implementation capabilities

How to invoke built-in, in-code or external (library/package) functions. In principle, they should use the same principles behind. In the case of built-in ones, a special space of the `BaseIRInstr` class so it can also follow the same workflow, aka be called through `resolve` method to address the correct function.

Considering Heather dialect uses function overloading, it will try to find the correct function through the combination of arguments types provided and the given function name. However, it cannot figure out the function output type, so a same function same with same number and types of arguments must not have different definitions with different outputs.


#### Add minimal built-in functions (dialect or core?)

A very specific set of built-in functions will be added at this moment. Hopefully I can get enough feedback to choose the best ones for the first working version. So your feedback matters here (or anywhere where you can find me, really)!

It is still uncertain whether it should be: (1) a core feature or a dialect-specific feature, (3) available by default or need to do some function importing.


#### Implement cast system

Cast system is a core feature of H-hat, and it has been tried a few times so far, with different outcomes from each iteration. I will write more about it in a separated post, but so far it suffices to say that this feature contains the heart of all I think is important to provide the proper level of high abstraction from programmers using quantum resources.


#### Refactor/reimplement OpenQASMv2 code logic and structure

This needs to be rethought... again. This part always seems easy and lazy to do, but always prove hard to be good enough to be extensible for all the optimizations and passes available by Qiskit ecosystem or some other custom-made features, and at the same time have a robust enough base API to be used by it or any other low level language (such as NetQASM). I keep postponing improving this part... maybe other things are more priority or interesting.


### October

#### Finish cast system implementation (structure and logic)

Nothing much to say here. Cast system is a delicate structure that interfaces quantum types with classical ones while performing all the execution requests, checks and casting type part for the quantum programs. It may take longer, but I hope that I have enough experience and material from previous iterations to finalize it by October (at most beginning of November?).


#### Finish working on OpenQASMv2 base code

I may drag this throughout October, but be nice (or do it for me 👼 ).


#### Refactor/reimplement Qiskit code logic and structure for target backends (no optimizations, extra passes, etc. yet)

This part is less traumatic than the OpenQASMv2 part (can't even start thinking of OpenQASMv3 yet), but it needs to have a good base API to handle not only Qiskit but also any other target backend infrastructure, such as NetQASM/SquidASM/AWSBraket/etc. So in the end, doing Qiskit will help shape the base API for it (and of course implement it throughout the process) and future backends.


#### Implement modifier feature

Modifier is a nice (I hope) feature I have been thinking that may bring some power to the programmer and also clarity on the code. It basically enables to modify the behavior, property or add extra properties to some instance, should it be a variable or a function, for example. The syntax is `something<mdfr-arg1=mdfr-value1 mdfr-arg2=mdfr-value2>`, where the `<>` brackets defines the scope of the modifier for a given instance (`something` in this case). A few simple examples:

- `some-var<&>` means the reference of `some-var`, or `&some_var` in some other languages, like Rust or C
- `@some-var<shots=3000>` means it will use `3000` shots for this quantum variable execution on the backend, regardless the default configuration is

In most cases, the modifier argument needs a argument name and a value. In specific unequivocal cases, a symbol alone can be used (as is the case of the reference `&`). It may stack modifiers and their order must not matter, unless they are used in different moments throughout the code. In the later case, the current modifier overwrites any repeated modifier argument, but must use all previous ones.

_Maybe having a tag in the modifier stating "use it once" should be a good idea, so that the modifier will only work at that specific moment and not after._


### November

#### More modifier

Hopefully it will be done by November.


#### Meta module feature

Something that bothers me _a lot_ in Python is the hacky way to do dynamic imports. So I thought "why not trying to do something better, like creating a meta module with a template so other modules can use it and define their expected functions and behaviors?". Seemed a good idea, so I am going to implement it. Still unsure whether it makes sense to be implemented at this point, but I see potential and need for it.


#### NetQASM implementation

It is not the first implementation, but _will be_ the first successful working one. On the previous ones, I spent too much time fighting with divergent approaches and could never make up my mind on which one to use. In the end, I had to focus on other things, and it was put aside to freeze. It will basically take the same ideas from OpenQASMv2 successful implementation and, using the base API, should be no more than writing down the NetQASM-specific instructions.

Previously, I was stuck because NetQASM uses a very thoughtful approach to have internal memory for classical and quantum data inside its routines. It was very nice for NetQASM, but very hard to access it smoothly from the outside to read or write its content. I ended up lost in their code logic and couldn't find a neat solution at that time without changing H-hat internals. Result: I _had_ to change H-hat internals to account for that. So I decided to create a memory manager for quantum programs that basically handles classical and quantum memory, qubits, scopes and other relevant resources. It is still not extensible, so if in the future some other low level language requires other kinds of features, I may need to rethink... again.

### December

December will be full of wrapping up previous tasks.


### January

#### NetSquid/SquidASM

Then, it comes to the time of implementing NetSquid/SquidASM (maybe Simulaqron?) backend. I just think that having at least one "standalone" and one quantum networks backends would make sense to test, try and develop relevant features that the language want the programmer to benefit from and also to learn how to create them.


#### Distributed features

Besides the quantum networks backend, H-hat needs to have some support that can show such capabilities even if just on simulators. So having distributed features is very important, but maybe not detrimental for the release of version 0.3. Let's see how it works out.

#### Release!(?)

At this point, it should be able to be good enough to at least be tested. Hopefully, kind people will join to help feedback, guide and improve the features, language and its ecosystem, and maybe even be part of the community!


### February

I expect February be a January++.


## Conferences

Besides the code development side, some interesting conferences are right in the horizon and I think they cannot be missed (again). I missed a few ones this year due to work and personal reasons, for instance, the 2nd Workshop on Quantum Software 2025 in Seoul (https://pldi25.sigplan.org/home/wqs-2025) and the 7th International Workshop on Quantum Compilation in Helsinki (https://quantum-compilers.github.io/iwqc25/). So now, there are a few opportunities coming up due this year:

- Munich Quantum Software Forum 2025 (https://www.cda.cit.tum.de/research/quantum/mqsf/); _H-hat was accepted and is attending! preparations in progress_
- Seventh International Workshop on Quantum Software Engineering (Q-SE 2026) (https://conf.researchr.org/home/icse-2026/q-se-2026); _checking viability_
- International Conference on Quantum Communications, Networking, and Computing (QCNC 2026) (https://www.ieee-qcnc.org/2026/); _draft in progress_


## On the stable version part

Depending on how things evolve people-wise, code-wise, time-wise, opportunities-wise, it may be possible to resume the Rust side, making the _actual JIT compiler_ for the stable version. And that is another exciting challenge and project on its own that I have been studying and testing a few things (with less frequency). Using [Pliron](https://github.com/vaivaswatha/pliron), [Cranelift](https://github.com/bytecodealliance/wasmtime/tree/main/cranelift) or [Melior](https://github.com/mlir-rs/melior) framework?

I have been in touch with Pliron's creator and collaborators, and it has been a very interesting experience so far to learn about it. Still unsure how practical it can be to use on its current state for H-hat current needs, but definitely I want to test it in practice. Cranelift is another one that caught my attention, especially because its JIT compiler-driven features already in place.

If that depends only on me, I will try to use whatever uses less C++ for now.


## Final remarks

I hope this post can bring some light on what is in progress and what is planned for the coming months. Hopefully more people can join the effort! Feedback, reviews, discussions, beta testing, coding, designing, emotional support. Anything helps!

Well, that is it. Until the next post.
