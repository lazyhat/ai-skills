# Architecture

The compiler worker and IDE analysis worker are isolated processes. Each currently owns a local content-addressed
cache scoped to its toolchain identity. There is no shared service, authentication model, cross-worker cache identity,
invalidation policy, availability requirement, or operational owner.
