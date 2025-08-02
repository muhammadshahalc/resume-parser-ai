# Example Usage
if __name__ == "__main__":
    # resume parsing
    resume_path = "C:/Users/pessh/Desktop/resume-parser-ai/backend/resume/resume.pdf"
    parsed_data = parse_resume("C:/Users/pessh/Desktop/resume-parser-ai/backend/resume/resume.pdf")
    
    # company requirements
    company_requirements = {
        "skills": ["Python", "SQL", "Machine Learning", "Pandas", "Deep Learning"],
        "education_keywords": ["B.Tech", "Bachelor of Technology", "Computer Science"],
        "experience_years_required": 1
    }
    
    #match score
    parsed_data["match_score"] = calculate_match_score(parsed_data, company_requirements)
    
    # print results
    from pprint import pprint
    pprint(parsed_data)