# Cryptography

Use this reference when code handles encryption, hashing, signatures, tokens,
certificates, random values, key derivation, or sensitive data protection.

## Evidence First

Look for crypto libraries, algorithms, key material, certificate handling,
random number generation, password hashing, token signing, and custom encoding.
Do not claim cryptographic weakness without identifying the algorithm, mode,
key handling, or misuse.

## Findings To Open

Open a finding when evidence shows:

- custom cryptographic algorithm or homegrown protocol;
- MD5/SHA1 for security-sensitive hashing;
- AES-ECB or unauthenticated encryption for sensitive data;
- static IV/nonce, predictable IV/nonce, or nonce reuse;
- insecure randomness for tokens, reset codes, API keys, or session IDs;
- hardcoded encryption/signing keys;
- TLS certificate validation disabled;
- secrets encrypted with keys stored alongside ciphertext;
- passwords hashed with fast hashes instead of password hashing functions;
- JWT or signed payloads accepted without signature/key/issuer/audience checks.

## Do Not Open A Finding Solely Because

- SHA256 appears for checksums or non-security integrity;
- Base64 appears;
- test fixtures use fake weak keys;
- TLS config is delegated to infrastructure and no deployment evidence exists.

## Severity Guidance

- `critical`: key exposure enabling token forgery or data decryption, disabled
  TLS validation for sensitive production traffic.
- `high`: weak password hashing, unauthenticated encryption, predictable
  security tokens.
- `medium`: key rotation gaps, weak defaults in non-production configs,
  incomplete certificate pinning/validation where required.
- `low`: documentation and crypto agility improvements.

## Remediation Guidance

- use vetted libraries and standard protocols;
- use Argon2id/bcrypt/scrypt for passwords;
- use authenticated encryption such as AES-GCM or ChaCha20-Poly1305;
- use CSPRNG APIs for tokens and keys;
- store keys in managed secret/KMS systems;
- validate TLS certificates and hostname;
- rotate exposed or long-lived keys;
- add tests for invalid signatures, expired tokens, wrong issuer/audience, and
  tampered ciphertext.
