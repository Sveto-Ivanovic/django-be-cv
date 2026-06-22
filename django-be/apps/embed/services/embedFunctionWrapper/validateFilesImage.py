
def validate_files_image(files):
    """
    Validate uploaded files for image embedding.
    Ensures that each file is an image and meets size requirements.
    """
    if not files:
        raise ValueError("No files provided for embedding.")
    
    for file_key, file in files.items():
        if not file.content_type.startswith('image/'):
            raise ValueError(f"File {file.name} is not a valid image.")
        
        if file.size > 4 * 1024 * 1024:  # Example size limit of 4MB
            raise ValueError(f"File {file.name} exceeds size limit of 4MB.")
    
    return True