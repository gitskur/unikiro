const pptxgen = require('pptxgenjs');
const pres = new pptxgen();

pres.layout = 'LAYOUT_WIDE';
pres.author = 'Coupa AI Team';
pres.title = 'Coupa AI Facilitator';

// Slide 1: Title
let slide = pres.addSlide();
slide.background = { color: '0D1117' };
slide.addText('🏆 1-Day Hackathon · 2026.04.17', { x: '35%', y: '20%', fontSize: 12, color: '388BFD', bold: true });
slide.addText('Coupa AI Facilitator', { x: '20%', y: '30%', w: '60%', fontSize: 44, color: '79C0FF', bold: true, align: 'center' });
slide.addText('사내 구매/계약 프로세스 AI 챗봇', { x: '20%', y: '45%', w: '60%', fontSize: 18, color: '8B949E', align: 'center' });
slide.addText([
  { text: '1일 ', options: { fontSize: 16, color: '388BFD', bold: true } },
  { text: '개발 기간  ', options: { fontSize: 12, color: '8B949E' } },
  { text: '3개 ', options: { fontSize: 16, color: '388BFD', bold: true } },
  { text: 'Lambda  ', options: { fontSize: 12, color: '8B949E' } },
  { text: '155 ', options: { fontSize: 16, color: '388BFD', bold: true } },
  { text: 'RAG 청크  ', options: { fontSize: 12, color: '8B949E' } },
  { text: '5/6 ', options: { fontSize: 16, color: '388BFD', bold: true } },
  { text: 'UAT PASS', options: { fontSize: 12, color: '8B949E' } }
], { x: '15%', y: '60%', w: '70%', align: 'center' });

// Slide 2: 배경/문제
slide = pres.addSlide();
slide.background = { color: '0D1117' };
slide.addText('Background', { x: '5%', y: '8%', fontSize: 12, color: '388BFD', bold: true });
slide.addText('왜 만들었나요?', { x: '5%', y: '12%', fontSize: 32, color: 'E6EDF3', bold: true });
slide.addShape(pres.ShapeType.rect, { x: '5%', y: '22%', w: '21%', h: '28%', fill: { color: '161B22' }, line: { color: '30363D', width: 1 } });
slide.addText('😤 반복 문의 집중\n\n구매 절차·결재 라인 등 동일 질문이 담당자에게 반복 집중', { x: '6%', y: '24%', w: '19%', h: '24%', fontSize: 12, color: '8B949E', valign: 'top' });
slide.addShape(pres.ShapeType.rect, { x: '28%', y: '22%', w: '21%', h: '28%', fill: { color: '161B22' }, line: { color: '30363D', width: 1 } });
slide.addText('📄 문서 파편화\n\nPDF 매뉴얼 3종이 분산되어 최신 정책 찾기 어려움', { x: '29%', y: '24%', w: '19%', h: '24%', fontSize: 12, color: '8B949E', valign: 'top' });
slide.addShape(pres.ShapeType.rect, { x: '51%', y: '22%', w: '21%', h: '28%', fill: { color: '161B22' }, line: { color: '30363D', width: 1 } });
slide.addText('⏰ 계약 만료 누락\n\nD-60 알림이 수동 관리되어 갱신 시기 놓치는 리스크', { x: '52%', y: '24%', w: '19%', h: '24%', fontSize: 12, color: '8B949E', valign: 'top' });
slide.addShape(pres.ShapeType.rect, { x: '74%', y: '22%', w: '21%', h: '28%', fill: { color: '161B22' }, line: { color: '30363D', width: 1 } });
slide.addText('🔗 시스템 단절\n\nCoupa ↔ Teams 연동 부재로 실시간 상태 확인 불가', { x: '75%', y: '24%', w: '19%', h: '24%', fontSize: 12, color: '8B949E', valign: 'top' });

