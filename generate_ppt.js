const pptxgen = require('pptxgenjs');
const pres = new pptxgen();

pres.layout = 'LAYOUT_WIDE';
pres.title = 'Coupa AI Facilitator';

const BG = '0D1117';
const BLUE = '388BFD';
const LIGHT_BLUE = '79C0FF';
const GRAY = '8B949E';
const WHITE = 'E6EDF3';
const DARK = '161B22';
const BORDER = '30363D';
const GREEN = '3FB950';
const YELLOW = 'D29922';

function addSlideBase(title, subtitle) {
  const s = pres.addSlide();
  s.background = { color: BG };
  if (subtitle) s.addText(subtitle, { x: '5%', y: '7%', w: '90%', fontSize: 11, color: BLUE, bold: true });
  if (title) s.addText(title, { x: '5%', y: '12%', w: '90%', fontSize: 30, color: WHITE, bold: true });
  s.addShape(pres.ShapeType.rect, { x: '5%', y: '21%', w: '6%', h: '0.8%', fill: { color: BLUE }, line: { color: BLUE } });
  return s;
}

// ── Slide 1: Title ──────────────────────────────────────────────
{
  const s = pres.addSlide();
  s.background = { color: BG };
  s.addText('🏆 1-Day Hackathon · 2026.04.17', { x: '25%', y: '15%', w: '50%', fontSize: 12, color: BLUE, bold: true, align: 'center' });
  s.addText('Coupa AI Facilitator', { x: '10%', y: '25%', w: '80%', fontSize: 44, color: LIGHT_BLUE, bold: true, align: 'center' });
  s.addText('사내 구매/계약 프로세스 AI 챗봇', { x: '10%', y: '40%', w: '80%', fontSize: 18, color: GRAY, align: 'center' });
  s.addText('팀 유니키로  |  최정아 · 유지원 · 김동현', { x: '10%', y: '50%', w: '80%', fontSize: 14, color: WHITE, align: 'center', bold: true });
  // Stats
  const stats = [['1일','개발 기간'],['3개','Lambda 함수'],['155','RAG 청크'],['5/6','UAT PASS'],['$35~100','월 운영비']];
  stats.forEach((st, i) => {
    const x = `${8 + i * 18}%`;
    s.addText(st[0], { x, y: '62%', w: '16%', fontSize: 22, color: BLUE, bold: true, align: 'center' });
    s.addText(st[1], { x, y: '70%', w: '16%', fontSize: 10, color: GRAY, align: 'center' });
  });
  s.addText('AWS Lambda  ·  Amazon Bedrock  ·  FAISS RAG  ·  DynamoDB  ·  Teams Bot  ·  Coupa REST API', { x: '5%', y: '80%', w: '90%', fontSize: 10, color: GRAY, align: 'center' });
}

// ── Slide 2: 배경/문제 ──────────────────────────────────────────
{
  const s = addSlideBase('왜 만들었나요?', 'Background');
  const items = [
    ['😤 반복 문의 집중', '구매 절차·결재 라인 등\n동일 질문이 담당자에게\n반복 집중'],
    ['📄 문서 파편화', 'PDF 매뉴얼 3종이 분산\n직원이 최신 정책\n찾기 어려움'],
    ['⏰ 계약 만료 누락', 'D-60 알림이 수동 관리\n갱신 시기 놓치는\n리스크 상존'],
    ['🔗 시스템 단절', 'Coupa ↔ Teams 연동 부재\n승인 현황 실시간\n확인 불가'],
  ];
  items.forEach((item, i) => {
    const x = `${5 + i * 23.5}%`;
    s.addShape(pres.ShapeType.rect, { x, y: '25%', w: '22%', h: '45%', fill: { color: DARK }, line: { color: BORDER, width: 1 } });
    s.addText(item[0], { x, y: '27%', w: '22%', fontSize: 12, color: LIGHT_BLUE, bold: true, align: 'center' });
    s.addText(item[1], { x, y: '35%', w: '22%', h: '30%', fontSize: 11, color: GRAY, align: 'center', valign: 'top' });
  });
  s.addShape(pres.ShapeType.rect, { x: '5%', y: '75%', w: '90%', h: '15%', fill: { color: '388BFD11' }, line: { color: BLUE, width: 1 } });
  s.addText('1일 해커톤  ·  3개 Lambda  ·  Serverless  ·  월 $35~100  ·  UAT 5/6 PASS', { x: '5%', y: '79%', w: '90%', fontSize: 13, color: BLUE, bold: true, align: 'center' });
}

