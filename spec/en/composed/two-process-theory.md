# Two-Process Theory

> Part of the contingency-dsl composed layer. Two-process theory is one theoretical account under which the composed procedures in this layer can be unified. It posits that Pavlovian and instrumental learning are distinct processes whose products interact to generate observed behavior. This file documents the framework itself rather than any particular procedure; it summarizes the Rescorla–Solomon (1967) account and distinguishes, paragraph by paragraph, what is *observed* when the composed procedures are run from what two-process theory *says about* those observations.

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

Rescorla and Solomon (1967) refined and generalized the bifurcation into a unified **two-process** theory of learning. Their central claim: Pavlovian conditioning and instrumental conditioning are distinguishable processes that operate under different contingency structures (two-term CS–US versus three-term SD–R–SR), and the products of Pavlovian learning — which Rescorla and Solomon describe in terms of acquired motivational / emotional "central states" tied to CSs — can modulate instrumental performance without themselves being operant responses. The vocabulary of "motivational state," "central state," and "acquired motivational properties" in §2 below is Rescorla and Solomon's theoretical vocabulary, not the DSL's. The DSL itself expresses only the procedural arrangement and the empirical patterns observed under it; two-process theory supplies one candidate interpretation of why those patterns arise.

## 2. Central Propositions of Rescorla and Solomon (1967)

Rescorla and Solomon (1967) commit to four interlocking claims. Each claim is stated here in two parts: the *empirical pattern* that the composed procedures generate (what is observed when the procedures are run) and the *theoretical explanation* that two-process theory offers for that pattern.

1. **Two distinct learning processes exist.**
   - *Empirical pattern:* procedures that arrange only a two-term CS–US contingency (respondent layer) and procedures that arrange only a three-term SD–R–SR contingency (operant layer) produce distinguishable behavioral effects; the products of one cannot be reduced to the products of the other (e.g., the diagnostic function of omission; see `composed/omission.md`).
   - *Theoretical explanation (two-process theory):* Pavlovian learning and instrumental learning are separate processes, not one process acting on different inputs. Pavlovian learning establishes relations between stimuli (CS → US); instrumental learning establishes relations between responses and consequences (R → Sr).

2. **A CS paired with a US later influences behavior that was not part of the pairing.**
   - *Empirical pattern:* after a CS has been paired with an appetitive US in a Pavlovian arrangement, subsequent presentation of that CS during an appetitive operant baseline increases operant response rate; after a CS has been paired with an aversive US, subsequent presentation during an appetitive operant baseline decreases operant response rate. These effects are observed under conditions in which neither the original Pavlovian pairing nor the later test phase delivers the US contingent on the operant response.
   - *Theoretical explanation (two-process theory):* the Pavlovian pairing is said to endow the CS with *acquired motivational (or emotional) properties* — "central states" in Rescorla and Solomon's terms — that modulate subsequent operant performance. The DSL does not adopt "central state" vocabulary in its own voice; it records the empirical pattern and notes that two-process theory supplies the preceding vocabulary for those who use it.

