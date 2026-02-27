# Local Split Market

동네 주민들이 공동구매 후 물품을 소분하여 나눌 수 있는 웹 서비스입니다.  
단순 중고거래 플랫폼이 아니라, 공동구매와 나눔을 중심으로 한 지역 기반 서비스 구현을 목표로 개발 중입니다.

---

## 1. Project Goal

- 데이터베이스 수업에서 학습한 관계형 모델과 정규화 개념을 실제 서비스에 적용
- Flask 기반 웹 애플리케이션 구조 설계 경험
- 사용자 인증 및 데이터 모델 설계 이해
- Git을 활용한 협업 경험

---

## 2. Tech Stack

- Backend: Flask
- Database: SQLite
- ORM: SQLAlchemy
- Version Control: Git

---

## 3. Implemented Features

- 회원가입 및 로그인 기능
- 게시글 작성 및 조회
- 카테고리 기반 게시글 필터링
- 기본적인 데이터 모델 설계 (User, Post, JoinRequest)

---

## 4. Database Design

- User: 사용자 정보 저장
- Post: 공동구매 게시글
- JoinRequest: 참여 요청 정보

테이블 간 관계를 정의하여 데이터 중복을 최소화하고, 향후 기능 확장이 가능하도록 설계하였습니다.

---

## 5. Current Progress

- 기본 CRUD 기능 구현 완료
- 로그인 세션 관리 적용
- Git 브랜치 기반 협업 진행 중

---

## 6. Future Improvements

- RESTful API 구조로 리팩토링
- 게시글 정렬 및 검색 기능 고도화
- 권한 관리 구조 개선
- 데이터베이스 모델 확장 및 성능 고려 설계
- 배포 환경 구성
