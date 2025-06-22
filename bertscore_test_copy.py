import os
import json
from dotenv import load_dotenv
from bert_score import score
from retell import Retell
import re
from typing import List, Dict, Tuple, Optional

# .env 파일에서 환경 변수 로드
load_dotenv()

# 환경 변수에서 RetellApiKey 가져오기
retell_api_key = os.getenv('RetellApiKey')
DEFAULT_LANG = os.getenv("DEFAULT_LANG", "ko")

# Retell API 클라이언트 초기화
client = Retell(api_key=retell_api_key)

def extract_turns_from_transcript(transcript: str) -> List[Tuple[str, str]]:
    """User → Agent 짝으로 응답만 추출"""
    lines = transcript.strip().split('\n')
    pairs = []
    current_question = None

    for line in lines:
        if line.startswith("User:"):
            current_question = line.replace("User:", "").strip()
        elif line.startswith("Agent:") and current_question:
            answer = line.replace("Agent:", "").strip()
            pairs.append((current_question, answer))
            current_question = None  # 다음 User를 기다림

    return pairs

def remove_followup_question(answer: str) -> str:
    """Agent의 응답에서 후속 질문을 제거"""
    followup_patterns = [
        r"(더|추가|자세|혹시|언제든지|필요).*?(궁금|문의|말씀|원하|도와드릴|알려).*?(있으신가요|있을까요|주세요|해 주세요|해주세요|부탁|원하시면|필요하시면)[.!]?",
        r"(궁금한 점|궁금한 사항|문의사항|질문|알고 싶은 점).*?(있으신가요|있을까요|있으시면|있으면|있으시다면|있다면)[.!]?",
        r"(언제든지|필요하시면|추가로|더).*?(문의|연락|말씀|알려).*?(주세요|해 주세요|해주세요)[.!]?",
    ]
    
    sentences = re.split(r'(?<=[.!?])\s+', answer)
    result_sentences = []
    
    for sent in sentences:
        sent_strip = sent.strip()
        if not any(re.search(pattern, sent_strip, re.IGNORECASE) for pattern in followup_patterns):
            result_sentences.append(sent_strip)
            
    return ' '.join(result_sentences).strip()

def get_call_data(call_ids_with_kb: Dict[str, bool]) -> Dict[str, List[Tuple[str, str]]]:
    """
    여러 call ID에서 대화 데이터를 가져옵니다.
    
    Args:
        call_ids_with_kb: {call_id: has_kb} 형태의 딕셔너리
        
    Returns:
        Dictionary: {call_id: [(question, answer), ...]}
    """
    call_data = {}
    
    for call_id, has_kb in call_ids_with_kb.items():
        try:
            # 통화 데이터 가져오기
            call_response = client.call.retrieve(call_id)
            
            # transcript 추출
            transcript = getattr(call_response, 'transcript', "")
            
            if transcript:
                # 대화 턴 추출
                pairs = extract_turns_from_transcript(transcript)
                
                # 후속 질문 제거
                cleaned_pairs = [(q, remove_followup_question(a)) for q, a in pairs]
                
                # KB 유무 정보와 함께 저장
                call_data[call_id] = {
                    'has_kb': has_kb,
                    'pairs': cleaned_pairs
                }
            else:
                print(f"Warning: No transcript found for call ID {call_id}")
                
        except Exception as e:
            print(f"Error retrieving data for call ID {call_id}: {e}")
    
    return call_data

def organize_qa_pairs(call_data: Dict[str, Dict]) -> Dict[str, Dict[str, List[str]]]:
    """
    질문별로 KB 있는 응답과 없는 응답을 정리합니다.
    
    Args:
        call_data: {call_id: {'has_kb': bool, 'pairs': [(question, answer), ...]}}
        
    Returns:
        Dictionary: {question: {'with_kb': [answers], 'without_kb': [answers]}}
    """
    organized_data = {}
    
    # 모든 질문 수집 및 중복 제거
    all_questions = []
    for call_info in call_data.values():
        for q, _ in call_info['pairs']:
            if q not in all_questions:
                all_questions.append(q)
    
    # 각 질문에 대해 KB 있는/없는 응답 분류
    for question in all_questions:
        with_kb_answers = []
        without_kb_answers = []
        
        for call_id, call_info in call_data.items():
            for q, a in call_info['pairs']:
                if q == question:
                    if call_info['has_kb']:
                        with_kb_answers.append(a)
                    else:
                        without_kb_answers.append(a)
        
        organized_data[question] = {
            'with_kb': with_kb_answers,
            'without_kb': without_kb_answers
        }
    
    return organized_data

def calculate_bert_scores(reference_list: List[str], organized_data: Dict[str, Dict[str, List[str]]]) -> None:
    """
    각 질문에 대해 KB 있는/없는 응답의 BERTScore를 계산하고 출력합니다.
    
    Args:
        reference_list: 참조 응답 목록
        organized_data: {question: {'with_kb': [answers], 'without_kb': [answers]}}
    """
    # 질문 목록 (정렬된 상태로)
    questions = list(organized_data.keys())
    
    # 참조 응답 목록 길이 확인
    if len(reference_list) < len(questions):
        print(f"Warning: Reference list has {len(reference_list)} items but there are {len(questions)} questions.")
        # 참조 응답이 부족한 경우 질문 수에 맞게 자름
        questions = questions[:len(reference_list)]
    
    # 각 질문에 대해 BERTScore 계산
    for i, question in enumerate(questions):
        if i >= len(reference_list):
            break
            
        ref = reference_list[i]
        qa_data = organized_data[question]
        
        print(f"\n🧪 케이스 {i+1}")
        print(f"질문: {question}")
        print(f"참조(정답): {ref}")
        
        # KB 없는 응답
        if qa_data['without_kb']:
            for j, answer in enumerate(qa_data['without_kb']):
                P, R, F1 = score([answer], [ref], lang=DEFAULT_LANG)
                print(f"KB 없음 #{j+1} → {answer} | Precision: {P[0]:.4f} | Recall: {R[0]:.4f} | F1: {F1[0]:.4f}")
        else:
            print("KB 없는 응답이 없습니다.")
        
        # KB 있는 응답
        if qa_data['with_kb']:
            for j, answer in enumerate(qa_data['with_kb']):
                P, R, F1 = score([answer], [ref], lang=DEFAULT_LANG)
                print(f"KB 있음 #{j+1} → {answer} | Precision: {P[0]:.4f} | Recall: {R[0]:.4f} | F1: {F1[0]:.4f}")
        else:
            print("KB 있는 응답이 없습니다.")

def main():
    # call ID와 KB 유무를 명시적으로 지정
    call_ids_with_kb = {
        "call_7254a3f03e8cea191a91c9641d0": True,   # KB 있는 통화
        "call_82aeddf48f532fb260ce4f4ae1a": False,  # KB 없는 통화
        # 추가 call ID들...
    }
    
    # 통화 데이터 가져오기
    call_data = get_call_data(call_ids_with_kb)
    
    # 질문별로 KB 있는/없는 응답 정리
    organized_data = organize_qa_pairs(call_data)
    
    # 참조 응답 목록 (예시)
    reference = [
        "AI 포트폴리오 리포트는 고객님의 투자 내역과 시장 데이터를 기반으로 자산 배분, 수익률, 리스크를 자동 분석해주는 기능입니다. 매주 금요일 업데이트되며, '마이 자산 > AI 리포트'에서 확인하실 수 있습니다.",
        # ... 나머지 참조 응답들
    ]
    
    # BERTScore 계산 및 출력
    calculate_bert_scores(reference, organized_data)

if __name__ == "__main__":
    main()
