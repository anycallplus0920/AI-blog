# -*- coding: utf-8 -*-
import streamlit as st
import random
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="블로그 AI: 포토 디렉터 모드", page_icon="📸", layout="wide")

# --- 기존 함수들 (그대로 유지) ---
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
            text = soup.get_text(separator=' ', strip=True)[:800]
            combined_content += f"\n[참고{i+1}]: {text}\n"
        except: pass
    return combined_content

def get_structure_pattern():
    patterns = [
        "A타입: 결과물 사진부터 '똬!' 보여주고 시작하기",
        "B타입: 현장의 답답했던 문제 상황 묘사로 시작하기",
        "C타입: 작업 전(Before)과 후(After)를 확실하게 비교하기",
        "D타입: 기술적 원리를 하나하나 짚어주는 전문가 스타일"
    ]
    return random.choice(patterns)

def get_intro_style():
    intros = [
        "1. 날씨/계절형: 날씨 얘기로 자연스럽게 시작 (안녕하세요 금지)",
        "2. 현장상황형: 다급한 전화나 긴박한 상황 묘사로 시작",
        "3. 질문형: 독자에게 질문을 던지며 시작",
        "4. 팩트형: 인사 생략하고 장소와 장비 설명으로 바로 진입"
    ]
    return random.choice(intros)

# --- [NEW] 사진 지시사항 생성 함수 ---
def generate_photo_instructions(photo_list):
    if not photo_list:
        return "특별한 사진 지시사항 없음. 일반적인 흐름대로 작성해."
    
    instructions = "\n# 📸 [사진 배치 및 묘사 가이드] (매우 중요)\n"
    instructions += "내가 이 프롬프트와 함께 **실제 사진들을 업로드**할 거야. 각 사진을 설명할 때 아래 포인트를 꼭 살려서 묘사해줘.\n"
    
    for i, item in enumerate(photo_list):
        instructions += f"""
    - **[사진 {i+1}]: {item['name']}**
      👉 묘사 포인트: "{item['desc']}"
      (이 내용을 바탕으로 독자가 사진을 뚫어지게 쳐다보게끔 생생하게 표현해줘.)
        """
    return instructions

# --- 최종 프롬프트 생성 ---
def generate_pro_prompt(category, equipment, location, work_detail, urgency, length_option, contact_info, ref_content, photo_instructions):
    
    pattern = get_structure_pattern()
    intro_style = get_intro_style()
    
    length_rule = "1,500자 이상" if length_option == "보통" else ("1,000자 내외" if length_option == "짧게" else "2,500자 이상")

    ref_section = f"\n# [참고 자료]\n{ref_content}\n" if ref_content else ""
    
    prompt = f"""
# 역할
너는 20년 경력의 '{category}' 현장 전문가야.
사진을 보며 옆에서 설명해주듯 현장감 있게 글을 써야 해.

# 입력 정보
- 업종: {category}
- 장비: {equipment}
- 장소: {location}
- 작업: {work_detail}
- 상황: {urgency}

{photo_instructions}

{ref_section}

# 작성 가이드
1. **도입부**: **[{intro_style}]** 방식으로 시작해. (식상한 인사 금지)
2. **글 구조**: **[{pattern}]**
3. **분량**: {length_rule}
4. **말투**: "~했습니다"와 "~했네요", "~보이시죠?"를 섞어서 대화하듯이.

# 필수 요소
- 글 마지막에만 연락처 강조:
{contact_info}

위 가이드를 완벽히 소화해서 작성해줘.
    """
    return prompt, intro_style, pattern

# --- UI 레이아웃 ---
st.title("📸 블로그 AI (사진별 코멘트 기능)")

col_main_1, col_main_2 = st.columns([1, 1.2])

with col_main_1:
    st.header("1. 기본/벤치마킹")
    category = st.text_input("업종", placeholder="예: CCTV 설치")
    contact_info = st.text_area("명함 문구", "문의: 010-XXXX-XXXX", height=70)
    ref_urls = st.text_area("참고 URL (줄바꿈)", height=70)

    st.header("2. 현장 팩트")
    equipment = st.text_input("장비명", placeholder="예: 캐논 3826")
    location = st.text_input("장소", placeholder="예: 학원 3층")
    urgency = st.radio("상황", ["긴급", "난이도 상", "신규", "점검"], horizontal=True)
    length_option = st.select_slider("길이", options=["짧게", "보통", "길게"], value="보통")

with col_main_2:
    st.header("3. 작업 내용 & 사진 설명")
    work_detail = st.text_area("전체 작업 내용", placeholder="예: 급지 롤러 교체, 선정리 완료", height=100)
    
    st.markdown("---")
    st.subheader("🖼️ 사진 업로드 & 설명 (핵심 기능)")
    st.info("GPT에게 보여줄 사진을 올리고, **'이 사진은 어떤 장면인지'** 적어주세요.")
    
    # 파일 업로더
    uploaded_files = st.file_uploader("사진 선택 (여러 장 가능)", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])
    
    photo_data = []
    if uploaded_files:
        for uploaded_file in uploaded_files:
            # 사진 미리보기와 입력창을 나란히 배치
            p_col1, p_col2 = st.columns([1, 2])
            with p_col1:
                st.image(uploaded_file, width=100)
            with p_col2:
                desc = st.text_input(f"👆 '{uploaded_file.name}' 설명", placeholder="예: 녹슨 기어 확대샷, 먼지 낀 필터")
                if desc:
                    photo_data.append({"name": uploaded_file.name, "desc": desc})

    generate_btn = st.button("📝 프롬프트 생성 (사진 지시사항 포함)", type="primary", use_container_width=True)

if generate_btn:
    if not category or not work_detail:
        st.warning("업종과 작업 내용은 필수입니다!")
    else:
        ref_content = scrape_naver_blogs(ref_urls) if ref_urls else ""
        
        # 사진 지시사항 생성
        photo_instructions = generate_photo_instructions(photo_data)
        
        final_prompt, intro, pattern = generate_pro_prompt(category, equipment, location, work_detail, urgency, length_option, contact_info, ref_content, photo_instructions)
        
        st.divider()
        st.success("✅ 사진 설명이 포함된 프롬프트가 생성되었습니다!")
        
        res_col1, res_col2 = st.columns([1, 2])
        with res_col1:
            st.info(f"**도입부:** {intro}")
            st.warning(f"**전개:** {pattern}")
            if photo_data:
                st.markdown("### 📸 입력된 사진 정보")
                for p in photo_data:
                    st.write(f"- {p['desc']}")
                    
        with res_col2:
            st.subheader("🤖 GPT 입력용 프롬프트")
            st.code(final_prompt, language="text")
            st.markdown("👉 **팁:** 이 프롬프트를 GPT에 붙여넣고, **위에서 올린 사진들도 같이 드래그해서 GPT에게 주세요.**")
