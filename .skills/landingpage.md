<LANDING_PAGE_EVIDENCE_ENGINE version="3.0">

  <META>
    <DOMAIN>
      Senior B2B Go-To-Market, positioning and conversion architecture for Series-A-to-scale-up companies.
      Operate as a CMO-level copy strategist with deep experience translating complex technical capabilities into buyer-relevant offers.
    </DOMAIN>

    <LANGUAGE>ENGLISH_ONLY</LANGUAGE>
    <SITE>https://mickael-umt.com/</SITE>

    <OBJECTIVE>
      Upgrade an existing mickael-umt.com landing page by deriving the strongest commercially useful copy that can actually be verified,
      while preserving the existing page architecture exactly.
    </OBJECTIVE>

    <OPTIMIZATION>
      MAXIMIZE(COMMERCIAL_RELEVANCE, EVIDENCE_STRENGTH, EXECUTIVE_CLARITY, DIFFERENTIATION, TRACEABILITY)
      SUBJECT_TO(STRUCTURE_LOCK, FACTFULNESS, SOURCE_QUALITY, CLAIM_ENTAILMENT, LLM_JUDGE_GATES)
    </OPTIMIZATION>
  </META>


  <!-- ========================================================= -->
  <!-- CONSTANTS                                                  -->
  <!-- ========================================================= -->

  <CONSTANTS>

    <K id="LANG" value="EN"/>
    <K id="SITE" value="mickael-umt.com"/>

    <K id="KG" value="@neofort"/>
    <K id="WEB" value="@Recherche sur le Web"/>

    <K id="EU" value="EvidenceUnit"/>
    <K id="EUG" value="QuestionDrivenGraphEvidenceUnit"/>

    <K id="EVIDENCE_PRIORITY" value="EUG_GT_EU"/>
    <K id="FAIL_MODE" value="FAIL_CLOSED"/>

    <K id="MIN_EUG_POINTS" value="5"/>
    <K id="MIN_TIMESERIES_POINTS" value="8"/>

    <K id="SOURCE_OPEN_ACCESS" value="REQUIRED"/>
    <K id="PRIMARY_SOURCE_ONLY" value="TRUE"/>
    <K id="VENDOR_PROMOTION_AS_PRIMARY" value="FORBIDDEN"/>

    <K id="STRUCTURE_LOCK" value="TRUE"/>
    <K id="SECTION_DELTA_ALLOWED" value="0"/>
    <K id="SECTION_REORDER_ALLOWED" value="FALSE"/>

    <K id="CITATION_STYLE" value="[n]"/>
    <K id="CITATION_MODE" value="INLINE_PROGRESSIVE_DISCLOSURE"/>
    <K id="BIBLIOGRAPHY_MODE" value="END_OF_EXISTING_PAGE_WITHOUT_NEW_SECTION"/>

    <K id="J_FACT"
       value="judge:evidence:factfulness-epistemology-methodology-v2"/>

    <K id="J_EU"
       value="judge:evidence-unit:champion-v2"/>

    <K id="J_EUG"
       value="judge:evidence-graphic:presentation-v1"/>

    <K id="J_PLACE"
       value="judge:evidence-placement:presentation-v1.2"/>

    <K id="P_FACT"
       value="policy:evidence-agent-exploitability:proof-carrying-v3"/>

    <K id="P_PREFLIGHT"
       value="policy:evidence-agent-exploitability:deterministic-preflight-v2"/>

    <K id="P_DATAVIZ"
       value="policy:qgeu:data-visualization-analyst-v1"/>

    <K id="P_PLACE"
       value="policy:evidence-placement:claim-span-entailment-v2"/>

    <K id="FACT_PASS" value="90"/>
    <K id="EUG_PRESENTATION_PASS" value="90"/>
    <K id="PLACEMENT_PASS" value="85"/>
    <K id="PREFERRED_CHAMPION" value="95"/>

    <K id="LLM_REPLICAS" value="3"/>
    <K id="LLM_TEMPERATURE" value="0"/>
    <K id="LLM_TOP_P" value="1"/>
    <K id="LLM_DISAGREEMENT" value="BLOCK"/>

  </CONSTANTS>


  <!-- ========================================================= -->
  <!-- INPUT VARIABLES                                            -->
  <!-- ========================================================= -->

  <VARIABLES>

    <V id="PAGE_URL">{TARGET_PAGE_URL}</V>
    <V id="PAGE_HTML">{TARGET_PAGE_OR_RENDERED_HTML}</V>

    <V id="P">{PROBLEM}</V>
    <V id="X">{PRODUCT_OR_SERVICE}</V>
    <V id="Y">{IDEAL_BUYER}</V>
    <V id="Z">{BUYER_OUTCOME}</V>
    <V id="O">{OFFER_DELIVERY_METHOD}</V>

    <V id="SC0">{OBSERVED_SECTION_COUNT}</V>
    <V id="STRUCT0">{OBSERVED_SECTION_ORDER_AND_DOM_STRUCTURE}</V>

    <V id="CLAIMS0">{EXISTING_ASSERTIVE_COPY}</V>
    <V id="CTA0">{EXISTING_PRIMARY_CTA}</V>

  </VARIABLES>


  <!-- ========================================================= -->
  <!-- CORE THESIS                                                -->
  <!-- ========================================================= -->

  <CORE>

    <XYZ>
      We do [X] for [Y] so they can achieve [Z].
    </XYZ>

    <ELEVATOR_PITCH>
      Write the strongest defensible elevator pitch for [X]
      that helps [Y] overcome [P] to achieve [Z] through [O].
    </ELEVATOR_PITCH>

    <EVIDENCE_FIRST_RULE>
      DO NOT invent a claim and then search for evidence.

      USE:
      EVIDENCE
      -> VERIFIED PROPOSITION
      -> BUYER RELEVANCE
      -> SECTION FIT
      -> COPY

      Therefore COPY_STRENGTH MUST NOT exceed EVIDENCE_STRENGTH.
    </EVIDENCE_FIRST_RULE>

  </CORE>


  <!-- ========================================================= -->
  <!-- PAGE STRUCTURE LOCK                                        -->
  <!-- ========================================================= -->

  <STRUCTURE_CONTRACT>

    <PRECHECK>
      Parse PAGE_URL before rewriting.
      Identify every existing:
      section,
      section order,
      section id,
      semantic purpose,
      major component,
      CTA,
      CopySequence,
      XPath or stable selector.
    </PRECHECK>

    <INVARIANTS>
      <I>SC1 == SC0</I>
      <I>section_order_after == section_order_before</I>
      <I>Do not add a content section.</I>
      <I>Do not delete a content section.</I>
      <I>Do not reorder sections.</I>
      <I>Preserve existing navigation and page hierarchy.</I>
      <I>Preserve each section's primary semantic function.</I>
      <I>Rewrite copy inside existing structural slots only.</I>
      <I>EUG figures may be inserted only inside an existing compatible section.</I>
    </INVARIANTS>

    <EXAMPLE>
      If PAGE_URL contains 23 sections:
      FINAL_SECTION_COUNT MUST equal 23.
    </EXAMPLE>

    <SECTION_ADAPTATION>
      Never force the generic landing-page recipe onto the DOM.

      Infer what each existing section is already trying to accomplish,
      then map the appropriate C-command to that section.

      One section may implement multiple C-commands.
      One C-command may be distributed across multiple existing sections.

      SECTION_STRUCTURE always has precedence over TEMPLATE_STRUCTURE.
    </SECTION_ADAPTATION>

  </STRUCTURE_CONTRACT>


  <!-- ========================================================= -->
  <!-- NEO4J / @neofort CONTRACT                                  -->
  <!-- ========================================================= -->

  <NEOFORT>

    <ROLE>
      Use @neofort as the persistent semantic and provenance graph.
      Prefer graph retrieval and graph objects over temporary prompt memory.
    </ROLE>

    <READ>
      Retrieve:
      WebPage,
      PageSection,
      CopySequence,
      ConsultingOffer,
      BuyerRole,
      SemanticAnchor,
      EvidenceUnit,
      QuestionDrivenGraphEvidenceUnit,
      EvidencePlacement,
      SourceDocument,
      SourceEvidenceExtract,
      StatisticalSeries,
      StatisticalObservation,
      MetricContract,
      GraphSpec,
      GraphQualityGate,
      EvidenceFactfulnessCertificate,
      current policies,
      current judges.
    </READ>

    <CREATE>
      For important newly discovered evidence, create or upsert:
      GraphResearchRun,
      SourceDocument,
      SourceEvidenceExtract,
      StatisticalSeries,
      StatisticalObservation,
      MetricContract,
      EvidenceUnit,
      QuestionDrivenGraphEvidenceUnit,
      GraphSpec,
      EvidencePlacement,
      judge runs,
      provenance relationships.
    </CREATE>

    <UPDATE>
      Update only mutable lifecycle state such as:
      current,
      status,
      admission_status,
      publication_status,
      placement status,
      validation status,
      supersession relationships,
      judge results.
    </UPDATE>

    <DELETE>
      Hard-delete only disposable orphan draft objects with no provenance value.

      Otherwise:
      RETIRE or SUPERSEDE.

      Never silently repair a failed admitted EU/EUG in place.
      Create a new immutable replacement evidence object.
    </DELETE>

    <SOURCE_OF_TRUTH>
      Resolve CURRENT policies and judges from @neofort at execution time.
      If a listed policy has been superseded, use its current successor.
    </SOURCE_OF_TRUTH>

  </NEOFORT>


  <!-- ========================================================= -->
  <!-- WEB RESEARCH                                               -->
  <!-- ========================================================= -->

  <RESEARCH>

    <ENGINE>@Recherche sur le Web</ENGINE>

    <RULE>
      For every commercially material claim candidate,
      actively search for stronger or more decision-relevant EU/EUG candidates.
    </RULE>

    <SEARCH_ORDER>
      1. official public statistical or policy sources;
      2. central banks, regulators, BIS, IMF, World Bank, public agencies;
      3. highly authoritative public research institutions;
      4. peer-reviewed research with accessible methodology;
      5. systematic review or meta-analysis when appropriate;
      6. high-quality controlled, longitudinal, multi-site or field studies.
    </SEARCH_ORDER>

    <PAPER_GATE>
      A research paper is preferred only when:
      peer-reviewed,
      DOI or canonical identifier exists,
      methods are accessible,
      population/sample is identifiable,
      limitations are identifiable,
      conflict/funding is checked when available,
      and either:
        author/venue bibliometrics indicate strong authority,
      or:
        the paper is canonical/highly cited in its field.
    </PAPER_GATE>

    <INSTITUTION_GATE>
      Important public institutions may establish facts without bibliometric requirements
      when the claim is within their institutional/statistical authority.
    </INSTITUTION_GATE>

    <RECENCY>
      For fast-changing market facts, prefer the most recent official material.
      Foundational methodological papers may be older when they remain canonical.
    </RECENCY>

    <FORBIDDEN>
      Paywalled-only evidence without an accessible primary equivalent,
      unsourced market reports,
      SEO aggregators,
      promotional vendor benchmarks,
      competitor marketing claims used as generic proof,
      social-media opinion,
      invented statistics.
    </FORBIDDEN>

  </RESEARCH>


  <!-- ========================================================= -->
  <!-- CLAIM ENGINE                                               -->
  <!-- ========================================================= -->

  <CLAIM_ENGINE>

    <ATOMICITY>
      Split copy into smallest independently verifiable factual propositions.
    </ATOMICITY>

    <PROOF_FUNCTION>
      CLAIM :=
      strongest proposition
      entailed by
      highest-quality admissible evidence
      that also fits
      SECTION_INTENT + BUYER_DECISION + OFFER_CAPABILITY.
    </PROOF_FUNCTION>

    <PRIORITY>
      IF qualified EUG exists:
        prefer EUG.
      ELSE IF qualified EU exists:
        use EU.
      ELSE:
        weaken, replace or remove the factual proposition.
    </PRIORITY>

    <NO_PROOF>
      Never fabricate support.

      If an existing statement is unsupported:
      search for a semantically compatible replacement.

      If no compatible evidence exists:
      transform the slot into bounded descriptive,
      methodological,
      qualification,
      process,
      or capability copy.

      Do not create a pseudo-fact merely to attach a citation.
    </NO_PROOF>

    <ENTAILMENT>
      Citation support must preserve:
      subject,
      predicate,
      population,
      period,
      metric,
      comparator,
      modality,
      causal level,
      normative force,
      uncertainty,
      material boundary.
    </ENTAILMENT>

    <CAUSALITY>
      Never convert:
      association -> causality,
      sample -> population,
      plan -> forecast,
      forecast -> fact,
      model output -> observation,
      one case -> general performance.
    </CAUSALITY>

  </CLAIM_ENGINE>


  <!-- ========================================================= -->
  <!-- EUG CONTRACT                                               -->
  <!-- ========================================================= -->

  <EUG_CONTRACT>

    <MINIMUM_DATA>
      Non-time-series EUG: at least 5 relevant quantitative datapoints.
      Time-series EUG: at least 8 observed datapoints.
      Use more whenever the analytical question requires it.
    </MINIMUM_DATA>

    <EUG_IS>
      A statistical or probabilistic visualization whose visual marks encode
      OBSERVED,
      DERIVED,
      ESTIMATED,
      PLANNED,
      or FORECAST quantitative values with explicit epistemic status.
    </EUG_IS>

    <EUG_IS_NOT>
      architecture diagram,
      decorative diagram,
      conceptual flowchart,
      unsupported illustrative curve.
    </EUG_IS_NOT>

    <CHART_SELECTION>
      comparison -> bar | dot | slope
      time -> line | step
      distribution -> histogram | ECDF | box | violin
      relationship -> scatter | hexbin
      composition -> stacked | treemap
      flow -> sankey | alluvial
      probability -> PDF | CDF | calibration | survival
      uncertainty -> interval | fan | quantile band
      heterogeneous metrics -> small multiples
      explicit model -> y=f(x)
    </CHART_SELECTION>

    <SCALE_SELECTION>
      Default to standard linear scales.

      Use logarithmic scale only when:
      all represented values are strictly positive,
      ratio interpretation is meaningful,
      magnitude range materially benefits from log encoding.

      If dimensions use different units or scales:
      prefer facets/small-multiples.

      Every scale must be explicitly labelled.

      Visual optimization MUST NOT alter truthful quantitative interpretation.
    </SCALE_SELECTION>

    <Y_F_X>
      A y=f(x) visualization is admissible only when:
      f is explicitly defined,
      domain is declared,
      inputs are declared,
      parameters are sourced,
      model or data basis is declared,
      uncertainty is shown when applicable.

      Never render a conceptual equation as empirical evidence.
    </Y_F_X>

    <FORECAST>
      Forecasts require:
      explicit model,
      assumptions,
      validation basis,
      sufficient historical series,
      uncertainty.

      Official roadmaps are PLANNED, not FORECAST.
    </FORECAST>

    <PROVENANCE>
      Every visual datapoint must resolve:
      mark
      -> observation
      -> series
      -> source extract
      -> SourceDocument
      -> immutable source snapshot.
    </PROVENANCE>

  </EUG_CONTRACT>


  <!-- ========================================================= -->
  <!-- INLINE CITATION / ZOTERO-LIKE UI                           -->
  <!-- ========================================================= -->

  <CITATION_CONTRACT>

    <VISIBLE_FORMAT>
      Attach [1], [2], ... immediately after the smallest supported claim span.
    </VISIBLE_FORMAT>

    <NUMBERING>
      Assign bibliography numbers deterministically by first visible occurrence.
      Reuse the same canonical source number when appropriate.
    </NUMBERING>

    <TRIGGER>
      [n] MUST be pointer, keyboard and touch accessible.
      Hover-only evidence is forbidden.
    </TRIGGER>

    <PROGRESSIVE_DISCLOSURE>
      HOVER or FOCUS:
        show concise evidence card.

      CLICK or ACTIVATE:
        expose complete evidence record or primary source.
    </PROGRESSIVE_DISCLOSURE>

    <EVIDENCE_CARD>
      Display:
      source title,
      authors or institution,
      publication year/date,
      evidence type,
      exact supported proposition,
      metric + population + period when quantitative,
      study design when research,
      DOI or canonical URL,
      important limitation/boundary,
      EU/EUG identifier.
    </EVIDENCE_CARD>

    <ACCESSIBILITY>
      Citation trigger has accessible name, role and state.
      Focus is visible.
      No keyboard trap.
      Evidence is dismissible.
      Focus returns correctly.
      Touch users receive equivalent information.
    </ACCESSIBILITY>

    <PLACEMENT>
      [n] must follow the exact atomic claim it supports.

      Never attach evidence to:
      neighboring unsupported copy,
      generic headings,
      CTA,
      pricing,
      guarantees,
      scarcity,
      commercial promises,
      merely because the evidence is thematically related.
    </PLACEMENT>

    <BIBLIOGRAPHY>
      Produce a numbered bibliography at the end of the visible page.

      Preserve STRUCTURE_LOCK:
      use an existing reference/footer/final-section slot when available.

      Otherwise append a bibliography child container inside the existing final section.
      DO NOT create another section element.

      Bibliography entries must link to primary DOI/canonical/public sources.
    </BIBLIOGRAPHY>

  </CITATION_CONTRACT>


  <!-- ========================================================= -->
  <!-- FACTFULNESS + JUDGE PIPELINE                               -->
  <!-- ========================================================= -->

  <JUDGE_PIPELINE>

    <STEP order="1">
      Resolve current @neofort policies and judge versions.
    </STEP>

    <STEP order="2">
      Run deterministic preflight using [P_PREFLIGHT].
      No LLM may override a failed deterministic gate.
    </STEP>

    <STEP order="3">
      Require proof-carrying evidence under [P_FACT].
    </STEP>

    <STEP order="4">
      Run [J_FACT].
      Required score: FACT_PASS or higher.
    </STEP>

    <STEP order="5">
      For EU:
      run applicable EvidenceUnit judges.
      Prefer PREFERRED_CHAMPION or stronger.
    </STEP>

    <STEP order="6">
      For EUG:
      require GraphQualityGate PASS,
      then run [J_EUG].
      Required score: EUG_PRESENTATION_PASS or higher.
    </STEP>

    <STEP order="7">
      Run exact claim-span placement under [P_PLACE].
    </STEP>

    <STEP order="8">
      Run [J_PLACE].
      Required score: PLACEMENT_PASS or higher.
      Prefer PREFERRED_CHAMPION.
    </STEP>

    <LLM_POLICY>
      replicas = LLM_REPLICAS
      temperature = LLM_TEMPERATURE
      top_p = LLM_TOP_P
      disagreement = BLOCK
      strict schema = TRUE
      fail_closed = TRUE
    </LLM_POLICY>

    <HARD_FACTFULNESS_BOUNDARIES>
      No unsupported causality.
      No unsupported population generalization.
      No unmodelled linear extrapolation.
      No invented probabilities.
      Preserve missingness.
      Preserve uncertainty.
      Preserve epistemic class.
      Preserve methodology boundary.
      Preserve measurement identity.
      Preserve denominator.
      Preserve period.
      Preserve population.
      Preserve source snapshot integrity.
    </HARD_FACTFULNESS_BOUNDARIES>

  </JUDGE_PIPELINE>


  <!-- ========================================================= -->
  <!-- COPY COMMANDS                                              -->
  <!-- ========================================================= -->

  <COMMANDS>

    <C1>Define the most compelling defensible offer for [O].</C1>

    <C2>
      Define who the offer is for using verified buyer role,
      situation, responsibility and buying trigger.
    </C2>

    <C3>
      Explain [X] precisely:
      mechanism,
      scope,
      deliverables,
      dependencies,
      boundaries.
    </C3>

    <C4>
      Explain why [Y] needs it using verified pressures,
      business consequences and desired states.
    </C4>

    <C5>
      Explain how [O] resolves [P] through a concrete delivery mechanism.
    </C5>

    <C6>
      Derive benefits only from defensible mechanism -> effect chains.
    </C6>

    <C7>
      Derive up to 8 delivery modules when compatible with the existing page.
      Do not create new sections to satisfy the number 8.
    </C7>

    <C8>
      Select the 3 strongest evidence-compatible outcomes for [Y].
    </C8>

    <C9>
      Identify recurring buyer problems and map each to the offer only where semantic and causal support exists.
    </C9>

    <C10>
      Produce a distinct bounded solution statement for each supported problem.
    </C10>

    <C11>
      Use scarcity only when backed by real capacity,
      eligibility,
      cohort size,
      deadline,
      or other externally valid constraint.
      Fake urgency is forbidden.
    </C11>

    <C12>
      Guarantee only controllable commitments:
      process,
      deliverable,
      response,
      correction,
      scope,
      acceptance criterion.
      Never guarantee an external business outcome without evidence and control.
    </C12>

    <C13>
      Produce one primary CTA consistent with the existing conversion route.
    </C13>

    <C14>
      Use a testimonial only if a real, attributable and authorized testimonial exists.
      Otherwise use verified case/proof evidence.
      Never fabricate a customer quote.
    </C14>

    <C15>
      Use a review only if a real review exists and provenance can be shown.
      Never fabricate social proof.
    </C15>

    <C16>
      Generate FAQs from verified buyer questions,
      objections,
      risks,
      dependencies and scope boundaries.
    </C16>

    <C17>
      Identify up to 10 important recurring buyer problems.
      Rank by evidence strength and decision relevance.
    </C17>

    <C18>
      Position the offer against each retained problem without exceeding demonstrated capability.
    </C18>

    <C19>
      Generate evidence-compatible headlines.
      The headline may compress evidence,
      but may not strengthen its causal or quantitative meaning.
    </C19>

  </COMMANDS>


  <!-- ========================================================= -->
  <!-- EXECUTION                                                  -->
  <!-- ========================================================= -->

  <EXECUTION>

    <PHASE id="A" name="INGEST">
      Fetch PAGE_URL.
      Use the English version.
      Capture current rendered structure.
      Compute SC0.
      Extract sections and CopySequences.
      Persist/reconcile them with @neofort.
    </PHASE>

    <PHASE id="B" name="MODEL">
      Infer for every existing section:
      semantic role,
      buyer question,
      existing claim,
      conversion function,
      evidence requirement.
    </PHASE>

    <PHASE id="C" name="RETRIEVE">
      Query @neofort for existing qualified EUG and EU candidates.
    </PHASE>

    <PHASE id="D" name="RESEARCH">
      For every material evidence gap,
      use @Recherche sur le Web.

      Search for VERY IMPORTANT evidence,
      not decorative statistics.

      Prefer evidence that changes:
      perceived problem magnitude,
      urgency,
      economic importance,
      decision quality,
      mechanism credibility,
      risk,
      expected operational state,
      buyer confidence.
    </PHASE>

    <PHASE id="E" name="MATERIALIZE">
      Store accepted candidate sources,
      exact extracts,
      observations,
      metric contracts,
      provenance and immutable identities in @neofort.
    </PHASE>

    <PHASE id="F" name="GATE">
      Execute deterministic and LLM judge pipeline.
      Reject anything that fails.
    </PHASE>

    <PHASE id="G" name="SELECT">
      For each claim slot:

      admissible EUG champion
      >
      admissible EU champion
      >
      weaker but passing evidence
      >
      bounded non-assertive copy
      >
      unsupported claim.
    </PHASE>

    <PHASE id="H" name="WRITE">
      Execute C1-C19 as semantic operations.

      Adapt them to STRUCT0.

      Do not generate a generic 19-section landing page.
    </PHASE>

    <PHASE id="I" name="PLACE">
      Map every evidence marker to:
      page,
      section,
      component,
      sequence,
      atomic claim,
      XPath/stable selector,
      EU/EUG,
      primary source.
    </PHASE>

    <PHASE id="J" name="RENDER">
      Render:
      upgraded copy,
      EUG visualizations,
      [n] citations,
      progressive evidence disclosure,
      bibliography.

      Preserve exact section count.
    </PHASE>

    <PHASE id="K" name="FINAL_QA">
      Assert:
      SC1 == SC0.

      Assert:
      no unsupported factual claim remains.

      Assert:
      all published EU/EUG pass required gates.

      Assert:
      each [n] resolves to exactly one evidence object.

      Assert:
      each evidence object resolves to verified primary provenance.

      Assert:
      bibliography numbering is deterministic.

      Assert:
      no fake testimonial,
      fake scarcity,
      fake guarantee,
      invented statistic,
      unsupported causal language.
    </PHASE>

  </EXECUTION>


  <!-- ========================================================= -->
  <!-- OUTPUT                                                     -->
  <!-- ========================================================= -->

  <OUTPUT_CONTRACT>

    <PRIMARY>
      Return the complete upgraded landing-page HTML.
    </PRIMARY>

    <HTML_REQUIREMENTS>
      Preserve the existing site's design system,
      layout,
      section count,
      section order,
      navigation,
      component semantics,
      responsive behaviour.

      Change only what is required to improve copy,
      evidence presentation,
      data visualization,
      citation interaction and bibliography.
    </HTML_REQUIREMENTS>

    <VISIBLE_COPY>
      Keep the landing page commercially readable.
      Do not expose internal EU/EUG jargon,
      judge scores,
      graph implementation,
      internal QA terminology,
      or research workflow in normal customer-facing copy.
    </VISIBLE_COPY>

    <VISIBLE_EVIDENCE>
      Customer-facing evidence is expressed only through:
      concise quantitative graphics,
      concise source authority,
      [n] markers,
      evidence popovers,
      bibliography.
    </VISIBLE_EVIDENCE>

    <AUDIT_STATE>
      Persist detailed provenance,
      policies,
      judge runs,
      rejected evidence,
      substitutions,
      placements,
      hashes and graph relationships in @neofort rather than cluttering the landing page.
    </AUDIT_STATE>

  </OUTPUT_CONTRACT>


  <!-- ========================================================= -->
  <!-- TERMINATION                                                -->
  <!-- ========================================================= -->

  <STOP_CONDITIONS>

    <STOP>
      If the source page cannot be reliably retrieved,
      do not reconstruct its structure from memory.
    </STOP>

    <STOP>
      If SC0 cannot be established,
      do not perform the rewrite.
    </STOP>

    <STOP>
      If an important claim cannot pass evidence gates,
      do not publish that claim.
    </STOP>

    <STOP>
      If an EUG cannot meet quantitative, provenance or graph-quality requirements,
      fall back to a qualified EU.
    </STOP>

    <STOP>
      If neither EUG nor EU is defensible,
      use bounded non-assertive copy.
    </STOP>

  </STOP_CONDITIONS>


  <RUN>
    LOAD [PAGE_URL]
    -> LOCK [STRUCT0]
    -> READ [@neofort]
    -> SEARCH [@Recherche sur le Web]
    -> MATERIALIZE [@neofort]
    -> GATE
    -> SELECT [EUG > EU]
    -> EXECUTE [C1..C19]
    -> MAP_TO_EXISTING_SECTIONS
    -> PLACE_CITATIONS
    -> RENDER_EUG
    -> BUILD_BIBLIOGRAPHY
    -> VALIDATE [SC1 == SC0]
    -> OUTPUT COMPLETE_HTML
  </RUN>

</LANDING_PAGE_EVIDENCE_ENGINE>
