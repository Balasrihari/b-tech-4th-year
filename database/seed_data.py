"""
Seed data script for initial database population with FICTIONAL DEMO DATA.

This script creates fictional test data for development and testing purposes only.
All data is clearly identified as fictional and should not be used in production.

Run this after migrations to populate initial data.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from app.models.user import User, UserRole
from app.models.role import Role
from app.models.course import Course
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.core.security import get_password_hash


def seed_database():
    db: Session = SessionLocal()
    
    try:
        print("=" * 60)
        print("SEEDING FICTIONAL DEMO DATA FOR TESTING ONLY")
        print("=" * 60)
        print("WARNING: All data below is fictional and for demo purposes only!")
        print("=" * 60)
        
        # Create roles
        print("\nCreating roles...")
        roles_data = [
            {"name": "student", "description": "Student role with learning features", "permissions": "{}"},
            {"name": "faculty", "description": "Faculty role with course management", "permissions": "{}"},
            {"name": "admin", "description": "Administrator role with system management", "permissions": "{}"},
        ]
        
        for role_data in roles_data:
            existing_role = db.query(Role).filter(Role.name == role_data["name"]).first()
            if not existing_role:
                role = Role(**role_data, is_active=True)
                db.add(role)
                print(f"  Created role: {role_data['name']}")
        
        # Create fictional admin user
        print("\nCreating fictional admin user...")
        admin_user = db.query(User).filter(User.email == "demo_admin@fictional.test").first()
        if not admin_user:
            admin_user = User(
                email="demo_admin@fictional.test",
                full_name="Demo Administrator (FICTIONAL)",
                hashed_password=get_password_hash("demo_admin_123"),
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(admin_user)
            print("  Created fictional admin: demo_admin@fictional.test / demo_admin_123")
        
        # Create fictional faculty users
        print("\nCreating fictional faculty users...")
        faculty_users = [
            {
                "email": "demo_faculty1@fictional.test",
                "full_name": "Dr. Jane Smith (FICTIONAL)",
                "password": "demo_faculty_123"
            },
            {
                "email": "demo_faculty2@fictional.test",
                "full_name": "Prof. John Doe (FICTIONAL)",
                "password": "demo_faculty_123"
            },
        ]
        
        for faculty_data in faculty_users:
            existing_user = db.query(User).filter(User.email == faculty_data["email"]).first()
            if not existing_user:
                faculty_user = User(
                    email=faculty_data["email"],
                    full_name=faculty_data["full_name"],
                    hashed_password=get_password_hash(faculty_data["password"]),
                    role=UserRole.FACULTY,
                    is_active=True
                )
                db.add(faculty_user)
                print(f"  Created fictional faculty: {faculty_data['email']} / {faculty_data['password']}")
        
        # Create fictional student users
        print("\nCreating fictional student users...")
        student_users = [
            {
                "email": "demo_student1@fictional.test",
                "full_name": "Alice Johnson (FICTIONAL)",
                "password": "demo_student_123"
            },
            {
                "email": "demo_student2@fictional.test",
                "full_name": "Bob Williams (FICTIONAL)",
                "password": "demo_student_123"
            },
            {
                "email": "demo_student3@fictional.test",
                "full_name": "Carol Davis (FICTIONAL)",
                "password": "demo_student_123"
            },
        ]
        
        for student_data in student_users:
            existing_user = db.query(User).filter(User.email == student_data["email"]).first()
            if not existing_user:
                student_user = User(
                    email=student_data["email"],
                    full_name=student_data["full_name"],
                    hashed_password=get_password_hash(student_data["password"]),
                    role=UserRole.STUDENT,
                    is_active=True
                )
                db.add(student_user)
                print(f"  Created fictional student: {student_data['email']} / {student_data['password']}")
        
        # Create fictional courses
        print("\nCreating fictional courses...")
        faculty1 = db.query(User).filter(User.email == "demo_faculty1@fictional.test").first()
        faculty2 = db.query(User).filter(User.email == "demo_faculty2@fictional.test").first()
        
        courses_data = [
            {
                "title": "Introduction to Computer Science (FICTIONAL)",
                "code": "CS101",
                "description": "Basic computer science concepts and programming fundamentals",
                "faculty_id": faculty1.id if faculty1 else None
            },
            {
                "title": "Data Structures and Algorithms (FICTIONAL)",
                "code": "CS201",
                "description": "Advanced data structures and algorithm analysis",
                "faculty_id": faculty1.id if faculty1 else None
            },
            {
                "title": "Machine Learning Fundamentals (FICTIONAL)",
                "code": "ML301",
                "description": "Introduction to machine learning and neural networks",
                "faculty_id": faculty2.id if faculty2 else None
            },
        ]
        
        for course_data in courses_data:
            existing_course = db.query(Course).filter(Course.code == course_data["code"]).first()
            if not existing_course:
                course = Course(**course_data, is_active=True)
                db.add(course)
                print(f"  Created fictional course: {course_data['code']} - {course_data['title']}")
        
        # Create fictional enrollments
        print("\nCreating fictional enrollments...")
        student1 = db.query(User).filter(User.email == "demo_student1@fictional.test").first()
        student2 = db.query(User).filter(User.email == "demo_student2@fictional.test").first()
        student3 = db.query(User).filter(User.email == "demo_student3@fictional.test").first()
        
        course_cs101 = db.query(Course).filter(Course.code == "CS101").first()
        course_cs201 = db.query(Course).filter(Course.code == "CS201").first()
        course_ml301 = db.query(Course).filter(Course.code == "ML301").first()
        
        enrollments_data = [
            {"student_id": student1.id if student1 else None, "course_id": course_cs101.id if course_cs101 else None},
            {"student_id": student1.id if student1 else None, "course_id": course_cs201.id if course_cs201 else None},
            {"student_id": student2.id if student2 else None, "course_id": course_cs101.id if course_cs101 else None},
            {"student_id": student2.id if student2 else None, "course_id": course_ml301.id if course_ml301 else None},
            {"student_id": student3.id if student3 else None, "course_id": course_cs101.id if course_cs101 else None},
            {"student_id": student3.id if student3 else None, "course_id": course_ml301.id if course_ml301 else None},
        ]
        
        for enrollment_data in enrollments_data:
            if enrollment_data["student_id"] and enrollment_data["course_id"]:
                existing_enrollment = db.query(Enrollment).filter(
                    Enrollment.student_id == enrollment_data["student_id"],
                    Enrollment.course_id == enrollment_data["course_id"]
                ).first()
                if not existing_enrollment:
                    enrollment = Enrollment(**enrollment_data, status=EnrollmentStatus.ACTIVE)
                    db.add(enrollment)
                    print(f"  Created fictional enrollment: Student {enrollment_data['student_id']} -> Course {enrollment_data['course_id']}")
        
        db.commit()
        print("\n" + "=" * 60)
        print("FICTIONAL DEMO DATA SEEDED SUCCESSFULLY")
        print("=" * 60)
        print("\nFictional Demo Credentials:")
        print("  Admin: demo_admin@fictional.test / demo_admin_123")
        print("  Faculty: demo_faculty1@fictional.test / demo_faculty_123")
        print("  Student: demo_student1@fictional.test / demo_student_123")
        print("\nREMINDER: All data is fictional and for testing only!")
        print("=" * 60)
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
