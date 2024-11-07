from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr, conint
import threading
import httpx
from typing import List, Optional
import asyncio

# Initialize FastAPI app
app = FastAPI(title="Student Management API")

# Student Model
class StudentBase(BaseModel):
    name: str
    age: conint(ge=16, le=120)  # Constrained integer between 16 and 120
    email: EmailStr

class StudentUpdateBase(BaseModel):
    name: Optional[str] = None
    age: Optional[conint(ge=16, le=120)] = None  # Constrained integer between 16 and 120
    email: Optional[EmailStr] = None

class Student(StudentBase):
    id: int

# In-memory storage
class StudentDB:
    def __init__(self):
        self.students = {}
        self.counter = 0
        self.lock = threading.Lock()

    def add_student(self, student_data: StudentBase) -> Student:
        with self.lock:
            self.counter += 1
            student = Student(
                id=self.counter,
                name=student_data.name,
                age=student_data.age,
                email=student_data.email
            )
            self.students[self.counter] = student
            return student

    def get_student(self, student_id: int) -> Optional[Student]:
        return self.students.get(student_id)

    def get_all_students(self) -> List[Student]:
        return list(self.students.values())

    def update_student(self, student_id: int, student_data: StudentUpdateBase) -> Optional[Student]:
        with self.lock:
            if student_id not in self.students:
                return None
            
            # Get current student data
            current_student = self.students[student_id]
            
            # Update only the fields that are provided
            updated_student = Student(
                id=student_id,
                name=student_data.name if student_data.name is not None else current_student.name,
                age=student_data.age if student_data.age is not None else current_student.age,
                email=student_data.email if student_data.email is not None else current_student.email
            )
            
            self.students[student_id] = updated_student
            return updated_student

    def delete_student(self, student_id: int) -> bool:
        with self.lock:
            if student_id not in self.students:
                return False
            del self.students[student_id]
            return True

# Create global database instance
db = StudentDB()

# Dependency to get DB instance
async def get_db():
    return db

# API Endpoints
@app.post("/students", response_model=Student)
async def create_student(student: StudentBase, db: StudentDB = Depends(get_db)):
    return db.add_student(student)

@app.get("/students", response_model=List[Student])
async def get_students(db: StudentDB = Depends(get_db)):
    return db.get_all_students()

@app.get("/students/{student_id}", response_model=Student)
async def get_student(student_id: int, db: StudentDB = Depends(get_db)):
    student = db.get_student(student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.put("/students/{student_id}", response_model=Student)
async def update_student(student_id: int, student: StudentBase, db: StudentDB = Depends(get_db)):
    updated_student = db.update_student(student_id, student)
    if updated_student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return updated_student

@app.delete("/students/{student_id}")
async def delete_student(student_id: int, db: StudentDB = Depends(get_db)):
    if not db.delete_student(student_id):
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Student deleted successfully"}

@app.get("/students/{student_id}/summary")
async def get_student_summary(student_id: int, db: StudentDB = Depends(get_db)):
    student = db.get_student(student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    # Modified prompt to guide the model for cleaner output
    prompt = f"""Generate a brief, formal description of this student in clear text format:
    
Student Details:
- Name: {student.name}
- Age: {student.age}
- Email: {student.email}
- Student ID: {student.id}

Please provide a concise, professional summary without any markdown formatting or special characters. Focus on presenting the information in a clear, readable format."""

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3.2",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail="Error generating summary from Ollama"
                )
                
            result = response.json()
            
            # Clean up the response
            summary = result["response"]
            # Remove markdown formatting
            summary = summary.replace("*", "")
            summary = summary.replace("#", "")
            summary = summary.replace("+", "")
            summary = summary.replace("[", "")
            summary = summary.replace("]", "")
            summary = summary.replace("(", "")
            summary = summary.replace(")", "")
            
            # Remove any mailto: links
            summary = summary.replace("mailto:", "")
            
            # Remove multiple newlines
            summary = "\n".join(line.strip() for line in summary.splitlines() if line.strip())
            
            return {
                "student_id": student_id,
                "name": student.name,
                "formatted_summary": summary
            }

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail="Could not connect to Ollama service"
        )