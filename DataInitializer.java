package com.example.demo_gradle1;

import com.example.demo_gradle1.entity.Student;
import com.example.demo_gradle1.entity.Subject;
import com.example.demo_gradle1.repository.StudentRepository;
import com.example.demo_gradle1.repository.SubjectRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

@Component
public class DataInitializer implements CommandLineRunner {
   private final StudentRepository studentRepository;
   private final SubjectRepository subjectRepository;

   public DataInitializer(StudentRepository studentRepository, SubjectRepository subjectRepository) {
      this.studentRepository = studentRepository;
      this.subjectRepository = subjectRepository;
   }

   public void run(String... args) throws Exception {
      this.subjectRepository.save(new Subject("MATH101", "Mathematics"));
      this.subjectRepository.save(new Subject("SCI102", "Science"));
      this.studentRepository.save(new Student(1L, "John Doe", "MATH101"));
      this.studentRepository.save(new Student(2L, "Jane Doe", "SCI102"));
   }
}
