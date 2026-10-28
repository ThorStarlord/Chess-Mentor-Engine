# Owner Decision Capsule

## 1. Decision Needed

State the exact owner-reserved decision.

## 2. Why Repository Evidence Cannot Resolve It

Separate facts from preference/policy/authority.

## 3. Credible Options

Describe only materially real options.

## 4. Tradeoffs Reversibility and Deferral

Explain what differs and what waiting changes.

## 5. Authority Effects

State what authority each option would grant if the owner selects it.

## 6. Evidence

List repository/external evidence used.

## 7. Machine-Readable Summary

```yaml
artifact_id: owner_decision_capsule
decision_id: OWNER-DECISION-1
target_repository: owner/repository
decision_statement: "<exact owner decision>"
repository_can_resolve: false
options:
  - option_id: OPTION-A
    statement: "<option>"
    unlocks: ["<future capability>"]
    tradeoffs: ["<material tradeoff>"]
    reversibility: "<qualitative>"
    deferral_effect: "<what waiting changes>"
    authority_if_selected: ["<authority granted by this explicit choice>"]
owner_decision_made_by_artifact: false
implementation_authority_established_by_artifact: false
created_at: "YYYY-MM-DDTHH:MM:SSZ"
immutable: true
```
