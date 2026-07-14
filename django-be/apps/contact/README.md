# Contact API Documentation

## Overview

The Contact app provides a single endpoint for visitors to leave a message along with contact details (email and/or phone). Submitted messages are persisted to the database for follow-up.

---

# Base URL

```http
http://localhost:8000/messages/send-message/
```

Production:

```http
https://api.yourdomain.com/messages/send-message/
```

---

# Response Envelope

Matches the convention used across the rest of the API.

**Success:**
```json
{
  "res_status": "success",
  "response": "Message sent successfully!"
}
```

**Error:**
```json
{
  "res_status": "error",
  "response": "Human readable error message"
}
```

---

# Send Message

Submit a contact message.

## Endpoint

```http
POST /contact/send_message/
```

**Content-Type:** `application/json` or `application/x-www-form-urlencoded`

---

## Request Parameters

| Parameter | Type   | Required      | Description                                  |
| --------- | ------ | ------------- | --------------------------------------------- |
| message   | string | Yes           | The message content                           |
| email     | string | Conditional*  | Sender's email address                        |
| phone     | string | Conditional*  | Sender's phone number                          |
| name      | string | No            | Sender's name                                  |

`*` At least **one** of `email` or `phone` must be provided. Both may be provided together.

---

## Example Request

```bash
curl -X POST http://localhost:8000/messages/send-message/ \
-H "Content-Type: application/json" \
-d '{
    "message": "I would like to know more about your enterprise plan.",
    "email": "jane@example.com",
    "name": "Jane Doe"
}'
```

---

## Success Response

Status: `200 OK`

```json
{
  "res_status": "success",
  "response": "Message sent successfully!"
}
```

---

## Error Responses

### Missing Message

```json
{
  "res_status": "error",
  "response": "message is required."
}
```

Status: `400 Bad Request`

---

### Missing Contact Info

Returned when neither `email` nor `phone` is provided.

```json
{
  "res_status": "error",
  "response": "At least one of email or phone is required."
}
```

Status: `400 Bad Request`

---

### Invalid JSON

```json
{
  "res_status": "error",
  "response": "Invalid JSON payload"
}
```

Status: `400 Bad Request`

---

### Invalid Request Method

```json
{
  "res_status": "error",
  "response": "Invalid request method. Please use POST to send a message."
}
```

Status: `405 Method Not Allowed`

---

### Unhandled / Other Errors

Any other exception raised while saving the message (e.g. a database error) is caught and returned as:

```json
{
  "res_status": "error",
  "response": "<exception message>"
}
```

Status: `500 Internal Server Error`

---

## Notes on Changes From a Prior Version

If you're comparing against an older copy of this endpoint, the following were fixed:

- **Crash on missing contact info:** previously, if neither `email` nor `phone` was supplied, the message object was never created and the request raised an unhandled `UnboundLocalError`. This now returns a clean `400` instead.
- **`name` field:** previously accepted by the model but never read from the request; it is now captured from the `name` parameter.
- **Non-serializable error body:** previously the generic exception handler returned the raw exception object as `response`, which is not JSON-serializable and would itself raise an error inside `JsonResponse`. It now returns `str(e)`.
- **Status codes:** unhandled exceptions previously returned `401 Unauthorized`, which doesn't match the nature of the error; they now return `500 Internal Server Error`. The "invalid method" case now returns `405 Method Not Allowed` in the standard JSON envelope instead of a plain-text `200` response.

---

# Rate Limiting

This endpoint is protected by rate limiting to prevent abuse. The current limit is **20 requests per minute per IP address** (`rate="20/m"`). Exceeding this limit will result in the request being blocked.

---

# Security Features

* Rate Limiting
* Structured Logging
* Input Validation (`message` required, at least one of `email`/`phone` required)

---

# Dependencies

* Django
* django-ratelimit