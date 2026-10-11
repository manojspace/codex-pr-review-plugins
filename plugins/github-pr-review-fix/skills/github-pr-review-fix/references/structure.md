# Structure And Convention Evidence

Load when changed code adds responsibilities, copies policy/serialization, materially grows a file or crosses an explicit user/repository threshold. A threshold draws attention; it does not itself prove a defect or require extraction. The core multiline-braces rule remains mandatory independently of this reference.

- Identify the trusted rule, dominant nearby pattern, existing helper/constant or feature boundary that applies. Inspect enough surrounding code to distinguish intentional independence from drift; avoid repository-wide frequency counts.
- If a copied parser, formatter, validation rule or serializer differs, establish whether the difference is intentional and which consumer or maintenance obligation breaks. Equivalent implementations in separate runtimes need compatible contracts, not forced consolidation.
- For new capabilities, check required registration/export/config wiring under the actual repository pattern. A missing registration that makes the feature unreachable is a functional defect, not merely an organizational preference.
- For proposed extraction, identify the new responsibility or coupling introduced by this change, intended ownership, reuse and dependency direction. Compare the smallest local fix with extraction's imports, cycles and coordination cost. A tiny safe fix in an existing giant file does not justify a broad refactor.
- Consider lazy loading only with affected bundle/runtime evidence and route/loading/error behavior. File length, default exports and local error boundaries are not universal prerequisites or reasons for it.

Stop when the relevant boundary and consequence are established. Report explicit convention violations as such, normally non-blocking; assign stronger priority only for a separate proven correctness/operational defect or material maintenance cost. Preserve unrelated style and avoid single-use abstractions or speculative architecture.
