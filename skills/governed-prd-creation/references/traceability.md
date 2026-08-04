# Product-to-Delivery Traceability

## Required chain

Maintain:

`PRD -> requirement -> ADR decision(s) -> epic/story -> test -> staging evidence -> production evidence`

## Minimum fields

For each requirement:

- PRD ID and version;
- requirement ID and text;
- success metric or acceptance evidence;
- ADR IDs or `no_material_adr_required` rationale;
- epic/story/action IDs;
- test IDs or coverage group;
- staging result and evidence reference;
- production result and evidence reference;
- lifecycle state.

## Alignment gate

Before accepting an ADR set:

- every ADR cites triggering requirement IDs;
- every material architecture question has a disposition;
- no ADR silently changes product intent;
- PRD constraints and ADR decisions do not contradict;
- affected success metrics remain achievable;
- deferred ADRs do not block the minimum shippable scope.

Before implementation baselining:

- every story cites both PRD requirement IDs and applicable accepted ADRs;
- every requirement has test coverage or an explicit deferred rationale;
- environment evidence expectations are defined.
