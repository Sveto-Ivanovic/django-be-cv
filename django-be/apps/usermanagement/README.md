# User Management API Documentation

## Base URL

```http
http://localhost:8000/user/
```

Production example:

```http
https://api.yourdomain.com/user/
```
---

# Response Envelope

All endpoints now respond with a consistent envelope:

```json
{
  "res_status": "success",
  "response": { ... }
}
```

or on failure:

```json
{
  "res_status": "error",
  "response": "Some error message"
}
```

---

# Authentication Endpoints

## Register User

Creates a new user account and registers the user through Supabase Authentication.

### Endpoint

```http
POST /user/register_user/
```

### Request Body

```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "StrongPassword123!",
  "date_of_birth": "1995-06-15",
  "name": "John",
  "surname": "Doe"
}
```

### Example Request

```bash
curl -X POST http://localhost:8000/user/register_user/ \
-H "Content-Type: application/json" \
-d '{
    "username":"johndoe",
    "email":"john@example.com",
    "password":"StrongPassword123!",
    "date_of_birth":"1995-06-15",
    "name":"John",
    "surname":"Doe"
}'
```

### Success Response

**Status:** `201 Created`

```json
{
  "res_status": "success",
  "response": {
    "username": "johndoe"
  }
}
```

### Error Response

```json
{
  "res_status": "error",
  "response": "Missing required fields"
}
```

---

## Login User

Signs in a user using Supabase authentication.

### Endpoint

```http
POST /user/login_user/
```

### Request Body

```json
{
  "email": "john@example.com",
  "password": "StrongPassword123!"
}
```

### Example Request

```bash
curl -X POST http://localhost:8000/user/login_user/ \
-H "Content-Type: application/json" \
-d '{
    "email":"john@example.com",
    "password":"StrongPassword123!"
}'
```

### Success Response

**Status:** `200 OK`

```json
{
  "res_status": "success",
  "response": {
    "access_token": "jwt-access-token",
    "username": "johndoe"
  }
}
```

### Error Response

```json
{
  "res_status": "error",
  "response": "Error signing in user: ..."
}
```

### Cookies

The response also sets:

```http
Set-Cookie: refresh_token=<token>; HttpOnly; Secure; SameSite=Strict; Max-Age=604800
```

---

## Refresh Token

Generates a new access token using the current access token and the refresh token stored in cookies.

### Endpoint

```http
POST /user/refresh_token/
```

### Request Body

The refresh token is read from the `refresh_token` cookie automatically — only the access token needs to be sent in the body.

```json
{
  "access_token": "current-access-token"
}
```

### Example Request

```bash
curl -X POST http://localhost:8000/user/refresh_token/ \
-H "Content-Type: application/json" \
--cookie "refresh_token=current-refresh-token" \
-d '{
    "access_token":"current-access-token"
}'
```

### Success Response

```json
{
  "res_status": "success",
  "response": {
    "access_token": "new-access-token",
    "username": "johndoe"
  }
}
```

### Error Response

```json
{
  "res_status": "error",
  "response": "Missing refresh token in cookies"
}
```

### Cookies

Returns a newly generated refresh token in a secure cookie.

---

## Logout User

Logs out the authenticated user and invalidates the session.

### Endpoint

```http
POST /user/logout_user/
```

### Request Body

`auth_id` is resolved from the authenticated request, and `refresh_token` is read from the cookie — only `access_token` is required in the body.

```json
{
  "access_token": "access-token"
}
```

### Example Request

```bash
curl -X POST http://localhost:8000/user/logout_user/ \
-H "Content-Type: application/json" \
--cookie "refresh_token=refresh-token" \
-d '{
    "access_token":"access-token"
}'
```

### Success Response

```json
{
  "res_status": "success",
  "response": "User signed out successfully"
}
```

### Error Response

```json
{
  "res_status": "error",
  "response": "Missing refresh token in cookies"
}
```

---

## Refresh CSRF Token

