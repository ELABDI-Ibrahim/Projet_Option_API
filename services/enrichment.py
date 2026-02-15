import json
import re
import os
import spacy
import warnings
import unicodedata
from difflib import SequenceMatcher
from langdetect import detect, LangDetectException
from dotenv import load_dotenv
from groq import Groq
from services.linkedin_scraper import scrape_linkedin_profile

# # Load environment variables
# load_dotenv()

# Suppress Spacy warnings
warnings.filterwarnings("ignore")

class DescriptionMergerNLP:
    def __init__(self):
        print("Loading NLP models... (This may take a moment)")
        try:
            # We ONLY need the English model now since we force everything to English
            self.nlp_en = spacy.load("en_core_web_sm")
        except OSError:
            print("Error: Spacy model 'en_core_web_sm' not found.")
            print("Please run: python -m spacy download en_core_web_sm")
            self.nlp_en = None

        # Initialize Groq Client
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("WARNING: GROQ_API_KEY not found in environment.")
            self.groq_client = None
        else:
            self.groq_client = Groq(api_key=api_key)

    def _detect_lang(self, text):
        try:
            return detect(text)
        except LangDetectException:
            return "en" 

    def _get_spacy_model(self, lang_code):
        return self.nlp_en

    def _clean_string(self, text):
        if not text: return ""
        text = re.sub(r'^[\s\•\-\*]+', '', text)
        return " ".join(text.split()).lower()

    def _translate_description_groq(self, text, target_lang='en'):
        if not self.groq_client or not text:
            return text

        lang_name = "English" 
        
        prompt = f"""
        Translate the following professional experience description into {lang_name}.
        Rules:
        1. Keep all technical terms, tool names, and acronyms (e.g., Python, SQL, ETL, ATS, Docker) exactly as they are.
        2. Maintain the original semantic meaning and professional tone.
        3. Do not summarize; translate sentence by sentence.
        4. If theres a redundant sentence, remove it. 
        5. If theres a sentence that contains only skills or technologies, remove it.
        
        Description to translate:
        "{text}"
        """

        schema = {
            "type": "json_schema",
            "json_schema": {
                "name": "translation_response",
                "schema": {
                    "type": "object",
                    "properties": {
                        "translated_text": {
                            "type": "string",
                            "description": "The full translated content preserving technical terms."
                        }
                    },
                    "required": ["translated_text"],
                    "additionalProperties": False
                },
                "strict": True
            }
        }

        try:
            completion = self.groq_client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {"role": "system", "content": "You are a precise technical translator."},
                    {"role": "user", "content": prompt}
                ],
                response_format=schema,
                temperature=0
            )
            
            resp_content = json.loads(completion.choices[0].message.content)
            return resp_content.get("translated_text", text)

        except Exception as e:
            print(f"   [Groq Translation Error]: {e}")
            return text 

    def _get_unique_sentences(self, text):
        nlp = self.nlp_en
        if not text or not nlp: return []
        
        doc = nlp(text)
        unique_spans = []
        seen_content = set()

        for sent in doc.sents:
            clean_txt = self._clean_string(sent.text)
            
            if len(clean_txt) < 20: continue
            if clean_txt.lower().startswith("skills") or clean_txt.lower().startswith("technologies"):
                continue

            if clean_txt not in seen_content:
                seen_content.add(clean_txt)
                unique_spans.append(sent)
        
        return unique_spans

    def _is_semantically_present(self, candidate_span, existing_sentences_text, threshold=0.80):
        cand_text = candidate_span.text.strip()
        cand_clean = self._clean_string(cand_text)
        
        # 1. Exact Match
        for existing_text in existing_sentences_text:
            if cand_clean == self._clean_string(existing_text):
                # print(f"[Exact Match] '{cand_text}' == '{existing_text}'")
                return True

        # 2. Fuzzy String Match (Fast & Catch typos/minor diffs)
            # This catches "Developed API" vs "Developed the API" (Score ~0.95)
            # significantly faster than Spacy vectors.
            text_similarity = SequenceMatcher(None, cand_clean, exist_clean).ratio()
            if text_similarity > 0.85:  # 90% character overlap
                # print(f"   [Fuzzy Match: {text_similarity:.2f}] '{cand_text}' ~= '{existing_text}'")
                return True

        # 2. Vector Similarity
        nlp = self.nlp_en
        if nlp:
            doc1 = nlp(cand_text)
            for existing_text in existing_sentences_text:
                doc2 = nlp(existing_text)
                sim_score = doc1.similarity(doc2)
                if sim_score > threshold:
                    # print(f"   [Sim: {sim_score:.2f}] MATCH FOUND (Dropped): '{cand_text}'")
                    return True
        return False

    def merge_text(self, resume_text, linkedin_text):
        if not self.nlp_en: 
            return resume_text or linkedin_text

        res_lang = self._detect_lang(resume_text) if resume_text else 'en'
        li_lang = self._detect_lang(linkedin_text) if linkedin_text else 'en'

        final_res_text = resume_text
        final_li_text = linkedin_text

        if res_lang != 'en' and resume_text:
            print(f"   [Translating Resume Description] {res_lang} -> en...")
            final_res_text = self._translate_description_groq(resume_text, 'en')

        if li_lang != 'en' and linkedin_text:
            print(f"   [Translating LinkedIn Description] {li_lang} -> en...")
            final_li_text = self._translate_description_groq(linkedin_text, 'en')

        res_spans = self._get_unique_sentences(final_res_text)
        li_spans = self._get_unique_sentences(final_li_text)

        final_sentences_text = []

        # BASE: Keep all English Resume sentences
        for r_span in res_spans:
            cleaned_r = re.sub(r'^[\s\•\-\*]+', '', r_span.text).strip()
            final_sentences_text.append(cleaned_r)

        # ENRICH: Add English LinkedIn sentences if unique + TAG THEM
        for l_span in li_spans:
            l_text_clean = re.sub(r'^[\s\•\-\*]+', '', l_span.text).strip()
            if not self._is_semantically_present(l_span, final_sentences_text):
                # <--- TAGGING ADDED HERE --->
                final_sentences_text.append(f"{l_text_clean} [Linkedin]")
        
        return "\n".join([f"• {s}" for s in final_sentences_text])