// Slide 3: 아키텍처
slide = pres.addSlide();
slide.background = { color: '0D1117' };
slide.addText('Architecture', { x: '5%', y: '8%', fontSize: 12, color: '388BFD', bold: true });
slide.addText('최종 시스템 아키텍처', { x: '5%', y: '12%', fontSize: 32, color: 'E6EDF3', bold: true });
slide.addText('Teams → Azure Bot → API GW /teams → Lambda:rag → FAISS → Bedrock → Teams 답변', { x: '5%', y: '25%', w: '90%', fontSize: 11, color: '8B949E' });
slide.addText('Chat UI v5 → API GW /chat → Lambda:rag → FAISS + Bedrock → 웹 답변', { x: '5%', y: '32%', w: '90%', fontSize: 11, color: '8B949E' });
slide.addText('EventBridge 09:00 KST → Lambda:scheduler → Coupa API D-60 → Teams 알림', { x: '5%', y: '39%', w: '90%', fontSize: 11, color: '8B949E' });
slide.addText('Coupa Webhook → API GW /coupa/webhook → Lambda:webhook → Teams 상태변경 알림', { x: '5%', y: '46%', w: '90%', fontSize: 11, color: '8B949E' });
slide.addShape(pres.ShapeType.rect, { x: '5%', y: '55%', w: '21%', h: '18%', fill: { color: '161B22' }, line: { color: '388BFD', width: 1 } });
slide.addText('🤖 Lambda 1: RAG 챗봇\n\nFAISS 155 chunks\nBedrock nova-lite\nDynamoDB 대화기억', { x: '6%', y: '57%', w: '19%', fontSize: 10, color: '8B949E' });
slide.addShape(pres.ShapeType.rect, { x: '28%', y: '55%', w: '21%', h: '18%', fill: { color: '161B22' }, line: { color: '388BFD', width: 1 } });
slide.addText('⏰ Lambda 2: 스케줄러\n\nEventBridge Cron\nD-60 계약 조회\nTeams 알림', { x: '29%', y: '57%', w: '19%', fontSize: 10, color: '8B949E' });
slide.addShape(pres.ShapeType.rect, { x: '51%', y: '55%', w: '21%', h: '18%', fill: { color: '161B22' }, line: { color: '388BFD', width: 1 } });
slide.addText('🔔 Lambda 3: Webhook\n\nCoupa 이벤트 수신\n상태변경 처리\nTeams 알림', { x: '52%', y: '57%', w: '19%', fontSize: 10, color: '8B949E' });
slide.addShape(pres.ShapeType.rect, { x: '74%', y: '55%', w: '21%', h: '18%', fill: { color: '161B22' }, line: { color: '30363D', width: 1 } });
slide.addText('📚 Knowledge\n\nPDF 3종\nprocess_guide.md\nFAISS 인덱스', { x: '75%', y: '57%', w: '19%', fontSize: 10, color: '8B949E' });

// Slide 4: 주요 기능
slide = pres.addSlide();
slide.background = { color: '0D1117' };
slide.addText('Features', { x: '5%', y: '8%', fontSize: 12, color: '388BFD', bold: true });
slide.addText('주요 기능 6가지', { x: '5%', y: '12%', fontSize: 32, color: 'E6EDF3', bold: true });
const features = [
  { x: '5%', y: '25%', icon: '🔍', title: 'RAG 기반 Q&A', desc: '155 chunks 벡터 검색\nprocess_guide 우선 참조\nClaude AI 한국어 답변' },
  { x: '35%', y: '25%', icon: '📅', title: '계약 만료 D-60 알림', desc: 'EventBridge 매일 09:00\nCoupa API 실시간 조회\nTeams Adaptive Card' },
  { x: '65%', y: '25%', icon: '⚡', title: 'Coupa 실시간 연동', desc: '계약/PO 상태 즉시 조회\nWebhook 이벤트 처리\n승인 단계별 알림' },
  { x: '5%', y: '55%', icon: '💬', title: 'Teams Bot 통합', desc: 'Azure Bot Service\n채널/DM 멘션 지원\nAdaptive Card UI' },
  { x: '35%', y: '55%', icon: '🖥️', title: 'Chat UI v5', desc: '드래그 이동 가능\n숨기기/복원\n화면 이탈 방지' },
  { x: '65%', y: '55%', icon: '☁️', title: 'Serverless IaC', desc: 'AWS SAM 배포\nLambda Layer\n유휴 비용 없음' }
];
features.forEach(f => {
  slide.addShape(pres.ShapeType.rect, { x: f.x, y: f.y, w: '28%', h: '24%', fill: { color: '161B22' }, line: { color: '30363D', width: 1 } });
  slide.addText(f.icon, { x: f.x, y: f.y, w: '28%', h: '6%', fontSize: 20, align: 'center', valign: 'middle' });
  slide.addText(f.title, { x: f.x, y: `${parseFloat(f.y)+6}%`, w: '28%', fontSize: 13, color: '79C0FF', bold: true, align: 'center' });
  slide.addText(f.desc, { x: f.x, y: `${parseFloat(f.y)+11}%`, w: '28%', h: '12%', fontSize: 10, color: '8B949E', align: 'center', valign: 'top' });
});

