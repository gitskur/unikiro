"""
Teams 앱 패키지(manifest.zip) 생성 스크립트.
실행 전: manifest.json의 <TEAMS_BOT_APP_ID>를 실제 Azure App ID로 교체하세요.
아이콘 파일(color.png 192x192, outline.png 32x32)을 teams_app/ 폴더에 넣으세요.
"""
import zipfile, os, sys

app_dir = os.path.join(os.path.dirname(__file__), "teams_app")
out_path = os.path.join(os.path.dirname(__file__), "teams_app_package.zip")

required = ["manifest.json", "color.png", "outline.png"]
missing = [f for f in required if not os.path.exists(os.path.join(app_dir, f))]
if missing:
    print(f"[오류] 누락 파일: {missing}")
    print("color.png (192x192), outline.png (32x32) 아이콘을 teams_app/ 폴더에 추가하세요.")
    sys.exit(1)

with zipfile.ZipFile(out_path, "w") as z:
    for f in required:
        z.write(os.path.join(app_dir, f), f)

print(f"앱 패키지 생성 완료: {out_path}")
print("Teams 관리 센터 또는 Teams > 앱 > 앱 업로드에서 이 zip 파일을 업로드하세요.")