3. **The behavioral influence described in (2) is not a direct consequence of response-contingent reinforcement.**
   - *Empirical pattern:* the modulation described in (2) is obtained in procedures in which the CS has never been presented contingent on the operant response and in which, during the test phase, no response-contingent reinforcement is delivered (e.g., PIT under extinction; see `composed/pit.md`). The effect is therefore not attributable to a history of response → US pairings within the test context.
   - *Theoretical explanation (two-process theory):* the modulation is *mediated* (Rescorla and Solomon's term) by the CS's acquired motivational state rather than by direct response-contingent reinforcement. The DSL records the empirical independence; "mediation" is Rescorla and Solomon's causal language and is offered here only as the account that two-process theory provides.

4. **The two processes can be experimentally dissociated.**
   - *Empirical pattern:* procedures such as PIT (independent Pavlovian and instrumental training phases, followed by a transfer test) and omission (Pavlovian pairing combined with a response → US cancellation rule) produce behavioral effects that a single-process description of the procedure cannot accommodate without contradiction (e.g., persistence of autoshaped pecking under omission; see `composed/omission.md`).
   - *Theoretical explanation (two-process theory):* the procedures isolate the contributions of the two processes; behavior on a transfer test that depends on prior Pavlovian training — when that training was conducted without operant-response opportunity — cannot be attributed to the operant process alone.

## 3. Why Composed Procedures Need a Unifying Frame

The four composed procedures documented in this layer — CER, PIT, autoshaping, omission — each combine an operant and a respondent constituent in their procedural arrangement. Under a single-process account that treats all learning as operant (or all as Pavlovian), at least one of the four procedures becomes theoretically incoherent:

- **Single-process operant account** cannot explain autoshaping (no operant contingency is programmed) or omission's persistence of pecking under negative response–US contingency.
- **Single-process Pavlovian account** cannot explain the independence of instrumental training from Pavlovian training in PIT (the transfer effect requires genuine instrumental learning that then interacts, on two-process theory, with the products of Pavlovian training).

Two-process theory accommodates all four procedures in a unified framework and motivates the DSL's decision to treat `composed/` as a sibling category of `operant/` and `respondent/` rather than as a subordinate of either. A composed procedure admitted in the future that could not be specified within this frame would require articulation of an alternative unifying account.

## 4. Relationship to Contemporary Theory

Two-process theory continues to inform contemporary accounts. Appetitive PIT remains a widely used procedure in the study of what Flagel et al. (2011) and related literatures label "cue-triggered motivation" — the DSL observes the underlying empirical phenomenon (an appetitive CS presented during an appetitive-maintained operant baseline increases operant response rate) and notes that the "cue-triggered motivation" label is vocabulary contributed by that literature, not by the DSL. Conditioned suppression remains a standard measure of Pavlovian fear conditioning strength (Annau & Kamin, 1961). Modern outcome-specific PIT procedures refine the theory by dissociating general from outcome-specific S–O associations.

The DSL does not commit to any particular modern elaboration of two-process theory; it provides the grammatical substrate (operant + respondent + composed + experiment layers) within which two-process accounts and their competitors can be expressed and compared.

## 5. Scope of This Document

This file is intentionally more theoretical than procedural. The procedural instances (CER, PIT, autoshaping, omission) appear in their own files and are written in neutral procedural vocabulary. The division of labor is:

- **Procedural files** (`conditioned-suppression.md`, `pit.md`, `autoshaping.md`, `omission.md`) describe the arrangement that the DSL encodes and the empirical patterns the arrangement generates. Theoretical vocabulary from two-process theory or any other account is tagged as such where it appears.
- **This file** documents the theoretical frame (Rescorla & Solomon, 1967) under which the four procedures are grouped. The Rescorla–Solomon vocabulary ("motivational state," "central state," "mediated by") appears here, but only as the explanation *two-process theory offers* — not as part of the DSL's own voice.

Additional composed procedures admitted in the future (see design-philosophy §8.1) are expected to fit within this frame or to motivate an articulated alternative; a composed procedure that cannot be specified within either frame would require a new unifying account, which would then be documented here or in a sibling file.

## 6. Citations

- Annau, Z., & Kamin, L. J. (1961). The conditioned emotional response as a function of intensity of the US. *Journal of Comparative and Physiological Psychology*, 54(4), 428–432. https://doi.org/10.1037/h0042199
- Estes, W. K., & Skinner, B. F. (1941). Some quantitative properties of anxiety. *Journal of Experimental Psychology*, 29(5), 390–400. https://doi.org/10.1037/h0062283
- Flagel, S. B., Clark, J. J., Robinson, T. E., Mayo, L., Czuj, A., Willuhn, I., Akers, C. A., Clinton, S. M., Phillips, P. E. M., & Akil, H. (2011). A selective role for dopamine in stimulus–reward learning. *Nature*, 469(7328), 53–57. https://doi.org/10.1038/nature09588
- Lovibond, P. F. (1983). Facilitation of instrumental behavior by a Pavlovian appetitive conditioned stimulus. *Journal of Experimental Psychology: Animal Behavior Processes*, 9(3), 225–247. https://doi.org/10.1037/0097-7403.9.3.225
- Mowrer, O. H. (1947). On the dual nature of learning: A re-interpretation of "conditioning" and "problem-solving." *Harvard Educational Review*, 17, 102–148.
- Rescorla, R. A., & Solomon, R. L. (1967). Two-process learning theory: Relationships between Pavlovian conditioning and instrumental learning. *Psychological Review*, 74(3), 151–182. https://doi.org/10.1037/h0024475
