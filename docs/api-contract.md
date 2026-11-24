# API Contract & Schema Reference

The Mig_Guard backend is built with FastAPI and exposes RESTful endpoints for document analysis, text-to-speech, and operational health checks.

## Endpoints

### 1. `POST /api/analyze`
Accepts one or more images (JPEG, PNG, WebP) or pasted text, along with language selection (`bn` or `en`).

**Request (Multipart Form):**
- `files`: List of image files (optional if text is provided)
- `text`: Pasted job offer or chat text (optional if files provided)
- `language`: `bn` (default) or `en`

**Response (`AnalyzeResponse` JSON):**
```json
{
  "verdict": "danger | caution | fewer_concerns",
  "score": 85,
  "language": "bn",
  "input_summary": "1 image(s) received in memory",
  "extracted": {
    "destination": { "value": "Cambodia", "confidence": 0.98, "source_snippet": "Sihanoukville, Cambodia" },
    "salary_amount": { "value": 2500, "confidence": 0.95, "source_snippet": "$2500 USD" },
    "visa_type": { "value": "Tourist Visa", "confidence": 0.97, "source_snippet": "Visit Visa" }
  },
  "flags": [
    {
      "rule_id": "R02_NON_WORK_VISA",
      "severity": "high",
      "weight": 30,
      "title_en": "Visit or tourist visa offered for work",
      "title_bn": "কাজের কথা বলে ভিজিট বা ট্যুরিস্ট ভিসা দেওয়া হচ্ছে",
      "explanation_en": "Working on a tourist visa is illegal and puts you at risk of arrest or trafficking.",
      "explanation_bn": "ট্যুরিস্ট বা ভিজিট ভিসায় বিদেশে কাজ করা অবৈধ এবং এতে গ্রেপ্তার ও প্রতারণার ঝুঁকি থাকে।",
      "question_en": "Why does the document say visit/tourist visa instead of an official employment visa?",
      "question_bn": "কাজের ভিসার বদলে এখানে ভিজিট বা ট্যুরিস্ট ভিসার কথা লেখা কেন?",
      "evidence_snippet": "Visit Visa"
    }
  ],
  "missing_clauses": ["working_hours", "accommodation", "return_ticket"],
  "questions_to_ask": [
    {
      "en": "Can you provide the official written contract stamped by the employer before I pay anything?",
      "bn": "টাকা দেওয়ার আগে কোম্পানির সিলসহ মূল লিখিত চুক্তিপত্র কি দেখাতে পারবেন?"
    }
  ],
  "unverifiable": ["Employer identity could not be verified (missing from document)."],
  "helplines": [
    {
      "name_en": "Probashi Kallyan Call Center (Probashbandhu)",
      "name_bn": "প্রবাসী কল্যাণ কল সেন্টার (প্রবাসবন্ধু)",
      "phone": "16135",
      "notes_bn": "বিদেশে যাওয়ার আগে ভিসা ও এজেন্সি যাচাই করতে কল করুন।"
    }
  ],
  "audio_script_bn": "সতর্কতা: এই অফারে গুরুতর ঝুঁকি রয়েছে..."
}
```

### 2. `POST /api/tts`
Converts verdict summaries into natural Bangla speech for low-literacy migrant workers.

### 3. `GET /api/health`
Health check endpoint used for automated monitoring and warming up free-tier backend instances before presentation.
