---
title: H-hat — quantum programming for software developers
description: H-hat is a rule system, compiler framework, and a statically typed, functional and distributed-system inspired, hybrid quantum-classical programming language family.
hide:
  - navigation
  - toc
---

<div class="hh-home" markdown>

<!-- ============================================================ -->
<!-- HERO                                                          -->
<!-- ============================================================ -->

<section class="hh-hero" markdown>

<div class="hh-hero__text" markdown>

<span class="hh-eyebrow">Pre-release &middot; v0.3 in development</span>

<h1 class="hh-hero__title">Quantum programming<br><span class="hh-hl">for software developers.</span></h1>

<p class="hh-lead">
H-hat is a <strong>rule system</strong>, a <strong>compiler framework</strong>, and a
<strong>statically typed, functional, distributed-system inspired</strong> family of
hybrid quantum&ndash;classical programming languages. Classical and quantum code live in
the same program &mdash; and no quantum physics is required to write it.
</p>

<div class="hh-actions">
  <a class="hh-btn hh-btn--primary" href="getting_started/">Get started</a>
  <a class="hh-btn" href="dialects/heather/syntax/">Learn Heather</a>
  <a class="hh-btn hh-btn--ghost" href="https://github.com/hhat-lang/hhat_lang/">GitHub &nearr;</a>
</div>

<p class="hh-badges">
  <a href="https://unitary.foundation"><img alt="Supported by Unitary Foundation" src="https://img.shields.io/badge/Supported%20By-Unitary%20Foundation-FFFF00.svg"></a>
  <a href="http://discord.unitary.foundation"><img alt="Discord" src="https://img.shields.io/badge/dynamic/json?color=blue&label=Discord&query=approximate_presence_count&suffix=%20online.&url=https%3A%2F%2Fdiscord.com%2Fapi%2Finvites%2FJqVGmpkP96%3Fwith_counts%3Dtrue"></a>
</p>

</div>

<div class="hh-window" markdown>

<div class="hh-window__bar"><span></span><span></span><span></span><em>hoi quantum</em></div>

=== "src/main.hat"

    ```hhat-heather
    main {
      print("hoi quantum")       // classical, as usual

      // quantum data: lazy, linear, prefixed with @
      @q:@bell_t =.{@s=@false @t=@false}
      @sync(@q)

      // the cast evaluates @q and realizes its result
      res:hashmap = @q * hashmap
      print(res)
    }
    ```

=== "src/hat_types/bell.hat"

    ```hhat-heather
    // a quantum struct may hold quantum
    // (and classical) members
    type @bell_t {
      @s:@bool
      @t:@bool
    }
    ```

</div>

</section>

<!-- ============================================================ -->
<!-- DEFINITION (dictionary entry) + AT A GLANCE                   -->
<!-- ============================================================ -->

<section class="hh-define" markdown>

<div class="hh-define__entry" markdown>

<p class="hh-define__word">H-hat <span class="hh-define__pos">noun</span></p>

<ol class="hh-define__senses">
  <li>
    <strong>A rule system.</strong> A set of rules that defines how every dialect must behave
    in specific contexts &mdash; how classical and quantum data coexist, how quantum data is
    evaluated, consumed and dropped.
  </li>
  <li>
    <strong>A compiler framework.</strong> A pipeline that lowers source code through
    intermediate representations and orchestrates one sub-compiler per backend
    through message passing.
  </li>
  <li>
    <strong>A programming language family.</strong> Dialects that implement the rules with
    their own syntax. The reference dialect, <a href="dialects/heather/">Heather</a>,
    ships with the project.
  </li>
</ol>

<p class="hh-define__see"><em>See also:</em> <a href="core/naming/">backend kind</a> &middot; <a href="core/naming/">lazy evaluation</a> &middot; <a href="dialects/heather/">Heather</a> &middot; <a href="rule_system/">rule system</a></p>

</div>

<aside class="hh-glance">
  <p class="hh-glance__title">At a glance</p>
  <dl>
    <dt>Typing</dt>        <dd>Static</dd>
    <dt>Paradigm</dt>      <dd>Functional, distributed-system inspired</dd>
    <dt>Backends</dt>      <dd>CPU &amp; QPU</dd>
    <dt>Evaluation</dt>    <dd>Strict (classical) &middot; lazy (quantum)</dd>
    <dt>Dialect</dt>       <dd>Heather</dd>
    <dt>Implemented in</dt><dd>Rust</dd>
    <dt>License</dt>       <dd>MIT</dd>
  </dl>
