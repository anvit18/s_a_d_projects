package com.example.demo_gradle1.repository;

import com.example.demo_gradle1.entity.Student;
import org.springframework.data.jpa.repository.JpaRepository;

public interface StudentRepository extends JpaRepository<Student, Long> {
}
