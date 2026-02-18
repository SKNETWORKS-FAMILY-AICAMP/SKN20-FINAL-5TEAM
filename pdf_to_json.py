import pdfplumber
import json
import os

def pdf_to_json(pdf_path, json_path):
    """
    PDF 파일에서 텍스트를 추출하여 JSON 형식으로 저장합니다.
    수정일: 2026-02-17
    수정내용: vLLM 논문 PDF 크롤링 및 JSON 변환 기능 초기 구현
    """
    data = {
        "title": "vLLM: Easy, Fast, and Cheap LLM Serving with PagedAttention",
        "file_name": os.path.basename(pdf_path),
        "pages": []
    }

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                data["pages"].append({
                    "page_number": i + 1,
                    "content": text if text else ""
                })
        
        # output 디렉토리가 없으면 생성
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        print(f"성공: {pdf_path}에서 텍스트를 추출하여 {json_path}에 저장했습니다.")
        return True
    except Exception as e:
        print(f"오류 발생: {e}")
        return False

if __name__ == "__main__":
    PDF_FILE = "2309.06180v1.pdf"
    JSON_OUTPUT = "output/vllm_paper_extracted.json"
    
    pdf_to_json(PDF_FILE, JSON_OUTPUT)
