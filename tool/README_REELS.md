# 강달콤 두부씨 릴스 생성기
- 의존성: python3, numpy, pillow, ffmpeg, Noto Sans CJK 폰트
- 실행: `python3 gen.py spec.json` → `<name>.mp4` (1080x1920, 원본 음악·효과음 포함)
- kind: `vs`(좌우 비교, beats 4개), `types`(유형별 특징, items 4개), `meme`(짤 형식, frames 5개)
- mood: happy / shock / smug / dead / derp / angry
- 예시: example_vs.json
- 사용한 주제는 topics_used.md 에 한 줄씩 기록 (중복 금지)

## K-서울 가이드 (2026-11-03~ 현재 컨셉)
- 실행: `python3 kguide.py spec.json` → `<name>.mp4` (1080x1920 고화질, 자체 그래픽·자체 음악)
- spec: kguide_example.json 참고. 선택 "hook": 제목 화면 맨 위 영어 한 줄 훅(예: "Don't visit Seoul before knowing this!"). items는 4개 권장(영상 약 12초). title{en,ko,ja,zh}, items 3~5개 {icon, ko, roman, en, ja, zh}
- icon: egg, potato, ricecake, pancake, skewer, hotel, subway, shop, camera, coffee, map, star
- 사실 정보만(가격·영업시간 등 바뀌는 숫자는 넣지 말 것), 다른 사람 영상·사진·음악 사용 금지
