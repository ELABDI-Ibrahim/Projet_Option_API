import spacy
import re

class DescriptionMerger:
    def __init__(self):
        # Load the small English model (efficient for CPU)
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            print("Please run: python -m spacy download en_core_web_sm")
            self.nlp = None

    def _clean_bullet(self, text):
        """Removes leading bullet points and extra whitespace."""
        return re.sub(r'^[\s\•\-\*]+', '', text).strip()

    def _has_numbers(self, text):
        """Checks if the sentence contains numbers (metrics are good!)."""
        return bool(re.search(r'\d', text))

    def merge_descriptions(self, resume_text, linkedin_text, threshold=0.75):
        """
        Merges two descriptions by removing semantic duplicates.
        Returns a single string with distinct bullet points.
        """
        if not resume_text: return linkedin_text or ""
        if not linkedin_text: return resume_text or ""
        
        # 1. Parse both texts into sentences
        doc_res = self.nlp(resume_text)
        doc_li = self.nlp(linkedin_text)
        
        # Convert to list of cleaned strings
        # We keep the Spacy 'Span' objects for vector comparison, but store text for output
        res_sentences = [sent for sent in doc_res.sents if sent.text.strip()]
        li_sentences = [sent for sent in doc_li.sents if sent.text.strip()]
        
        final_sentences = []
        
        # Track which LinkedIn sentences have been "used" (matched)
        matched_li_indices = set()

        # 2. Iterate through Resume sentences (The Base)
        for r_sent in res_sentences:
            best_match_score = 0
            best_match_idx = -1
            
            # Compare against all LinkedIn sentences
            for i, l_sent in enumerate(li_sentences):
                # Calculate semantic similarity
                score = r_sent.similarity(l_sent)
                
                if score > best_match_score:
                    best_match_score = score
                    best_match_idx = i
            
            # 3. Decision Logic
            if best_match_score > threshold:
                # MATCH FOUND: They are saying the same thing.
                match_l_sent = li_sentences[best_match_idx]
                matched_li_indices.add(best_match_idx)
                
                # Conflict Resolution: Which version is better?
                # Rule A: Prefer the one with numbers (metrics)
                res_has_num = self._has_numbers(r_sent.text)
                li_has_num = self._has_numbers(match_l_sent.text)
                
                if li_has_num and not res_has_num:
                    # LinkedIn version has metrics, Resume doesn't -> Upgrade to LinkedIn version
                    final_sentences.append(self._clean_bullet(match_l_sent.text))
                elif len(match_l_sent.text) > len(r_sent.text) * 1.5:
                     # Rule B: If LinkedIn version is significantly longer/more detailed, take it
                    final_sentences.append(self._clean_bullet(match_l_sent.text))
                else:
                    # Default: Keep the Resume version (usually more professional/concise)
                    final_sentences.append(self._clean_bullet(r_sent.text))
            else:
                # NO MATCH: Unique to Resume -> Keep it
                final_sentences.append(self._clean_bullet(r_sent.text))

        # 4. Add "Missing" Information
        # Any LinkedIn sentence that wasn't matched is unique info. Add it.
        for i, l_sent in enumerate(li_sentences):
            if i not in matched_li_indices:
                cleaned = self._clean_bullet(l_sent.text)
                # Filter out garbage like "Skills:..." if you extracted those elsewhere
                if not cleaned.lower().startswith("skills:"): 
                    final_sentences.append(cleaned)

        # 5. Reconstruct the Description
        # Join with newlines and add bullet points for consistency
        return "\n".join([f"• {s}" for s in final_sentences])

# --- Example Usage ---
if __name__ == "__main__":
    merger = DescriptionMerger()
    
    # Example from your data
    resume_desc = """
    Formulation of mathematical models for the optimization of passenger placement, considering multiple constraints (aircraft balancing, grouped placement of passengers traveling together, and taking into account passengers with reduced mobility).
    Evaluation of the performance of the passenger placement system using metrics such as boarding time, satisfaction rate of each type of passenger, and overall customer satisfaction.
    Resolution of the mathematical problem using Gurobi and other optimization algorithms.
    """
    
    linkedin_desc = """
    Analyzed SBTi reduction target of 58.8% for Scopes 1, 2, and 3 through scenario modeling and cost assessment.
    Recommended the optimal reduction pathway based on ROI analysis linked to the Green Cover Bond framework.
    Conducted natural disaster risk assessments (floods, heatwaves).
    """
    
    merged = merger.merge_descriptions(resume_desc, linkedin_desc)
    print("--- MERGED DESCRIPTION ---\n")
    print(merged)