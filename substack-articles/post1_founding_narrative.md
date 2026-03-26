# How Six Research Papers Convinced Me to Build a Photonics Platform

### The moment a stack of literature became an engineering mandate

---

*This is the first post in the **Precision with Light** founding series — a behind-the-scenes account of why this platform exists, what problem it is solving, and how six research papers written by scientists who will never meet each other collectively made the case for a General-Purpose Photonics AI Platform.*

---

## The Problem With Being Right Too Early

There is a specific kind of frustration that every engineer knows: seeing a solution clearly, before the tools exist to build it.

I have spent years at the intersection of optoelectronics, photonics, and systems engineering. I have watched the field of specialty fiber optics produce increasingly extraordinary results — fibers carrying kilowatts of laser power, hollow-core designs guiding light through air rather than glass, microstructured geometries achieving optical properties that seem to defy physical intuition. The science is exceptional.

The engineering workflow to produce that science, however, is not.

Designing a specialty optical fiber in 2025 still looks like this: a researcher or engineer opens a finite element simulation tool — COMSOL, Ansys Lumerical, RP Fiber Power — configures a geometry by hand, runs a simulation that takes minutes to hours, examines the result, adjusts the parameters by intuition, and runs again. A comprehensive design sweep — one that systematically explores the relevant parameter space — takes days or weeks. Each simulation answers the same question: *given this geometry, what does the light do?*

Nobody has built a tool that answers the inverse: *given what I need the light to do, what geometry should I build?*

That inversion is the platform.

But it took six research papers, read in sequence, to make the argument impossible to ignore.

---

## Paper One: The Comb That Changed the Index Profile
### *MDPI Sensors, 2023 — Large Mode Area fiber, 2,010 µm²*

The first paper was about a problem I knew well: how to build a fiber that carries more optical power without destroying itself or distorting the beam.

In high-power fiber lasers — the kind used for industrial metal cutting, aerospace welding, directed energy systems — the fundamental enemy is intensity. Too much optical power concentrated in too small an area triggers a cascade of destructive effects: stimulated Raman scattering, thermal lensing, catastrophic material damage. The engineering solution, known since the 1990s, is to expand the core diameter so that the power is spread over a larger cross-sectional area. A Large Mode Area (LMA) fiber.

The complication: a large core supports many spatial modes of light propagation. A fiber that carries a hundred modes produces a beam with a hundred overlapping patterns — useless for precision applications. The engineering challenge, therefore, is to make the core large enough to handle the power, while somehow forcing the light to travel only in the fundamental mode.

The 2023 MDPI Sensors paper addressed this with a specific geometric innovation: a **comb-shaped refractive index profile** in the core, combined with a gradient-index outer ring. By discretizing a continuously graded index profile into a series of high-index rings separated by lower-index gaps — the "comb" — the authors created a soft boundary condition that preferentially attenuates higher-order modes while preserving the fundamental. The result was a mode field area of **2,010 µm²** with ultra-low bending loss.

The physics was elegant. The process to find it was not. It required exhaustive finite element simulation, deep domain knowledge, and weeks of iteration to arrive at that single optimized design point.

I noted this and kept reading.

---

## Paper Two: Abandoning Solid Glass Entirely
### *MDPI Electronics, 2024 — Anti-Resonant LMA, >3,000 µm²*

The second paper made a more radical move: instead of engineering the solid glass refractive index profile to suppress unwanted modes, what if the cladding structure itself did the work?

The answer was nested U-shaped **anti-resonant tubes** — microstructured elements in the cladding that use a phenomenon called inhibited coupling to prevent light from leaking out of the core, regardless of how large that core becomes. The guidance mechanism is no longer total internal reflection (as in standard fiber) but **anti-resonance**: at specific wavelengths, the tube walls act as Fabry-Pérot resonators that reflect light back into the core. Between resonances, the field cannot penetrate the glass structure.

Mode field area: **over 3,000 µm²** at both 1064 nm and 1550 nm — simultaneously, in the same fiber. Polarization-insensitive, because the six-fold symmetry of the tube arrangement treats both polarization states identically. Suitable for miniaturized high-power laser systems.

A 50% jump in mode area, achieved by changing the geometry of the cladding rather than the composition of the glass.

Again, arrived at through weeks of FEM simulation and expert iteration. Again, a single design point produced by an exhaustive manual search.

---

## Paper Three: The Bridge From Simulation to Glass
### *Optics Express, 2025 — All-Solid Anti-Resonant Fiber, CVD Fabrication*

The third paper did something neither of the first two had done: it closed the loop between simulation and physical reality.