// ── Slide 3: 아키텍처 ───────────────────────────────────────────
{
  const s = addSlideBase('최종 시스템 아키텍처', 'Architecture');
  const flows = [
    ['🟦 Teams 챗봇', 'Teams → Azure Bot → API GW /teams → Lambda:rag → FAISS 벡터검색 → Bedrock Claude → Teams 답변'],
    ['🟥 Chat UI v5', 'Chat UI → API GW /chat → Lambda:rag → FAISS + Bedrock → 웹 답변'],
    ['🟨 D-60 알림', 'EventBridge 09:00 KST → Lambda:scheduler → Coupa API → Teams Adaptive Card'],
    ['🟧 Coupa Webhook', 'Coupa 이벤트 → API GW /coupa/webhook → Lambda:webhook → Teams 상태변경 알림'],
  ];
  flows.forEach((f, i) => {
    s.addText(f[0], { x: '5%', y: `${24 + i * 10}%`, w: '15%', fontSize: 11, color: WHITE, bold: true });
    s.addText(f[1], { x: '21%', y: `${24 + i * 10}%`, w: '74%', fontSize: 10, color: GRAY });
  });
  const boxes = [
    ['🤖 Lambda 1: RAG', 'FAISS 155 chunks\nBedrock nova-lite\nDynamoDB 대화기억'],
    ['⏰ Lambda 2: 스케줄러', 'EventBridge Cron\nD-60 계약 조회\nTeams 알림'],
    ['🔔 Lambda 3: Webhook', 'Coupa 이벤트 수신\n상태변경 처리\nTeams 알림'],
    ['📚 Knowledge Base', 'PDF 3종\nprocess_guide.md\nFAISS 155 chunks'],
  ];
  boxes.forEach((b, i) => {
    const x = `${5 + i * 23.5}%`;
    s.addShape(pres.ShapeType.rect, { x, y: '65%', w: '22%', h: '28%', fill: { color: DARK }, line: { color: i < 3 ? BLUE : BORDER, width: 1 } });
    s.addText(b[0], { x, y: '67%', w: '22%', fontSize: 11, color: LIGHT_BLUE, bold: true, align: 'center' });
    s.addText(b[1], { x, y: '74%', w: '22%', h: '16%', fontSize: 10, color: GRAY, align: 'center', valign: 'top' });
  });
}

// ── Slide 4: 주요 기능 ──────────────────────────────────────────
{
  const s = addSlideBase('주요 기능 6가지', 'Features');
  const features = [
    ['🔍 RAG 기반 Q&A', '155 chunks 벡터 검색\nprocess_guide 우선 참조\nClaude AI 한국어 답변\n대화 컨텍스트 유지'],
    ['📅 계약 만료 D-60', 'EventBridge 매일 09:00\nCoupa API 실시간 조회\nTeams Adaptive Card\nChannelMapping fallback'],
    ['⚡ Coupa 실시간 연동', '계약/PO 상태 즉시 조회\nWebhook 이벤트 처리\n승인 단계별 알림\napproved/rejected/cancelled'],
    ['💬 Teams Bot 통합', 'Azure Bot Service\n채널/DM 멘션 지원\nAdaptive Card UI\nBot Framework 인증'],
    ['🖥️ Chat UI v5', '드래그 이동 가능\n숨기기/복원 버튼\n화면 이탈 방지\n마크다운 렌더링'],
    ['☁️ Serverless IaC', 'AWS SAM 단일 배포\nLambda Layer\n유휴 비용 없음\n자동 확장'],
  ];
  features.forEach((f, i) => {
    const x = `${5 + (i % 3) * 31.5}%`;
    const y = `${24 + Math.floor(i / 3) * 38}%`;
    s.addShape(pres.ShapeType.rect, { x, y, w: '30%', h: '35%', fill: { color: DARK }, line: { color: BORDER, width: 1 } });
    s.addText(f[0], { x, y: `${parseFloat(y) + 2}%`, w: '30%', fontSize: 12, color: LIGHT_BLUE, bold: true, align: 'center' });
    s.addText(f[1], { x, y: `${parseFloat(y) + 10}%`, w: '30%', h: '22%', fontSize: 10, color: GRAY, align: 'center', valign: 'top' });
  });
}

