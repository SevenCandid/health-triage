# Security Architecture Specification

## 1. Threat Model & Security Scope

The **Health Triage Assistant** processes sensitive personal health data and emergency location information. The security architecture addresses the following threat vectors:

1. **Eavesdropping / Man-in-the-Middle (MitM)** on wireless/cellular connections.
2. **Unauthorized Access** to stored health profiles on shared mobile devices.
3. **Data Tampering / Injection** against Gemini AI prompts or API queries.
4. **Denial of Service (DoS)** targeting emergency endpoints.

---

## 2. Authentication & Authorization Architecture

```mermaid
graph TD
    Client[React PWA Client] -->|POST /auth/login (Phone + Password)| API[FastAPI Auth Controller]
    API -->|Validate Hash (Argon2id)| DB[(PostgreSQL Users)]
    API -->|Issue JWT Token (HS256, Exp: 60m)| Client
    
    Client -->|Header Authorization: Bearer JWT| ProtectedEndpoint[Protected Endpoint /users/me]
    ProtectedEndpoint -->|Verify JWT Signature & Expiry| Service[UseCase Execution]
```

### Security Parameters:
- **Password Hashing**: Passlib with `argon2id` (Salt length: 16 bytes, Memory cost: 64 MB).
- **JWT Signature**: HMAC-SHA256 with 256-bit environment secret key.
- **Token Expiry**: Access Token: 60 minutes; Refresh Token: 30 days (stored in HTTP-Only, SameSite=Strict cookies).

---

## 3. Data Encryption Standards

### 3.1 Encryption in Transit
- **TLS Protocol**: TLS 1.3 mandatory across all public-facing endpoints. TLS 1.0 and 1.1 explicitly disabled.
- **Cipher Suites**: `ECDHE-ECDSA-AES128-GCM-SHA256`, `ECDHE-RSA-AES256-GCM-SHA384`.
- **HSTS Header**: `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`.

### 3.2 Encryption at Rest
- **Client Storage (IndexedDB)**: Sensitive local profile fields (full name, allergies, contacts) encrypted using Web Crypto API (`AES-GCM-256`) before writing to IndexedDB.
- **Server Storage (PostgreSQL)**: Database volumes encrypted at rest via AWS EBS AES-256 / LUKS block device encryption.

---

## 4. Rate Limiting & Input Sanitization

### 4.1 Rate Limiting Matrix (FastAPI SlowAPI / Redis)
- `/api/v1/auth/login`: 5 requests per minute per IP.
- `/api/v1/triage/evaluate`: 30 requests per minute per user.
- `/api/v1/consultation/stream`: 10 requests per minute per user.
- `/api/v1/emergency/dispatch`: Unlimited / High Priority Queue.

### 4.2 Content Security Policy (CSP) & CORS
- **CORS Allowed Origins**: Strict whitelist configured via environment variable (e.g., `https://healthtriage.org`).
- **CSP Header**:
  ```text
  Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self' https://api.healthtriage.org https://generativelanguage.googleapis.com; media-src 'self' blob:;
  ```