// Slide 5: UAT 결과
slide = pres.addSlide();
slide.background = { color: '0D1117' };
slide.addText('UAT Results', { x: '5%', y: '8%', fontSize: 12, color: '388BFD', bold: true });
slide.addText('UAT 검증 결과', { x: '5%', y: '12%', fontSize: 32, color: 'E6EDF3', bold: true });
const rows = [
  ['TC', '테스트 항목', '입력', '판정'],
  ['TC-02', 'On-Budget 결재', 'On-Budget 500만원 결재 라인', '✅ PASS'],
  ['TC-03', 'On-Budget 고액', 'On-Budget 2000만원 결재 라인', '✅ PASS'],
  ['TC-05', 'Off-Budget 결재', 'Off-Budget 500만원 결재 라인', '✅ PASS'],
  ['TC-12', '경비 처리', '경비 처리는 어떻게 해?', '✅ PASS'],
  ['TC-16', '존재하지 않는 계약', '999999번 계약 알려줘', '✅ PASS'],
  ['TC-19', 'PO 발행 (번호 없이)', 'PO 발행됐어?', '⚠️ PARTIAL']
];
slide.addTable(rows, { x: '5%', y: '25%', w: '90%', fontSize: 11, color: 'E6EDF3', fill: '161B22', border: { pt: 1, color: '30363D' } });
slide.addShape(pres.ShapeType.rect, { x: '5%', y: '70%', w: '28%', h: '18%', fill: { color: '388BFD22' }, line: { color: '388BFD', width: 1 } });
slide.addText('5 / 6', { x: '5%', y: '72%', w: '28%', fontSize: 32, color: '3FB950', bold: true, align: 'center' });
slide.addText('PASS (83%)', { x: '5%', y: '80%', w: '28%', fontSize: 12, color: '8B949E', align: 'center' });
slide.addShape(pres.ShapeType.rect, { x: '36%', y: '70%', w: '28%', h: '18%', fill: { color: '161B22' }, line: { color: '30363D', width: 1 } });
slide.addText('1 / 6', { x: '36%', y: '72%', w: '28%', fontSize: 32, color: 'D29922', bold: true, align: 'center' });
slide.addText('PARTIAL', { x: '36%', y: '80%', w: '28%', fontSize: 12, color: '8B949E', align: 'center' });

// Slide 6: 비용
slide = pres.addSlide();
slide.background = { color: '0D1117' };
slide.addText('Cost', { x: '5%', y: '8%', fontSize: 12, color: '388BFD', bold: true });
slide.addText('운영 비용 분석', { x: '5%', y: '12%', fontSize: 32, color: 'E6EDF3', bold: true });
slide.addShape(pres.ShapeType.rect, { x: '20%', y: '25%', w: '60%', h: '18%', fill: { color: '388BFD22' }, line: { color: '388BFD', width: 2 } });
slide.addText('$35 ~ $100 / 월', { x: '20%', y: '28%', w: '60%', fontSize: 40, color: '388BFD', bold: true, align: 'center' });
slide.addText('200~300명 사용 기준 예상 운영 비용', { x: '20%', y: '37%', w: '60%', fontSize: 14, color: '8B949E', align: 'center' });
const costRows = [
  ['항목', '월 예상 비용', '특징'],
  ['Lambda (3개)', '~$0 (프리티어)', '요청 기반 과금'],
  ['API Gateway', '~$3~10', 'REST API 호출'],
  ['Bedrock Claude', '~$30~90', 'nova-lite 저비용'],
  ['DynamoDB', '~$5', '온디맨드 모드'],
  ['S3', '~$1', '문서 + FAISS'],
  ['합계', '$35~100', 'Serverless']
];
slide.addTable(costRows, { x: '10%', y: '50%', w: '80%', fontSize: 11, color: 'E6EDF3', fill: '161B22', border: { pt: 1, color: '30363D' } });

// Slide 7: 향후 계획
slide = pres.addSlide();
slide.background = { color: '0D1117' };
slide.addText('Roadmap', { x: '5%', y: '8%', fontSize: 12, color: '388BFD', bold: true });
slide.addText('향후 계획', { x: '5%', y: '12%', fontSize: 32, color: 'E6EDF3', bold: true });
slide.addText('Phase 1 — 즉시 (1~2주)\nTC-19 개선 · 청크 전략 최적화 · 프롬프트 튜닝', { x: '10%', y: '28%', w: '80%', fontSize: 12, color: '8B949E' });
slide.addText('Phase 2 — 단기 (1개월)\n지식베이스 확장 · 사용자 피드백 루프 · 답변 품질 모니터링', { x: '10%', y: '40%', w: '80%', fontSize: 12, color: '8B949E' });
slide.addText('Phase 3 — 중기 (3개월)\nCoupa 액션 실행 (PO 생성/승인 자동화) · 다국어 지원 · ROI 측정', { x: '10%', y: '52%', w: '80%', fontSize: 12, color: '8B949E' });
slide.addText('Phase 4 — 장기 (6개월+)\n타 ERP 연동 확장 · Fine-tuning · 전사 AI 어시스턴트 플랫폼', { x: '10%', y: '64%', w: '80%', fontSize: 12, color: '8B949E' });
slide.addShape(pres.ShapeType.rect, { x: '15%', y: '78%', w: '70%', h: '12%', fill: { color: '161B22' }, line: { color: '388BFD', width: 1 } });
slide.addText('🎉 1일 해커톤 → 실제 운영 가능한 AI 챗봇 완성', { x: '15%', y: '80%', w: '70%', fontSize: 16, color: '79C0FF', bold: true, align: 'center' });
slide.addText('Serverless · 저비용 · 확장 가능 · UAT 검증 완료', { x: '15%', y: '85%', w: '70%', fontSize: 12, color: '8B949E', align: 'center' });

pres.writeFile({ fileName: 'C:/Users/ryuji/unikiro/docs/Coupa_AI_Facilitator.pptx' })
  .then(() => console.log('✅ PPT 생성 완료: docs/Coupa_AI_Facilitator.pptx'))
  .catch(err => console.error('❌ 오류:', err));