</aside>

</section>

<!-- ============================================================ -->
<!-- MANIFESTO BAND                                                -->
<!-- ============================================================ -->

<section class="hh-band">
  <p class="hh-band__big">No PhD required.</p>
  <p class="hh-band__small">
    For quantum technologies to become widely available, they must interoperate with existing
    software, and software developers must be able to reason about them without a degree in
    quantum information. In H-hat, <strong>qubits, gates, circuits, pulses, Hamiltonians and
    measurements are not language constructs</strong>: the compiler handles them, keeping your
    code platform-independent and focused on the problem domain.
  </p>
</section>

<!-- ============================================================ -->
<!-- CODE TOUR                                                     -->
<!-- ============================================================ -->

<section class="hh-section" markdown>

<p class="hh-kicker">01 &mdash; A tour of Heather</p>

## Read it like a classical language

<p class="hh-section__intro">
Heather is H-hat's reference dialect: a small, <em>regular</em> syntax in which spaces, tabs,
newlines, <code>;</code> and <code>,</code> are all whitespace. Pick a topic below.
</p>

<div class="hh-tour" markdown>

=== "Hello, world"

    /// html | div.hh-tour__text

    ### One line, no ceremony

    A program starts at `main`. There are no semicolons and no commas to remember;
    organise statements in whatever layout fits your project.

    - `//` line comments and `/* … */` block comments
    - `main` lives in `main.hat`

    ///

    ```hhat-heather
    main { print("hoi quantum") }  // a "hello world" program
    ```

=== "Types"

    /// html | div.hh-tour__text

    ### Structs and enums

    User types live in `src/hat_types/`. A **struct** groups named members; an
    **enum** is a tagged union of identifiers or structs.

    - `=.{ … }` declares and assigns in one step
    - mutability is opt-in, through the `<mut>` modifier

    ///

    ```hhat-heather
    type point { x:i32 y:i32 }
    type status_t { ON OFF }

    main {
      p:point =.{x=34 y=43}

      p3<mut>:point
      p3.{x=143 y=331}
      p3.y=341

      status:status_t = status_t.ON
      print(p.x)
    }
    ```

=== "Functions"

    /// html | div.hh-tour__text

    ### Small, typed, overloadable

    Functions declare typed arguments and an optional return type.
    Returning has its own sugar: prefix the expression with `::`.

    - names may contain hyphens: `print-gt`
    - explicit overloading by argument and return types

    ///

    ```hhat-heather
    fn sum(a:i64 b:i64) i64 { ::add(a b) }

    fn print-gt(a:u64 b:u64) {
      if(
        gt(a b): print(a)
        true: print(b)
      )
    }
    ```

=== "Meta-functions"

    /// html | div.hh-tour__text

    ### Control flow is a library

    `if`, `match` and `pipe` are not keywords: they are **meta-functions**, which
    rewrite code at compile time. They come in three kinds &mdash; *option*, *body*
    and *option-body* &mdash; and you can define your own.

    ///

    ```hhat-heather
    // option
    if(gt(a b):a true:b)

    // body: apply double, then print
    pipe(var) { double print }

    // option-body
    match(status) {
      status_t.ON:print("on!")
      status_t.OFF:print("off!")
    }
    ```

=== "Quantum & cast"

    /// html | div.hh-tour__text

    ### Same syntax, `@` prefix

    Quantum types, literals, variables and functions mirror their classical
    counterparts, marked with `@`. Quantum data is **lazy**: instructions accumulate
    until a **cast** (`data * type`) evaluates them and converts the result.

    - strict data is converted on the spot
    - lazy data is evaluated once, then consumed

    ///

    ```hhat-heather
    // strict cast
    v1:u32 = 42
    v2:u64 = v1 * u64

    // lazy (quantum) cast
    @q:@bell_t =.{@s=@false @t=@false}
    @sync(@q)
    res:hashmap = @q * hashmap
    ```

