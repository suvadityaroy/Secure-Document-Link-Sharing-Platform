package com.filesharingplatform.fileservice.service;

import com.filesharingplatform.fileservice.entity.FileMetadata;
import com.filesharingplatform.fileservice.repository.FileMetadataRepository;
import com.filesharingplatform.fileservice.config.FileStorageConfig;
import com.filesharingplatform.fileservice.dto.FileUploadResponse;
import com.filesharingplatform.fileservice.dto.FileVerificationResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
public class FileStorageService {

    private final FileMetadataRepository fileMetadataRepository;
    private final FileStorageConfig fileStorageConfig;

    /**
     * Upload and store a file.
     * Returns file metadata including ID and hash.
     */
    public FileUploadResponse uploadFile(MultipartFile file) throws IOException, NoSuchAlgorithmException {
        // Validate file
        if (file.isEmpty()) {
            throw new IllegalArgumentException("File is empty");
        }

        // Generate unique file ID
        String fileId = UUID.randomUUID().toString();

        // Calculate file hash (SHA-256)
        String fileHash = calculateHash(file.getBytes());

        // Ensure storage directory exists
        fileStorageConfig.ensureStorageDir();

        // Save file to disk
        Path filePath = fileStorageConfig.getFileFullPath(fileId);
        Files.write(filePath, file.getBytes());

        // Save metadata to database
        FileMetadata metadata = new FileMetadata();
        metadata.setFileId(fileId);
        metadata.setOriginalFileName(file.getOriginalFilename());
        metadata.setFileSize(file.getSize());
        metadata.setFileHash(fileHash);
        metadata.setFilePath(filePath.toString());
        metadata.setMimeType(file.getContentType());

        fileMetadataRepository.save(metadata);

        log.info("File uploaded: {} (ID: {})", file.getOriginalFilename(), fileId);

        return new FileUploadResponse(
            fileId,
            file.getOriginalFilename(),
            file.getSize(),
            fileHash,
            "File uploaded successfully"
        );
    }

    /**
     * Download file by ID.
     */
    public byte[] downloadFile(String fileId) throws IOException {
        FileMetadata metadata = fileMetadataRepository
            .findByFileIdAndIsDeletedFalse(fileId)
            .orElseThrow(() -> new IllegalArgumentException("File not found: " + fileId));

        Path filePath = Path.of(metadata.getFilePath());
        if (!Files.exists(filePath)) {
            throw new IOException("File not found on disk: " + fileId);
        }

        log.info("File downloaded: {} (ID: {})", metadata.getOriginalFileName(), fileId);

        return Files.readAllBytes(filePath);
    }

    /**
     * Get file metadata.
     */
    public FileMetadata getFileMetadata(String fileId) {
        return fileMetadataRepository
            .findByFileIdAndIsDeletedFalse(fileId)
            .orElseThrow(() -> new IllegalArgumentException("File not found: " + fileId));
    }

    /**
     * Delete file (soft delete - mark as deleted in database).
     */
    public void deleteFile(String fileId) throws IOException {
        FileMetadata metadata = fileMetadataRepository
            .findByFileIdAndIsDeletedFalse(fileId)
            .orElseThrow(() -> new IllegalArgumentException("File not found: " + fileId));

        // Delete from disk
        Path filePath = Path.of(metadata.getFilePath());
        if (Files.exists(filePath)) {
            Files.delete(filePath);
        }

        // Mark as deleted in database
        metadata.setIsDeleted(true);
        fileMetadataRepository.save(metadata);

        log.info("File deleted: {} (ID: {})", metadata.getOriginalFileName(), fileId);
    }

    /**
     * Verify file integrity using hash.
     */
    public FileVerificationResponse verifyFile(String fileId, String expectedHash) throws IOException, NoSuchAlgorithmException {
        FileMetadata metadata = getFileMetadata(fileId);

        boolean verified = metadata.getFileHash().equals(expectedHash);

        log.info("File verification: {} - {}", fileId, verified ? "PASSED" : "FAILED");

        return new FileVerificationResponse(
            fileId,
            metadata.getOriginalFileName(),
            verified,
            verified ? "File integrity verified" : "File integrity check failed"
        );
    }

    /**
     * Calculate SHA-256 hash of file content.
     */
    private String calculateHash(byte[] fileContent) throws NoSuchAlgorithmException {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        byte[] hashBytes = digest.digest(fileContent);

        // Convert to hex string
        StringBuilder hexString = new StringBuilder();
        for (byte b : hashBytes) {
            String hex = Integer.toHexString(0xff & b);
            if (hex.length() == 1) hexString.append('0');
            hexString.append(hex);
        }

        return hexString.toString();
    }

    /**
     * Check if file exists.
     */
    public boolean fileExists(String fileId) {
        return fileMetadataRepository.existsByFileIdAndIsDeletedFalse(fileId);
    }
}
