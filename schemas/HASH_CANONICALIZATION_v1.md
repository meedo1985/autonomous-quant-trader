# HASH_CANONICALIZATION_v1.md

Canonicalization rules:
1. UTF-8, LF line endings.
2. For YAML/JSON, parse then recursively sort mapping keys; preserve list order.
3. Remove the self-referential hash field (or set it to the empty string) before hashing.
4. Serialize structured objects as compact JSON with ensure_ascii=false and separators ',' ':'.
5. For Markdown self-hash fields, replace only the hash value with the empty string before hashing.
6. SHA-256 the resulting bytes.
7. This file is sidecar-hashed; its own hash is not embedded in itself.
