# Two-Process Theory

> Part of the contingency-dsl composed layer. Two-process theory is the theoretical account under which the composed procedures in this layer are unified. It posits that Pavlovian and instrumental learning are distinct processes whose products interact to generate observed behavior, and that Pavlovian CSs acquire motivational properties that modulate instrumental performance. This file documents the framework itself rather than any particular procedure; it is the theoretical core that admits CER, PIT, autoshaping, and omission as composed constituents.

**Companion documents:**
- [Conditioned Suppression (CER)](conditioned-suppression.md)
- [Pavlovian-to-Instrumental Transfer (PIT)](pit.md)
- [Autoshaping](autoshaping.md)
- [Omission](omission.md)
- [Respondent Theory](../respondent/theory.md) — two-term contingency as a distinct formal object.
- [Operant Theory](../operant/theory.md) — three-term contingency.

---

## 1. Historical Origin

Mowrer (1947) proposed that classical conditioning and instrumental learning involve different neural substrates and different relational structures. In Mowrer's formulation, classical (Pavlovian) conditioning established an autonomic / emotional response (the "sign" learning), while instrumental conditioning established a skeletal / goal-directed response ("solution" learning). Though Mowrer's specific two-factor account was superseded, the bifurcation survived.

Rescorla and Solomon (1967) refined and generalized the bifurcation into a unified **two-process** theory of learning. Their central claim: Pavlovian conditioning and instrumental conditioning are distinguishable processes that operate under different contingency structures (two-term CS–US versus three-term SD–R–SR), and the products of Pavlovian learning (acquired motivational / emotional states tied to CSs) can modulate instrumental performance without themselves being operant responses.

## 2. Central Propositions

Two-process theory commits to four interlocking claims:

1. **Two distinct learning processes exist.**
   Pavlovian and instrumental learning are not reducible to one another. Pavlovian learning establishes relations between stimuli (CS → US); instrumental learning establishes relations between responses and consequences (R → Sr).
2. **Pavlovian CSs acquire motivational / emotional properties.**
   A CS that has been paired with an appetitive US acquires appetitive-motivational properties; a CS paired with an aversive US acquires aversive-motivational properties. These properties are "central states" that can modulate ongoing behavior.
3. **Pavlovian CSs can modulate instrumental performance.**
   An appetitive CS can facilitate appetitive instrumental responding (appetitive PIT, Lovibond 1983) or suppress aversive instrumental responding. An aversive CS can suppress appetitive instrumental responding (the CER effect, Estes & Skinner 1941) or facilitate aversive instrumental responding. The modulation is mediated by the CS's acquired motivational state, not by direct response-contingent reinforcement.
4. **The two processes can be experimentally dissociated.**
   Procedures such as PIT (independent Pavlovian and instrumental training, followed by transfer test) and omission (Pavlovian pairing combined with response–US cancellation) separate the contributions of the two processes. If behavior on a transfer test depends on the prior Pavlovian training, and if that training was conducted without operant response opportunity, then the behavioral effect cannot be attributed to the operant process alone.

## 3. Why Composed Procedures Need Two-Process Theory

The four composed procedures documented in this layer — CER, PIT, autoshaping, omission — each require *both* an operant and a respondent constituent to be fully specified. Under a single-process account that treats all learning as operant (or all as Pavlovian), at least one of the four procedures becomes theoretically incoherent:

- **Single-process operant account** cannot explain autoshaping (no operant contingency is programmed) or omission's persistence of pecking under negative response–US contingency.
- **Single-process Pavlovian account** cannot explain the independence of instrumental training from Pavlovian training in PIT (the transfer effect requires genuine instrumental learning that then interacts with Pavlovian-acquired CS properties).

Two-process theory accommodates all four procedures in a unified framework and motivates the DSL's decision to treat `composed/` as a sibling category of `operant/` and `respondent/` rather than as a subordinate of either.

## 4. Relationship to Contemporary Theory

Two-process theory continues to inform contemporary accounts. Appetitive PIT remains a widely used procedure in the study of cue-triggered motivation (Lovibond, 1983). Conditioned suppression remains a standard measure of Pavlovian fear conditioning strength (Annau & Kamin, 1961). Modern outcome-specific PIT procedures refine the theory by dissociating general from outcome-specific S–O associations.

The DSL does not commit to any particular modern elaboration of two-process theory; it provides the grammatical substrate (operant + respondent + composed + experiment layers) within which two-process accounts and their competitors can be expressed and compared.

## 5. Scope of This Document

This file is intentionally more theoretical than procedural. The procedural instances (CER, PIT, autoshaping, omission) appear in their own files. Additional composed procedures admitted in the future (see design-philosophy §8.1) are expected to fit within the two-process frame or to motivate an articulated alternative; a composed procedure that cannot be specified within either frame would require a new unifying account, which would then be documented here or in a sibling file.

## 6. Citations

- Annau, Z., & Kamin, L. J. (1961). The conditioned emotional response as a function of intensity of the US. *Journal of Comparative and Physiological Psychology*, 54(4), 428–432. https://doi.org/10.1037/h0042199
- Estes, W. K., & Skinner, B. F. (1941). Some quantitative properties of anxiety. *Journal of Experimental Psychology*, 29(5), 390–400. https://doi.org/10.1037/h0062283
- Lovibond, P. F. (1983). Facilitation of instrumental behavior by a Pavlovian appetitive conditioned stimulus. *Journal of Experimental Psychology: Animal Behavior Processes*, 9(3), 225–247. https://doi.org/10.1037/0097-7403.9.3.225
- Mowrer, O. H. (1947). On the dual nature of learning: A re-interpretation of "conditioning" and "problem-solving." *Harvard Educational Review*, 17, 102–148.
- Rescorla, R. A., & Solomon, R. L. (1967). Two-process learning theory: Relationships between Pavlovian conditioning and instrumental learning. *Psychological Review*, 74(3), 151–182. https://doi.org/10.1037/h0024475
