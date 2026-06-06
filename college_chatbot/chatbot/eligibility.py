import json
import re
import os

def get_tier(marks, tiers):
    for tier in tiers:
        if tier['min'] <= marks <= tier['max']:
            return tier
    return None

def check_eligibility(message, student_details=None):
    if student_details is None:
        student_details = {}

    # Only run if message actually contains a number
    if not re.search(r'\d', message):
        return None

    # Skip if message is clearly asking about courses not marks
    skip_words = ['which', 'what', 'how', 'tell', 'explain', 'show',
                  'list', 'give', 'describe', 'about', 'course', 'career',
                  'job', 'college list', 'subject', 'syllabus', 'skill']
    msg_lower = message.lower()
    if any(w in msg_lower for w in skip_words):
        # Only continue if message ALSO has clear marks indicators
        marks_indicators = ['scored', 'got', 'marks', 'percent', '%', 'my marks', 'i have']
        if not any(m in msg_lower for m in marks_indicators):
            return None

    marks = None
    patterns = [
        r'scored?\s*(\d+(?:\.\d+)?)\s*(?:%|percent|marks?)?',
        r'got\s*(\d+(?:\.\d+)?)\s*(?:%|percent|marks?)?',
        r'(\d+(?:\.\d+)?)\s*(?:%|percent)',
        r'marks?\s*(?:is|are)?\s*(\d+(?:\.\d+)?)',
        r'percentage\s*(?:is|are)?\s*(\d+(?:\.\d+)?)',
    ]
    for pattern in patterns:
        match = re.search(pattern, message.lower())
        if match:
            val = float(match.group(1))
            if 0 < val <= 100:
                marks = val
                break

    if not marks and student_details.get('marks'):
        try:
            marks = float(student_details['marks'])
        except Exception:
            pass

    if not marks:
        return None

    msg_lower = message.lower()
    field = None
    if any(w in msg_lower for w in ['engineer', 'btech', 'pcm', 'jee', 'tnea']):
        field = 'engineering'
    elif any(w in msg_lower for w in ['doctor', 'medical', 'mbbs', 'neet', 'pcb']):
        field = 'medical'
    elif any(w in msg_lower for w in ['arts', 'bsc', 'literature', 'history']):
        field = 'arts'

    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        eligibility_cfg = config.get('eligibility', {})
    except Exception as e:
        print('Config error:', e)
        return None

    if not field:
        results = []
        for f_name, f_cfg in eligibility_cfg.items():
            tier = get_tier(marks, f_cfg['tiers'])
            if tier:
                results.append((f_name, tier))
        if results:
            response = 'Based on your score of ' + str(marks) + '%, here is your eligibility:\n\n'
            suggestions = []
            for f_name, tier in results:
                label = f_name.title()
                response += label + ': ' + tier['message'] + '\n'
                if tier['colleges']:
                    response += 'Colleges: ' + ', '.join(tier['colleges'][:3]) + '\n'
                response += '\n'
                suggestions.append(label + ' Courses')
            return {'response': response, 'suggestions': suggestions, 'marks': marks}
        return None

    if field in eligibility_cfg:
        tier = get_tier(marks, eligibility_cfg[field]['tiers'])
        if tier:
            response = 'Eligibility Check for ' + field.title() + ' (' + str(marks) + '%)\n\n'
            response += 'Status: ' + tier['label'] + '\n\n'
            response += tier['message'] + '\n\n'
            if tier['colleges']:
                response += 'Recommended Colleges:\n'
                for college in tier['colleges']:
                    response += '- ' + college + '\n'
            response += '\nRequired Stream: ' + eligibility_cfg[field]['stream']
            suggestions = [
                field.title() + ' Courses',
                'Top Colleges in Tamil Nadu',
                'Explore Other Fields'
            ]
            return {'response': response, 'suggestions': suggestions, 'marks': marks}

    return None