// ── Slide 5: 데모 ───────────────────────────────────────────────
{
  const s = addSlideBase('실제 사용 예시', 'Demo');
  const demos = [
    ['💰 결재 라인 문의', '"Off-Budget 500만원\n결재 라인 알려줘"', '팀장 → 본부장 → CFO\n✅ UAT PASS'],
    ['📄 계약 조회', '"123번 계약\n만료일이 언제야?"', '계약명/상태/만료일/담당자\nCoupa API 실시간 조회'],
    ['🔔 자동 만료 알림', 'EventBridge 매일 09:00\n자동 실행', '⚠️ D-60 계약 만료 알림\nTeams Adaptive Card 발송'],
    ['🧾 경비 처리', '"경비 처리는\n어떻게 해?"', 'Concur 시스템에서\n경비 보고서 작성 안내'],
    ['✅ 승인 알림', 'Coupa 계약 approved\nWebhook 수신', '✅ 계약 최종 승인\nTeams 즉시 알림'],
    ['📝 계약 절차', '"Coupa 작성 후\n다음 단계가 뭐야?"', '법무팀→인감신청→날인\n단계별 안내'],
  ];
  demos.forEach((d, i) => {
    const x = `${5 + (i % 3) * 31.5}%`;
    const y = `${24 + Math.floor(i / 3) * 38}%`;
    s.addShape(pres.ShapeType.rect, { x, y, w: '30%', h: '35%', fill: { color: DARK }, line: { color: BORDER, width: 1 } });
    s.addText(d[0], { x, y: `${parseFloat(y) + 2}%`, w: '30%', fontSize: 11, color: LIGHT_BLUE, bold: true, align: 'center' });
    s.addText(d[1], { x, y: `${parseFloat(y) + 9}%`, w: '30%', fontSize: 10, color: GRAY, align: 'center' });
    s.addText(d[2], { x, y: `${parseFloat(y) + 20}%`, w: '30%', fontSize: 10, color: WHITE, align: 'center' });
  });
}

