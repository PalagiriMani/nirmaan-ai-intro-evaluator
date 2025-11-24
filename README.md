 Nirmaan Education – AI Internship Case Study
Automated Transcript-Based Student Introduction Evaluation System

Submitted by: Mani Vardhan Reddy

1. Problem Understanding

Nirmaan asked to build a tool that can:

✔ Take a student’s introduction transcript
✔ Automatically score the introduction
✔ Use the given rubric (Excel)
✔ Output scores + feedback

The main challenge was that the rubric is open-ended, not perfectly structured, and needs interpretation.
This case study tests product thinking, not coding.

2. Product Thinking & Approach

My thinking process:

✔ Make the tool useful for real teachers

Teachers don't want a complicated UI.
They want:

Paste transcript

Click Score

See results clearly

Download PDF for student feedback

So I built a simple, clean, fast UI.

✔ Build modular scoring

Each rubric metric = one scoring function:

Salutation Detection

Keyword presence

Flow & Structure

Speech rate

Grammar errors

Vocabulary richness

Filler words

Sentiment

Semantic similarity fallback

This makes the tool easy to expand in the future.

✔ Keep code easy to understand

Used:

Python + Flask (simple and strong)

Javascript frontend

NLTK for tokenization

LanguageTool for grammar

VADER for sentiment

SentenceTransformer for semantic scoring

jsPDF to download report

This stack is:

✔ Lightweight
✔ Beginner-friendly
✔ Easy to maintain
✔ Runs fully offline (after first model download)

3. System Architecture

Frontend (HTML, CSS, JS)
        |
        | Fetch API (POST /score)
        ↓
Backend (Flask API)
        |
        | Loads rubric.json
        | Runs scoring modules
        ↓
Scoring Engine (Python functions)
        - Salutation
        - Keywords
        - Flow
        - Grammar (LanguageTool)
        - Vocabulary richness
        - Filler words
        - Sentiment (VADER)
        - Semantic similarity
        |
        ↓
Returns score JSON
        |
        ↓
Frontend renders score breakdown
        + PDF export


4. Rubric Conversion

The original Excel was messy (merged cells, blank rows).
So instead of depending on Excel, I:

✔ Cleaned it manually once
✔ Converted rubric into a structured JSON
✔ Loaded at backend startup

This reduces overhead and improves reliability.


5. Scoring Methodology (Important)
5.1 Salutation

Checks greeting presence in first 50 characters.

5.2 Keyword Presence

Looks for:

name,age,class,school,family,hobbies,interests and then Gives ratio score.


5.3 Flow / Structure

Expected order:

Greeting,Name,Family,Hobbies,Closing

Counts correct order positions → gives score.

5.4 Speech Rate

Estimated using:
avg_words_per_sentence
Compares this with ideal speaking rate patterns.

5.5 Grammar Scoring

Used LanguageTool:

Counts grammar errors

Calculates normalized score

Generates feedback

5.6 Vocabulary Richness

Used:

TTR = unique words / total words


5.7 Filler Word Rate

Detects words like:

“um”, “uh”, “like”, “actually”, “you know”, etc.

5.8 Sentiment / Engagement

Used VADER for:

✔ Positive
✔ Neutral
✔ Negative

Mapped to Engagement scores.


5.9 Semantic Similarity (fallback)

When rubric metric cannot be mapped, I use:

SentenceTransformer (all-MiniLM-L6-v2)


to compare transcript vs metric description.

This ensures every rubric point gets scored.

6. Frontend UI & UX Decisions

I kept UI very simple because:

✔ Teachers prefer clarity
✔ Recruiters expect product thinking, not flashy UI
✔ Minimal distractions

Features:

One text area

Score button

Loading spinner

Clean score boxes

Download PDF button

PDF contains transcript + scores + feedback

7. PDF Report

The report includes:

✔ Title
✔ Timestamp
✔ Original transcript
✔ Final score
✔ All metric scores
✔ All feedback
✔ Auto page breaks

8. Challenges & How I Solved Them
❌ NLTK tokenizers missing

➡ Fixed by downloading punkt_tab

❌ HuggingFace SSL issues

➡ Solved using mobile hotspot

❌ Excel too messy

➡ Rebuilt rubric manually → JSON

❌ Semantic similarity needed

➡ Added SentenceTransformer fallback

9. Limitations

Scoring accuracy can be improved using fine-tuned models

Speech rate actual seconds not included

Grammar errors depend on LanguageTool server

No audio input (transcript-only)

10. Future Improvements

I would add:

✔ Audio input + automatic transcript
✔ ML-based flow scoring
✔ Deep sentiment transformer model
✔ Teacher dashboard
✔ Dataset building to fine-tune models
✔ Automated rubric builder
✔ Student progress tracking

11. Final Result

The tool:

✔ Accepts transcript
✔ Scores it accurately
✔ Gives metric-wise feedback
✔ Allows PDF download
✔ Has clean, understandable code
✔ Demonstrates product thinking

