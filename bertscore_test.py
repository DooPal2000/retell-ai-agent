# bertscore_eval.py

# import os
# import json
# from dotenv import load_dotenv
# from bert_score import score

# # .env 파일 로드
# load_dotenv()
# # 환경 변수에서 RetellApiKey 값 가져오기
# retell_api_key = os.getenv('RetellApiKey')

# # 이제 retell_api_key를 코드에서 사용할 수 있습니다
# print(retell_api_key)  # 테스트용 출력

# # (선택) TypeScript 프로젝트에서 설정한 환경 변수 예시
# DEFAULT_LANG = os.getenv("DEFAULT_LANG", "ko")  # 없으면 'ko'로 기본 설정


# def extract_turns_from_transcript(transcript: str):
#     """User → Agent 짝으로 응답만 추출"""
#     lines = transcript.strip().split('\n')
#     pairs = []
#     current_question = None

#     for line in lines:
#         if line.startswith("User:"):
#             current_question = line.replace("User:", "").strip()
#         elif line.startswith("Agent:") and current_question:
#             answer = line.replace("Agent:", "").strip()
#             pairs.append((current_question, answer))
#             current_question = None  # 다음 User를 기다림

#     return pairs  # 리스트: [(질문, 응답), ...]


# # === 입력 ===
# reference = ["고객님의 계좌에는 현재 100,000원이 있습니다."]
# candidate_a = ["고객님 계좌 잔액은 10만원입니다."]   # KB 없는 응답
# candidate_b = ["현재 고객님의 계좌에는 100,000원이 있습니다."]  # KB 있는 응답

# # === BERTScore 계산 ===
# P_a, R_a, F1_a = score(candidate_a, reference, lang=DEFAULT_LANG)
# P_b, R_b, F1_b = score(candidate_b, reference, lang=DEFAULT_LANG)

# # === 출력 ===
# print(" -->  KB 없음:")
# print(f"Precision: {P_a[0]:.4f}, Recall: {R_a[0]:.4f}, F1: {F1_a[0]:.4f}")

# print("\n -->  KB 있음:")
# print(f"Precision: {P_b[0]:.4f}, Recall: {R_b[0]:.4f}, F1: {F1_b[0]:.4f}")

import os
import json
from dotenv import load_dotenv
from bert_score import score
from retell import Retell

# .env 파일에서 환경 변수 로드
load_dotenv()

# 환경 변수에서 RetellApiKey 가져오기
retell_api_key = os.getenv('RetellApiKey')
DEFAULT_LANG = os.getenv("DEFAULT_LANG", "ko")

# Retell API 클라이언트 초기화
client = Retell(api_key=retell_api_key)

# Transcripts 데이터를 가져오는 예시 (ID는 하드코딩)
call_res_kb = client.call.retrieve("call_2dd7f08d415ca29069eaf15f54a")
call_res_general = client.call.retrieve("call_82aeddf48f532fb260ce4f4ae1a")

# call_response에서 'transcript' 추출
transcript_kb = getattr(call_res_kb, 'transcript', "")  # 'transcript' 속성 접근
transcript_general = getattr(call_res_general, 'transcript', "")  # 'transcript' 속성 접근
# print(transcript_kb)
# print(transcript_general)

# extract_turns_from_transcript 함수 예시로, 데이터에서 대화 턴 추출
def extract_turns_from_transcript(transcript: str):
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

    return pairs  # 리스트: [(질문, 응답), ...]

# 대화 턴 추출
pairs_kb = extract_turns_from_transcript(transcript_kb)
pairs_general = extract_turns_from_transcript(transcript_general)

# # 비교를 위한 참조 응답 및 후보 응답 리스트 
# reference = ["..."]
# candidate_kb = [""]  # KB 포함 응답
# candidate_general = [""]  # KB 없는 응답

