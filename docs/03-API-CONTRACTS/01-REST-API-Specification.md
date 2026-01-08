# VIRA: REST API Specification

**Version:** 1.0  
**Last Updated:** November 25, 2025  
**Status:** ✅ Implemented

---

## Base URL

```
Development: http://localhost:8001
Production: TBD
```

---

## Authentication

**Current:** None (prototype)  
**Future:** Bearer token authentication

---

## Core Endpoints

### POST /analyze

Analyze business plan (text input).

**Request:**
```json
{
  "company_name": "TechStartup Inc",
  "plan_text": "Full business plan text..."
}
```

**Response:**
```json
{
  "company_name": "TechStartup Inc",
  "aligns": [
    {
      "description": "Market focus on enterprise SaaS",
      "evidence": "Matches a16z investment thesis",
      "source": "https://a16z.com/enterprise-saas/"
    }
  ],
  "gaps": [...],
  "summary": "Overall assessment...",
  "sources": ["url1", "url2"],
  "num_docs_retrieved": 6,
  "model_used": "gpt-4o-mini"
}
```

### POST /analyze/upload

Analyze business plan (file upload).

**Request:** `multipart/form-data`
- `company_name`: string
- `file`: PDF/DOCX/TXT file

**Response:** Same as `/analyze`

### Session Management

#### POST /api/sessions
Create new session.

#### GET /api/sessions
List sessions (limit, status filter).

#### POST /api/sessions/{id}/analyze
Analyze plan for session.

---

## Status Codes

- `200` - Success
- `400` - Bad request (invalid input)
- `404` - Resource not found
- `500` - Internal server error

---

**See full API documentation at:** [`/docs`](http://localhost:8001/docs) (FastAPI auto-generated)
