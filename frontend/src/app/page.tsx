
"use client";

import { useEffect, useRef, useState } from "react";
import { analyzeOffer } from "@/lib/api";
import { speakBangla, stopSpeaking } from "@/lib/tts";
import type { AnalysisResponse } from "@/lib/types";

type Language = "en" | "bn";

const copy = {
  en: {
    nav: ["Home", "How It Works", "Why Mig_Guard", "Help"],
    navCta: "Check Your Offer",
    eyebrow: "BEFORE YOU GO, VERIFY",
    hero1: "Every Job Offer Deserves a Closer Look.",
    hero2: "Verify Before You Trust.",
    heroDesc: "Understand the risks before you make your next career move.",
    heroCta: "Check My Job Offer",
    heroSecondary: "Discover How It Works",
    trust: ["Evidence-based checks", "Privacy-conscious processing", "Easy Bangla explanations"],
    uploadLabel: "GET STARTED",
    uploadTitle: "Let's check your job offer.",
    uploadDesc: "Upload your offer letter or paste the recruiter's message to get started.",
    drag: "Drag & drop your offer letter here",
    choose: "or choose an option below",
    device: "Upload from device",
    camera: "Take a photo",
    paste: "Paste text",
    fileHint: "JPG, PNG or WEBP · Maximum 8 MB",
    privacy: "Your document is sent securely for analysis. Avoid sharing unnecessary personal information.",
    start: "Start checking",
    remove: "Remove file",
    textLabel: "Paste your job offer or recruiter's message",
    placeholder: "Paste the job offer details here...",
    backUpload: "Back to file upload",
    stepsLabel: "THREE SIMPLE STEPS",
    stepsTitle: "	Understand Your Job Offer, Step by Step.",
    stepsDesc: "Get a clearer picture of the terms, details and possible warning signs in your offer.",
    stepTitles: ["Share Your Job Offer", "Review the Key Details", "Know What Needs Attention"],
    stepDescs: [
      "Share a photo of your offer letter or paste the recruiter's message.",
      "Review important details such as salary, fees, working hours and contract terms.",
      "Identify unclear terms and questions to raise before making a decision."
    ],
    featureEyebrow: "SUPPORT FOR YOUR DECISION",
    featureTitle: "Know What to Check Before You Accept a Job.",
    featureDesc: "Mig_Guard helps you review important job offer details, spot potential warning signs and identify questions worth asking.",
    featureNames: ["Potential Warning Signs", "Agency Details to Check", "Important Contract Details", "Clear Findings and Explanations", "Guidance in Bangla"],
    featureDescList: [
      "Flag unusual promises, urgent payments and unclear conditions.",
      "Understand which agency details need further checking.",
      "Look for essential details on salary, working hours, housing and leave.",
      "Understand the reasons behind every alert.",
      "Listen to important findings in simple Bangla."
    ],
    finalTitle: "Your Next Career Move Deserves Care.",
    finalHighlight: "Review Your Offer Before You Decide.",
    finalDesc: "Understand the terms, check the details and make a more informed decision.",
    footerDesc: "Helping Bangladeshi migrant workers understand overseas job offers.",
    footerProduct: "PRODUCT",
    footerSupport: "SUPPORT",
    footerPrivacy: "PRIVACY",
    disclaimer: "Mig_Guard provides informational support. It does not guarantee that a job offer is safe or replace verification with the relevant government authority.",
    loading: "Checking your offer...",
    resultTitle: "Your analysis",
    resultDesc: "Here is what our initial checks found.",
    tryAgain: "Check another offer",
    error: "We couldn't connect to the analysis service. Please check that the backend is running and try again.",
    verdict: ["Potential danger detected", "Needs closer attention", "Fewer concerns identified"],
    score: "Risk score",
    flags: "Important findings",
    missing: "Missing contract details",
    questions: "Questions to ask",
    audio: "Bangla audio guidance",
    speak: "Play audio",
    stopAudio: "Stop audio",
    audioError: "Audio playback is not available in this browser.",
    extractionTitle: "Details found in your document",
    noExtractedFields: "No offer details could be extracted from this submission.",
    source: "Source",
    helplines: "Official support",
    riskPendingTitle: "Risk assessment is not available yet",
    riskPending: "Only document extraction has completed. No risk score or safety assessment has been produced.",
  },
  bn: {
    nav: ["হোম", "যেভাবে কাজ করে", "আমাদের সম্পর্কে", "সাহায্য"],
    navCta: "অফার যাচাই করুন",
    eyebrow: "চাকরির অফার গ্রহণের আগে, যাচাই করুন",
    hero1: "প্রতিটি চাকরির অফার যাচাইয়ের দাবি রাখে।",
    hero2: "বিশ্বাস করার আগে যাচাই করুন।",
    heroDesc: "বিদেশে নতুন কর্মজীবনের সিদ্ধান্ত নেওয়ার আগে চাকরির অফারের ঝুঁকিগুলো বুঝে নিন।",
    heroCta: "আমার অফার যাচাই করুন",
    heroSecondary: "যেভাবে কাজ করে",
    trust: ["তথ্যভিত্তিক যাচাই", "ব্যক্তিগত তথ্যের সুরক্ষা", "সহজ বাংলা ব্যাখ্যা"],
    uploadLabel: "যাচাই শুরু করুন",
uploadTitle: "আপনার চাকরির অফারটি যাচাই করুন।",
uploadDesc: "আপনার অফার লেটার আপলোড করুন অথবা নিয়োগকর্তার পাঠানো মেসেজ পেস্ট করুন।",
drag: "আপনার অফার লেটার এখানে আপলোড করুন",
choose: "অথবা নিচের যেকোনো একটি পদ্ধতি বেছে নিন",
device: "ডিভাইস থেকে ফাইল আপলোড",
camera: "ছবি তুলুন",
paste: "লেখা পেস্ট করুন",
fileHint: "JPG, PNG অথবা WEBP · সর্বোচ্চ ৮ MB",
privacy: "আপনার ফাইল বিশ্লেষণের জন্য পাঠানো হবে। অপ্রয়োজনীয় ব্যক্তিগত তথ্য শেয়ার করা থেকে বিরত থাকুন।",
start: "যাচাই শুরু করুন",
remove: "ফাইল সরান",
textLabel: "চাকরির অফার অথবা নিয়োগকর্তার মেসেজ পেস্ট করুন",
placeholder: "এখানে চাকরির অফারের বিস্তারিত লিখুন বা পেস্ট করুন...",
backUpload: "ফাইল আপলোডে ফিরে যান",
    stepsLabel: "মাত্র তিনটি ধাপ",
stepsTitle: "চাকরির অফার বুঝুন, ধাপে ধাপে।",
stepsDesc: "আপনার অফারের শর্ত, গুরুত্বপূর্ণ তথ্য এবং সম্ভাব্য সতর্কসংকেত সম্পর্কে পরিষ্কার ধারণা নিন।",

stepTitles: [
  "চাকরির অফার জমা দিন",
  "গুরুত্বপূর্ণ তথ্য যাচাই করুন",
  "যেসব বিষয়ে সতর্কতা প্রয়োজন বুঝুন"
],

stepDescs: [
  "অফার লেটারের ছবি আপলোড করুন অথবা নিয়োগকর্তার মেসেজ পেস্ট করুন।",
  "বেতন, ফি, কাজের সময় এবং চুক্তির গুরুত্বপূর্ণ শর্তগুলো পর্যালোচনা করুন।",
  "অস্পষ্ট শর্ত ও সিদ্ধান্ত নেওয়ার আগে যে প্রশ্নগুলো করা প্রয়োজন, সেগুলো চিহ্নিত করুন।"
],
    featureEyebrow: "সচেতন সিদ্ধান্ত নিতে সহায়তা",
    featureTitle: "চাকরির অফার গ্রহণের আগে যা যাচাই করা জরুরি।",
    featureDesc: "Mig_Guard আপনাকে চাকরির অফারের গুরুত্বপূর্ণ তথ্য পর্যালোচনা করতে, সম্ভাব্য সতর্কসংকেত শনাক্ত করতে এবং প্রয়োজনীয় প্রশ্নগুলো বুঝতে সাহায্য করে।",
    featureNames: [
  "সম্ভাব্য ঝুঁকির লক্ষণ",
  "নিয়োগকারী প্রতিষ্ঠানের তথ্য",
  "চুক্তির গুরুত্বপূর্ণ শর্ত",
  "পরিষ্কার বিশ্লেষণ ও ব্যাখ্যা",
  "বাংলায় নির্দেশনা"
],

    featureDescList: [
  "অস্বাভাবিক প্রতিশ্রুতি, দ্রুত টাকা জমা দেওয়ার চাপ এবং অস্পষ্ট শর্ত শনাক্ত করুন।",
  "নিয়োগকারী প্রতিষ্ঠান বা এজেন্সির কোন তথ্য আরও যাচাই করা প্রয়োজন বুঝুন।",
  "বেতন, কাজের সময়, বাসস্থান ও ছুটির মতো গুরুত্বপূর্ণ শর্তগুলো পর্যালোচনা করুন।",
  "প্রতিটি সতর্কসংকেতের পেছনের কারণ সহজভাবে বুঝুন।",
  "গুরুত্বপূর্ণ বিশ্লেষণ ও নির্দেশনা সহজ বাংলায় শুনুন।"
],
    finalTitle: "আপনার পরবর্তী কর্মজীবনের সিদ্ধান্ত গুরুত্বপূর্ণ।",
finalHighlight: "সিদ্ধান্তের আগে অফারটি যাচাই করুন।",
finalDesc: "চাকরির শর্ত বুঝুন, গুরুত্বপূর্ণ তথ্য যাচাই করুন এবং সচেতন সিদ্ধান্ত নিন।",
    footerDesc: "বিদেশে চাকরির অফার সম্পর্কে সচেতন সিদ্ধান্ত নিতে সহায়তা করে Mig_Guard।",
footerProduct: "প্রোডাক্ট",
footerSupport: "সহায়তা",
footerPrivacy: "গোপনীয়তা",
    
    disclaimer: "Mig_Guard তথ্যভিত্তিক সহায়তা দেয়। এটি চাকরির অফার নিরাপদ হওয়ার নিশ্চয়তা দেয় না বা সরকারি কর্তৃপক্ষের যাচাইয়ের বিকল্প নয়।",
    loading: "আপনার চাকরির অফার যাচাই করা হচ্ছে...",
resultTitle: "বিশ্লেষণের ফলাফল",
resultDesc: "প্রাথমিক বিশ্লেষণে যেসব বিষয় পাওয়া গেছে।",
tryAgain: "অন্য একটি অফার যাচাই করুন",
error: "বিশ্লেষণ সার্ভারের সঙ্গে সংযোগ করা যাচ্ছে না। Backend চালু আছে কি না পরীক্ষা করে আবার চেষ্টা করুন।",
verdict: [
  "সম্ভাব্য ঝুঁকি শনাক্ত হয়েছে",
  "আরও সতর্কভাবে যাচাই করা প্রয়োজন",
  "তুলনামূলকভাবে কম ঝুঁকির লক্ষণ পাওয়া গেছে"
],
score: "ঝুঁকির স্কোর",
flags: "গুরুত্বপূর্ণ পর্যবেক্ষণ",
missing: "চুক্তিতে অনুপস্থিত গুরুত্বপূর্ণ শর্ত",
questions: "নিয়োগকর্তাকে যে প্রশ্নগুলো করবেন",
audio: "বাংলা অডিও নির্দেশনা",
speak: "অডিও চালান",
stopAudio: "অডিও বন্ধ করুন",
audioError: "এই ব্রাউজারে অডিও চালানো যাচ্ছে না।",
extractionTitle: "আপনার নথি থেকে পাওয়া তথ্য",
noExtractedFields: "এই জমা দেওয়া নথি থেকে কোনো চাকরির তথ্য পাওয়া যায়নি।",
source: "সূত্র",
helplines: "সরকারি সহায়তা",
riskPendingTitle: "ঝুঁকি মূল্যায়ন এখনো পাওয়া যাচ্ছে না",
riskPending: "শুধু নথি থেকে তথ্য সংগ্রহ করা হয়েছে। কোনো ঝুঁকির স্কোর বা নিরাপত্তা মূল্যায়ন করা হয়নি।",
  },
};

