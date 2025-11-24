from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import nltk
import language_tool_python

from sentence_transformers import SentenceTransformer, util

# Load model once
similarity_model = SentenceTransformer('all-MiniLM-L6-v2')


# Download NLTK tokenizer data
nltk.download('punkt')

app = Flask(__name__)
CORS(app)

# Load the rubric once when the app starts
with open("rubric.json", "r") as f:
    RUBRIC = json.load(f)

# -------------------------------------------------------
# Utility Functions
# -------------------------------------------------------

def get_word_count(text):
    words = nltk.word_tokenize(text)
    return len(words)

def get_sentence_count(text):
    sentences = nltk.sent_tokenize(text)
    return len(sentences)

# -------------------------------------------------------
# RULE-BASED SCORING FUNCTIONS (Salutation, Keywords, Flow)
# -------------------------------------------------------

def score_salutation(text):
    """Check if the introduction starts with a greeting."""
    greetings = ["hello", "hi", "good morning", "good afternoon", "good evening"]
    text_lower = text.lower()

    for g in greetings:
        if g in text_lower[:60]:   # check beginning
            return 1, "Good: Salutation found."
    return 0, "No salutation found."


def score_keyword_presence(text):
    """Check if important introduction keywords are present."""
    keywords = ["name", "age", "class", "school", "family", "hobby", "hobbies", "interest"]
    text_lower = text.lower()

    found = [kw for kw in keywords if kw in text_lower]

    score = len(found) / len(keywords)
    feedback = f"Found keywords: {found}"

    return score, feedback


def score_flow(text):
    """Check if introduction follows structured order."""
    text_lower = text.lower()
    order = ["hello", "name", "family", "hobby", "thank"]

    score = 0
    last_pos = -1

    for item in order:
        pos = text_lower.find(item)
        if pos != -1 and pos > last_pos:
            score += 1
            last_pos = pos

    score /= len(order)
    feedback = f"Flow score: {score:.2f}"

    return score, feedback


# -------------------------------------------------------
# RULE 9.2 — SPEECH RATE (WPM estimation)
# -------------------------------------------------------

def score_speech_rate(text):
    """Estimate speaking rate using avg words per sentence."""
    words = get_word_count(text)
    sentences = get_sentence_count(text)

    if sentences == 0:
        return 0, "No sentences detected."

    avg = words / sentences  # average words per sentence

    if 10 <= avg <= 18:
        score = 1.0
        feedback = f"Good speaking pace. Avg words/sentence = {avg:.2f}"
    elif 8 <= avg < 10 or 18 < avg <= 22:
        score = 0.6
        feedback = f"Moderate pace. Avg words/sentence = {avg:.2f}"
    else:
        score = 0.3
        feedback = f"Too fast or too slow. Avg words/sentence = {avg:.2f}"

    return score, feedback


# -------------------------------------------------------
# RULE 9.3 — GRAMMAR ERRORS USING LANGUAGETOOL
# -------------------------------------------------------

def score_grammar(text):
    """Check grammar errors using LanguageTool."""
    tool = language_tool_python.LanguageTool('en-US')
    matches = tool.check(text)

    error_count = len(matches)

    # Scoring logic:
    if error_count == 0:
        score = 1.0
        feedback = "Excellent grammar. No errors found."
    elif error_count <= 3:
        score = 0.7
        feedback = f"Good grammar. Only {error_count} minor errors."
    elif error_count <= 8:
        score = 0.4
        feedback = f"Moderate grammar. {error_count} errors detected."
    else:
        score = 0.2
        feedback = f"Too many errors: {error_count}."

    return score, feedback

# -------------------------------------------------------
# RULE 9.4 — VOCABULARY RICHNESS (TTR)
# -------------------------------------------------------

def score_vocabulary(text):
    """Calculate vocabulary richness using TTR."""
    words = nltk.word_tokenize(text.lower())
    words = [w for w in words if w.isalpha()]  # keep only words

    if len(words) == 0:
        return 0, "No valid words found."

    unique_words = set(words)

    ttr = len(unique_words) / len(words)

    # Assign score based on TTR
    if ttr > 0.60:
        score = 1.0
        feedback = f"Excellent vocabulary richness. TTR = {ttr:.2f}"
    elif ttr > 0.45:
        score = 0.7
        feedback = f"Good vocabulary richness. TTR = {ttr:.2f}"
    elif ttr > 0.30:
        score = 0.4
        feedback = f"Average vocabulary richness. TTR = {ttr:.2f}"
    else:
        score = 0.2
        feedback = f"Poor vocabulary richness. TTR = {ttr:.2f}"

    return score, feedback