=== "Modifiers"

    /// html | div.hh-tour__text

    ### Change properties, not types

    **Modifiers** adjust an instance's properties &mdash; reference, pointer,
    mutability, laziness, visibility &mdash; from that point on. They are applied
    left to right and can be defined by the user.

    ///

    ```hhat-heather
    modifier &(self) u32 { ... }       // for u32
    modifier &(self) [u32] { ... }     // for arrays of u32
    modifier &(self) status_t { ... }

    // usage
    var:status_t<&>
    ```

=== "Imports"

    /// html | div.hh-tour__text

    ### Explicit by design

    Constants, types, functions, meta-functions and modifiers are imported
    explicitly with `use`, one at a time or grouped.

    ///

    ```hhat-heather
    use(
      const:[
        math.pi32
        math.pi64
      ]
      type:geometry.point
    )
    ```

</div>

<p class="hh-more"><a href="dialects/heather/syntax/">Full Heather syntax &rarr;</a></p>

</section>

<!-- ============================================================ -->
<!-- KEY FEATURES                                                  -->
<!-- ============================================================ -->

<section class="hh-section" markdown>

<p class="hh-kicker">02 &mdash; Key features</p>

## Built on a few strong rules

<div class="hh-features">

  <article class="hh-card">
    <span class="hh-card__n">01</span>
    <h3>Classical &amp; quantum, together</h3>
    <p>Both paradigms coexist in the same program, with similar syntax and components.</p>
  </article>

  <article class="hh-card hh-card--accent">
    <span class="hh-card__n">02</span>
    <h3>Quantum is first-class</h3>
    <p>Quantum types, literals, constants, variables and functions, denoted by the <code>@</code> prefix.</p>
  </article>

  <article class="hh-card">
    <span class="hh-card__n">03</span>
    <h3>No physics exposed</h3>
    <p>Qubits, gates and circuits are handled by the compiler, not written by you.</p>
  </article>

  <article class="hh-card">
    <span class="hh-card__n">04</span>
    <h3>Declarative quantum functions</h3>
    <p>Low-level languages and target backends decide how each quantum primitive is interpreted.</p>
  </article>

  <article class="hh-card">
    <span class="hh-card__n">05</span>
    <h3>Lazy, linear quantum data</h3>
    <p>Evaluated only when cast, exactly once, then freed &mdash; it cannot be reused or partially evaluated.</p>
  </article>

  <article class="hh-card">
    <span class="hh-card__n">06</span>
    <h3>Platform-independent</h3>
    <p>Targets CPU (x86_64, aarch64) and gate- or analog-based QPU technologies alike.</p>
  </article>

  <article class="hh-card">
    <span class="hh-card__n">07</span>
    <h3>Meta-functions</h3>
    <p>Compile-time code rewriting: <code>if</code>, <code>match</code> and <code>pipe</code> are ordinary, user-definable meta-functions.</p>
  </article>

  <article class="hh-card">
    <span class="hh-card__n">08</span>
    <h3>Ownership &amp; RAII-like drops</h3>
    <p>Use-after-free, double-free and illegal borrowing are reported during compilation.</p>
  </article>

  <article class="hh-card">
    <span class="hh-card__n">09</span>
    <h3>Super-types</h3>
    <p>Structural, ad hoc polymorphism: a type belongs to a super-type by the functions that accept it.</p>
  </article>

</div>

</section>

<!-- ============================================================ -->
<!-- PIPELINE                                                      -->
<!-- ============================================================ -->

<section class="hh-section" markdown>

<p class="hh-kicker">03 &mdash; Under the hood</p>

## From `.hat` to hardware

<p class="hh-section__intro">
H-hat has no abstract syntax tree: source files are parsed directly into a high-level
intermediate representation. The compiler then resolves, checks and lowers it, and hands the
result to a sub-compiler per target, which exchange data through message passing.
</p>

