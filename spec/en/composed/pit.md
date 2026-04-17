# Pavlovian-to-Instrumental Transfer (PIT)

> Part of the contingency-dsl composed layer. PIT denotes the modulation of an instrumentally trained response by a separately trained Pavlovian CS. The two training histories are established independently; the test phase presents the Pavlovian CS while the operant response is available under extinction (or maintained baseline).

**Companion documents:**
- [Two-Process Theory](two-process-theory.md) — the Rescorla–Solomon (1967) framework that motivates the transfer effect.
- [Operant Grammar](../operant/grammar.md) — operant response productions.
- [Respondent Grammar](../respondent/grammar.md) — Pavlovian training productions.
- [Experiment / Phase Sequence](../experiment/phase-sequence.md) — multi-phase design.

---

## 1. Procedure

The PIT procedure has three phases, the first two of which are established **independently** before the critical test:

1. **Pavlovian training.** A CS is paired with a US in the absence of the operant response requirement (e.g., `Pair.ForwardDelay(cs, food, ...)`). The CS acquires predictive properties without any operant-response history.
2. **Instrumental training.** An operant response (e.g., lever press) is trained on a schedule that produces the same US, without the Pavlovian CS (e.g., VI 60 s maintained by food delivery). The operant history is established without CS exposure.
3. **Transfer test.** The Pavlovian CS is presented while the instrumental response is available, typically under extinction (no US delivered during the test) to isolate the CS's motivational influence from ongoing reinforcement.

The dependent measure is the change in operant response rate during CS presentations versus during matched no-CS intervals in the test.

Estes (1948) first demonstrated the transfer effect. Rescorla and Solomon (1967) articulated the theoretical interpretation, and Lovibond (1983) extended the paradigm to appetitive designs in which the Pavlovian CS facilitates (rather than suppresses) instrumental performance.

## 2. General versus Specific PIT

Two principal variants are distinguished by what the Pavlovian and instrumental training share:

- **General PIT.** The Pavlovian and instrumental training use outcomes of the **same motivational class** but not necessarily the identical outcome (e.g., Pavlovian CS paired with sucrose; instrumental response reinforced with food pellets). The CS facilitates the instrumental response via a shared motivational state.
- **Outcome-specific PIT.** The Pavlovian CS and the instrumental response share the **identical outcome** (e.g., both trained with sucrose). The CS selectively enhances instrumental responding for that specific outcome when multiple outcome-specific responses are tested simultaneously. This variant is taken as evidence for outcome-specific S–O associations at the Pavlovian stage.

The DSL expresses both variants with the same composed structure; the distinction is carried by the `@us` / reinforcer labels on the Pavlovian and operant phases.

## 3. DSL Encoding

```
@cs(label="tone", duration=10-s, modality="auditory")
@us(label="food", intensity="45mg_pellet", delivery="signaled")

phase pavlovian_training:
  sessions = 8
  Pair.ForwardDelay(tone, food, isi=10-s, cs_duration=10-s)

phase instrumental_training:
  sessions = 10
  VI60s

phase transfer_test:
  sessions = 1
  use instrumental_training
```

Each phase carries a single schedule body and runs in separate sessions (or in clearly separated blocks within a session); the phase sequence ensures the temporal separation. The transfer test reinstates the operant baseline by reference (`use instrumental_training`); during the test, the Pavlovian CS is presented (typically as probe trials whose schedule is governed by `@cs_interval` annotations) so that the CS's modulating effect on the instrumental response can be quantified.

## 4. Relationship to CER

Both PIT and CER (see `conditioned-suppression.md`) involve a Pavlovian CS modulating operant performance. They differ in training history:

- **CER**: Pavlovian overlay is superimposed on an already-trained operant baseline, typically within the same session; the CS acquires its properties while the operant is concurrently being maintained.
- **PIT**: Pavlovian and instrumental training are explicitly **independent**; the critical test presents a CS that has never been paired with the instrumental response.

This independence is what makes PIT a diagnostic procedure for the transfer of Pavlovian learning into instrumental performance, rather than a within-session modulation.

## 5. Citations

- Estes, W. K. (1948). Discriminative conditioning. II. Effects of a Pavlovian conditioned stimulus upon a subsequently established operant response. *Journal of Experimental Psychology*, 38(2), 173–177. https://doi.org/10.1037/h0057525
- Lovibond, P. F. (1983). Facilitation of instrumental behavior by a Pavlovian appetitive conditioned stimulus. *Journal of Experimental Psychology: Animal Behavior Processes*, 9(3), 225–247. https://doi.org/10.1037/0097-7403.9.3.225
- Rescorla, R. A., & Solomon, R. L. (1967). Two-process learning theory: Relationships between Pavlovian conditioning and instrumental learning. *Psychological Review*, 74(3), 151–182. https://doi.org/10.1037/h0024475
