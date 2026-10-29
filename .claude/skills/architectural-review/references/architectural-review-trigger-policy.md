# Architectural Review Trigger Policy

This document defines when architectural-review should be invoked.

---

## Trigger Checklist

Invoke architectural-review when **all** of the following are true:

- [ ] A specific architectural proposal or direction has been identified (not exploratory)
- [ ] The proposal involves capability, integration, or authority-model changes
- [ ] The fog classification includes architecture_fog or ui_fog (not just product_fog or docs_fog)
- [ ] The proposed response requires explicit risk acceptance (not low-risk feature work)
- [ ] Timeline constraints permit a review cycle (review adds 4-8 hours)

---

## Bypass Conditions

Skip architectural review if:

- **Routine feature work**: Changes internal implementation details without affecting boundaries
  - Example: Refactoring a data layer to improve performance (no API/contract changes)
  - Example: Adding UI polish to existing workflows
  
- **Low-risk isolated changes**: Changes with clear scope and proven patterns
  - Example: Adding a new data model following established schema conventions
  - Example: Extending an existing integration point without new external dependencies

- **Deferred decision**: Review was requested but risks are accepted explicitly without review
  - Record the override reason in the workflow orchestration plan (see ADR 0008)

---

## Trigger Examples

### ✅ Should trigger

1. **Proposal**: Introduce an Author Workspace capability to coordinate published artifacts
   - **Why**: New authority model potentially conflicts with identity model (architecture_fog)
   - **Risk**: Creates second orchestration layer if not carefully scoped
   - **Action**: Invoke with proposal, get review before implementation

2. **Proposal**: Split monolithic reconciliation subsystem into microservices
   - **Why**: Major architectural restructuring (architecture_fog)
   - **Risk**: Performance bottlenecks, distributed state management
   - **Action**: Invoke with proposal, establish success measures

3. **Proposal**: Add real-time collaboration features via WebSocket
   - **Why**: Introduces concurrency and real-time coordination (ui_fog + architecture_fog)
   - **Risk**: Conflict with existing sync model, complexity spike
   - **Action**: Invoke with proposal, define failure boundaries

### ❌ Should not trigger

1. **Proposal**: Update user-facing error messages
   - **Why**: Local polish, no architecture change
   - **Risk**: Minimal
   - **Action**: Proceed without review

2. **Proposal**: Add database indices to improve query performance
   - **Why**: Implementation optimization, no boundary change
   - **Risk**: Low (indices are reversible)
   - **Action**: Proceed with performance testing

3. **Proposal**: Add new REST endpoint following existing patterns
   - **Why**: Extension of proven pattern, no new authority model
   - **Risk**: Low (follows established contracts)
   - **Action**: Proceed with API testing

---

## Process

1. **Identify fog type** from repository_sensemaking_brief
2. **Check trigger conditions** against this checklist
3. **If triggered**: select the `architectural_review` responsibility and invoke the `architectural-review` Skill directly with the current `repository_sensemaking_brief` plus the proposed direction.
4. **If not triggered**: return to ordinary bounded implementation/responsibility selection.
5. **Record decision when durability matters**: preserve it in the normal decision/handoff/Campaign surface already warranted for the task; do not create a workflow plan merely to carry the decision.

---

## Notes

- Architectural reviews add latency (4-8 hours typical). Schedule them early when timeline permits.
- If uncertainty exists, prefer triggering the review. False positives are cheap; missed risks are expensive.
- Reviews can be abbreviated if proposal scope is small and risks are well-bounded.
- Large proposals may require multiple review cycles (initial + revised proposal + final approval).

---

**Owner**: Architecture review skill  
**Last updated**: 2026-07-18  
**Related**: ADR 0008 (Routing Divergence and Action Audit Trail), ADR 0007 (Soft-Context Routing)
