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

def get_call_data(call_ids_with_kb: Dict[str, bool]) -> Dict[str, Dict]:
    """
    여러 call ID에서 대화 데이터를 가져옵니다.
    
    Args:
        call_ids_with_kb: {call_id: has_kb} 형태의 딕셔너리
        
    Returns:
        Dictionary: {call_id: {'has_kb': bool, 'pairs': [(question, answer), ...]}}
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

def organize_qa_pairs_by_order(call_data: Dict[str, Dict]) -> Dict[int, Dict[str, List[Tuple[str, str]]]]:
    """
    순서별로 KB 있는 응답과 없는 응답을 정리합니다.
    
    Args:
        call_data: {call_id: {'has_kb': bool, 'pairs': [(question, answer), ...]}}
        
    Returns:
        Dictionary: {index: {'with_kb': [(question, answer)], 'without_kb': [(question, answer)]}}
    """
    organized_data = {}
    
    # 각 call_id별 최대 질문 수 확인
    max_questions = max([len(call_info['pairs']) for call_info in call_data.values()])
    
    # 각 인덱스(순서)별로 KB 있는/없는 응답 분류
    for i in range(max_questions):
        with_kb_qa_pairs = []
        without_kb_qa_pairs = []
        
        for call_id, call_info in call_data.items():
            pairs = call_info['pairs']
            if i < len(pairs):
                if call_info['has_kb']:
                    with_kb_qa_pairs.append(pairs[i])
                else:
                    without_kb_qa_pairs.append(pairs[i])
        
        organized_data[i] = {
            'with_kb': with_kb_qa_pairs,
            'without_kb': without_kb_qa_pairs
        }
    
    return organized_data

def calculate_bert_scores_by_order(reference_list: List[str], organized_data: Dict[int, Dict[str, List[Tuple[str, str]]]]) -> None:
    """
    순서별로 KB 있는/없는 응답의 BERTScore를 계산하고 출력합니다.
    
    Args:
        reference_list: 참조 응답 목록
        organized_data: {index: {'with_kb': [(question, answer)], 'without_kb': [(question, answer)]}}
    """
    # 참조 응답 목록 길이 확인
    max_index = max(organized_data.keys())
    if len(reference_list) < max_index + 1:
        print(f"Warning: Reference list has {len(reference_list)} items but there are {max_index + 1} question indices.")
        max_index = len(reference_list) - 1
    
    # 각 순서에 대해 BERTScore 계산
    for i in range(max_index + 1):
        if i >= len(reference_list):
            break
            
        ref = reference_list[i]
        qa_data = organized_data[i]
        
        print(f"\n🧪 케이스 {i+1}")
        
        # KB 없는 응답
        if qa_data['without_kb']:
            for j, (question, answer) in enumerate(qa_data['without_kb']):
                P, R, F1 = score([answer], [ref], lang=DEFAULT_LANG)
                print(f"질문(KB 없음 #{j+1}): {question}")
                print(f"참조(정답): {ref}")
                print(f"KB 없음 #{j+1} → {answer} | Precision: {P[0]:.4f} | Recall: {R[0]:.4f} | F1: {F1[0]:.4f}")
        else:
            print("KB 없는 응답이 없습니다.")
        
        # KB 있는 응답
        if qa_data['with_kb']:
            for j, (question, answer) in enumerate(qa_data['with_kb']):
                P, R, F1 = score([answer], [ref], lang=DEFAULT_LANG)
                print(f"질문(KB 있음 #{j+1}): {question}")
                print(f"참조(정답): {ref}")
                print(f"KB 있음 #{j+1} → {answer} | Precision: {P[0]:.4f} | Recall: {R[0]:.4f} | F1: {F1[0]:.4f}")
        else:
            print("KB 있는 응답이 없습니다.")

def main():
    # call ID와 KB 유무를 명시적으로 지정
    call_ids_with_kb = {
        "call_3d748d827d9ee1fe5de77c01601": True,   # KB 있는 통화
        "call_451943b6132144a0a3765da70be": False,  # KB 없는 통화
        # 추가 call ID들...
    }
    
    # 통화 데이터 가져오기
    call_data = get_call_data(call_ids_with_kb)
    
    # 순서별로 KB 있는/없는 응답 정리
    organized_data = organize_qa_pairs_by_order(call_data)
    
    # 참조 응답 목록
    reference = [
        "AI 포트폴리오 리포트는 고객님의 투자 내역과 시장 데이터를 기반으로 자산 배분, 수익률, 리스크를 자동 분석해주는 기능입니다. 매주 금요일 업데이트되며, '마이 자산 > AI 리포트'에서 확인하실 수 있습니다.",
        "미나리 에셋의 자체 알고리즘이 과도한 집중 투자나 수익 편차가 큰 경우를 감지하여 월 1회 기준으로 리밸런싱 타이밍을 제안합니다.",
        "최근 6개월 내 평균 자산 5천만 원 이상 고객님께 부여되는 등급입니다. 전용 리서치 리포트(월 2회), 리밸런싱 전화 컨설팅 연 2회, 수수료 우대 ETF 목록 접근권, 세미나 우선 초대 등 혜택이 제공됩니다.",
        "네. '미나리 ESG 글로벌 ETF랩', 'AI 로보랩 2호'와 같은 상품은 미나리 에셋에서만 가입 가능합니다. 전용 상품 페이지를 통해 신청할 수 있습니다.",
        "가능합니다. 미나리GO 앱에서는 해외 주식 거래 내역을 바탕으로 연간 예상 양도소득세를 자동 추정해 드립니다. 해당 리포트는 12월 말 기준 산출되어 '세금 리포트' 메뉴에서 다운로드하실 수 있습니다.",
        "연금납입 증명서, 해외주식 양도소득 리포트, 환급 내역 증명서 등을 PDF 또는 XML 형식으로 바로 내려받을 수 있습니다.",
        "미나리GO 앱에서 '세금 리포트' 메뉴에 들어가시면 연금납입 증명서를 다운로드할 수 있습니다. 이메일 또는 SMS로도 발송 가능합니다.",
        "상담 중 미나리GO 앱을 통해 본인 인증 알림이 발송됩니다. 고객님이 해당 알림을 수락하시면 비밀번호 입력 없이 인증이 완료됩니다.",
        "전화상담 중 요청해 주시면 고객센터 상담원이 실시간으로 전자 서명을 통한 처리 절차를 도와드립니다. 필요한 서류는 문자나 이메일로 보내드립니다.",
        "미나리 고객센터에서는 미나리 전용 상품에 대한 상담과 개인화된 투자 전략에 대해 안내해 드립니다. 특히 AI 포트폴리오 리포트와 관련된 상담을 받을 수 있습니다.",
        "미나리GO 앱을 통해 비대면으로 5분 안에 계좌 개설을 완료하실 수 있습니다. 신분증만 준비해 주세요.",
        "온라인으로 직접 주문하시면 0.015%의 낮은 수수료가 적용됩니다.",
        "모든 투자는 원금 손실 가능성이 있으며, 고객님의 투자 성향에 맞춰 안내드리고 있습니다.",
        "로보어드바이저가 고객님의 위험 성향과 투자 목표를 분석해 최적의 포트폴리오를 추천합니다.",
        "연금 상품은 크게 개인연금, 퇴직연금, 연금보험으로 나뉩니다. 고객님의 연금 필요에 맞는 상품을 추천해드리겠습니다.",
        "펀드의 수수료는 상품에 따라 다르며, 보통 0.5%에서 1.5% 사이입니다. 직접 펀드를 선택하시면 수수료율을 확인할 수 있습니다.",
        "ETF는 상장된 펀드로, 주식처럼 실시간 거래가 가능하며 낮은 수수료가 특징입니다. 반면, 펀드는 펀드 매니저가 운용하고 수수료가 상대적으로 높습니다.",
        "해외 주식에서 발생한 양도소득은 1년에 한 번 종합적으로 세금이 부과됩니다. 250만 원을 초과하면 22%의 세금이 부과됩니다.",
        "연금 이연과세는 납입한 금액에 대해 세금이 이연되어, 연금을 받을 때 세금을 내는 방식입니다. 이를 통해 납입 시 세금 혜택을 받을 수 있습니다.",
        "세금 혜택을 제공하는 상품으로는 연금저축계좌(연금저축펀드), 퇴직연금 계좌 등이 있습니다. 해당 상품들은 세액공제를 받을 수 있는 혜택이 있습니다.",
        "자산 배분은 고객님의 위험 성향과 목표에 맞춰야 합니다. 일반적으로 주식, 채권, 현금을 일정 비율로 배분하여 리스크를 분산하는 것이 좋습니다.",
        "ETF는 자산을 실제로 보유하는 반면, ETN은 증권사의 부채에 해당하는 금융상품입니다. ETF는 자산에 직접 투자, ETN은 추적 지수에 대한 계약입니다.",
        "연금저축펀드나 IRP(Individual Retirement Pension)는 세액공제 혜택을 제공하는 상품입니다. 이를 통해 세액 공제 혜택을 받을 수 있습니다.",
        "펀드는 투자자들이 돈을 모아 전문가가 다양한 자산에 분산 투자하는 금융 상품입니다. 주식, 채권 등 다양한 자산군에 투자할 수 있습니다.",
        "해외주식에서 발생한 양도소득은 세무서에 신고해야 하며, 미나리GO 앱에서 세금 리포트를 통해 자동으로 계산된 세액을 확인할 수 있습니다."
    ]
    
    # BERTScore 계산 및 출력
    calculate_bert_scores_by_order(reference, organized_data)

if __name__ == "__main__":
    main()
