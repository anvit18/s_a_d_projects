package com.example.demo.repositories;

import com.example.demo.entities.Book;
import org.springframework.data.jpa.repository.JpaRepository;

public interface BookRep extends JpaRepository<Book, Integer> {
}