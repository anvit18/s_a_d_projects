package com.example.demo_gradle1.entity;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;

@Entity
public class Subject {
   @Id
   private String subjectCode;
   private String subjectName;

   public Subject() {
   }

   public Subject(String subjectCode, String subjectName) {
      this.subjectCode = subjectCode;
      this.subjectName = subjectName;
   }

   public String getSubjectCode() {
      return this.subjectCode;
   }

   public void setSubjectCode(String subjectCode) {
      this.subjectCode = subjectCode;
   }

   public String getSubjectName() {
      return this.subjectName;
   }

   public void setSubjectName(String subjectName) {
      this.subjectName = subjectName;
   }
}
