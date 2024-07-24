package com.example.demo_gradle1.entity;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;

@Entity
public class Student {
   @Id
   private Long regNo;
   private String studentName;
   private String subjectCode;

   public Student() {
   }

   public Student(Long regNo, String studentName, String subjectCode) {
      this.regNo = regNo;
      this.studentName = studentName;
      this.subjectCode = subjectCode;
   }

   public Long getRegNo() {
      return this.regNo;
   }

   public void setRegNo(Long regNo) {
      this.regNo = regNo;
   }

   public String getStudentName() {
      return this.studentName;
   }

   public void setStudentName(String studentName) {
      this.studentName = studentName;
   }

   public String getSubjectCode() {
      return this.subjectCode;
   }

   public void setSubjectCode(String subjectCode) {
      this.subjectCode = subjectCode;
   }
}
