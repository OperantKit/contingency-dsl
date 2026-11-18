# Stimuli — Name, Physical Properties, Onset and Offset

> Part of the contingency-dsl foundations layer. Defines what a stimulus is in the DSL, independently of any theory of what the stimulus does. Role names (discriminative stimulus, reinforcer, conditioned stimulus, unconditioned stimulus, and so on) are not defined here; each paradigm layer gives its own role names as aliases for positions in the paradigm-neutral dependency types of [`contingency-types.md`](contingency-types.md).

---

## 1. Stimulus

**Definition 1 (Stimulus).** A stimulus is a named physical event source in the apparatus. It has:

- a **name** — the identifier by which programs and annotations refer to it (`tone`, `food`, `shock`, `key_light`);
- **physical properties** — modality (auditory, visual, tactile, gustatory, olfactory, electrical), intensity, duration, and similar parameters. Physical properties are annotation-level, not grammatical.

**Definition 2 (Stimulus events).** A stimulus has exactly two kinds of event: **onset** (the stimulus begins) and **offset** (the stimulus ends). A momentary stimulus is one whose offset follows its onset after a fixed duration.

**One name, one stimulus.** Within a program, a name denotes one stimulus. The identifier `food` in an expression, `@reinforcer("food")`, and `@us(label="food")` all refer to the same stimulus. Two names denote two stimuli, even if their physical properties coincide.

## 2. One Stimulus, Different Roles

A given physical stimulus can play different roles across procedures (e.g., a tone that is paired with food in one phase can later be the stimulus in whose presence a response produces food). The stimulus is defined once by its name; the role it plays is a property of the dependency it enters, not of the stimulus. Re-use across procedures is accomplished through `let` bindings of annotation-level stimulus identifiers.

## 3. Where the Role Names Are Defined

Each paradigm layer names the positions that stimuli occupy in its dependencies. These names are aliases: they add no meaning beyond the position in the paradigm-neutral dependency type.

- Operant role names: [Operant Theory, Stimulus Roles as Aliases](../operant/theory.md#stimulus-roles-as-aliases).
- Respondent role names: [Respondent Theory §0](../respondent/theory.md#0-stimulus-roles-as-aliases).

## 4. What This File Does **Not** Cover

- Physical property parameters (frequency, intensity, duration) in detail. Those are annotation-level.
- Response-side typing (operant responses, elicited responses). The response-side taxonomy is treated in `operant/theory.md` and `respondent/theory.md`.
- Effects of stimuli on behavior (increasing or decreasing a response, eliciting a response, being worked for or avoided). Those are readings within each paradigm layer, recorded as notes there.
- Derived stimulus classes (equivalence classes, relational frames). Those are behavioral outcomes, not stimulus definitions.

## References

- Catania, A. C. (2013). *Learning* (5th ed.). Sloan.
