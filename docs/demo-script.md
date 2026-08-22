# Demo Script — Kardashev Scaler

Use this stable historical NASA POWER query throughout the presentation:

- Location: **New Delhi, India** — latitude `28.6139`, longitude `77.2090`
- Date range: `2025-08-01` to `2025-08-07`
- Panel area: `10 m²`
- Panel efficiency: `22%`
- Usage Intelligence consumption: `6 kWh`

## Presenter flow

1. Open `/`, introduce the glowing mark, then select **Enter**.
2. On Overview, confirm the Delhi coordinates and replace the default dates/specs with the values above. Select **Run comparison**. Expect non-zero fixed and tracked output, with tracked output higher than fixed.
3. Expect roughly **53.48 kWh fixed**, **57.10 kWh tracked**, and **6.78% gain**. Explain that Kardashev Progress is Earth-scale, not a panel score. If Supabase is configured, the stored comparison enables the Earth-scale projection card. Without it, the panel honestly explains that session persistence is needed.
4. Select **Usage Intelligence** and enter `6` kWh consumption. Select **Analyze usage**. Compare captured, consumed, waste, and deficit; explain that these are derived from a reconciled per-window energy ledger.
5. Select **Absorption Optimization**, then **Rank zones**. The 3 × 3 text grid ranks the high-resource, low-density areas around Delhi. This is the only step that makes several NASA requests, so allow a few seconds.
6. Select **Distribution Logic**, then **Model allocation**. Explain the proportional 40/40/20 allocation and visible placeholder-baseline shortfalls.
7. Select **Recommendation Engine**, then **Generate recommendations**. Explain that every result is an auditable rule, not a black-box model.

## Demo-day fallback

The exact Delhi date/location query above is pre-warmed with real NASA POWER results. If NASA POWER is unreachable, Tracker Comparison automatically uses that cached sample and visibly states: **“Showing cached sample data — NASA POWER was unavailable.”** It is limited to this exact documented query and must not be represented as a live response.