An **all-solid anti-resonant fiber** — no air holes, no hollow core, no pressurized gas. Instead, high-index glass inclusions embedded in a lower-index silica matrix, achieving anti-resonant guidance entirely within a solid structure. The waveguide physics are described by the **ARROW model** (Anti-Resonant Reflecting Optical Waveguide), an analytical framework that predicts the optimal geometry from first principles.

Crucially, this fiber was not just simulated. It was fabricated using **chemical vapor deposition (CVD)** — the same family of industrial deposition processes used in semiconductor manufacturing — and the fabricated device matched the simulation. The ARROW model worked. The manufacturing process delivered the predicted geometry within tolerance.

This was the paper that established fabricability as a design constraint, not an afterthought. CVD imposes real limits: minimum feature sizes, maximum achievable index contrast, layer thickness tolerances of a few percent. Any design that ignores these limits is academically interesting and industrially useless.

Three papers in. Three FEM-intensive design exercises. Three extraordinary results. And a pattern beginning to emerge.

---

## Paper Four: Fill the Hollow Core With Gas
### *MDPI Sensors, 2020 — Hollow-Core PCF Gas Sensing*

The fourth paper shifted the application entirely — from power delivery to sensing — and in doing so revealed a capability of hollow-core photonic crystal fibers that no solid-core fiber can match.

In a conventional optical fiber, the light travels through glass. If you fill the space around a solid-core fiber with a gas, the light barely interacts with it — the **overlap factor** between the optical field and the analyte is effectively zero.

In a hollow-core PCF, the light travels through air. Fill that air with a gas of interest, and the overlap factor approaches **0.95 to 0.99** — nearly the entire optical field is interacting with the analyte at every point along the fiber length. The detection sensitivity that would require kilometers of free-space optical path can be achieved with meters of hollow-core fiber. Parts-per-billion gas detection. In a fiber. That fits in your hand.

The design parameters that govern this are the same geometric parameters that govern loss and mode area: core radius, tube geometry, cladding structure. But the *objective function* has changed. You are no longer minimizing loss alone. You are simultaneously maximizing overlap factor and minimizing loss — two objectives that partially compete with each other.

This is a multi-objective optimization problem. And the only way to navigate it without a surrogate model is to run thousands of FEM simulations and plot a Pareto front by hand.

---

## Paper Five: The Physical Limit of Loss
### *MDPI Photonics, 2025 — Double-Tube Nested AR Fiber, 0.00088 dB/km*

The fifth paper arrived at a number that requires a moment to absorb.

**0.00088 dB/km.**

To place this in context: the best conventional single-mode silica fiber — Corning SMF-28, the fiber that carries the internet — achieves approximately 0.18 dB/km, limited by Rayleigh scattering in glass. This hollow-core anti-resonant fiber, made of the same glass, achieves loss **200 times lower** — because the light is no longer traveling through the glass at all.

The mechanism is a **double-tube nesting** design: an outer anti-resonant tube provides the primary confinement boundary, while an inner nested tube provides a secondary reflection that destructively interferes with any field leaking toward the cladding. The geometry is precisely engineered so that the ARROW condition is satisfied at the target wavelength: tube wall thickness t = mλ / 2√(n²-1), where m is the resonance order and n is the glass index.

Six geometric parameters, coupled through the confinement loss in a highly nonlinear way. The design space cannot be navigated analytically. It requires either weeks of FEM simulation or a trained surrogate model that reduces each evaluation from hours to milliseconds.

0.00088 dB/km is the benchmark. It is the result that a correctly designed inverse engine should be able to reproduce from a performance specification as input.

---

## Paper Six: The Question Asked in Reverse
### *MDPI Photonics, 2023 — DNN Inverse Design for Four-Wave Mixing, 1064 nm → 770 nm*

The sixth paper broke the pattern of the first five — and made the platform argument inescapable.

**Four-Wave Mixing (FWM)** is a nonlinear optical process in which two pump photons at frequency ω_p interact to generate a signal at ω_s and an idler at ω_i, conserving energy: 2ω_p = ω_s + ω_i. The efficiency of this conversion depends critically on **phase matching** — a condition governed by the fiber's group velocity dispersion profile D(λ), which is itself determined entirely by fiber geometry.

The target application was biomedical imaging: a 1064 nm pump laser, a fiber specifically engineered to generate a signal at exactly **770 nm** — a wavelength that sits in the first biological transparency window, where tissue scattering is minimized and two-photon imaging becomes possible.

But this paper did not start with a geometry and ask what it produced. It started with the target — 770 nm signal from a 1064 nm pump — and worked backwards. A **Deep Neural Network**, trained on a library of geometry-to-dispersion mappings, was used as an inverse solver. The result: the network synthesized a PCF geometry whose dispersion profile satisfies the phase matching condition for the desired frequency conversion.

