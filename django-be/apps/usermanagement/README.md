# API Documentation

Base URL: `/api/` (prefix all routes below with your base URL)

---

## Table of Contents

- [POST /register_user/](#post-register_user)
- [POST /login_user/](#post-login_user)
- [POST /refresh_token/](#post-refresh_token)
- [POST /logout_user/](#post-logout_user)
- [GET /refresh_csrf_token/](#get-refresh_csrf_token)
- [PUT /update_user_keys/](#put-update_user_keys)
- [PUT /remove_key/](#put-remove_key)

---

## POST /register_user/

Registers a new user with Supabase authentication and stores user details in the database.

**Rate Limit:** 50 requests/day per IP

**Content-Type:** `application/json` or `application/x-www-form-urlencoded`

### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `username` | string | ✅ | Unique username |
| `email` | string | ✅ | User's email address |
| `password` | string | ✅ | User's password (handled by Supabase auth) |
| `date_of_birth` | string | ✅ | Date of birth (e.g. `"1990-01-15"`) |
| `name` | string | ✅ | First name |
| `surname` | string | ✅ | Last name |

### Example Request

```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "date_of_birth": "1990-01-15",
  "name": "John",
  "surname": "Doe"
}
```

### Success Response — `201 Created`

```json
{
  "status": "success",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "auth_id": "supabase-auth-uuid",
  "username": "johndoe"
}
```

### Error Responses

| Status | Description |
|--------|-------------|
| `400` | Missing required fields or registration error |
| `405` | Wrong HTTP method |

---

## POST /login_user/

Signs in a user via Supabase authentication and returns session tokens.

**Rate Limit:** 100 requests/hour per IP

**Content-Type:** `application/json` or `application/x-www-form-urlencoded`

### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | ✅ | Registered email address |
| `password` | string | ✅ | User's password |

### Example Request

```json
{
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

### Success Response — `200 OK`

```json
{
  "status": "success",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI...",
  "refresh_token": "v1.refresh_token_string...",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "auth_id": "supabase-auth-uuid",
  "username": "johndoe"
}
```

### Error Responses

| Status | Description |
|--------|-------------|
| `400` | Missing fields, invalid credentials, or sign-in error |
| `405` | Wrong HTTP method |

---

## POST /refresh_token/

Refreshes the Supabase session using an existing access and refresh token pair.

**Rate Limit:** 100 requests/hour per IP

**Content-Type:** `application/json` or `application/x-www-form-urlencoded`

### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `access_token` | string | ✅ | Current access token |
| `refresh_token` | string | ✅ | Current refresh token |

### Example Request

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI...",
  "refresh_token": "v1.refresh_token_string..."
}
```

### Success Response — `200 OK`

```json
{
  "status": "success",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI...(new)",
  "refresh_token": "v1.new_refresh_token...",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "auth_id": "supabase-auth-uuid",
  "username": "johndoe"
}
```

### Error Responses

| Status | Description |
|--------|-------------|
| `400` | Missing tokens or refresh failure |
| `405` | Wrong HTTP method |

---

## POST /logout_user/

Signs out a user by invalidating their Supabase session.

**Rate Limit:** 100 requests/hour per IP

**Content-Type:** `application/json` or `application/x-www-form-urlencoded`

### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `auth_id` | string | ✅ | User's Supabase auth ID |
| `access_token` | string | ✅ | Current access token |
| `refresh_token` | string | ✅ | Current refresh token |

### Example Request

```json
{
  "auth_id": "supabase-auth-uuid",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI...",
  "refresh_token": "v1.refresh_token_string..."
}
```

### Success Response — `200 OK`

```json
{
  "status": "success",
  "message": "User signed out successfully"
}
```

### Error Responses

| Status | Description |
|--------|-------------|
| `400` | Missing fields or sign-out error |
| `405` | Wrong HTTP method |

---

## GET /refresh_csrf_token/

Returns a fresh CSRF token for the current session. Use this token in subsequent state-changing requests if CSRF protection is enabled on the client.

**Rate Limit:** 40 requests/minute per IP

### Example Request

```
GET /refresh_csrf_token/
```

### Success Response — `200 OK`

```json
{
  "csrfToken": "abc123xyzCSRFtokenvalue"
}
```

---

## PUT /update_user_keys/

Stores or updates an encrypted third-party API key for a user. Keys are encrypted with AES-256 before being persisted.

**Rate Limit:** 20 requests/minute per IP

**Content-Type:** `application/json` or `application/x-www-form-urlencoded`

### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user_id` | string | ✅ | The user's UUID |
| `key_type` | string | ✅ | One of the accepted key types (see below) |
| `api_key` | string | ✅ | The plaintext API key to encrypt and store |

**Accepted `key_type` values:**

| Value | Provider |
|-------|----------|
| `pine_cone_api_key` | Pinecone |
| `gemini_api_key` | Google Gemini |
| `groq_api_key` | Groq |
| `mistral_api_key` | Mistral AI |
| `cohere_api_key` | Cohere |
| `jina_api_key` | Jina AI |

### Example Request

```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "key_type": "groq_api_key",
  "api_key": "gsk_youractualgroqapikey"
}
```

### Success Response — `200 OK`

```json
{
  "status": "success",
  "message": "groq_api_key updated successfully for user john@example.com"
}
```

### Error Responses

| Status | Description |
|--------|-------------|
| `400` | Missing fields, invalid `key_type`, or DB error |
| `405` | Wrong HTTP method (must be PUT) |

---

## PUT /remove_key/

Removes (nullifies) a stored API key for a user.

**Rate Limit:** 20 requests/minute per IP

**Content-Type:** `application/json` or `application/x-www-form-urlencoded`

### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user_id` | string | ✅ | The user's UUID |
| `key_type` | string | ✅ | One of the accepted key types (see table above) |

### Example Request

```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "key_type": "groq_api_key"
}
```

### Success Response — `200 OK`

```json
{
  "status": "success",
  "message": "groq_api_key removed successfully for user 550e8400-e29b-41d4-a716-446655440000"
}
```

### Error Responses

| Status | Description |
|--------|-------------|
| `400` | Missing fields, invalid `key_type`, or DB error |
| `405` | Wrong HTTP method (must be PUT) |

---

## Notes

- All endpoints except `refresh_csrf_token` use `@csrf_exempt`, meaning CSRF tokens are **not** enforced server-side on those routes.
- API keys stored via `update_user_keys` are encrypted using AES-256 before being written to the database.
- User actions (registration, login, logout, token refresh, key updates) are all recorded in the `UserLogs` table for auditing.
- Supabase manages the underlying authentication; the Django layer stores supplementary user data and handles logging.