// ── Slide 6: UAT 결과 ───────────────────────────────────────────
{
  const s = addSlideBase('UAT 검증 결과', 'UAT Results');
  const rows = [
    [{ text: 'TC', options: { bold: true, color: GRAY } }, { text: '테스트 항목', options: { bold: true, color: GRAY } }, { text: '입력', options: { bold: true, color: GRAY } }, { text: '판정', options: { bold: true, color: GRAY } }],
    ['TC-02', 'On-Budget 결재 라인', 'On-Budget 500만원 결재 라인 알려줘', { text: '✅ PASS', options: { color: GREEN, bold: true } }],
    ['TC-03', 'On-Budget 고액 결재', 'On-Budget 2000만원 결재 라인 알려줘', { text: '✅ PASS', options: { color: GREEN, bold: true } }],
    ['TC-05', 'Off-Budget 결재 라인', 'Off-Budget 500만원 결재 라인 알려줘', { text: '✅ PASS', options: { color: GREEN, bold: true } }],
    ['TC-12', '경비 처리 안내', '경비 처리는 어떻게 해?', { text: '✅ PASS', options: { color: GREEN, bold: true } }],
    ['TC-16', '존재하지 않는 계약', '999999번 계약 알려줘', { text: '✅ PASS', options: { color: GREEN, bold: true } }],
    ['TC-19', 'PO 발행 (번호 없이)', 'PO 발행됐어?', { text: '⚠️ PARTIAL', options: { color: YELLOW, bold: true } }],
  ];
  s.addTable(rows, { x: '5%', y: '24%', w: '90%', fontSize: 11, color: WHITE, fill: DARK, border: { pt: 1, color: BORDER }, rowH: 0.4 });
  s.addShape(pres.ShapeType.rect, { x: '5%', y: '72%', w: '28%', h: '18%', fill: { color: '388BFD11' }, line: { color: BLUE, width: 1 } });
  s.addText('5 / 6', { x: '5%', y: '74%', w: '28%', fontSize: 28, color: GREEN, bold: true, align: 'center' });
  s.addText('PASS (83%)', { x: '5%', y: '83%', w: '28%', fontSize: 11, color: GRAY, align: 'center' });
  s.addShape(pres.ShapeType.rect, { x: '36%', y: '72%', w: '28%', h: '18%', fill: { color: DARK }, line: { color: BORDER, width: 1 } });
  s.addText('1 / 6', { x: '36%', y: '74%', w: '28%', fontSize: 28, color: YELLOW, bold: true, align: 'center' });
  s.addText('PARTIAL', { x: '36%', y: '83%', w: '28%', fontSize: 11, color: GRAY, align: 'center' });
  s.addShape(pres.ShapeType.rect, { x: '67%', y: '72%', w: '28%', h: '18%', fill: { color: DARK }, line: { color: BORDER, width: 1 } });
  s.addText('0 / 6', { x: '67%', y: '74%', w: '28%', fontSize: 28, color: BLUE, bold: true, align: 'center' });
  s.addText('FAIL (인코딩 이슈 수정 완료)', { x: '67%', y: '83%', w: '28%', fontSize: 11, color: GRAY, align: 'center' });
}

// ── Slide 7: 비용 ───────────────────────────────────────────────
{
  const s = addSlideBase('운영 비용 분석', 'Cost');
  s.addShape(pres.ShapeType.rect, { x: '20%', y: '24%', w: '60%', h: '20%', fill: { color: '388BFD11' }, line: { color: BLUE, width: 2 } });
  s.addText('$35 ~ $100 / 월', { x: '20%', y: '27%', w: '60%', fontSize: 36, color: BLUE, bold: true, align: 'center' });
  s.addText('200~300명 사용 기준 예상 운영 비용', { x: '20%', y: '37%', w: '60%', fontSize: 13, color: GRAY, align: 'center' });
  const rows = [
    [{ text: '항목', options: { bold: true, color: GRAY } }, { text: '월 예상 비용', options: { bold: true, color: GRAY } }, { text: '특징', options: { bold: true, color: GRAY } }],
    ['Lambda (3개)', { text: '~$0 (프리티어)', options: { color: GREEN } }, '요청 기반 과금, 유휴 비용 없음'],
    ['API Gateway', '~$3~10', 'REST API 호출 건수 기반'],
    ['Bedrock Claude', '~$30~90', 'nova-lite-v1:0 저비용 모델'],
    ['DynamoDB', '~$5', '온디맨드 모드, TTL 자동 만료'],
    ['S3', '~$1', '문서 저장 + FAISS 인덱스'],
    [{ text: '합계', options: { bold: true } }, { text: '$35~100', options: { color: BLUE, bold: true } }, 'Serverless, 사용량 기반'],
  ];
  s.addTable(rows, { x: '10%', y: '50%', w: '80%', fontSize: 11, color: WHITE, fill: DARK, border: { pt: 1, color: BORDER }, rowH: 0.38 });
}

