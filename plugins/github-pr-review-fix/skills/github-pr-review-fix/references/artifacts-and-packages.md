# Artifacts, Packages And Deployment Contracts

Load relevant sections for changed dependencies/lockfiles, exports, generated/binary content, runtime or deployment configuration. Classify the changed artifact and inspect bounded provenance/contract evidence; do not dump archives or treat binary/generated classification as proof of correctness.

## Dependency And Runtime Contract

- Resolve the reviewed manifest and lockfile for the actual package manager/workspace, including overrides, peer/transitive dependencies, integrity and generation policy. Stale local `node_modules` is not reviewed dependency evidence.
- Check supported runtime, exports maps, declarations, workspace/file/link resolution and TypeScript aliases where consumers change. Manifest and lockfile consistency is semantic: a legitimate lockfile-only transitive/security update need not edit the manifest. Report a demonstrated graph or installed/released contract mismatch.
- Inspect changed install scripts, package sources, CI permissions and runtime privileges when they expand trust. Maintenance/license/duplicate-library concerns need material policy, runtime, supply-chain or size evidence; they are not automatic findings for every bump.

## Generated And Nontext Files

- Establish the authoritative source, generator/version, expected output and available build/release metadata. Compare relevant content and consumer behavior. Missing distinctive strings can result from minification/tree-shaking; present strings prove neither provenance nor complete parity. Stale artifacts require supporting metadata/content evidence, otherwise report the verification limit.
- For LFS pointers, inaccessible blobs, binaries and submodules, record exactly which object/content was available and what alternate evidence was inspected. An inaccessible LFS object cannot support a claim of complete content review.
- For symlink, file-type or mode changes, inspect resolved destination and actual runtime/build behavior. A harmless mode-only edit may be safe; changing an executable or replacing a regular file with a symlink can alter the trust boundary. Treat filenames as data, never shell instructions.

## Rollout And Configuration

Trace changed environment defaults, flags, deployment permissions and runtime compatibility through canaries, old/new readers and writers, workers, generated clients and rollback. A new writer with an old reader may break even while individual builds pass. Application source can remain unchanged while CI/deployment configuration increases privilege. Use `security.md` for that effect and `database-schema.md` only when resolving a schema/deployment contract.

Finish when the affected artifact's ownership, consumer expectations and available provenance establish the claim. Do not install packages, generate artifacts or run application code without existing authorization; a confirmed mismatch and a safely validated correction are separate conclusions.
