# Chess Knowledge Coaching Context

**Context schema:** `chess-knowledge-coaching-context.v1`  
**Binding schema:** `chess-knowledge-model-binding.v1`

## Purpose

K6 makes qualified chess-knowledge assertions available to language-generation
consumers without modifying the existing M19 request contract.

The composition is:

```text
M19 model coaching request
    exact ID + fingerprint

CKO assertion bundle
    exact ID + fingerprint
        ↓
CKO coaching context
    exact concept definitions + authority
        ↓
knowledge-model binding
    references both exact artifacts
```

The M19 request remains byte-for-byte and fingerprint-for-fingerprint unchanged.

## Why this is a sidecar

M19 already has a qualified content-addressed request whose model role is
`language_renderer_only`. Adding ontology fields directly to that request would
silently change its schema, fingerprint, fixtures, provider contract, and historical
qualification.

K6 therefore validates the existing M19 request through its native identity validator
and binds a separate CKO context beside it.

## Projected assertion content

Each model-consumable assertion contains:

```text
exact KnowledgeAssertionRef
preferred ontology name
concept kind
definition
assertion status
authority class
exact qualifiers
related concept IDs
selected recognition questions
```

The projection is rebuilt from the current exact ontology and exact assertion bundle.
Rewriting a display label, definition, authority, qualifier, or assertion reference
causes validation failure rather than being treated as harmless prompt decoration.

## Fixed model instructions

The CKO context carries a deterministic instruction contract that requires the model
to:

1. treat deterministic assertions as established only within their exact subject and
   claim scope;
2. preserve the weaker authority of heuristic, external-taxonomy, model, and human
   assertions;
3. avoid inferring participant reasoning or learner weakness from a chess concept
   assertion alone;
4. avoid inventing ontology assertions not supplied in the context;
5. use ontology definitions/relationships for explanation while preserving M16 as
   the deterministic mentor-grounding ceiling.

These instructions constrain how knowledge is expressed. They do not establish that
arbitrary generated prose is semantically correct.

## Provider wrapper

`build_knowledge_augmented_provider_payload(...)` returns an explicit wrapper:

```text
m19_request
chess_knowledge_context
knowledge_binding
```

This is an opt-in integration payload. It does not replace the currently qualified
M19 provider interface and does not cause existing reviewed-coaching flows to begin
sending ontology context automatically.

A future provider-adoption package can explicitly decide whether and how to consume
this wrapper.

## Authority examples

A context can safely carry both:

```text
position.isolated_pawn
    present
    deterministic_position_fact
```

and:

```text
tactic.fork
    supported
    external_taxonomy_tag
```

without converting the second into detector evidence merely because both are shown
to the same model.

## Non-goals

K6 does not:

- modify M19 request identity;
- change M16 deterministic feedback;
- automatically call a provider with ontology context;
- grant a model new objective-chess authority;
- infer player reasoning from motifs;
- infer or mutate M7 learner hypotheses;
- select M9 training interventions;
- claim that ontology context eliminates model hallucination.

## Qualification

The K6 regression package verifies:

- exact assertion metadata and authority survive projection;
- deterministic rebuild from identical inputs;
- rewritten concept metadata is rejected;
- an actual qualified M19 request validates before binding;
- sidecar creation does not mutate or refingerprint that request;
- request/context binding drift is rejected;
- the fixed instruction contract contains explicit anti-promotion and anti-invention
  rules.
