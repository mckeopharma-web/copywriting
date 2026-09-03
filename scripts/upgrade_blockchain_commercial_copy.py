from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "expertises/blockchain/blockchain.html"
CONTRACT = ROOT / "contracts/blockchain-offer-structure-lock.json"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one source fragment, found {count}")
    return text.replace(old, new, 1)


def main() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    text = PAGE.read_text(encoding="utf-8")

    html_marker = 'data-commercial-copy-version="blockchain-commercial-v1"'
    if html_marker not in text:
        text = replace_once(
            text,
            '<html lang="en" data-theme="night"',
            '<html lang="en" data-theme="night" data-commercial-copy-version="blockchain-commercial-v1"',
            "html commercial version",
        )

    text = replace_once(
        text,
        '<meta name="description" content="Architecture, applied R&amp;D and delivery for blockchain and verifiable computing: prove the bounded property, expose the minimum data, and use the least complex mechanism that an independent verifier can accept.">',
        '<meta name="description" content="Blockchain and verifiable-computing consulting for teams that need a defensible GO / NO-GO architecture, implementation, governance and independent acceptance package — without forcing every problem on-chain.">',
        "meta description",
    )

    for section in contract["sections"]:
        sid = section["id"]
        kind = section["kind"]
        role = section["semantic_role"]
        marker = f'data-section-kind="{kind}" data-semantic-role="{role}"'
        if marker in text:
            continue
        if sid == "top":
            old = '<section class="hero" id="top">'
            new = f'<section class="hero" id="top" {marker}>'
        elif sid == "engagement":
            old = '<section id="engagement" class="final">'
            new = f'<section id="engagement" class="final" {marker}>'
        else:
            old = f'<section id="{sid}">'
            new = f'<section id="{sid}" {marker}>'
        text = replace_once(text, old, new, f"section metadata {sid}")

    text = replace_once(
        text,
        '<div class="kicker">ZK expertise · 3+ month engagements</div><h1>Blockchain &amp;<br>Verifiable Computing</h1><p class="lead">Anchor on-chain only what another party must be able to establish independently — not what a conventional system can safely store.</p><p class="sectionIntro">Architecture, applied R&amp;D and delivery for teams deciding where shared state, programmable settlement, attestations, selective disclosure or zero-knowledge verification are justified.</p><div class="ctaRow"><a class="cta primary" href="#engagement">Evaluate the mission</a><a class="cta secondary" href="#qualification">Run the fit check</a></div>',
        '<div class="kicker">Blockchain architecture · verifiable systems · 3–12 month delivery</div><h1>Blockchain systems<br>that earn their complexity.</h1><p class="lead">When a counterparty must verify a critical state, transaction or claim, turn that requirement into the smallest architecture they can independently check.</p><p class="sectionIntro">Start with a GO / NO-GO decision. If blockchain, attestations, selective disclosure or ZK are justified, continue through implementation, governance, verifier tooling and handoff.</p><div class="ctaRow"><a class="cta primary" href="#engagement">Scope the decision</a><a class="cta secondary" href="#qualification">Check fit first</a></div>',
        "hero commercial message",
    )
    text = replace_once(
        text,
        '<div class="facts"><div><b>Result</b><span>A defensible mechanism choice</span></div><div><b>Format</b><span>3–12 months · architecture + delivery</span></div><div><b>Buyer</b><span>Innovation / trust architecture lead</span></div><div><b>Stack</b><span>Solidity · Rust · EVM · Solana · Foundry · EZKL</span></div></div>',
        '<div class="facts"><div><b>Result</b><span>GO / NO-GO architecture + acceptance package</span></div><div><b>Format</b><span>3–12 months · decision through delivery</span></div><div><b>Buyer</b><span>CTO · Innovation · Platform · Trust</span></div><div><b>Stack</b><span>Solidity · Rust · EVM · Solana · Foundry · EZKL</span></div></div>',
        "hero buying facts",
    )

    text = replace_once(
        text,
        '<div class="kicker">Triggers</div><h2>When “put it on-chain” is not yet a requirement.</h2><p class="sectionIntro">The useful trigger is a verification problem, not a technology preference. Start when one of these situations becomes material.</p>',
        '<div class="kicker">Triggers</div><h2>Call when a verification problem is blocking a decision, partnership or launch.</h2><p class="sectionIntro">The buying trigger is not “we want blockchain.” It is a trust boundary that the current architecture cannot make independently verifiable without unacceptable disclosure, coordination or authority risk.</p>',
        "trigger framing",
    )
    text = replace_once(
        text,
        '<article class="card"><span class="num">01</span><h3>A counterparty must verify a claim</h3><p>They need independent acceptance, but handing over the full source dataset is not acceptable.</p></article><article class="card"><span class="num">02</span><h3>Your own registry is the trust bottleneck</h3><p>The audit trail exists, but the party evaluating it still has to trust the operator who controls it.</p></article><article class="card"><span class="num">03</span><h3>Authority can outlive the design assumptions</h3><p>Keys, delegates, smart accounts and admin rights need explicit recovery, revocation and separation-of-duty rules.</p></article><article class="card"><span class="num">04</span><h3>The board asks the right question</h3><p>“What could another party establish if we were unavailable, compromised or simply disputed the history?”</p></article>',
        '<article class="card"><span class="num">01</span><h3>A partner will not accept your internal evidence</h3><p>They need an independent check, but sharing the complete source dataset is commercially, operationally or legally unacceptable.</p></article><article class="card"><span class="num">02</span><h3>Your operator is also the trust bottleneck</h3><p>The audit trail exists, yet the reviewer must still trust the same organization that controls writes, history and access.</p></article><article class="card"><span class="num">03</span><h3>Key and admin authority became a business risk</h3><p>Delegation, revocation, recovery, emergency control or multi-party approval now affects whether the system can be accepted.</p></article><article class="card"><span class="num">04</span><h3>A launch depends on proving a property externally</h3><p>You need a concrete answer to: what can another party establish if your organization is unavailable, compromised or disputes the history?</p></article>',
        "trigger cards",
    )

    text = replace_once(
        text,
        '<div class="kicker">Consequences</div><h2>Judge programmability by delivery properties, not by blockchain volume.</h2><p class="sectionIntro">The mechanism only earns its complexity when it changes a bounded operational property: settlement, coordination, disclosure, authorization or independent verification.</p>',
        '<div class="kicker">Consequences</div><h2>The expensive mistake is paying for the wrong trust model.</h2><p class="sectionIntro">A ledger, smart contract or proof system earns its complexity only when it changes a bounded delivery property: settlement, coordination, disclosure, authorization or independent verification. The evidence below is market and mechanism context — not a promise that DLT is universally cheaper or faster.</p>',
        "consequence commercial framing",
    )

    text = replace_once(
        text,
        '<div class="kicker">For whom</div><h2>Élodie Marchand — innovation lead / trust architect.</h2>',
        '<div class="kicker">For whom</div><h2>For the owner of the architecture decision when security, legal and operations all need to sign off.</h2>',
        "buyer heading",
    )
    text = replace_once(
        text,
        '<div class="card"><h3>Before</h3><p>Vendor-led architecture, vague “immutability” claims, and a debate that starts with chain selection.</p></div><div class="card"><h3>After</h3><p>A property-to-proof decision, explicit alternatives, verification criteria, key governance and a transferable implementation package.</p></div>',
        '<div class="card"><h3>Before</h3><p>Protocol-first debate, vendor pressure, vague “immutability” claims and no common acceptance test across stakeholders.</p></div><div class="card"><h3>After</h3><p>A decision package security, legal and operations can challenge: alternatives, property-to-proof mapping, governance, acceptance criteria and an implementation path.</p></div>',
        "buyer before after",
    )

    text = replace_once(
        text,
        '<div class="kicker">Qualification</div><h2>Good fit when another party must not simply trust your operator.</h2>',
        '<div class="kicker">Qualification</div><h2>Strong fit when the business cannot simply ask another party to trust your operator.</h2>',
        "qualification heading",
    )

    text = replace_once(
        text,
        '<div class="kicker">Proposition</div><h2>From claim to proof, with the minimum sufficient mechanism.</h2><p class="sectionIntro">The engagement converts an ambiguous trust claim into an independently testable property, then selects the least complex mechanism that can satisfy it.</p>',
        '<div class="kicker">Proposition</div><h2>Buy the architecture decision first. Implement only what survives it.</h2><p class="sectionIntro">The engagement converts an ambiguous trust claim into an independently testable property, compares conventional and verifiable mechanisms, and then delivers the least complex option that satisfies the acceptance boundary.</p>',
        "proposition commercial framing",
    )

    old_offers = '''<section id="offers" data-section-kind="buying_configurations" data-semantic-role="how_to_buy_and_offer_configurations"><div class="wrap"><div class="kicker">Offers</div><h2>Choose the configuration around the decision, not around a protocol.</h2><div class="offers"><article class="offer"><small>01 · Decision</small><h3>Property-to-Proof Architecture</h3><p>Qualification, trust-boundary mapping, architecture options, decision record and acceptance plan.</p></article><article class="offer"><small>02 · Delivery</small><h3>Smart Contract Engineering</h3><p>Solidity/EVM implementation, tests, deployment rehearsal and operational controls where justified.</p></article><article class="offer"><small>03 · Verification</small><h3>Attestation &amp; Selective Disclosure</h3><p>Credentials, signatures, commitments and selective proof paths for bounded claims.</p></article><article class="offer"><small>04 · Privacy</small><h3>ZK / ZKML Applied R&amp;D</h3><p>Feasibility, circuit/proof boundary, prover-verifier integration and fallback design.</p></article><article class="offer"><small>05 · Governance</small><h3>Key &amp; Authority Design</h3><p>Multisignature policy, delegated authority, revocation, recovery and emergency paths.</p></article><article class="offer"><small>06 · Integration</small><h3>On-chain / Off-chain Boundary</h3><p>Source-of-truth design, event interfaces, evidence storage and interoperability constraints.</p></article><article class="offer"><small>07 · Handoff</small><h3>Verification Package</h3><p>Source-controlled assets, reproducible tests, verifier scripts, runbooks and acceptance evidence.</p></article></div></div></section>'''
    new_offers = '''<section id="offers" data-section-kind="buying_configurations" data-semantic-role="how_to_buy_and_offer_configurations"><div class="wrap"><div class="kicker">Offers</div><h2>Five buyable configurations, from GO / NO-GO to implementation and handoff.</h2><p class="sectionIntro">Start at the decision layer. Expand into smart-contract, settlement, governance or ZK delivery only when that mechanism changes the acceptance result.</p><div class="offers"><article class="offer"><small>ZK-FIT · Diagnostic → applied architecture</small><h3>Tokenisation Fit &amp; Economic Architecture</h3><p>Decide whether tokenisation creates a real economic or verification advantage before selecting a chain. Leave with a bounded business case, value flow, settlement model, on/off-chain boundary and explicit GO / NO-GO.</p><a href="#engagement">Scope this configuration →</a></article><article class="offer"><small>ZK-XB · Scoping + prototype / integration architecture</small><h3>Stablecoin &amp; Cross-Border Settlement Architecture</h3><p>Translate a corridor or payment flow into settlement, identity, permission and transaction-evidence architecture without taking on issuer, reserve-management or licensing roles.</p><a href="#engagement">Scope this configuration →</a></article><article class="offer"><small>ZK-ASSET · Architecture + smart-contract delivery</small><h3>Tokenized Asset Lifecycle &amp; Governance</h3><p>Design issuance, transfer, authority, recovery, event provenance and verification across the asset lifecycle, then implement the justified state machine and controls.</p><a href="#engagement">Scope this configuration →</a></article><article class="offer"><small>ZK-RD · Applied R&amp;D / prototype → industrialisation decision</small><h3>Selective Disclosure &amp; ZK Verification R&amp;D</h3><p>Prototype a proof path when a partner must verify a property without receiving the raw data. Deliver the mechanism choice, disclosure model, verifier and documented fallback.</p><a href="#engagement">Scope this configuration →</a></article><article class="offer"><small>ZK · 3–12 months · architecture + R&amp;D + delivery</small><h3>Blockchain &amp; Verifiable Computing Delivery</h3><p>Combine smart contracts, attestations, identity, account abstraction, multisignature governance and verifiable-computing components into one accepted implementation boundary.</p><a href="#engagement">Scope this configuration →</a></article></div></div></section>'''
    text = replace_once(text, old_offers, new_offers, "commercial offer configurations")

    text = replace_once(
        text,
        '<div class="kicker">Deliverables</div><h2>Artifacts another technical team can inspect and operate.</h2>',
        '<div class="kicker">Deliverables</div><h2>You leave with decision assets, implementation artifacts and acceptance evidence.</h2>',
        "deliverables heading",
    )
    text = replace_once(
        text,
        '<div class="kicker">Before / after</div><h2>From “trust our system” to a bounded verification contract.</h2>',
        '<div class="kicker">Before / after</div><h2>From a blockchain debate to an approved, testable trust decision.</h2>',
        "before after heading",
    )
    text = replace_once(
        text,
        '<div class="kicker">Results</div><h2>Acceptance criteria, not a promise that “blockchain performs better”.</h2><p class="sectionIntro">The engagement is successful when the architecture decision and the implemented property can be checked independently within the agreed boundary.</p>',
        '<div class="kicker">Results</div><h2>What you should be able to approve at the end of the engagement.</h2><p class="sectionIntro">Success is not “we deployed blockchain.” Success is a defensible architecture decision and, when implementation is in scope, a property that can be independently checked inside the agreed boundary.</p>',
        "results heading",
    )
    text = replace_once(
        text,
        '<div class="kicker">Proof</div><h2>Public engineering evidence, separated from client claims.</h2><p class="sectionIntro">Public repositories demonstrate implementation breadth. They do not imply unmeasured client outcomes.</p>',
        '<div class="kicker">Proof</div><h2>Evidence I can execute, not just advise.</h2><p class="sectionIntro">Public repositories substantiate implementation capability while remaining separate from client-outcome claims. Use them to inspect how I build, test and document — not as a substitute for your own acceptance criteria.</p>',
        "proof framing",
    )
    text = replace_once(
        text,
        '<div class="kicker">Scope</div><h2>What is inside the engagement — and what is deliberately outside.</h2>',
        '<div class="kicker">Scope</div><h2>Know exactly what you are buying — and what remains a separate specialist role.</h2>',
        "scope heading",
    )
    text = replace_once(
        text,
        '<div class="kicker">Process</div><h2>Four phases from qualification to independent acceptance.</h2>',
        '<div class="kicker">Process</div><h2>A delivery path that can stop before unnecessary implementation.</h2>',
        "process heading",
    )
    text = replace_once(
        text,
        '<div class="kicker">Modules</div><h2>Assemble only the verification surfaces the use case needs.</h2>',
        '<div class="kicker">Modules</div><h2>Add only the modules that change the acceptance decision.</h2>',
        "modules heading",
    )
    text = replace_once(
        text,
        '<div class="kicker">Intersection</div><h2>The differentiator is the intersection, not the stack list.</h2>',
        '<div class="kicker">Intersection</div><h2>One owner across proof, data, authority and delivery removes expensive seams.</h2>',
        "intersection heading",
    )
    text = replace_once(
        text,
        '<div class="kicker">Commitments</div><h2>Bound the promise as tightly as the proof.</h2>',
        '<div class="kicker">Commitments</div><h2>What I will make inspectable before handoff.</h2>',
        "commitments heading",
    )
    text = replace_once(
        text,
        '<div class="kicker">Questions</div><h2>The four questions that usually decide the architecture.</h2>',
        '<div class="kicker">Questions</div><h2>Common buying objections, answered before scope expands.</h2>',
        "questions heading",
    )
    text = replace_once(
        text,
        '<div class="kicker">Engagement</div><h2>Evaluate the mission in 20 minutes.</h2><p class="sectionIntro" style="margin-inline:auto">Bring one property another party must verify, one current system boundary, and one reason the existing evidence path is not sufficient. The first decision is whether a verifiable-computing mechanism is justified at all.</p><div class="ctaRow" style="justify-content:center"><a class="cta primary" href="https://mickael-umt.com/contact/">Evaluate the mission</a><a class="cta secondary" href="#qualification">Review the fit criteria</a></div>',
        '<div class="kicker">Engagement</div><h2>Bring one disputed claim. Leave with a next-step decision.</h2><p class="sectionIntro" style="margin-inline:auto">In a 20-minute architecture triage, bring the property another party must verify, the current system boundary and the reason today’s evidence path is insufficient. The first outcome is a fit decision: conventional architecture, attestation, DLT, ZK — or no blockchain.</p><div class="ctaRow" style="justify-content:center"><a class="cta primary" href="https://mickael-umt.com/contact/">Request the architecture triage</a><a class="cta secondary" href="#qualification">Review fit before contacting</a></div>',
        "engagement CTA",
    )

    PAGE.write_text(text, encoding="utf-8")
    print("PASS: blockchain commercial copy v1 materialized; evidence claim spans untouched by design")


if __name__ == "__main__":
    main()
