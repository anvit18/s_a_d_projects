package com.example.demo_gradle1.repository;

import com.example.demo_gradle1.entity.Subject;
import org.springframework.data.jpa.repository.JpaRepository;

public interface SubjectRepository extends JpaRepository<Subject, String> {
}
