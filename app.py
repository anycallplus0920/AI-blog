# -*- coding: utf-8 -*-
import streamlit as st
import random
import requests
from bs4 import BeautifulSoup

# 페이지 설정
st.set_page_config(page_title="블로그 AI: 인간적인 도입부 적용", page_icon="🗣️", layout="wide")

# --- [기능 1] 네이버 블로그 스크래핑 ---
def scrape_naver_blogs(urls_text):
    if not urls_text: return ""
    url_list = [url.strip() for url in urls_text.split('\n') if url.strip()][:5]
    combined_content = ""
    for i, url in enumerate(url_list):
        try:
            if "m.blog.naver.com" not in url: url = url.replace("blog.naver.com", "m.blog.naver.com")
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text(separator=' ', strip=True)
            if len(text) > 800: text = text[:800] + "..."
            combined_content += f"\n[참고{i+1}]: {text}\n"
        except: pass
    return combined_content

# --- [기능 2] 글 전개 패턴 (구조) ---
def get_structure_pattern():
    patterns = [
        "A타입 (직설형): 결론(완료 사진)부터 보여주고, 역순으로 과정 풀기",
        "B타입 (스토리형): 현장의 문제 상황 묘사로 시작해 해결하는 과정",
        "C타입 (비교형): 작업 전(Before) vs 후(After) 비교 위주",
        "D타입 (정보형): 기술적 원리와 관리 팁을 섞어서 설명"
    ]
    return random.choice(patterns)

# --- [기능 3] ★도입부(인사말) 스타일 랜덤 생성 (NEW)★ ---
def get_intro_style():
    intros = [
        "1. 날씨/계절형: '날씨가 갑자기 추워져서 그런지...' 처럼 날씨 얘기로 자연스럽게 시작 (안녕하세요 금지)",
        "2. 현장상황형: '아침 9시부터 다급한 전화를 받고 달려갔습니다' 처럼 긴박하게 시작",
        "3. 질문형: '왜 꼭 급할 때만 장비가 말썽일까요?' 라고 독자에게 질문하며 시작",
        "4. 팩트형: 인사 생략하고 '오늘 현장은 OO동의 엘리베이터 없는 3층입니다' 라고 담백하게 시작"
    ]
    return random.choice(intros)

# --- [기능 4] 글 길이 지침 ---
def get_length_instruction(length_option):
    if length_option == "짧게": return "핵심만 간단히 1,000자 내외."
    elif length_option == "보통": return "에피소드 포함 1,500자 이상."
    else: return "관리꿀팁, FAQ 포함 2,500자 이상 아주 길게."

# --- [기능 5] 프롬프트 생성 (도입부 로직 강화) ---
def generate_pro_prompt(category, equipment, location, work_detail, urgency, length_option, contact_info, ref_content):
    
    pattern = get_structure_pattern()
    intro_style = get_intro_style()
    length_instruction = get_length_instruction(length_option)
    
    ref_section = ""
    if ref_content:
        ref_section = f"\n# [참고 자료]\n(아래 내용을 참고하되 문장은 새로 써)\n{ref_content}\n"
    
    prompt = f"""
# 역할
너는 20년 경력의 '{category}' 현장 전문가야.
광고성 멘트나 로봇 같은 인사는 집어치우고, **옆집 형/오빠가 말해주듯** 자연스럽게 써.

# 입력 정보
- 업종: {category}
- 장비: {equipment}
- 장소: {location}
- 작업: {work_detail}
- 상황: {urgency}

{ref_section}

# ★가장 중요한 도입부(시작) 가이드★
이번 글의 시작은 무조건 **[{intro_style}]** 방식으로 해.
**제발 "안녕하세요 OOO입니다" 라고 시작하지 마.** 
그냥 바로 날씨 얘기나, 현장 상황, 또는 질문으로 훅 치고 들어와.

# 글 전개 및 분량
1. 구조: **[{pattern}]**
2. 분량: {length_instruction}

# 말투 및 주의사항
1. **금지어**: "알아보겠습니다", "살펴보겠습니다", "결론적으로", "소개합니다". (절대 금지)
2. **말투**: "~했습니다"와 함께 "~했네요", "~더라구요", "~처리했죠"를 섞어서 리듬감 있게.
3. **전문성**: 감정보다는 '작업의 디테일(부품명, 증상)'을 구체적으로 묘사해.

# 필수 요소
- 중간중간 [사진: ~모습] 위치 표시.
- 글 마지막에만 연락처 강조:
{contact_info}

위 가이드를 지켜서 작성해.
    """
    return prompt, intro_style, pattern

# --- UI 레이아웃 ---
st.title("🗣️ 블로그 AI (자연스러운 도입부 적용)")

with st.sidebar:
    st.header("1. 기본 설정")
    category = st.text_input("업종 입력", placeholder="예: CCTV 설치, 누수 탐지")
    length_option = st.select_slider("글 길이", options=["짧게", "보통", "길게"], value="보통")
    contact_info = st.text_area("명함 문구", "문의: 010-XXXX-XXXX", height=70)
    
    st.divider()
    st.header("2. 벤치마킹 URL")
    ref_urls = st.text_area("참고할 블로그 주소 (줄바꿈)", height=100)
    
    st.divider()
    st.header("3. 현장 팩트")
    equipment = st.text_input("장비명", placeholder="예: 캐논 3826")
    location = st.text_input("장소", placeholder="예: 학원 3층")
    work_detail = st.text_area("작업내용", placeholder="예: 급지 롤러 교체", height=100)
    urgency = st.radio("상황", ["긴급", "난이도 상", "신규", "점검"])
    
    generate_btn = st.button("📝 프롬프트 생성", type="primary")

if generate_btn:
    if not category or not work_detail:
        st.warning("업종과 작업 내용은 필수입니다!")
    else:
        ref_content = scrape_naver_blogs(ref_urls) if ref_urls else ""
        
        final_prompt, intro, pattern = generate_pro_prompt(category, equipment, location, work_detail, urgency, length_option, contact_info, ref_content)
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.success("✅ 도입부 스타일 적용됨")
            st.info(f"**도입부 전략:**\n{intro}")
            st.warning(f"**전개 방식:**\n{pattern}")
        with col2:
            st.subheader("🤖 GPT 입력용 프롬프트")
            st.code(final_prompt, language="text")