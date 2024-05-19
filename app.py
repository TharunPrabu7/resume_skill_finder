from flask import Flask, render_template, request
import PyPDF2
import docx
import re
import nltk

app = Flask(__name__)

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    text = ""
    with open(pdf_file, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text

# Function to extract text from DOC
def extract_text_from_doc(doc_file):
    text = ""
    doc = docx.Document(doc_file)
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

# Function to extract skills from job description and resume
def extract_skills(job_description, resume_text):
    skill_set_file = 'skill_set.txt'
    
    # Extract skills from job description
    extracted_skills_job = set()
    
    # Read skills from the provided text file
    with open(skill_set_file, 'r') as file:
        skill_set = file.read()

    # Convert the skill set to lowercase
    skill_set = skill_set.lower()

    # Split the skill set by comma and strip whitespace
    skill_list = [skill.strip() for skill in skill_set.split(',')]

    # Tokenize job description using NLTK's word_tokenize
    skills_to_find_job = nltk.word_tokenize(job_description)
    skills_to_find_job = [word.lower() for word in skills_to_find_job]

    # Concatenate words in skills_to_find_job into a single string with no spaces
    paragraph_job = ''.join(skills_to_find_job)

    # Check if each skill in the skill list is present in the job description
    for skill in skill_list:
        # Remove spaces from the skill
        skill_no_spaces = re.sub(r'\s', '', skill)
        if skill_no_spaces in paragraph_job:
            extracted_skills_job.add(skill)

    # Extract skills from resume
    extracted_skills_resume = set()

    # Tokenize resume text using NLTK's word_tokenize
    skills_to_find_resume = nltk.word_tokenize(resume_text)
    skills_to_find_resume = [word.lower() for word in skills_to_find_resume]

    # Concatenate words in skills_to_find_resume into a single string with no spaces
    paragraph_resume = ''.join(skills_to_find_resume)

    # Check if each skill in the skill list is present in the resume
    for skill in skill_list:
        # Remove spaces from the skill
        skill_no_spaces = re.sub(r'\s', '', skill)
        if skill_no_spaces in paragraph_resume:
            extracted_skills_resume.add(skill)

    # Find missing skills in resume
    missing_skills_resume = set(extracted_skills_job) - extracted_skills_resume

    return extracted_skills_job, extracted_skills_resume, missing_skills_resume

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    resume = request.files['resume']
    job_description = request.form['job_description']

    # Check if resume file is provided
    if resume.filename == '':
        return "Error: No resume file provided."

    # Extract text from resume based on file extension
    if resume.filename.endswith('.pdf'):
        resume_text = extract_text_from_pdf(resume)
    elif resume.filename.endswith('.docx'):
        resume_text = extract_text_from_doc(resume)
    else:
        return "Error: Unsupported file format. Please upload a PDF or DOCX file."

    # Extract skills from job description and resume
    job_skills, resume_skills, missing_skills_resume = extract_skills(job_description, resume_text)

    # Render template with extracted skills and missing skills
    return render_template('result.html', job_skills=job_skills, resume_skills=resume_skills, missing_skills_resume=missing_skills_resume)

if __name__ == '__main__':
    app.run(debug=True)
