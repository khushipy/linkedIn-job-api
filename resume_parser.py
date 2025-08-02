#!/usr/bin/env python3
"""
Resume Parser and Job Matching Module
Extracts skills and experience from resume files and matches with job requirements
"""

import os
import re
import logging
from typing import List, Dict, Set, Tuple
import PyPDF2
from docx import Document
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class ResumeParser:
    """Parse resume files and extract relevant information"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Common skill keywords (can be expanded)
        self.tech_skills = {
            'programming': ['python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin'],
            'web': ['html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'spring'],
            'database': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'oracle', 'sqlite'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins', 'ci/cd'],
            'data': ['pandas', 'numpy', 'matplotlib', 'scikit-learn', 'tensorflow', 'pytorch', 'spark', 'hadoop'],
            'tools': ['git', 'jira', 'confluence', 'slack', 'trello', 'figma', 'photoshop', 'excel']
        }
        
        # Experience level keywords
        self.experience_keywords = {
            'junior': ['junior', 'entry', 'associate', 'intern', '0-2 years', 'graduate'],
            'mid': ['mid', 'intermediate', '2-5 years', '3-7 years', 'experienced'],
            'senior': ['senior', 'lead', 'principal', '5+ years', '7+ years', 'expert', 'architect']
        }

    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            self.logger.error(f"Error reading PDF {file_path}: {str(e)}")
            return ""

    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            self.logger.error(f"Error reading DOCX {file_path}: {str(e)}")
            return ""

    def extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            self.logger.error(f"Error reading TXT {file_path}: {str(e)}")
            return ""

    def parse_resume(self, file_path: str) -> Dict:
        """Parse resume file and extract information"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Resume file not found: {file_path}")
        
        # Extract text based on file extension
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.pdf':
            text = self.extract_text_from_pdf(file_path)
        elif file_ext == '.docx':
            text = self.extract_text_from_docx(file_path)
        elif file_ext == '.txt':
            text = self.extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
        
        if not text.strip():
            raise ValueError("No text could be extracted from the resume")
        
        # Parse the extracted text
        return self.analyze_resume_text(text)

    def analyze_resume_text(self, text: str) -> Dict:
        """Analyze resume text and extract structured information"""
        text_lower = text.lower()
        
        # Extract skills
        skills = self.extract_skills(text_lower)
        
        # Extract experience level
        experience_level = self.extract_experience_level(text_lower)
        
        # Extract years of experience
        years_experience = self.extract_years_experience(text_lower)
        
        # Extract education
        education = self.extract_education(text_lower)
        
        # Extract contact info
        contact_info = self.extract_contact_info(text)
        
        return {
            'skills': skills,
            'experience_level': experience_level,
            'years_experience': years_experience,
            'education': education,
            'contact_info': contact_info,
            'raw_text': text
        }

    def extract_skills(self, text: str) -> Dict[str, List[str]]:
        """Extract technical skills from resume text"""
        found_skills = {}
        
        for category, skill_list in self.tech_skills.items():
            found_skills[category] = []
            for skill in skill_list:
                if skill in text:
                    found_skills[category].append(skill)
        
        return found_skills

    def extract_experience_level(self, text: str) -> str:
        """Determine experience level from resume text"""
        for level, keywords in self.experience_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return level
        return 'unknown'

    def extract_years_experience(self, text: str) -> int:
        """Extract years of experience from resume text"""
        # Look for patterns like "5 years", "3+ years", etc.
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'(\d+)\+?\s*years?\s*in',
            r'experience\s*(?:of\s*)?(\d+)\+?\s*years?'
        ]
        
        years = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            years.extend([int(match) for match in matches])
        
        return max(years) if years else 0

    def extract_education(self, text: str) -> List[str]:
        """Extract education information"""
        education_keywords = ['bachelor', 'master', 'phd', 'degree', 'university', 'college', 'b.s.', 'm.s.', 'b.a.', 'm.a.']
        education = []
        
        for keyword in education_keywords:
            if keyword in text:
                # Try to extract the full education line
                lines = text.split('\n')
                for line in lines:
                    if keyword in line.lower():
                        education.append(line.strip())
                        break
        
        return list(set(education))  # Remove duplicates

    def extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract contact information"""
        contact_info = {}
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact_info['email'] = emails[0]
        
        # Phone pattern
        phone_pattern = r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, text)
        if phones:
            contact_info['phone'] = ''.join(phones[0]) if isinstance(phones[0], tuple) else phones[0]
        
        return contact_info

class JobMatcher:
    """Match jobs with resume based on skills and requirements"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)

    def calculate_job_match_score(self, resume_data: Dict, job_description: str, job_title: str) -> float:
        """Calculate match score between resume and job"""
        try:
            # Combine resume skills into text
            resume_skills_text = self.format_resume_skills(resume_data)
            
            # Combine resume text with skills
            resume_text = f"{resume_data.get('raw_text', '')} {resume_skills_text}"
            
            # Create corpus
            corpus = [resume_text, job_description.lower()]
            
            # Calculate TF-IDF similarity
            tfidf_matrix = self.vectorizer.fit_transform(corpus)
            similarity_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            # Boost score based on specific skill matches
            skill_boost = self.calculate_skill_match_boost(resume_data, job_description, job_title)
            
            # Final score (weighted combination)
            final_score = (similarity_score * 0.7) + (skill_boost * 0.3)
            
            return min(final_score, 1.0)  # Cap at 1.0
            
        except Exception as e:
            self.logger.error(f"Error calculating match score: {str(e)}")
            return 0.0

    def format_resume_skills(self, resume_data: Dict) -> str:
        """Format resume skills into a text string"""
        skills_text = ""
        skills = resume_data.get('skills', {})
        
        for category, skill_list in skills.items():
            skills_text += f"{category}: {' '.join(skill_list)} "
        
        return skills_text

    def calculate_skill_match_boost(self, resume_data: Dict, job_description: str, job_title: str) -> float:
        """Calculate additional boost based on specific skill matches"""
        job_text = f"{job_title} {job_description}".lower()
        resume_skills = resume_data.get('skills', {})
        
        total_skills = 0
        matched_skills = 0
        
        for category, skill_list in resume_skills.items():
            for skill in skill_list:
                total_skills += 1
                if skill.lower() in job_text:
                    matched_skills += 1
        
        if total_skills == 0:
            return 0.0
        
        return matched_skills / total_skills

    def is_suitable_job(self, resume_data: Dict, job_description: str, job_title: str, 
                       min_score: float = 0.3) -> Tuple[bool, float, str]:
        """Determine if a job is suitable based on resume match"""
        try:
            match_score = self.calculate_job_match_score(resume_data, job_description, job_title)
            
            is_suitable = match_score >= min_score
            
            # Generate explanation
            if is_suitable:
                explanation = f"Good match (Score: {match_score:.2f}) - Skills and experience align well"
            else:
                explanation = f"Poor match (Score: {match_score:.2f}) - Limited skill overlap"
            
            return is_suitable, match_score, explanation
            
        except Exception as e:
            self.logger.error(f"Error determining job suitability: {str(e)}")
            return False, 0.0, f"Error in analysis: {str(e)}"

    def rank_jobs(self, resume_data: Dict, jobs: List[Dict]) -> List[Dict]:
        """Rank jobs by match score"""
        try:
            for job in jobs:
                job_desc = job.get('description', '')
                job_title = job.get('title', '')
                
                is_suitable, score, explanation = self.is_suitable_job(
                    resume_data, job_desc, job_title
                )
                
                job['match_score'] = score
                job['is_suitable'] = is_suitable
                job['match_explanation'] = explanation
            
            # Sort by match score (descending)
            return sorted(jobs, key=lambda x: x.get('match_score', 0), reverse=True)
            
        except Exception as e:
            self.logger.error(f"Error ranking jobs: {str(e)}")
            return jobs

def main():
    """Test the resume parser and job matcher"""
    parser = ResumeParser()
    matcher = JobMatcher()
    
    # Example usage
    try:
        # Parse resume
        resume_path = input("Enter path to your resume file: ")
        resume_data = parser.parse_resume(resume_path)
        
        print("\n=== RESUME ANALYSIS ===")
        print(f"Skills found: {resume_data['skills']}")
        print(f"Experience level: {resume_data['experience_level']}")
        print(f"Years of experience: {resume_data['years_experience']}")
        print(f"Education: {resume_data['education']}")
        
        # Example job matching
        sample_job = {
            'title': 'Python Developer',
            'description': 'We are looking for a Python developer with experience in Django, Flask, and SQL databases.'
        }
        
        is_suitable, score, explanation = matcher.is_suitable_job(
            resume_data, sample_job['description'], sample_job['title']
        )
        
        print(f"\n=== JOB MATCH EXAMPLE ===")
        print(f"Job: {sample_job['title']}")
        print(f"Suitable: {is_suitable}")
        print(f"Score: {score:.2f}")
        print(f"Explanation: {explanation}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