Forward simulation time per geometry: hours. Inference time per design: milliseconds.

And here, finally, was the statement made explicit in the literature: the inverse problem is solvable. A neural network can learn to work backwards from desired optical properties to synthesized geometry. The mapping exists. The data is available. The training methodology is validated.

---

## The Pattern That Could Not Be Unseen

Six research groups. Six different problems. Six FEM-intensive design exercises.

And six instances of the same abstract problem.

In every case: a **geometry parameter space**, a set of **hard physical constraints**, a **performance target**, and a **fabrication rule set**. And in every case, the workflow was the same: configure the simulation manually, run it, examine the result, adjust by intuition, run again.

No tool in existence could take the performance target as input and synthesize the geometry as output. Every simulation tool in the field — Lumerical, COMSOL, RP Fiber Power — is a verification engine. You must already know the answer to use them. The design problem — the inverse problem — belongs entirely to human intuition.

This is the gap. And it is not a narrow gap. The global market for specialty photonics design tooling — the licenses that research groups, photonics companies, and defense contractors pay to run these simulations — represents hundreds of millions of dollars per year, spent on tools that still require weeks of expert time to produce a single optimized design.

**The realization was this:** these six papers did not just describe six fiber designs. They described six instances of the same solvable problem. And collectively, they described the training curriculum for a generative engine that could solve all of them.

An engine that sits above the simulation tools, speaks their language, and answers the question that they cannot: *given what I need the light to do — what should I build?*

That engine is **Precision with Light**.

---

## What the Platform Is

**Precision with Light** is a vertically integrated, AI-native design platform for photonics — built on the insight that every optical design problem is an inverse problem, and that inverse problems at this scale require generative AI constrained by hard physics, not just a faster version of the same simulation workflow.

The architecture has four layers:

**The Intent Layer** translates a natural language design brief or a structured specification into a precise set of physics constraints, fabrication rules, and performance targets — enforced before the generative engine fires. This is not a chatbot that passes your request to a simulation tool. It is a physics-aware constraint system that catches unphysical design requests at the front door.

**The Generative Engine** synthesizes candidate geometries using Physics-Informed Neural Networks (PINNs) and Conditional Wasserstein GANs (cWGAN-GP) — architectures specifically chosen because they produce outputs that satisfy Maxwell's equations by construction, not by luck.

**The Simulation Bridge** cross-validates every AI-generated design against industry-standard solvers — Lumerical FDTD/FDE and COMSOL Multiphysics — providing a scientific certificate of physical fidelity before any design leaves the platform.

**The Fabrication Export** translates validated designs directly into manufacturable files: GDSII layouts for silicon photonics foundry runs, STL meshes for two-photon polymerization printing, and fiber draw specifications for specialty fiber manufacturers.

This is not a research prototype. It is a production platform, built with a FastAPI backend, Pydantic-enforced data contracts, a React/TypeScript frontend, and Docker deployment — designed for integration into industrial R&D pipelines and academic research workflows alike.

---

## What Comes Next

This post is the first in the **Precision with Light** founding series. Over the coming weeks, I will be publishing the technical deep-dives that follow naturally from the corpus above:

**Post 2** — *"The Question Every Photonics Engineer Asks Backwards"*: a technical deep-dive into inverse design, the FWM paper, and why Physics-Informed Neural Networks are the only credible architecture for photonics design synthesis.

**Post 3** — *"From Glass to Qubits: Silicon Photonics and the Platform Under the Platform"*: programmable photonic meshes, quantum photonic processors, co-packaged optics for data centers, and why the MPW (Multi-Project Wafer) batch endpoint changes everything.

**Post 4** — *"Why AI Needs Physics: The Case Against Black-Box Surrogates in Photonics Design"*: the rigorous argument for physics-informed over purely data-driven approaches, and what the latest PINN methodology literature says about building surrogates you can actually trust.

**Post 5** — *"Open for Business"*: the platform architecture in full, partnership opportunities, the academic access model, and how to get involved.

---

*If this resonates with you — whether you are a photonics researcher, an optical engineer at an industrial company, an investor in deep technology, or a software builder interested in the intersection of physics and AI — I want to hear from you.*

*Subscribe below to follow the series. And if you are working on a problem that sounds like the ones described above, reach out directly.*

*The tools are finally catching up to the physics.*

---

**Nuno Edgar Nunes Fernandes**
*Founder, Precision with Light*
*[precisionwithlight.substack.com](https://precisionwithlight.substack.com) · [GitHub](https://github.com/nunofernandes-plight/Precision-with-Light-The-Photonics-Platform)*
