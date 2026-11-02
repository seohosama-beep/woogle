# 강달콤 두부씨 릴스 생성기
- 의존성: python3, numpy, pillow, ffmpeg, Noto Sans CJK 폰트
- 실행: `python3 gen.py spec.json` → `<name>.mp4` (1080x1920, 원본 음악·효과음 포함)
- kind: `vs`(좌우 비교, beats 4개), `types`(유형별 특징, items 4개), `meme`(짤 형식, frames 5개)
- mood: happy / shock / smug / dead / derp / angry
- 예시: example_vs.json
- 사용한 주제는 topics_used.md 에 한 줄씩 기록 (중복 금지)
