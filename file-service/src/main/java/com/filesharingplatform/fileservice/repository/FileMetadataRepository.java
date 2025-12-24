package com.filesharingplatform.fileservice.repository;

import com.filesharingplatform.fileservice.entity.FileMetadata;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface FileMetadataRepository extends JpaRepository<FileMetadata, String> {

    Optional<FileMetadata> findByFileIdAndIsDeletedFalse(String fileId);

    boolean existsByFileIdAndIsDeletedFalse(String fileId);
}