<ol class="hh-pipeline">
  <li>
    <span class="hh-pipeline__tag">Source</span>
    <strong>.hat files</strong>
    <small>constants, types, behaviour, proofs</small>
  </li>
  <li>
    <span class="hh-pipeline__tag">HIR</span>
    <strong>High-level IR</strong>
    <small>imports resolved, symbols identified</small>
  </li>
  <li>
    <span class="hh-pipeline__tag">MIR</span>
    <strong>Middle IR</strong>
    <small>type-checked; generics, meta-functions and drops resolved</small>
  </li>
  <li class="hh-pipeline__split">
    <span class="hh-pipeline__tag">Target IR</span>
    <span class="hh-pipeline__targets">
      <span><strong>CPU</strong><small>Cranelift CLIF, MLIR, Pliron&nbsp;IR</small></span>
      <span class="hh-q-target"><strong>@QPU</strong><small>OpenQASM, NetQASM, &hellip;</small></span>
    </span>
  </li>
</ol>

<p class="hh-more"><a href="core/compiler_framework/">Compiler framework &rarr;</a> &nbsp; <a href="core/naming/">Nomenclature &rarr;</a></p>

</section>

<!-- ============================================================ -->
<!-- DIALECTS + RESEARCH                                           -->
<!-- ============================================================ -->

<section class="hh-split" markdown>

<div class="hh-panel" markdown>

<p class="hh-kicker">04 &mdash; Dialects</p>

<div class="hh-dialect">
  <img src="assets/heather.svg" alt="Heather dialect logo" class="hh-dialect__logo">
  <div>
    <h3>Heather</h3>
    <p>
      The reference dialect, named after a flowering shrub (<em>Calluna vulgaris</em>) and a
      Billy Cobham song. Simple on purpose, it shows what H-hat code looks like.
    </p>
  </div>
</div>

<p>
H-hat defines rules, not a single syntax. Anyone may build a dialect &mdash; their own syntax,
interpreter or compiler &mdash; and, as long as it honours the rules, it works in harmony with
the others.
</p>

<p class="hh-more"><a href="dialects/">Explore dialects &rarr;</a></p>

</div>

<div class="hh-panel hh-panel--paper" markdown>

<p class="hh-kicker">05 &mdash; Research</p>

<p class="hh-paper__title">
  <a href="https://dl.acm.org/doi/10.1145/3837062.3839078">Toward Declarative Platform-Independent Modeling of Hybrid Quantum&ndash;Classical Software</a>
</p>

<p>
The features and capabilities H-hat aims to deliver, described in a peer-reviewed paper
available in the ACM Digital Library.
</p>

<p class="hh-inspired__label">Inspired by</p>
<ul class="hh-chips">
  <li>Fortran</li><li>Erlang</li><li>Rust</li><li>C</li><li>Lean</li>
</ul>

<p class="hh-small">
For good performance, integration, resilience in distributed computing, and algorithmic verifiability.
</p>

</div>

</section>

<!-- ============================================================ -->
<!-- COMMUNITY                                                     -->
<!-- ============================================================ -->

<section class="hh-section" markdown>

<p class="hh-kicker">06 &mdash; Community</p>

## Build quantum software in the open

<div class="hh-links">
  <a class="hh-link" href="http://discord.unitary.foundation">
    <strong>Discord</strong><span>Chat with the team and community</span>
  </a>
  <a class="hh-link" href="https://github.com/hhat-lang/hhat_lang/">
    <strong>GitHub</strong><span>Source, issues and discussions</span>
  </a>
  <a class="hh-link" href="how_contribute/">
    <strong>Contribute</strong><span>Code, docs, ideas and feedback</span>
  </a>
  <a class="hh-link" href="blog/">
    <strong>Blog</strong><span>Roadmap and technical notes</span>
  </a>
</div>

<p class="hh-small hh-center">
  Proudly supported by the <a href="https://unitary.foundation/grants/2023_h-hat/">Unitary Foundation</a>.
  Released under the MIT license.
</p>

</section>

<!-- ============================================================ -->
<!-- FINAL CALL TO ACTION                                          -->
<!-- ============================================================ -->

<section class="hh-cta">
  <p class="hh-cta__title">Ready to write your first <span class="hh-q-word">@</span>program?</p>
  <div class="hh-actions hh-actions--center">
    <a class="hh-btn hh-btn--primary" href="getting_started/">Get started</a>
    <a class="hh-btn" href="about/">About H-hat</a>
  </div>
  <p class="hh-small">
    H-hat is under active development; until v0.3 is released, expect breaking changes.
  </p>
</section>

</div>
