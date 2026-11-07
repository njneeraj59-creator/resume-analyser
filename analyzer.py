"""Offline resume analyzer: rule-based matching, no API or internet needed."""
import re
from collections import Counter

SKILLS = {
    "languages": ["python", "java", "javascript", "typescript", "c++", "c#", "go", "rust", "kotlin", "swift", "php", "ruby", "sql", "r", "matlab", "bash"],
    "web": ["html", "css", "react", "angular", "vue", "node.js", "nodejs", "django", "flask", "fastapi", "spring boot", "rest api", "graphql", "tailwind", "bootstrap"],
    "data/ai": ["machine learning", "deep learning", "nlp", "computer vision", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "data analysis", "data visualization", "power bi", "tableau", "excel", "statistics", "llm", "prompt engineering"],
    "cloud/devops": ["aws", "azure", "gcp", "docker", "kubernetes", "git", "github", "ci/cd", "jenkins", "linux", "terraform", "microservices"],
    "databases": ["mysql", "postgresql", "mongodb", "sqlite", "redis", "oracle", "firebase"],
    "practices": ["agile", "scrum", "jira", "unit testing", "oop", "data structures", "algorithms", "system design", "tdd"],
    "soft": ["communication", "teamwork", "leadership", "problem solving", "time management", "collaboration", "adaptability"],
}
ALL_SKILLS = sorted({s for group in SKILLS.values() for s in group}, key=len, reverse=True)
STOP = set("a an and are as at be by for from has have in is it of on or that the to was with you your we our will this their they can who not but if so do per such".split())
ACTION_VERBS = ["built", "developed", "designed", "led", "created", "implemented", "improved", "optimized", "launched", "managed", "automated", "reduced", "increased", "delivered", "deployed"]
SECTIONS = {"education": r"\beducation\b", "experience": r"\b(experience|internship|employment)\b",
            "projects": r"\bprojects?\b", "skills": r"\bskills\b"}


def _find_skills(text: str) -> set:
    t = text.lower()
    found = set()
    for s in ALL_SKILLS:
        if re.search(r"(?<![a-z0-9+#.])" + re.escape(s) + r"(?![a-z0-9+#])", t):
            found.add(s)
    return found


def _keywords(text: str) -> Counter:
    words = re.findall(r"[a-z][a-z+#.]{2,}", text.lower())
    return Counter(w for w in words if w not in STOP)


def analyze(resume: str, job: str) -> dict:
    r_sk, j_sk = _find_skills(resume), _find_skills(job)
    matching = sorted(j_sk & r_sk)
    missing = sorted(j_sk - r_sk)

    # Score = 60% skill coverage + 30% keyword overlap + 10% resume structure
    skill_cov = len(matching) / len(j_sk) if j_sk else 0.5
    jk, rk = _keywords(job), _keywords(resume)
    top_job = [w for w, _ in jk.most_common(40)]
    kw_cov = sum(1 for w in top_job if w in rk) / len(top_job) if top_job else 0
    sections_found = [n for n, p in SECTIONS.items() if re.search(p, resume.lower())]
    structure = len(sections_found) / len(SECTIONS)
    score = round(100 * (0.6 * skill_cov + 0.3 * kw_cov + 0.1 * structure))

    strengths, tips = [], []
    verbs = [v for v in ACTION_VERBS if re.search(rf"\b{v}\b", resume.lower())]
    numbers = re.findall(r"\b\d+(?:\.\d+)?\s?(?:%|\+|x|k|users|clients|projects)?", resume)
    if len(matching) >= 3:
        strengths.append(f"Covers {len(matching)} skills the job asks for.")
    if len(verbs) >= 3:
        strengths.append("Uses strong action verbs (" + ", ".join(verbs[:4]) + ").")
    if len(numbers) >= 3:
        strengths.append("Includes measurable results with numbers.")
    if "projects" in sections_found:
        strengths.append("Has a projects section that shows practical work.")

    for s in missing[:6]:
        tips.append(f"The job mentions '{s}'. If you have used it, add it to your skills or a project; if not, consider a small project with it.")
    for name in SECTIONS:
        if name not in sections_found:
            tips.append(f"Add a clear '{name.title()}' section.")
    if len(verbs) < 3:
        tips.append("Start bullet points with action verbs such as built, designed, improved.")
    if len(numbers) < 3:
        tips.append("Add numbers to your achievements (e.g. 'reduced load time by 30%').")
    if not re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", resume):
        tips.append("Add an email address so recruiters can contact you.")
    words = len(resume.split())
    if words < 150:
        tips.append("Your resume looks short. Add more detail on projects and experience.")
    elif words > 900:
        tips.append("Your resume is long. Aim for one to two pages.")

    top = ", ".join(matching[:5]) if matching else "your core skills"
    target = ", ".join(missing[:2])
    summary = (f"Motivated candidate with hands-on experience in {top}. "
               f"Seeking a role where I can apply these skills and keep growing"
               + (f", including in {target}." if target else "."))
    verdict = ("Strong match." if score >= 75 else "Decent match with some gaps." if score >= 50 else "Weak match: close the missing skills first.")
    return {"match_score": score, "summary": f"{verdict} {len(matching)} of {len(j_sk)} detected job skills found in your resume.",
            "matching_skills": matching, "missing_skills": missing, "strengths": strengths or ["Add more detail to reveal strengths."],
            "improvements": tips or ["Looks solid. Tailor wording to the job description."], "improved_summary": summary}
