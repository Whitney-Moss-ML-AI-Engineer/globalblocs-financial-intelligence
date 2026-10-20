# Global Economic and Political Blocs: Comparison and Data Model

## Requirement

GlobalBLOCS must distinguish **formal intergovernmental organizations**, **political/economic forums**, **regional integration arrangements**, and **analytical market groupings**. They are not interchangeable. Membership, status, mandate, and institutional structures must be stored as time-aware data and verified against official organization sources before production use.

## Core groups

### BRICS and BRICS+

BRICS is a coordination grouping whose membership and partner-country arrangements have evolved. The original five were Brazil, Russia, India, China, and South Africa. Additional full members and partner arrangements have been announced in later expansion rounds; invitation, partner status, accession, and full membership must not be treated as equivalent. Store each jurisdiction's status, effective date, source URL, and verification timestamp.

Research themes: development finance, trade and investment cooperation, reform of international financial institutions, South-South cooperation, energy and food security, technology, and payment-system discussions.

Institutions and mechanisms to track include the New Development Bank (NDB), the Contingent Reserve Arrangement (CRA), summits, ministerial meetings, and published declarations. Do not assume that currency or de-dollarization proposals represent a unified implemented currency.

### G7

Members: Canada, France, Germany, Italy, Japan, the United Kingdom, and the United States. The European Union participates in G7 work but is not one of the seven national members.

Research themes: advanced-economy policy coordination, financial stability, security, sanctions, energy, climate, global health, and development finance. Track leaders' declarations, finance-minister communiqués, and official policy announcements as timestamped events.

### G20

The G20 is a major forum for international economic cooperation. Its membership comprises 19 countries plus the European Union and, following the African Union's admission, the African Union. Membership lists must be versioned by effective date. The G20 is not a treaty-based supranational government.

Research themes: global growth, financial stability, debt, development, tax, trade, climate, and international financial architecture. Track summit declarations, finance-track documents, and working-group releases.

### OECD

The Organisation for Economic Co-operation and Development develops comparative statistics, policy analysis, standards, and recommendations. Membership is a changing, formally defined list; do not hard-code an unverified count in application logic.

Research themes: national accounts, productivity, taxation, education, employment, innovation, corporate governance, competition, environment, and policy standards. OECD indicators should be recorded with definition, unit, frequency, release date, and revision status.

### European Union (EU)

The EU is a political and economic union. Store EU membership separately from Euro Area membership, Schengen participation, and other overlapping European arrangements; these memberships are not identical.

Research themes: single market, customs and trade policy, competition, financial regulation, climate policy, regional development, and common legislation. Relevant institutions include the European Commission, European Parliament, Council of the European Union, European Council, European Central Bank for euro-area monetary policy, and EU supervisory authorities.

## Other organizations and regional alignments to include

- ASEAN: Southeast Asian regional cooperation and economic integration.
- African Union (AU): continental cooperation, development, and integration.
- MERCOSUR: South American regional integration and trade.
- APEC: Asia-Pacific economic cooperation forum.
- African Continental Free Trade Area (AfCFTA): continental trade framework.
- Gulf Cooperation Council (GCC): Gulf regional cooperation.
- CPTPP and RCEP: trade agreements with distinct membership and rules.
- USMCA: North American trade agreement.
- EAEU: Eurasian economic integration.
- OPEC: oil-producing country coordination; track separately from general trade blocs.
- IMF and World Bank Group: multilateral financial institutions, not political blocs.
- WTO: multilateral trade organization, not a regional bloc.
- BIS and FSB: international financial cooperation and standard-setting bodies, not country blocs.

## Comparison dimensions

For each bloc or organization, store:
- legal/formal type and mandate;
- membership and membership status, with effective dates;
- population and GDP using clearly identified year and methodology;
- nominal GDP and PPP GDP as separate metrics;
- intra-group and external trade, FDI, portfolio flows, and supply-chain exposures;
- currencies, monetary arrangements, tariffs, and trade rules where applicable;
- energy, food, technology, defense, and transport/logistics exposures where reliable data exists;
- central-bank, financial-regulator, and securities-market coverage;
- policy announcements, sanctions, enforcement, and geopolitical-risk events;
- data sources, release dates, revision history, and quality status.

## Important comparison rules

1. Do not hard-code claims such as "BRICS represents X% of GDP" without the year, member set, and whether the calculation uses nominal GDP or purchasing-power parity (PPP).
2. Do not infer policy alignment from membership alone.
3. A country can belong to several overlapping organizations and analytical groups.
4. Membership status is time-dependent. Preserve historical membership rather than rewriting the past when a group expands.
5. Use official organization and national statistical sources for membership and indicators; use IMF, World Bank, OECD, UN, WTO, BIS, and other multilateral datasets for comparable measures and cross-checks.
6. Distinguish announcements and proposals from implemented policies.
7. Store uncertainty and missingness explicitly; unavailable data is not zero.

## Dashboard requirements

The Global BLOCS workspace should provide:
- selectable organizations and analytical groupings;
- member-country map and membership timeline;
- comparable GDP, growth, inflation, debt, trade, investment, employment, productivity, energy, and technology indicators;
- nominal-versus-PPP switch with year and source visible;
- intra-bloc versus external trade flows;
- policy-event timeline and official document retrieval;
- country, bloc, sector, and cross-bloc comparison;
- RAG answers with citations to official sources and clear distinction between facts, estimates, and model interpretation.

## Relationship to the 25 analytical groups

The repository's `configs/global_blocs.yaml` contains 25 analytical coverage groups. These are useful for market monitoring but are not a substitute for the formal organization registry. Maintain both:
- `bloc_group`: analytical grouping for comparison;
- `organization`: formal or recognized organization/forum/agreement;
- `membership`: time-aware many-to-many relationship between jurisdiction and organization/group.
