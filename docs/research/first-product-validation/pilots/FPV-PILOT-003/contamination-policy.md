# Pilot 003 contamination policy

## Measurement states

- Observation: open Stage A prompt capturing natural reasoning.
- Diagnostic probing: frozen Stage B questions surfacing additional reasoning.
- Tutoring intervention: instruction or a prompt that teaches a chess-solving routine.

These states must not be treated as equivalent.

## Contamination criteria

Flag a probe as intervention-like if it contains a chess heuristic, names a tactical motif, suggests a move category, directs attention to a piece or square, instructs a known training routine, or strongly implies that the current choice is wrong.

Also record participant-initiated external analysis, facilitator improvisation, engine exposure, prior-report exposure, or any position-specific hint as a protocol deviation.

## Handling

Do not erase contaminated data. Preserve it, mark the affected stage/position, describe the event, and exclude it from the relevant clean inference when required. A probe-induced decision change is measured as a result; it is not silently reclassified as invalid.

## Boundary principle

If a question changes the player's decision, it may be part of the tutoring mechanism rather than measurement. Pilot 003 tests that possibility instead of assuming it away.
