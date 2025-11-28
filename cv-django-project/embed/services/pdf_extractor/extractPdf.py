import base64
import fitz  
from PIL import Image
import io
import pdfplumber
from langchain_text_splitters import RecursiveCharacterTextSplitter



def extract_pdf_content(pdf_stream, pdf_file_name: str, chunk_size: int = 1200, overlap: int = 200):
    """Extract text and images from a PDF stream using pdfplumber and PyMuPDF."""
    try:

        text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=chunk_size,
                    chunk_overlap=overlap,
                    length_function=len,
                    separators=["\n\n","\n"," ",".",","])
        
        doc = fitz.open(stream=pdf_stream, filetype="pdf")
        len_of_doc = len(doc)

        results_texts=[]
        results_images=[]
        with pdfplumber.open(pdf_stream) as pdf:

            if len_of_doc != len(pdf.pages):
                raise ValueError("Number of pages fetched via pdfplumber and fitz don't match.")

            # Go through each page and extract text and images
            for i in range(len_of_doc):

                # Extract text using pdfplumber
                text = pdf.pages[i].extract_text(layout=True)

                if len(text)>chunk_size:

                    text = text_splitter.split_text(text)

                    for j, chunk in enumerate(text):
                        results_texts.append({
                            "page": i+1,
                            "text": chunk,
                            "chunk_index": j,
                            "source": pdf_file_name,
                            "file_type": "pdf",      
                            "type_of_flow":"text"                    
                        })

                else:
                    results_texts.append({
                        "page": i+1,
                        "text": text,
                        "source": pdf_file_name,
                        "file_type": "pdf",
                        "type_of_flow":"text"
                    })

                # Extract images using PyMuPDF
                doc_page = doc[i]
                for img in doc_page.get_images(full=True):
                    base = doc.extract_image(img[0])
                    
                    ext = base["ext"]
                    image_type = f"image/{ext}"
                    img_base64 = base64.b64encode(base["image"]).decode('utf-8')
                    results_images.append({
                        "ext": image_type,
                        "base64_str": f"data:{image_type};base64,{img_base64}",
                        "page": i+1,
                        "source": pdf_file_name,
                        "file_type": "pdf",
                        "type_of_flow":"image"
                    })
        return results_texts, results_images
    
    except Exception as e:
        raise ValueError(f"Error extracting content from PDF {pdf_file_name}: {str(e)}")
    

def extract_pdf_content_with_metadata(pdf_stream, pdf_file_name: str, chunk_size: int, overlap: int, input_metadata: dict):
    """Extract text and images from a PDF stream using pdfplumber and PyMuPDF. With metadata support."""
    try:

        text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=chunk_size,
                    chunk_overlap=overlap,
                    length_function=len,
                    separators=["\n\n","\n"," ",".",","])
        
        doc = fitz.open(stream=pdf_stream, filetype="pdf")
        len_of_doc = len(doc)

        results_texts=[]
        results_images=[]
        with pdfplumber.open(pdf_stream) as pdf:

            if len_of_doc != len(pdf.pages):
                raise ValueError("Number of pages fetched via pdfplumber and fitz don't match.")

            # Go through each page and extract text and images
            for i in range(len_of_doc):

                # Extract text using pdfplumber
                text = pdf.pages[i].extract_text(layout=True)

                if len(text)>chunk_size:

                    text = text_splitter.split_text(text)

                    for j, chunk in enumerate(text):
                        results_texts.append({
                            "page": i+1,
                            "text": chunk,
                            "chunk_index": j,
                            "source": pdf_file_name,
                            "file_type": "pdf",
                            "type_of_flow":"text",
                            **input_metadata                            
                        })

                else:
                    results_texts.append({
                        "page": i+1,
                        "text": text,
                        "source": pdf_file_name,
                        "file_type": "pdf",
                        "type_of_flow":"text",
                        **input_metadata
                    })

                # Extract images using PyMuPDF
                doc_page = doc[i]
                for img in doc_page.get_images(full=True):
                    base = doc.extract_image(img[0])
                    ext = base["ext"]
                    image_type = f"image/{ext}"
                    img_base64 = base64.b64encode(base["image"]).decode('utf-8')
                    results_images.append({
                        "ext": image_type,
                        "base64_str": f"data:{image_type};base64,{img_base64}",
                        "page": i+1,
                        "source": pdf_file_name,
                        "file_type": "pdf",
                        "type_of_flow":"image",
                        **input_metadata
                    })
        return results_texts, results_images
    
    except Exception as e:
        raise ValueError(f"Error extracting content from PDF {pdf_file_name}: {str(e)}")