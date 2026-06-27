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
  "status": "success",
  "user_id": "7ab0ec74-8a12-4f5c-8e75-0b2f3f4c1234",
  "auth_id": "supabase-auth-id",
  "username": "johndoe"
}
```

### Error Response

```json
{
  "message": "Missing required fields"
}
```

---

## Login User

Authenticates a user and returns an access token.

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
  "status": "success",
  "access_token": "jwt-access-token",
  "user_id": "7ab0ec74-8a12-4f5c-8e75-0b2f3f4c1234",
  "auth_id": "supabase-auth-id",
  "username": "johndoe"
}
```

### Cookies

The response also sets:

```http
Set-Cookie: refresh_token=<token>; HttpOnly; Secure; SameSite=Strict
```

---

## Refresh Token

Generates a new access token using the current access token and refresh token.

### Endpoint

```http
POST /user/refresh_token/
```

### Request Body

```json
{
  "access_token": "current-access-token",
  "refresh_token": "current-refresh-token"
}
```

### Example Request

```bash
curl -X POST http://localhost:8000/user/refresh_token/ \
-H "Content-Type: application/json" \
-d '{
    "access_token":"current-access-token",
    "refresh_token":"current-refresh-token"
}'
```

### Success Response

```json
{
  "status": "success",
  "access_token": "new-access-token",
  "user_id": "7ab0ec74-8a12-4f5c-8e75-0b2f3f4c1234",
  "auth_id": "supabase-auth-id",
  "username": "johndoe"
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

```json
{
  "auth_id": "supabase-auth-id",
  "access_token": "access-token",
  "refresh_token": "refresh-token"
}
```

### Example Request

```bash
curl -X POST http://localhost:8000/user/logout_user/ \
-H "Content-Type: application/json" \
-d '{
    "auth_id":"supabase-auth-id",
    "access_token":"access-token",
    "refresh_token":"refresh-token"
}'
```

### Success Response

```json
{
  "status": "success",
  "message": "User signed out successfully"
}
```

---

## Refresh CSRF Token

Generates a fresh CSRF token for frontend applications.

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
  "csrfToken": "generated-csrf-token"
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

Adds or updates an encrypted API key for a user.

### Endpoint

```http
PUT /user/update_user_keys/
```

### Request Body

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
    "user_id":"7ab0ec74-8a12-4f5c-8e75-0b2f3f4c1234",
    "key_type":"gemini_api_key",
    "api_key":"AIza..."
}'
```

### Success Response

```json
{
  "status": "success",
  "message": "gemini_api_key updated successfully for user john@example.com"
}
```

### Validation Errors

```json
{
  "message": "Invalid key type"
}
```

---

## Remove User API Key

Deletes a stored API key for a user.

### Endpoint

```http
PUT /user/remove_key/
```

### Request Body

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
    "user_id":"7ab0ec74-8a12-4f5c-8e75-0b2f3f4c1234",
    "key_type":"gemini_api_key"
}'
```

### Success Response

```json
{
  "status": "success",
  "message": "gemini_api_key removed successfully for user 7ab0ec74-8a12-4f5c-8e75-0b2f3f4c1234"
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

---

# Authentication Flow

```text
Register User
      ↓
Login User
      ↓
Receive Access Token + Refresh Token
      ↓
Use Access Token for API Requests
      ↓
Access Token Expires
      ↓
Refresh Token Endpoint
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
