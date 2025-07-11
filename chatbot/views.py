import json
import os
from pathlib import Path
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
from .nlp_classifier import get_local_answer, call_palm

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
DATA_DIR.mkdir(exist_ok=True)
PERF_CSV = DATA_DIR / 'student_performance.csv'

@csrf_exempt
def index(request):
    return render(request, 'chatbot/index.html')

@csrf_exempt
def chat(request):
    query = request.POST.get('query', '')
    if not query:
        return JsonResponse({'error': 'Empty query'}, status=400)

    answer = get_local_answer(query)
    if answer is None:
        answer = call_palm(query)

    return JsonResponse({'answer': answer})

@csrf_exempt
def analyze_scores(request):
    """Analyze individual-subject and overall performance.
    Accepts:
        – multipart/form-data with `file` (CSV) OR
        – application/x-www-form-urlencoded with `data` = JSON object of {subject: score}
    Returns JSON with overall stats and a per-subject breakdown.
    """
    # 1. Ingest marks -------------------------------------------------------
    if 'file' in request.FILES:
        try:
            df = pd.read_csv(request.FILES['file'])
        except Exception:
            return JsonResponse({'error': 'Unable to read CSV'}, status=400)
    else:
        raw = request.POST.get('data', '{}')
        try:
            # Expecting a JSON object: {"Math": 78, "Physics": 65}
            marks = json.loads(raw)
            if isinstance(marks, list):  # allow list of dicts too
                # list ⇒ take first row
                marks = marks[0] if marks else {}
            df = pd.DataFrame([marks])
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid data format'}, status=400)

    if df.empty:
        return JsonResponse({'error': 'No scores provided'}, status=400)

    # 2. Compute statistics --------------------------------------------------
    subj_scores = df.iloc[0].to_dict()
    breakdown = []
    for subject, score in subj_scores.items():
        score = float(score)
        if score >= 75:
            cat = 'High'
            tip = f'Excellent in {subject}! Keep up the great work.'
        elif score >= 50:
            cat = 'Medium'
            tip = f'You can improve {subject}. Focus on problem areas and practice more.'
        else:
            cat = 'Low'
            tip = f'{subject} needs serious attention. Review basics and seek faculty help.'
        breakdown.append({'subject': subject, 'score': score, 'category': cat, 'tips': tip})

    overall = sum(subj_scores.values()) / len(subj_scores)
    if overall >= 75:
        overall_cat = 'High'
        overall_tip = 'Great job across subjects! Continue your study strategy.'
    elif overall >= 50:
        overall_cat = 'Medium'
        overall_tip = 'Overall OK but improvement needed; prioritise weaker subjects.'
    else:
        overall_cat = 'Low'
        overall_tip = 'Overall performance is low. Create a study timetable and get mentoring.'

    # 3. Persist ----------------------------------------------------------------
    try:
        df.to_csv(PERF_CSV, mode='a', index=False, header=not PERF_CSV.exists())
    except Exception:
        pass  # Non-fatal

    return JsonResponse({
        'overall': round(overall, 2),
        'overall_category': overall_cat,
        'overall_tips': overall_tip,
        'subjects': breakdown,
    })
