# Global_Data and current surveillance separation policy

`outbreaks/Global_Data/` is for finalized or source-audited historical outbreak index work.

`surveillance-current/` is for mutable, rapidly evolving current situation monitoring.

Separation rules:

1. Historical Phase 1 outputs must only read from locked HDX historical sources and audited historical metadata.
2. Current surveillance data must use separate files, separate source registry entries, and separate report labels.
3. Current surveillance must not alter West Africa 2014-2016 or North Kivu/Ituri 2018-2020 processed tables.
4. Any future merge from current surveillance into Global_Data requires a freeze date, checksum/snapshot hash, and explicit review.
