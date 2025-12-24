package com.filesharingplatform.fileservice.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class FileUploadResponse {

    private String fileId;
    private String fileName;
    private Long fileSize;
    private String fileHash;
    private String message;
}
