import os
import re
from dotenv import load_dotenv
from google import genai

BASE_DIR = os.path.dirname(__file__)

# Load .env from multiple possible locations
import pathlib as _pl
load_dotenv('.env')


api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

SYSTEM_PROMPT = """You are GuidX, an expert AI career guidance counselor for students all across India.

Help students with:
1. Courses after 12th - Engineering, Medical, Arts, Science, Commerce, Law
2. Colleges across India - IITs, NITs, AIIMS, Anna University, VIT, SRM, Manipal, DU, BHU
3. Entrance exams - JEE, NEET, CUET, CLAT, CAT
4. Career opportunities and salary prospects
5. Eligibility based on marks and scores
6. Higher studies - MTech, MBA, MD, MS Abroad
7. Scholarships and government jobs

LANGUAGE RULE - VERY IMPORTANT:
Reply in the SAME language the student uses.
Tamil input = Tamil reply.
Hindi input = Hindi reply.
Malayalam input = Malayalam reply.
Telugu input = Telugu reply.
English input = English reply."""

def detect_language(text):
    tamil = set("அஆஇஈஉஊெேைஒஓஔகசடதநபமயரலவழளறன")
    hindi = set("अआइईउऊएऐओऔकखगघचछजझटठडढणतथदधनपफबभमयरलवशषसह")
    malayalam = set("അആഇഈഉഊഎഏഐഒഓഔകഖഗഘചഛജഝടഠഡഢണതഥദധനപഫബഭമയരലവശഷസഹ")
    telugu = set("అఆఇఈఉఊఎఏఐఒఓఔకఖగఘచఛజఝటఠడఢణతథదధనపఫబభమయరలవశషసహ")
    chars = set(text)
    if chars & tamil: return "tamil"
    if chars & hindi: return "hindi"
    if chars & malayalam: return "malayalam"
    if chars & telugu: return "telugu"
    return "english"

def extract_details(message, student_details):
    updated = student_details.copy()
    msg = message.lower()
    marks_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:%|percent|marks?|cgpa)', msg)
    if marks_match:
        val = float(marks_match.group(1))
        if val > 10:
            updated['marks'] = val
    neet = re.search(r'neet\s*(?:score|marks?)?\s*[:-]?\s*(\d+)', msg)
    if neet: updated['neet_score'] = int(neet.group(1))
    jee = re.search(r'jee\s*(?:score|marks?|percentile)?\s*[:-]?\s*(\d+)', msg)
    if jee: updated['jee_score'] = int(jee.group(1))
    if any(w in msg for w in ['engineering','btech','iit','nit','jee']): updated['interest'] = 'Engineering'
    elif any(w in msg for w in ['medical','neet','doctor','mbbs','aiims']): updated['interest'] = 'Medical'
    elif any(w in msg for w in ['arts','ba ','journalism','psychology']): updated['interest'] = 'Arts'
    elif any(w in msg for w in ['science','bsc','research']): updated['interest'] = 'Science'
    elif any(w in msg for w in ['commerce','bcom','ca ','finance']): updated['interest'] = 'Commerce'
    elif any(w in msg for w in ['law','llb','clat','legal']): updated['interest'] = 'Law'
    lang = detect_language(message)
    if lang != 'english': updated['language'] = lang
    return updated

def build_context(student_details):
    parts = []
    if student_details.get('marks'): parts.append(f"12th marks: {student_details['marks']}%")
    if student_details.get('neet_score'): parts.append(f"NEET score: {student_details['neet_score']}")
    if student_details.get('jee_score'): parts.append(f"JEE score: {student_details['jee_score']}")
    if student_details.get('interest'): parts.append(f"Interest: {student_details['interest']}")
    if student_details.get('stream'): parts.append(f"Stream: {student_details['stream']}")
    if student_details.get('location'): parts.append(f"Location: {student_details['location']}")
    if student_details.get('language'): parts.append(f"IMPORTANT - Reply in this language: {student_details['language']}")
    return " | ".join(parts) if parts else ""