# -------------------------------------------------------
# RULE 9.5 — FILLER WORD RATE (CLARITY)
# -------------------------------------------------------

def score_filler_words(text):
    """Detect filler words and score based on frequency."""
    filler_words = [
        "um", "uh", "like", "you know", "so", "actually", "basically", "right",
        "i mean", "kinda", "sort of", "okay", "hmm", "ah"
    ]

    text_lower = text.lower()

    filler_count = 0
    for fw in filler_words:
        filler_count += text_lower.count(fw)

    word_count = get_word_count(text)

    if word_count == 0:
        return 0, "No words found."

    filler_rate = filler_count / word_count  # filler words per total words

    # Scoring logic
    if filler_rate == 0:
        score = 1.0
        feedback = "Excellent clarity. No filler words found."
    elif filler_rate <= 0.02:
        score = 0.7
        feedback = f"Good clarity. Few filler words ({filler_count})."
    elif filler_rate <= 0.05:
        score = 0.4
        feedback = f"Moderate clarity. Several filler words ({filler_count})."
    else:
        score = 0.2
        feedback = f"Poor clarity. Too many filler words ({filler_count})."

    return score, feedback

# -------------------------------------------------------
# RULE 9.6 — SENTIMENT / POSITIVITY (ENGAGEMENT)
# -------------------------------------------------------
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def score_sentiment(text):
    """Analyze positivity using VADER sentiment analyzer."""
    analyzer = SentimentIntensityAnalyzer()
    scores = analyzer.polarity_scores(text)

    comp = scores["compound"]

    if comp > 0.4:
        score = 1.0
        feedback = f"Positive and engaging tone. Sentiment = {comp:.2f}"
    elif comp > 0.1:
        score = 0.7
        feedback = f"Somewhat positive tone. Sentiment = {comp:.2f}"
    elif comp > -0.1:
        score = 0.5
        feedback = f"Neutral tone. Sentiment = {comp:.2f}"
    else:
        score = 0.2
        feedback = f"Negative/low engagement. Sentiment = {comp:.2f}"

    return score, feedback

# -------------------------------------------------------
# RULE 9.7 — SEMANTIC SIMILARITY SCORE
# -------------------------------------------------------

def score_semantic_similarity(text, metric_description):
    """Compute semantic similarity between transcript and metric."""
    if not metric_description:
        return 0, "No description to compare."

    emb1 = similarity_model.encode(text, convert_to_tensor=True)
    emb2 = similarity_model.encode(metric_description, convert_to_tensor=True)

    similarity = util.cos_sim(emb1, emb2).item()  # value between -1 and +1

    # Normalize from [-1..1] → [0..1]
    normalized = (similarity + 1) / 2

    feedback = f"Semantic similarity = {normalized:.2f}"

    return normalized, feedback



# -------------------------------------------------------
# API ENDPOINT
# -------------------------------------------------------

@app.route("/score", methods=["POST"])
def score_text():
    data = request.get_json()
    transcript = data.get("transcript", "").strip()

    if not transcript:
        return jsonify({"error": "Transcript is empty"}), 400

    results = []

    # Go through each rubric metric
    for item in RUBRIC:
        metric_name = item["metric"]

        # Map rubric metric → scoring function
        if "Salutation" in metric_name:
            s, fb = score_salutation(transcript)
        elif "Keyword" in metric_name:
            s, fb = score_keyword_presence(transcript)
        elif "Flow" in metric_name:
            s, fb = score_flow(transcript)
        elif "Speech Rate" in metric_name:
            s, fb = score_speech_rate(transcript)
        elif "Grammar" in metric_name:
            s, fb = score_grammar(transcript)
        elif "Vocabulary" in metric_name:
            s, fb = score_vocabulary(transcript)
        elif "Filler" in metric_name or "Clarity" in metric_name:
            s, fb = score_filler_words(transcript)
        elif "Sentiment" in metric_name or "Engagement" in metric_name:
            s, fb = score_sentiment(transcript)
        else:
    # fallback: semantic similarity for any metric not matched above
            metric_description = item["metric"]
            s, fb = score_semantic_similarity(transcript, metric_description)

            
        results.append({
            "criterion": item["criterion"],
            "metric": item["metric"],
            "weight": item["weight"],
            "score": s,
            "feedback": fb
        })

    # Weighted final score
    final_score = sum(r["score"] * r["weight"] for r in results)

    return jsonify({
        "final_score": final_score,
        "details": results
    })


@app.route("/", methods=["GET"])
def home():
    return {"message": "Backend is running!"}


if __name__ == "__main__":
    app.run(debug=True)
