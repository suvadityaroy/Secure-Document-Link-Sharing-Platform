package com.filesharingplatform.fileservice.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class FileVerificationResponse {

    private String fileId;
    private String originalFileName;
    private Boolean verified;
    private String message;
}