def get_suggestions(message, student_details):
    lang = student_details.get('language', 'english')
    msg = message.lower()
    if lang == 'tamil':
        return ['இன்ஜினியரிங் கல்லூரிகள்', 'மருத்துவ படிப்புகள்', 'கலை அறிவியல் கோர்ஸ்கள்', 'என் மதிப்பெண்களுக்கு எந்த கல்லூரி?']
    elif lang == 'hindi':
        return ['इंजीनियरिंग कॉलेज', 'मेडिकल कोर्स', 'आर्ट्स कोर्स', 'मेरे नंबरों के लिए कॉलेज?']
    elif lang == 'malayalam':
        return ['എൻജിനിയറിംഗ് കോഴ്സുകൾ', 'മെഡിക്കൽ കോഴ്സുകൾ', 'ആർട്സ് കോഴ്സുകൾ', 'എന്റെ മാർക്കിന് ഏത് കോളേജ്?']
    elif lang == 'telugu':
        return ['ఇంజనీరింగ్ కోర్సులు', 'మెడికల్ కోర్సులు', 'ఆర్ట్స్ కోర్సులు', 'నా మార్కులకు ఏ కాలేజీ?']
    if any(w in msg for w in ['engineering','btech','iit','jee']):
        return ['Top CSE colleges in India', 'JEE preparation tips', 'NIT vs private college', 'Data Science vs AI ML']
    elif any(w in msg for w in ['medical','neet','mbbs','aiims']):
        return ['AIIMS admission process', 'NEET preparation tips', 'Top government medical colleges', 'Medical without NEET']
    elif any(w in msg for w in ['commerce','ca','finance']):
        return ['CA vs MBA which is better?', 'BCom career options', 'Finance jobs after 12th', 'Best commerce colleges']
    elif any(w in msg for w in ['law','llb','clat']):
        return ['CLAT preparation tips', 'Top NLUs in India', 'LLB career options', '5-year integrated law']
    return ['Engineering courses after 12th', 'Medical courses after 12th', 'Arts and Science courses', 'I scored 85% what can I do?']

def get_bot_response(user_input, history=None, student_details=None):
    if history is None: history = []
    if student_details is None: student_details = {}
    updated_details = extract_details(user_input, student_details)
    if not client:
        return "GuidX API not configured.", [], updated_details
    try:
        context = build_context(updated_details)
        history_text = ""
        if history:
            last_3 = history[-3:]
            history_text = "\n".join([f"Student: {h['user']}\nGuidX: {h['bot']}" for h in last_3])
        full_prompt = SYSTEM_PROMPT
        if context: full_prompt += f"\n\nStudent Profile: {context}"
        if history_text: full_prompt += f"\n\nRecent conversation:\n{history_text}"
        full_prompt += f"\n\nStudent: {user_input}\nGuidX:"
        models = ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-flash-latest"]
        response = None
        for m in models:
            try:
                response = client.models.generate_content(model=m, contents=full_prompt)
                break
            except Exception as me:
                print(f"Model {m} failed: {me}")
                continue
        if not response: raise Exception("All models failed")
        reply = response.text.strip()
        suggestions = get_suggestions(user_input, updated_details)
        return reply, suggestions, updated_details
    except Exception as e:
        print(f"Gemini API Error: {e}")
        lang = updated_details.get('language', 'english')
        if lang == 'tamil':
            fallback = "தொழில்நுட்ப சிக்கல். சற்று நேரத்தில் மீண்டும் முயற்சிக்கவும்!"
        elif lang == 'hindi':
            fallback = "तकनीकी समस्या। कृपया थोड़ी देर बाद पुनः प्रयास करें!"
        elif lang == 'malayalam':
            fallback = "സാങ്കേതിക പ്രശ്നം. ദയവായി വീണ്ടും ശ്രമിക്കുക!"
        elif lang == 'telugu':
            fallback = "సాంకేతిక సమస్య. దయచేసి మళ్ళీ ప్రయత్నించండి!"
        else:
            fallback = "Technical issue. Please try again!"
        return fallback, get_suggestions("", updated_details), updated_details
