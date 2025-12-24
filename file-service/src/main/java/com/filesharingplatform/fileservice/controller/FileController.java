package com.filesharingplatform.fileservice.controller;

import com.filesharingplatform.fileservice.service.FileStorageService;
import com.filesharingplatform.fileservice.dto.FileUploadResponse;
import com.filesharingplatform.fileservice.dto.FileHashVerificationRequest;
import com.filesharingplatform.fileservice.dto.FileVerificationResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.security.NoSuchAlgorithmException;

@RestController
@RequestMapping("/api/files")
@RequiredArgsConstructor
@Slf4j
public class FileController {

    private final FileStorageService fileStorageService;

    /**
     * Health check endpoint.
     */
    @GetMapping("/health")
    public ResponseEntity<?> health() {
        return ResponseEntity.ok().body("File service is running");
    }

    /**
     * Upload a file.
     * 
     * POST /api/files/upload
     * Content-Type: multipart/form-data
     * 
     * Returns: FileUploadResponse with fileId and fileHash
     */
    @PostMapping("/upload")
    public ResponseEntity<FileUploadResponse> uploadFile(
        @RequestParam("file") MultipartFile file
    ) {
        try {
            log.info("Uploading file: {}", file.getOriginalFilename());

            FileUploadResponse response = fileStorageService.uploadFile(file);

            return ResponseEntity.status(HttpStatus.OK).body(response);

        } catch (IllegalArgumentException e) {
            log.warn("Invalid file upload: {}", e.getMessage());
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).build();

        } catch (NoSuchAlgorithmException | IOException e) {
            log.error("Error uploading file", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    /**
     * Download a file by ID.
     * 
     * GET /api/files/download/{fileId}
     * 
     * Returns: File content as binary stream
     */
    @GetMapping("/download/{fileId}")
    public ResponseEntity<?> downloadFile(
        @PathVariable String fileId
    ) {
        try {
            log.info("Downloading file: {}", fileId);

            byte[] fileContent = fileStorageService.downloadFile(fileId);

            String originalFileName = fileStorageService.getFileMetadata(fileId).getOriginalFileName();

            return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + originalFileName + "\"")
                .contentType(MediaType.APPLICATION_OCTET_STREAM)
                .body(fileContent);

        } catch (IllegalArgumentException e) {
            log.warn("File not found: {}", fileId);
            return ResponseEntity.status(HttpStatus.NOT_FOUND).build();

        } catch (IOException e) {
            log.error("Error downloading file: {}", fileId, e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    /**
     * Delete a file by ID (soft delete).
     * 
     * DELETE /api/files/delete/{fileId}
     * 
     * Returns: 204 No Content on success
     */
    @DeleteMapping("/delete/{fileId}")
    public ResponseEntity<?> deleteFile(
        @PathVariable String fileId
    ) {
        try {
            log.info("Deleting file: {}", fileId);

            fileStorageService.deleteFile(fileId);

            return ResponseEntity.status(HttpStatus.NO_CONTENT).build();

        } catch (IllegalArgumentException e) {
            log.warn("File not found for deletion: {}", fileId);
            return ResponseEntity.status(HttpStatus.NOT_FOUND).build();

        } catch (IOException e) {
            log.error("Error deleting file: {}", fileId, e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    /**
     * Verify file integrity.
     * 
     * POST /api/files/verify/{fileId}
     * Content-Type: application/json
     * Body: {"expectedHash": "sha256_hash"}
     * 
     * Returns: FileVerificationResponse with verification result
     */
    @PostMapping("/verify/{fileId}")
    public ResponseEntity<FileVerificationResponse> verifyFile(
        @PathVariable String fileId,
        @RequestBody FileHashVerificationRequest request
    ) {
        try {
            log.info("Verifying file: {}", fileId);

            FileVerificationResponse response = fileStorageService.verifyFile(
                fileId,
                request.getExpectedHash()
            );

            return ResponseEntity.ok().body(response);

        } catch (IllegalArgumentException e) {
            log.warn("File not found for verification: {}", fileId);
            return ResponseEntity.status(HttpStatus.NOT_FOUND).build();

        } catch (NoSuchAlgorithmException | IOException e) {
            log.error("Error verifying file: {}", fileId, e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    /**
     * Check if file exists.
     * 
     * HEAD /api/files/exists/{fileId}
     * 
     * Returns: 200 OK if exists, 404 Not Found otherwise
     */
    @HeadMapping("/exists/{fileId}")
    public ResponseEntity<?> checkFileExists(
        @PathVariable String fileId
    ) {
        boolean exists = fileStorageService.fileExists(fileId);

        return exists ? ResponseEntity.ok().build() : ResponseEntity.notFound().build();
    }
}
