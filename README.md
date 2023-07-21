## 나이키 SNKRS 신발 자동 구매, 응모 시스템
### (대학교 졸업 프로젝트, 학과 경진대회 1위 최우수상 수상)

### 소개
- 나이키 SNKRS 신발 출시 예정일, 이미지 , 가격, 구매 또는 응모여부 등 전반적인 정보 크롤링
- 웹서버에서 유저가 원하는 신발의 사이즈 선택후 확정시 출시일에 맞춰 Selenium으로 구매,응모 진행
- 구매 같은경우 카카오페이로 결제 직접 진행
- Bot 동작시 모든 상황은 텔레그램 메세지로 유저에게 전송됨


### 서버구성
1. 웹서버 Node.JS : 유저의 구매,응모 예약 기능 수행
2. 크롤링서버 Python Flask : SNKRS 신발 출시 관련 크롤링 수행
3. 구매봇 Python ( Exe 파일 ) : 매일 아침 웹서버 API 통신하여 확정된 신발 출시 정보에따라 구매, 응모 수행

### 기술
1. Python ( Selenium, Flask )
2. Node.Js ( Express, Telegram API )
3. Postgresql

## 사진
![img0.png](https://raw.githubusercontent.com/lomal788/nike-snkrs-shoe-bot/main/img/img0.png)
![img1.png](https://raw.githubusercontent.com/lomal788/nike-snkrs-shoe-bot/main/img/img1.png)


## Warning - 본 프로그램은 매크로를 이용한 신발 구매,응모를 부추키는 프로그램이 아니며, 해당 프로그램을 사용함으로서 생기는 책임은 모두 이용자 본인에게 있습니다. 또한 나이키 SNKRS 사이트의 개편으로 인해 현재 프로그램을 사용할수없습니다.