# 응답 리스트 생성
# 미나리 고객센터 전용 질문 (50%)
reference = [
    "AI 포트폴리오 리포트는 고객님의 투자 내역과 시장 데이터를 기반으로 자산 배분, 수익률, 리스크를 자동 분석해주는 기능입니다. 매주 금요일 업데이트되며, '마이 자산 > AI 리포트'에서 확인하실 수 있습니다.",
    "미나리 에셋의 자체 알고리즘이 과도한 집중 투자나 수익 편차가 큰 경우를 감지하여 월 1회 기준으로 리밸런싱 타이밍을 제안합니다.",
    "최근 6개월 내 평균 자산 5천만 원 이상 고객님께 부여되는 등급입니다. 전용 리서치 리포트(월 2회), 리밸런싱 전화 컨설팅 연 2회, 수수료 우대 ETF 목록 접근권, 세미나 우선 초대 등 혜택이 제공됩니다.",
    "네. ‘미나리 ESG 글로벌 ETF랩’, ‘AI 로보랩 2호’와 같은 상품은 미나리 에셋에서만 가입 가능합니다. 전용 상품 페이지를 통해 신청할 수 있습니다.",
    "가능합니다. 미나리GO 앱에서는 해외 주식 거래 내역을 바탕으로 연간 예상 양도소득세를 자동 추정해 드립니다. 해당 리포트는 12월 말 기준 산출되어 ‘세금 리포트’ 메뉴에서 다운로드하실 수 있습니다.",
    "연금납입 증명서, 해외주식 양도소득 리포트, 환급 내역 증명서 등을 PDF 또는 XML 형식으로 바로 내려받을 수 있습니다.",
    "미나리GO 앱에서 '세금 리포트' 메뉴에 들어가시면 연금납입 증명서를 다운로드할 수 있습니다. 이메일 또는 SMS로도 발송 가능합니다.",
    "상담 중 미나리GO 앱을 통해 본인 인증 알림이 발송됩니다. 고객님이 해당 알림을 수락하시면 비밀번호 입력 없이 인증이 완료됩니다.",
    "전화상담 중 요청해 주시면 고객센터 상담원이 실시간으로 전자 서명을 통한 처리 절차를 도와드립니다. 필요한 서류는 문자나 이메일로 보내드립니다.",
    "미나리 고객센터에서는 미나리 전용 상품에 대한 상담과 개인화된 투자 전략에 대해 안내해 드립니다. 특히 AI 포트폴리오 리포트와 관련된 상담을 받을 수 있습니다."
]

# 일반 금융 질문 (50%)
reference += [
    "미나리GO 앱을 통해 비대면으로 5분 안에 계좌 개설을 완료하실 수 있습니다. 신분증만 준비해 주세요.",
    "온라인으로 직접 주문하시면 0.015%의 낮은 수수료가 적용됩니다.",
    "모든 투자는 원금 손실 가능성이 있으며, 고객님의 투자 성향에 맞춰 안내드리고 있습니다.",
    "로보어드바이저가 고객님의 위험 성향과 투자 목표를 분석해 최적의 포트폴리오를 추천합니다.",
    "연금 상품은 크게 개인연금, 퇴직연금, 연금보험으로 나뉩니다. 고객님의 연금 필요에 맞는 상품을 추천해드리겠습니다.",
    "펀드의 수수료는 상품에 따라 다르며, 보통 0.5%에서 1.5% 사이입니다. 직접 펀드를 선택하시면 수수료율을 확인할 수 있습니다.",
    "ETF는 상장된 펀드로, 주식처럼 실시간 거래가 가능하며 낮은 수수료가 특징입니다. 반면, 펀드는 펀드 매니저가 운용하고 수수료가 상대적으로 높습니다.",
    "해외 주식에서 발생한 양도소득은 1년에 한 번 종합적으로 세금이 부과됩니다. 250만 원을 초과하면 22%의 세금이 부과됩니다.",
    "연금 이연과세는 납입한 금액에 대해 세금이 이연되어, 연금을 받을 때 세금을 내는 방식입니다. 이를 통해 납입 시 세금 혜택을 받을 수 있습니다.",
    "세금 혜택을 제공하는 상품으로는 연금저축계좌(연금저축펀드), 퇴직연금 계좌 등이 있습니다. 해당 상품들은 세액공제를 받을 수 있는 혜택이 있습니다."
]

