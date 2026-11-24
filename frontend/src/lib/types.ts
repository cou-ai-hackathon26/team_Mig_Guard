export type VerdictType = "danger" | "caution" | "fewer_concerns";

export interface ExtractedField {
  value?: string | null;
  confidence: number;
  source_snippet?: string;
}

export interface RedFlag {
  rule_id: string;
  severity: string;
  weight: number;
  title_en: string;
  title_bn: string;
  explanation_en: string;
  explanation_bn: string;
  evidence_snippet?: string;
  question_en?: string;
  question_bn?: string;
}

export interface QuestionToAsk {
  en: string;
  bn: string;
}

export interface Helpline {
  name: string;
  number: string;
  hours?: string;
  description?: string;
}

export interface AnalysisResponse {
  verdict: VerdictType;
  score: number;
  language: string;
  input_summary: string;
  extracted: Record<string, ExtractedField>;
  flags: RedFlag[];
  missing_clauses: string[];
  questions_to_ask: QuestionToAsk[];
  unverifiable: string[];
  helplines: Helpline[];
  audio_script_bn: string;
}
