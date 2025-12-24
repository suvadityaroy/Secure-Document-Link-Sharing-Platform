package com.filesharingplatform.fileservice.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

@Component
public class FileStorageConfig {

    @Value("${file.storage.path:/tmp/uploads}")
    private String storagePath;

    public Path getStorageDir() {
        return Paths.get(storagePath);
    }

    public void ensureStorageDir() throws IOException {
        Path storageDir = getStorageDir();
        if (!Files.exists(storageDir)) {
            Files.createDirectories(storageDir);
        }
    }

    public Path getFileFullPath(String fileName) {
        return getStorageDir().resolve(fileName);
    }
}