# 기타 질문들
reference += [
    "자산 배분은 고객님의 위험 성향과 목표에 맞춰야 합니다. 일반적으로 주식, 채권, 현금을 일정 비율로 배분하여 리스크를 분산하는 것이 좋습니다.",
    "ETF는 자산을 실제로 보유하는 반면, ETN은 증권사의 부채에 해당하는 금융상품입니다. ETF는 자산에 직접 투자, ETN은 추적 지수에 대한 계약입니다.",
    "연금저축펀드나 IRP(Individual Retirement Pension)는 세액공제 혜택을 제공하는 상품입니다. 이를 통해 세액 공제 혜택을 받을 수 있습니다.",
    "펀드는 투자자들이 돈을 모아 전문가가 다양한 자산에 분산 투자하는 금융 상품입니다. 주식, 채권 등 다양한 자산군에 투자할 수 있습니다.",
    "해외주식에서 발생한 양도소득은 세무서에 신고해야 하며, 미나리GO 앱에서 세금 리포트를 통해 자동으로 계산된 세액을 확인할 수 있습니다."
]

# # 결과: reference 리스트가 이제 모든 응답을 포함한 상태입니다.
# print(reference)

candidate_kb = [answer for _, answer in pairs_kb]
candidate_general = [answer for _, answer in pairs_general]

# 리스트 길이 맞추기
min_len = min(len(reference), len(candidate_kb), len(candidate_general))
reference = reference[:min_len]
candidate_kb = candidate_kb[:min_len]
candidate_general = candidate_general[:min_len]


# BERTScore 계산 및 출력
# for i, ref in enumerate(reference):
#     P_a, R_a, F1_a = score([candidate_general[i]], [ref], lang=DEFAULT_LANG)
#     P_b, R_b, F1_b = score([candidate_kb[i]], [ref], lang=DEFAULT_LANG)

#     print(f"\n🧪 케이스 {i+1}")
#     print(f"KB 없음 → F1: {F1_a[0]:.4f}")
#     print(f"KB 있음 → F1: {F1_b[0]:.4f}")

for i, ref in enumerate(reference):
    # 각 turn별로 BERTScore 계산
    P_a, R_a, F1_a = score([candidate_general[i]], [ref], lang=DEFAULT_LANG)
    P_b, R_b, F1_b = score([candidate_kb[i]], [ref], lang=DEFAULT_LANG)


    print(f"\n🧪 케이스 {i+1}")
    print(f"질문: {pairs_kb[i][0]}")
    print(f"참조(정답): {ref}")
    print(f"KB 없음 → {candidate_general[i]} | Precision: {P_a[0]:.4f} | Recall: {R_a[0]:.4f} | F1: {F1_a[0]:.4f}")
    print(f"KB 있음 → {candidate_kb[i]} | Precision: {P_b[0]:.4f} | Recall: {R_b[0]:.4f} | F1: {F1_b[0]:.4f}")






















# 여기 30가지 질문과 그에 대한 응답을 한국어로 정리해보았습니다. **50%는 미나리 고객센터 전용 질문**이고, 나머지 **50%는 일반적인 금융 질문**입니다. 질문과 응답을 따로 묶어서 제공했습니다.

# ### 1. **미나리 고객센터 전용 질문 (50%)**

# ### 1.1. **Q:** 미나리GO 앱에서 제공하는 ‘AI 포트폴리오 리포트’는 무엇인가요?