// ── Slide 8: 기술 스택 ──────────────────────────────────────────
{
  const s = addSlideBase('기술 스택 상세', 'Tech Stack');
  const stacks = [
    ['🤖 AI/ML', 'Amazon Bedrock Claude\n(nova-lite-v1:0)\nFAISS 벡터 검색\nTitan Embed v2 (1024차원)\npypdf PDF 파싱'],
    ['☁️ AWS 인프라', 'Lambda (Python 3.9)\nAPI Gateway (5 endpoints)\nDynamoDB (2 tables)\nS3 + EventBridge\nAWS SAM IaC'],
    ['🔗 외부 연동', 'Microsoft Teams\nAzure Bot Service\nCoupa REST API\nBot Framework SDK\nWebhook 이벤트'],
    ['🎨 프론트엔드', 'Chat UI v5\n드래그/숨기기/이탈방지\nmarked.js 마크다운\nVanilla JS\n플로팅 위젯'],
  ];
  stacks.forEach((st, i) => {
    const x = `${5 + (i % 2) * 48}%`;
    const y = `${24 + Math.floor(i / 2) * 38}%`;
    s.addShape(pres.ShapeType.rect, { x, y, w: '45%', h: '35%', fill: { color: DARK }, line: { color: i < 2 ? BLUE : BORDER, width: 1 } });
    s.addText(st[0], { x, y: `${parseFloat(y) + 2}%`, w: '45%', fontSize: 13, color: LIGHT_BLUE, bold: true, align: 'center' });
    s.addText(st[1], { x, y: `${parseFloat(y) + 10}%`, w: '45%', h: '22%', fontSize: 11, color: GRAY, align: 'center', valign: 'top' });
  });
}

// ── Slide 9: 향후 계획 ──────────────────────────────────────────
{
  const s = addSlideBase('향후 계획', 'Roadmap');
  const phases = [
    ['Phase 1 — 즉시 (1~2주)', 'TC-19 개선 · 청크 전략 최적화 · 프롬프트 튜닝', BLUE],
    ['Phase 2 — 단기 (1개월)', '지식베이스 확장 · 사용자 피드백 루프 · 답변 품질 모니터링', BLUE],
    ['Phase 3 — 중기 (3개월)', 'Coupa 액션 실행 (PO 생성/승인 자동화) · 다국어 지원 · ROI 측정', BORDER],
    ['Phase 4 — 장기 (6개월+)', '타 ERP 연동 확장 · Fine-tuning · 전사 AI 어시스턴트 플랫폼', BORDER],
  ];
  phases.forEach((p, i) => {
    s.addShape(pres.ShapeType.ellipse, { x: '5%', y: `${26 + i * 13}%`, w: '1.5%', h: '2.5%', fill: { color: p[2] }, line: { color: p[2] } });
    s.addText(p[0], { x: '8%', y: `${25 + i * 13}%`, w: '30%', fontSize: 13, color: WHITE, bold: true });
    s.addText(p[1], { x: '8%', y: `${30 + i * 13}%`, w: '85%', fontSize: 11, color: GRAY });
  });
  s.addShape(pres.ShapeType.rect, { x: '10%', y: '80%', w: '80%', h: '12%', fill: { color: DARK }, line: { color: BLUE, width: 1 } });
  s.addText('🎉 1일 해커톤 → 실제 운영 가능한 AI 챗봇 완성', { x: '10%', y: '82%', w: '80%', fontSize: 16, color: LIGHT_BLUE, bold: true, align: 'center' });
  s.addText('팀 유니키로  |  최정아 · 유지원 · 김동현', { x: '10%', y: '87%', w: '80%', fontSize: 12, color: GRAY, align: 'center' });
}

pres.writeFile({ fileName: 'C:/Users/ryuji/unikiro/docs/Coupa_AI_Facilitator.pptx' })
  .then(() => console.log('✅ PPT 생성 완료'))
  .catch(err => console.error('❌ 오류:', err));