Generates a fresh CSRF token for frontend applications (set on the session via Django's CSRF cookie).

### Endpoint

```http
GET /user/refresh_csrf_token/
```

### Example Request

```bash
curl http://localhost:8000/user/refresh_csrf_token/
```

### Success Response

```json
{
  "res_status": "success",
  "response": "Token generated successfully"
}
```

---

# API Key Management

The system supports storing encrypted API keys for supported AI and Vector Database providers.

Supported key types:

```text
pine_cone_api_key
gemini_api_key
groq_api_key
mistral_api_key
cohere_api_key
jina_api_key
```

---

## Update User API Key

Adds or updates an encrypted API key for the authenticated user.

### Endpoint

```http
PUT /user/update_user_keys/
```

### Request Body

`user_id` is resolved server-side from the authenticated request — it does not need to be sent in the body.

```json
{
  "key_type": "gemini_api_key",
  "api_key": "AIza..."
}
```

### Example Request

```bash
curl -X PUT http://localhost:8000/user/update_user_keys/ \
-H "Content-Type: application/json" \
-d '{
    "key_type":"gemini_api_key",
    "api_key":"AIza..."
}'
```

### Success Response

```json
{
  "res_status": "success",
  "response": "gemini_api_key updated successfully for user 7ab0ec74-8a12-4f5c-8e75-0b2f3f4c1234"
}
```

### Validation Errors

```json
{
  "res_status": "error",
  "response": "Invalid key type"
}
```

---

## Remove User API Key

Deletes a stored API key for the authenticated user.

### Endpoint

```http
PUT /user/remove_key/
```

### Request Body

`user_id` is resolved server-side from the authenticated request — it does not need to be sent in the body.

```json
{
  "key_type": "gemini_api_key"
}
```

### Example Request

```bash
curl -X PUT http://localhost:8000/user/remove_key/ \
-H "Content-Type: application/json" \
-d '{
    "key_type":"gemini_api_key"
}'
```

### Success Response

```json
{
  "res_status": "success",
  "response": "gemini_api_key removed successfully for user 7ab0ec74-8a12-4f5c-8e75-0b2f3f4c1234"
}
```

---

## Get User Info

Returns profile details and API-key presence flags for the authenticated user.

### Endpoint

```http
GET /user/get_user_info/
```

### Example Request

```bash
curl -X GET http://localhost:8000/user/get_user_info/ \
-H "Content-Type: application/json"
```

### Success Response

```json
{
  "res_status": "success",
  "response": {
    "user_id": "7ab0ec74-8a12-4f5c-8e75-0b2f3f4c1234",
    "username": "johndoe",
    "email": "john@example.com",
    "date_of_birth": "1995-06-15",
    "name": "John",
    "surname": "Doe",
    "user_classification": "standard",
    "api_keys": {
      "has_pinecone_api_key": true,
      "has_gemini_api_key": false,
      "has_groq_api_key": false,
      "has_mistral_api_key": false,
      "has_cohere_api_key": false,
      "has_jina_api_key": false
    }
  }
}
```

### Error Response

```json
{
  "res_status": "error",
  "response": "user_id is required"
}
```

---

# Rate Limits

| Endpoint           | Limit     |
| ------------------ | --------- |
| Register User      | 50/day    |
| Login User         | 100/hour  |
| Refresh Token      | 100/hour  |
| Logout User        | 100/hour  |
| Refresh CSRF Token | 40/minute |
| Update User Keys   | 20/minute |
| Remove Key         | 20/minute |
| Get User Info      | 20/minute |

---

# Authentication Flow

```text
Register User
      ↓
Login User
      ↓
Receive Access Token (refresh token set as HttpOnly cookie)
      ↓
Use Access Token for API Requests
      ↓
Access Token Expires
      ↓
Refresh Token Endpoint (uses cookie automatically)
      ↓
Receive New Access Token
      ↓
Logout User
```

---

# Security Features

* Supabase Authentication
* Argon2 Password Hashing
* AES-256 API Key Encryption
* HttpOnly Refresh Token Cookies
* CSRF Token Support
* Rate Limiting
* Secure Session Refresh
* Audit Logging for User Actions