# **A:** AI 포트폴리오 리포트는 고객님의 투자 내역과 시장 데이터를 기반으로 자산 배분, 수익률, 리스크를 자동 분석해주는 기능입니다. 매주 금요일 업데이트되며, '마이 자산 > AI 리포트'에서 확인하실 수 있습니다.

# ### 1.2. **Q:** 리밸런싱 추천은 어떻게 이루어지나요?

# **A:** 미나리 에셋의 자체 알고리즘이 과도한 집중 투자나 수익 편차가 큰 경우를 감지하여 월 1회 기준으로 리밸런싱 타이밍을 제안합니다.

# ### 1.3. **Q:** 미나리 클럽 회원 혜택은 무엇인가요?

# **A:** 최근 6개월 내 평균 자산 5천만 원 이상 고객님께 부여되는 등급입니다. 전용 리서치 리포트(월 2회), 리밸런싱 전화 컨설팅 연 2회, 수수료 우대 ETF 목록 접근권, 세미나 우선 초대 등 혜택이 제공됩니다.

# ### 1.4. **Q:** 미나리 전용 상품이 따로 있나요?

# **A:** 네. ‘미나리 ESG 글로벌 ETF랩’, ‘AI 로보랩 2호’와 같은 상품은 미나리 에셋에서만 가입 가능합니다. 전용 상품 페이지를 통해 신청할 수 있습니다.

# ### 1.5. **Q:** 해외 주식 세금 계산이 가능한가요?

# **A:** 가능합니다. 미나리GO 앱에서는 해외 주식 거래 내역을 바탕으로 연간 예상 양도소득세를 자동 추정해 드립니다. 해당 리포트는 12월 말 기준 산출되어 ‘세금 리포트’ 메뉴에서 다운로드하실 수 있습니다.

# ### 1.6. **Q:** 세무서 제출용 문서는 어디서 받을 수 있나요?

# **A:** 연금납입 증명서, 해외주식 양도소득 리포트, 환급 내역 증명서 등을 PDF 또는 XML 형식으로 바로 내려받을 수 있습니다.

# ### 1.7. **Q:** 미나리GO에서 연금납입 증명서는 어떻게 받을 수 있나요?

# **A:** 미나리GO 앱에서 '세금 리포트' 메뉴에 들어가시면 연금납입 증명서를 다운로드할 수 있습니다. 이메일 또는 SMS로도 발송 가능합니다.

# ### 1.8. **Q:** 고객 상담 중 본인 인증은 어떻게 하나요?

# **A:** 상담 중 미나리GO 앱을 통해 본인 인증 알림이 발송됩니다. 고객님이 해당 알림을 수락하시면 비밀번호 입력 없이 인증이 완료됩니다.

# ### 1.9. **Q:** 주소 변경이나 연금 계좌 통합을 하려면 어떻게 해야 하나요?

# **A:** 전화상담 중 요청해 주시면 고객센터 상담원이 실시간으로 전자 서명을 통한 처리 절차를 도와드립니다. 필요한 서류는 문자나 이메일로 보내드립니다.

# ### 1.10. **Q:** 미나리 고객센터에서는 어떤 금융 상품에 대한 상세한 상담을 받을 수 있나요?

# **A:** 미나리 고객센터에서는 미나리 전용 상품에 대한 상담과 개인화된 투자 전략에 대해 안내해 드립니다. 특히 AI 포트폴리오 리포트와 관련된 상담을 받을 수 있습니다.

# ---

# ### 2. **일반 금융 질문 (50%)**

# ### 2.1. **Q:** 계좌 개설은 어떻게 하나요?

# **A:** 미나리GO 앱을 통해 비대면으로 5분 안에 계좌 개설을 완료하실 수 있습니다. 신분증만 준비해 주세요.

# ### 2.2. **Q:**수수료는 얼마인가요?

# **A:** 온라인으로 직접 주문하시면 0.015%의 낮은 수수료가 적용됩니다.