class ProfileMerger:
    def __init__(self, resume_json, linkedin_json):
        # Data Loading
        if 'experiences' in linkedin_json: self.linkedin = linkedin_json
        elif 'data' in linkedin_json and isinstance(linkedin_json['data'], dict): self.linkedin = linkedin_json['data']
        else: self.linkedin = linkedin_json

        if 'experiences' in resume_json: self.resume = resume_json
        elif 'data' in resume_json and isinstance(resume_json['data'], dict): self.resume = resume_json['data']
        else: self.resume = resume_json

        self.nlp_merger = DescriptionMergerNLP()
        self.output = {}

    def normalize_str(self, s):
        if not s: return ""
        s = unicodedata.normalize('NFD', s)
        s = "".join([c for c in s if unicodedata.category(c) != 'Mn'])
        s = s.lower()
        noise_words = ["internship", "stage", "apprenticeship", "alternance", "group", "groupe", "ltd", "s.a.", "official account"]
        for word in noise_words:
            s = s.replace(word, "")
        s = re.sub(r'^[\s\•\-\*]+', '', s).strip()
        return re.sub(r'\W+', '', s)

    def is_similar(self, a, b, threshold=0.50):
        if not a or not b: return False
        norm_a = self.normalize_str(a)
        norm_b = self.normalize_str(b)
        return SequenceMatcher(None, norm_a, norm_b).ratio() > threshold
    
    def _enrich_field(self, resume_val, linkedin_val):
        """Helper to tag simple fields if they come from LinkedIn."""
        if resume_val:
            return resume_val
        if linkedin_val:
            return f"{linkedin_val} [Linkedin]"
        return None

    def merge_section(self, section_name, match_keys):
        merged_list = []
        res_items = self.resume.get(section_name, [])
        li_items = self.linkedin.get(section_name, [])

        print(f"\n--- PROCESSING SECTION: {section_name} ---")
        matched_li_indices = set()

        for res_item in res_items:
            best_match = None
            best_match_idx = -1
            best_score = 0
            
            for i, li_item in enumerate(li_items):
                if i in matched_li_indices: continue
                match_count = 0
                sim_score = 0
                for key in match_keys:
                    val_a = res_item.get(key)
                    val_b = li_item.get(key)
                    if self.is_similar(val_a, val_b):
                        match_count += 1
                        sim_score = SequenceMatcher(None, self.normalize_str(val_a), self.normalize_str(val_b)).ratio()
                
                if match_count >= 1 and sim_score > best_score:
                    best_score = sim_score
                    best_match = li_item
                    best_match_idx = i

            final_item = res_item.copy()

            if best_match:
                print(f"MATCH: {res_item.get(match_keys[0])} == {best_match.get(match_keys[0])}")
                matched_li_indices.add(best_match_idx)
                
                # Merge Dates/URL (Tag if new)
                for k in ['from_date', 'to_date', 'linkedin_url']:
                    if not final_item.get(k) and best_match.get(k):
                        final_item[k] = f"{best_match[k]}" # Usually don't tag URLs/Dates as [Linkedin] for readability, but you can add it if needed.

                # Merge Description
                res_desc = final_item.get('description', '')
                li_desc = best_match.get('description', '')
                if li_desc:
                    final_item['description'] = self.nlp_merger.merge_text(res_desc, li_desc)
            
            merged_list.append(final_item)

        # Add remaining (Unique) LinkedIn items
        for i, li_item in enumerate(li_items):
            if i not in matched_li_indices:
                name = li_item.get(match_keys[0], "Unknown Item")
                print(f"   -> Adding NEW item from LinkedIn: '{name}'")
                
                new_item = li_item.copy()
                # Tag the Title/Name
                title_key = 'position_title' if 'position_title' in new_item else 'project_name'
                if title_key in new_item:
                    new_item[title_key] = f"{new_item[title_key]} [Linkedin]"
                
                # Tag the description if it exists
                if new_item.get('description'):
                     # We still translate it to ensure English consistency
                     trans_desc = self.nlp_merger._translate_description_groq(new_item['description'], 'en')
                     new_item['description'] = f"{trans_desc} [Linkedin]"

                merged_list.append(new_item)

        return merged_list

    def process(self):
        # 1. Basic Info (Tag if from LinkedIn)
        self.output['linkedin_url'] = self.resume.get('linkedin_url') or self.linkedin.get('linkedin_url')
        self.output['name'] = self._enrich_field(self.resume.get('name'), self.linkedin.get('name'))
        self.output['location'] = self._enrich_field(self.resume.get('location'), self.linkedin.get('location'))
        self.output['about'] = self._enrich_field(self.resume.get('about'), self.linkedin.get('about'))
        self.output['open_to_work'] = self.linkedin.get('open_to_work', False)

        # 2. Sections
        self.output['experiences'] = self.merge_section('experiences', ['institution_name'])
        self.output['educations'] = self.merge_section('educations', ['institution_name'])
        self.output['projects'] = self.merge_section('projects', ['project_name'])

        # 3. Skills (Prefer LinkedIn structure usually)
        if self.linkedin.get('skills'):
            self.output['skills'] = self.linkedin.get('skills') # Structured data usually better left untagged
        else:
            self.output['skills'] = self.resume.get('skills', [])

        # 4. Arrays
        for k in ['interests', 'accomplishments']:
            res_list = self.resume.get(k, [])
            li_list = self.linkedin.get(k, [])
            # Combine unique items
            combined = list(res_list)
            for item in li_list:
                if item not in res_list:
                    combined.append(f"{item} [Linkedin]")
            self.output[k] = combined

        # 5. Contacts
        res_contacts = set(self.resume.get('contacts', []))
        li_contacts = set(self.linkedin.get('contacts', []))
        self.output['contacts'] = list(res_contacts) + [f"{c} [Linkedin]" for c in li_contacts if c not in res_contacts]

        return self.output

async def enrich_candidate(resume_data: dict, linkedin_url: str = None, name: str = None) -> dict:
    """
    Enriches resume data with LinkedIn data.
    """
    print(f"Enriching candidate: {name} ({linkedin_url})")
    
    # 1. Scrape (or fetch from local cache) LinkedIn Data
    linkedin_data = await scrape_linkedin_profile(linkedin_url, name)
    
    if not linkedin_data:
        print("No LinkedIn data found. Returning original resume.")
        return resume_data

    # 2. Merge
    merger = ProfileMerger(resume_data, linkedin_data)
    merged_data = merger.process()
    
    return merged_data
