# Post-V1 Local Product-Use Observation

## Status

**Proposed post-V1 repository objective.**

This package intentionally makes a weaker claim than "tutor validation" or "learning validation".

Its purpose is to make the qualified V1 local tutor path easier to exercise and to record bounded, descriptive product-use evidence about what happened during a local session.

It does **not** establish that the tutor is effective, that a learner improved, that an intervention caused an outcome, or that any concept is mastered.

## Primary question

Can one local participant repeatedly exercise the qualified CME review path with low enough operational friction that we can observe where the next real product bottleneck is?

## Claim ceiling

```text
claim_scope = descriptive_local_product_use_only
learning_effect = not_established
tutor_efficacy = not_established
mastery = not_established
```

Product-use observations are not M7/M7C learner inference, M9 intervention selection, M10 outcome evidence, M11 longitudinal learner state, or M46 tutoring authority.

## Initial surface

The first guided surface stops at the existing M8 baseline-freeze boundary:

```text
exact M18 queue + exact M44 view + optional exact M42 plan(s)
        |
        v
M45 review proposal
        |
        v
explicit review selection + capture consent
        |
        v
M23 -> persisted M8 session
        |
        v
guided position presentation + protocol-bound baseline capture
        |
        v
all baseline responses frozen
        |
        v
M46 proposal may be GENERATED for operator inspection
```

The guided surface does not execute the M46 proposal. Existing M8 execution/exposure surfaces remain authoritative for assisted prompts, objective reveal, comparison, explanation, and completion.

## Descriptive observations

The package may persist immutable participant-scoped records for events such as review start, position presentation, prompt presentation, response submission/freeze, generated proposal, abandonment, completion, and explicit participant feedback.

The observation layer may aggregate counts and self-report. It must not infer learning, diagnose a learner, rewrite an upstream artifact, or claim tutoring efficacy.

## Non-goals

- browser UI;
- hosted deployment;
- authentication or multi-tenancy;
- billing;
- automatic policy optimization;
- a new M47 or K8 subsystem;
- generic ontology expansion;
- causal learning or mastery claims.

## Exit condition

The repository package is complete when the local guided baseline path and descriptive report are qualified. Real use remains external evidence. A later repository change requires a fresh evidence-backed decision about the dominant bottleneck.