# ### 2.3. **Q:** 투자 손실도 발생하나요?

# **A:** 모든 투자는 원금 손실 가능성이 있으며, 고객님의 투자 성향에 맞춰 안내드리고 있습니다.

# ### 2.4. **Q:** 맞춤형 포트폴리오는 어떻게 구성되나요?

# **A:** 로보어드바이저가 고객님의 위험 성향과 투자 목표를 분석해 최적의 포트폴리오를 추천합니다.

# ### 2.5. **Q:** 투자에 적합한 연금 상품은 무엇인가요?

# **A:** 연금 상품은 크게 개인연금, 퇴직연금, 연금보험으로 나뉩니다. 고객님의 연금 필요에 맞는 상품을 추천해드리겠습니다.

# ### 2.6. **Q:** 펀드 수수료는 어떻게 되나요?

# **A:** 펀드의 수수료는 상품에 따라 다르며, 보통 0.5%에서 1.5% 사이입니다. 직접 펀드를 선택하시면 수수료율을 확인할 수 있습니다.

# ### 2.7. **Q:** ETF 투자와 펀드 투자 차이는 무엇인가요?

# **A:** ETF는 상장된 펀드로, 주식처럼 실시간 거래가 가능하며 낮은 수수료가 특징입니다. 반면, 펀드는 펀드 매니저가 운용하고 수수료가 상대적으로 높습니다.

# ### 2.8. **Q:** 해외 주식 투자 시 세금은 어떻게 부과되나요?

# **A:** 해외 주식에서 발생한 양도소득은 1년에 한 번 종합적으로 세금이 부과됩니다. 250만 원을 초과하면 22%의 세금이 부과됩니다.

# ### 2.9. **Q:** 연금 이연과세가 무엇인가요?

# **A:** 연금 이연과세는 납입한 금액에 대해 세금이 이연되어, 연금을 받을 때 세금을 내는 방식입니다. 이를 통해 납입 시 세금 혜택을 받을 수 있습니다.

# ### 2.10. **Q:** 세금 혜택이 큰 투자 상품은 무엇인가요?

# **A:** 세금 혜택을 제공하는 상품으로는 연금저축계좌(연금저축펀드), 퇴직연금 계좌 등이 있습니다. 해당 상품들은 세액공제를 받을 수 있는 혜택이 있습니다.

# ---

# ### 3. **기타 질문들**

# ### 3.1. **Q:** 투자할 때 적정 비율로 자산 배분을 어떻게 해야 하나요?

# **A:** 자산 배분은 고객님의 위험 성향과 목표에 맞춰야 합니다. 일반적으로 주식, 채권, 현금을 일정 비율로 배분하여 리스크를 분산하는 것이 좋습니다.

# ### 3.2. **Q:** ETF와 ETN의 차이는 무엇인가요?

# **A:** ETF는 자산을 실제로 보유하는 반면, ETN은 증권사의 부채에 해당하는 금융상품입니다. ETF는 자산에 직접 투자, ETN은 추적 지수에 대한 계약입니다.

# ### 3.3. **Q:** 세금 공제 혜택이 큰 연금 상품은 무엇인가요?

# **A:** 연금저축펀드나 IRP(Individual Retirement Pension)는 세액공제 혜택을 제공하는 상품입니다. 이를 통해 세액 공제 혜택을 받을 수 있습니다.

# ### 3.4. **Q:** 펀드가 무엇인가요?

# **A:** 펀드는 투자자들이 돈을 모아 전문가가 다양한 자산에 분산 투자하는 금융 상품입니다. 주식, 채권 등 다양한 자산군에 투자할 수 있습니다.

# ### 3.5. **Q:** 해외주식의 세금은 어떻게 신고하나요?

# **A:** 해외주식에서 발생한 양도소득은 세무서에 신고해야 하며, 미나리GO 앱에서 세금 리포트를 통해 자동으로 계산된 세액을 확인할 수 있습니다.