const features = ["◈", "⌂", "▤", "⌕", "◖))"];
const steps = ["↥", "⌕", "⚑"];

export default function Home() {
  const [lang, setLang] = useState<Language>("en");
  const [mode, setMode] = useState<"upload" | "text">("upload");
  const [file, setFile] = useState<File | null>(null);
  const [text, setText] = useState("");
  const [preview, setPreview] = useState("");
  const [dragging, setDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<AnalysisResponse | null>(null);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [audioError, setAudioError] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [cameraOpen, setCameraOpen] = useState(false);
  const [cameraError, setCameraError] = useState("");
  const t = copy[lang];

  function clearFile() {
    if (preview) URL.revokeObjectURL(preview);
    setFile(null);
    setPreview("");
    if (fileRef.current) fileRef.current.value = "";
  }

  async function openCamera() {
    setCameraError("");

    if (!navigator.mediaDevices?.getUserMedia) {
      setCameraError(
        "Camera is not supported in this browser. Try a recent version of Chrome or Edge."
      );
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: { ideal: "environment" } },
        audio: false,
      });

      streamRef.current = stream;
      setCameraOpen(true);
    } catch (cameraErr) {
      const message =
        cameraErr instanceof Error && cameraErr.name === "NotAllowedError"
          ? "Camera permission was denied. Allow camera access in your browser settings and try again."
          : "Could not open the camera. Check that a camera is connected and not being used by another app.";
      setCameraError(message);
    }
  }

  function closeCamera() {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    setCameraOpen(false);
  }

  function capturePhoto() {
    const video = videoRef.current;
    if (!video || !video.videoWidth || !video.videoHeight) return;

    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const context = canvas.getContext("2d");
    if (!context) {
      setCameraError("Could not capture the photo. Please try again.");
      return;
    }

    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    canvas.toBlob(
      (blob) => {
        if (!blob) {
          setCameraError("Could not capture the photo. Please try again.");
          return;
        }

        const photo = new File([blob], "mig-guard-capture.jpg", {
          type: "image/jpeg",
        });
        chooseFile(photo);
        closeCamera();
      },
      "image/jpeg",
      0.92
    );
  }

  useEffect(() => {
    if (cameraOpen && videoRef.current && streamRef.current) {
      videoRef.current.srcObject = streamRef.current;
      videoRef.current.play().catch(() => {
        setCameraError("The camera preview could not start. Please try again.");
      });
    }
  }, [cameraOpen]);

  useEffect(() => {
    return () => {
      streamRef.current?.getTracks().forEach((track) => track.stop());
    };
  }, []);

  function chooseFile(selected?: File) {
    if (!selected) return;
    setError("");

    const validTypes = ["image/jpeg", "image/png", "image/webp"];

    if (!validTypes.includes(selected.type)) {
      setError(lang === "bn" ? "শুধু JPG, PNG অথবা WEBP ছবি আপলোড করুন।" : "Please upload a JPG, PNG or WEBP image.");
      return;
    }

    if (selected.size > 8 * 1024 * 1024) {
      setError(lang === "bn" ? "ফাইলের সাইজ ৮ MB-এর বেশি হতে পারবে না।" : "File size must not exceed 8 MB.");
      return;
    }

    clearFile();
    setFile(selected);
    setPreview(URL.createObjectURL(selected));
  }

  async function analyze() {
    if (!file && !text.trim()) return;

    stopSpeaking();
    setIsSpeaking(false);
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const data = await analyzeOffer(file ? [file] : [], text, lang);
      setResult(data);
      document.getElementById("analysis-result")?.scrollIntoView({ behavior: "smooth" });
    } catch (err) {
      setError(err instanceof Error ? err.message : t.error);
    } finally {
      setLoading(false);
    }
  }

  async function playAudio() {
    if (!result?.audio_script_bn) return;

    setAudioError("");
    setIsSpeaking(true);
    try {
      await speakBangla(result.audio_script_bn);
    } catch {
      setAudioError(t.audioError);
    } finally {
      setIsSpeaking(false);
    }
  }

  function stopAudio() {
    stopSpeaking();
    setIsSpeaking(false);
  }

  useEffect(() => {
    return () => stopSpeaking();
  }, []);

  const riskAssessmentPending = result?.unverifiable.includes(
    "risk_assessment_pending_phase_2"
  );
  const extractedFields = result
    ? Object.entries(result.extracted).filter(([, field]) => field.value?.trim())
    : [];
  const helplines = result?.helplines ?? [];

  const verdictIndex = result?.verdict === "danger" ? 0 : result?.verdict === "fewer_concerns" ? 2 : 1;

  return (
    <main className="mg-site" lang={lang}>
      <header className="mg-nav">
        <a className="mg-brand" href="#">
          <span className="mg-logo">MG</span>
          <span>Mig_<b>Guard</b></span>
        </a>

        <nav className="mg-nav-links">
          {t.nav.map((item, i) => (
            <a key={item} href={["#", "#how-it-works", "#why-us", "#help"][i]}>
              {item}
            </a>
          ))}
        </nav>

        <div className="mg-nav-actions">
          <div className="mg-language">
            <button className={lang === "bn" ? "selected" : ""} onClick={() => setLang("bn")}>বাংলা</button>
            <span />
            <button className={lang === "en" ? "selected" : ""} onClick={() => setLang("en")}>EN</button>
          </div>
          <a className="mg-nav-cta" href="#upload">{t.navCta} <span>↗</span></a>
        </div>
      </header>

      <section className="mg-hero">
        <div className="hero-orbit orbit-one" />
        <div className="hero-orbit orbit-two" />
        <div className="hero-content">
          <div className="mg-eyebrow light"><i />{t.eyebrow}</div>
          <h1>
            <span className="hero-title-main">{t.hero1}</span>
            <br />
            <span className="hero-title-highlight">{t.hero2}</span>
          </h1>
          <p>{t.heroDesc}</p>
          <div className="hero-actions">
            <a href="#upload" className="yellow-button">{t.heroCta} <span>→</span></a>
            <a href="#how-it-works" className="text-button">{t.heroSecondary} <span>↘</span></a>
          </div>
          <div className="hero-note"><span>✓</span> {lang === "bn" ? "সচেতন সিদ্ধান্তের জন্য তথ্যভিত্তিক সহায়তা" : "Practical guidance for informed decisions"}</div>
        </div>

        <div className="hero-visual" aria-label="Illustration of a job offer being checked">
          <div className="visual-sun" />
          <div className="visual-ring" />
          <div className="offer-paper">
            <div className="paper-top">
              <div className="paper-company-mark">▥</div>
              <div><b>INTERNATIONAL<br />WORKFORCE</b><small>EMPLOYMENT SERVICES</small></div>
              <span className="offer-tag">OFFER</span>
            </div>
            <div className="paper-rule" />
            <small className="paper-kicker">OVERSEAS EMPLOYMENT OFFER</small>
            <h3>Employment<br />Offer Letter</h3>
            <div className="paper-details">
              <div><small>APPLICANT</small><b>Applicant Name</b></div>
              <div><small>POSITION</small><b>Site Technician</b></div>
            </div>
            <div className="paper-lines"><i/><i/><i/><i/></div>
            <div className="paper-signature">Employer signature<br /><b>___________</b></div>
          </div>
          <div className="verified-stamp"><span>♢</span><b>VERIFIED</b><small>DETAIL CHECK</small></div>
          <div className="float-check check-top"><span>▤</span><div><small>Visa Type</small><b>Employment</b></div><i>✓</i></div>
          <div className="float-check check-bottom"><span>⌂</span><div><small>Agency Details</small><b>Information found</b></div><i>✓</i></div>
          <div className="float-check check-fee"><span>৳</span><div><small>Recruitment Fee</small><b>Needs a closer look</b></div><i>!</i></div>
          <div className="visual-dots" />
        </div>
      </section>

      <section className="mg-trust">
        {t.trust.map((item, i) => (
          <div key={item}><span>{["⌕", "♙", "▱"][i]}</span>{item}</div>
        ))}
      </section>

      <section className="mg-upload-section" id="upload">
        <div className="upload-heading">
          <div className="mg-eyebrow"><i />{t.uploadLabel}</div>
          <h2>{t.uploadTitle}</h2>
          <p>{t.uploadDesc}</p>
        </div>

        <div className="upload-panel">
          <div className="upload-tabs">
            <button className={mode === "upload" ? "active" : ""} onClick={() => setMode("upload")}>▧ {t.device}</button>
            <button className={mode === "text" ? "active" : ""} onClick={() => setMode("text")}>≡ {t.paste}</button>
          </div>

          {mode === "upload" ? (
            <div
              className={`drop-zone ${dragging ? "dragging" : ""} ${file ? "has-file" : ""}`}
              onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
              onDragLeave={() => setDragging(false)}
              onDrop={(e) => { e.preventDefault(); setDragging(false); chooseFile(e.dataTransfer.files[0]); }}
              onClick={() => !file && fileRef.current?.click()}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => { if (e.key === "Enter") fileRef.current?.click(); }}
            >
              <input ref={fileRef} hidden type="file" accept="image/jpeg,image/png,image/webp" onChange={(e) => chooseFile(e.target.files?.[0])} />

              {file ? (
                <div className="file-preview" onClick={(e) => e.stopPropagation()}>
                  {preview && <img src={preview} alt="Selected job offer preview" />}
                  <div className="file-info"><b>{file.name}</b><small>{(file.size / 1024 / 1024).toFixed(2)} MB · Ready to check</small></div>
                  <button className="remove-file" onClick={clearFile} aria-label={t.remove}>×</button>
                </div>
              ) : (
                <>
                  <div className="upload-symbol">↥</div>
                  <h3>{t.drag}</h3>
                  <p>{t.choose}</p>
                  <div className="upload-options">
                    <button onClick={(e) => { e.stopPropagation(); fileRef.current?.click(); }}>↥ {t.device}</button>
                    <button onClick={(e) => { e.stopPropagation(); openCamera(); }}>◎ {t.camera}</button>
                    <button onClick={(e) => { e.stopPropagation(); setMode("text"); }}>▤ {t.paste}</button>
                  </div>
                  <small className="file-hint">{t.fileHint}</small>
                </>
              )}
            </div>
          ) : (
            <div className="paste-area">
              <label htmlFor="offer-text">{t.textLabel}</label>
              <textarea id="offer-text" value={text} onChange={(e) => setText(e.target.value)} placeholder={t.placeholder} />
              <button className="back-link" onClick={() => setMode("upload")}>← {t.backUpload}</button>
            </div>
          )}

          {error && <div className="mg-error" role="alert">{error}</div>}
          {cameraError && <div className="mg-error" role="alert">{cameraError}</div>}

          <div className="upload-bottom">
            <p><span>♙</span>{t.privacy}</p>
            <button className="yellow-button analyze-button" disabled={loading || (!file && !text.trim())} onClick={analyze}>
              {loading ? t.loading : t.start} <span>→</span>
            </button>
          </div>
        </div>
      </section>

      {loading && (
        <section className="loading-panel">
          <div className="loader" />
          <h3>{t.loading}</h3>
          <p>{lang === "bn" ? "অনুগ্রহ করে অপেক্ষা করুন..." : "Please wait while we process your submission."}</p>
        </section>
      )}

      {result && (
        <section className="result-section" id="analysis-result">
          <div className="mg-eyebrow"><i />{t.resultTitle}</div>
          <h2>{t.resultDesc}</h2>
          <div className={`result-card verdict-${result.verdict}`}>
            {riskAssessmentPending ? (
              <div className="result-pending" role="status">
                <h3>{t.riskPendingTitle}</h3>
                <p>{t.riskPending}</p>
              </div>
            ) : (
              <>
                <div className="result-top">
                  <span className="result-symbol">{result.verdict === "danger" ? "!" : result.verdict === "fewer_concerns" ? "✓" : "!"}</span>
                  <div><small>{t.score}</small><h3>{t.verdict[verdictIndex]}</h3></div>
                  <strong>{result.score}/100</strong>
                </div>
                <div className="score-track"><span style={{ width: `${result.score}%` }} /></div>
              </>
            )}
            <p className="result-summary">{result.input_summary}</p>

            <div className="result-list">
              <h4>{t.extractionTitle}</h4>
              {extractedFields.length > 0 ? extractedFields.map(([name, field]) => (
                <article key={name}>
                  <b>{name.replace(/_/g, " ")}</b>
                  <p>{field.value}</p>
                  {field.source_snippet && <p><small>{t.source}: “{field.source_snippet}”</small></p>}
                </article>
              )) : <p>{t.noExtractedFields}</p>}
            </div>
            {result.flags.length > 0 && <div className="result-list"><h4>{t.flags}</h4>{result.flags.map((flag) => <article key={flag.rule_id}><b>{lang === "bn" ? flag.title_bn : flag.title_en}</b><p>{lang === "bn" ? flag.explanation_bn : flag.explanation_en}</p>{flag.evidence_snippet && <p><small>{t.source}: “{flag.evidence_snippet}”</small></p>}</article>)}</div>}
            {result.missing_clauses && result.missing_clauses.length > 0 && <div className="result-list"><h4>{t.missing}</h4>{result.missing_clauses.map((item, i) => <p key={i}>• {item}</p>)}</div>}
            {result.questions_to_ask && result.questions_to_ask.length > 0 && <div className="result-list"><h4>{t.questions}</h4>{result.questions_to_ask.map((item, i) => <article key={i}><b>{lang === "bn" ? item.bn : item.en}</b></article>)}</div>}
            {helplines.length > 0 && <div className="result-list"><h4>{t.helplines}</h4>{helplines.map((helpline) => <article key={`${helpline.name}-${helpline.number}`}><b>{helpline.name}</b><p><a href={`tel:${helpline.number}`}>{helpline.number}</a></p>{helpline.description && <p>{helpline.description}</p>}{helpline.hours && <p>{helpline.hours}</p>}</article>)}</div>}
            {result.audio_script_bn && <div className="result-list"><h4>{t.audio}</h4><p>{result.audio_script_bn}</p><button type="button" onClick={isSpeaking ? stopAudio : playAudio}>{isSpeaking ? t.stopAudio : t.speak}</button>{audioError && <p role="alert">{audioError}</p>}</div>}
            <p className="result-disclaimer">{t.disclaimer}</p>
          </div>
          <button className="yellow-button" onClick={() => { stopAudio(); setAudioError(""); setResult(null); clearFile(); setText(""); document.getElementById("upload")?.scrollIntoView({ behavior: "smooth" }); }}>{t.tryAgain} →</button>
        </section>
      )}

      <section className="mg-steps-section" id="how-it-works">
        <div className="steps-intro">
          <div><div className="mg-eyebrow"><i />{t.stepsLabel}</div><h2>{t.stepsTitle}</h2></div>
          <p>{t.stepsDesc}</p>
        </div>
        <div className="steps-grid">
          {t.stepTitles.map((title, i) => (
            <article className={`step-card step-${i + 1}`} key={title}>
              <div className="step-art"><span className="step-index">0{i + 1}</span><div className="step-icon">{steps[i]}</div>{i === 1 && <span className="step-check">✓</span>}{i === 2 && <div className="step-bars"><i/><i/><i/></div>}</div>
              <div className="step-copy"><h3>{title}</h3><p>{t.stepDescs[i]}</p></div>
            </article>
          ))}
        </div>
      </section>

      <section className="mg-features-section" id="why-us">
        <div className="features-copy">
          <div className="mg-eyebrow light"><i />{t.featureEyebrow}</div>
          <h2>{t.featureTitle}</h2>
          <p>{t.featureDesc}</p>
          <div className="sample-analysis">
            <small>{lang === "bn" ? "নমুনা যাচাই" : "SAMPLE ANALYSIS"}</small>
            <b>{lang === "bn" ? "আমরা যা দেখি" : "What we look for"}</b>
            {[
              lang === "bn" ? "বেতন ও মুদ্রা উল্লেখ আছে" : "Salary and currency stated",
              lang === "bn" ? "কাজের সময় অস্পষ্ট" : "Working hours unclear",
              lang === "bn" ? "অগ্রিম ফি যাচাই প্রয়োজন" : "Advance fee needs checking"
            ].map((item, i) => <div key={item}><span className={`sample-mark mark-${i}`}>{["✓", "?", "!"][i]}</span>{item}<small>{["Clear", "Review", "Attention"][i]}</small></div>)}
          </div>
        </div>
        <div className="feature-grid">
          {t.featureNames.map((name, i) => <article className={`feature-card feature-${i}`} key={name}><span>{features[i]}</span><h3>{name}</h3><p>{t.featureDescList[i]}</p></article>)}
        </div>
      </section>

      <section className="mg-final-cta">
        <div><h2>{t.finalTitle}<br /><span>{t.finalHighlight}</span></h2><p>{t.finalDesc}</p></div>
        <a href="#upload" className="yellow-button">{t.navCta} →</a>
      </section>

      <footer className="mg-footer" id="help">
        <div className="footer-main">
          <div className="footer-brand"><a className="mg-brand" href="#"><span className="mg-logo">MG</span><span>Mig_<b>Guard</b></span></a><p>{t.footerDesc}</p></div>
          <div><b>{t.footerProduct}</b><a href="#how-it-works">{t.nav[1]}</a><a href="#why-us">{t.nav[2]}</a><a href="#upload">{t.navCta}</a></div>
          <div><b>{t.footerSupport}</b><a href="#help">{t.nav[3]}</a><a href="#upload">{lang === "bn" ? "যোগাযোগ" : "Contact us"}</a></div>
          <div><b>{t.footerPrivacy}</b><a href="#help">{lang === "bn" ? "গোপনীয়তা নীতি" : "Privacy policy"}</a><a href="#help">{lang === "bn" ? "ব্যবহারের শর্ত" : "Terms of use"}</a></div>
        </div>
        <div className="footer-disclaimer"><span>ⓘ</span><b>{lang === "bn" ? "গুরুত্বপূর্ণ ঘোষণা" : "Important disclaimer"}</b><p>{t.disclaimer}</p></div>
        <div className="footer-bottom"><span>© 2026 Mig_Guard. All rights reserved.</span><span><button onClick={() => setLang("bn")}>বাংলা</button> · <button onClick={() => setLang("en")}>English</button></span></div>
      </footer>

      {cameraOpen && (
        <div
          className="camera-overlay"
          role="dialog"
          aria-modal="true"
          aria-labelledby="camera-title"
        >
          <div className="camera-modal">
            <div className="camera-header">
              <h2 id="camera-title">{lang === "bn" ? "ছবি তুলুন" : "Capture job offer"}</h2>
              <button type="button" onClick={closeCamera} aria-label="Close camera">
                ×
              </button>
            </div>

            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="camera-video"
            />

            <p>
              {lang === "bn"
                ? "অফার লেটারটি ক্যামেরার সামনে পরিষ্কারভাবে ধরুন।"
                : "Position your job offer clearly in front of the camera."}
            </p>

            <div className="camera-actions">
              <button type="button" onClick={closeCamera}>
                {lang === "bn" ? "বাতিল" : "Cancel"}
              </button>
              <button type="button" onClick={capturePhoto}>
                {lang === "bn" ? "ছবি তুলুন" : "Capture photo"}
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
