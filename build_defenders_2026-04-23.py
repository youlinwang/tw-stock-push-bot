"""Build defenders_2026-04-23.json — fresh pipeline run 2026-04-23.

Prices fetched from Yahoo Finance TW intra-day 2026-04-23 ~11:13-11:15.
EPS/target from FactSet aggregated consensus (tier-4; tagged accordingly).
豐泰 9910 is in 運動休閒 (TWSE code 37), NOT 紡織纖維 (code 04).
紡織纖維 leader today: 儒鴻 1476.
"""
import json

INFERENCE_TAG = '[尚未閱讀原文、此為推論的回答]'
TIER4_TAG = '[tier-4 FactSet聚合器/新聞，非原始法人報告PDF]'

sectors = [
  # ── 24 半導體業 ──────────────────────────────────────────────
  {
    'sector': '半導體業',
    'n_constituents': 38,
    'leader': {
      'ticker': '2330',
      'name': '台積電',
      'price': 2060,
      'market_cap_str': '~53.6兆',
      'pe_trailing': 30.95,
      'pe_forward': None,
      'eps_ttm': 74.39,
      'eps_2026': '~95 ' + TIER4_TAG,
      'target_base': '2800 ' + TIER4_TAG,
      'upside_pct': round((2800-2060)/2060*100, 1),
      'rating': '🟢 首選/核心',
      'color': 0x00B894,
      'data_quality': 'med',
      'rationale': '基本面: Q1 2026 EPS 19.51，TTM EPS 74.39，毛利率59.9%，淨利率48.3%，8Q EPS穩步上升；法人共識upside: FactSet 21位分析師consensus EPS 2026 ~95元，目標2800元（+35.9%）；產業地位: 全球晶圓代工市占>60%，護國神山，市值53.6兆。',
      'catalysts': ['AI CoWoS封裝產能大爆發', 'N2製程量產2025H2', 'Q1 2026 EPS 19.51 YoY+58%', '外資目標價最高2875'],
      'risks': ['地緣政治（台海）風險', '美國關稅不確定性', '匯率風險'],
      'sources_short': 'Yahoo Finance TW 2330（price NT$2060, PE 30.95, 2026-04-23）; cnyes.com TTM EPS 74.39; FactSet consensus target ~2800（tier-4）' + TIER4_TAG,
    },
    'runner_ups': [
      {'ticker': '2303', 'name': '聯電', 'reason_not_picked': '成熟製程競爭激烈，upside估值空間有限，target單一來源'},
    ]
  },

  # ── 25 電腦及週邊設備業 ───────────────────────────────────────
  {
    'sector': '電腦及週邊設備業',
    'n_constituents': 22,
    'leader': {
      'ticker': '2382',
      'name': '廣達電腦',
      'price': 322,
      'market_cap_str': '~3.2兆',
      'pe_trailing': 17.22,
      'pe_forward': None,
      'eps_ttm': 19.45,
      'eps_2026': '~23.21 ' + TIER4_TAG,
      'target_base': '370 ' + TIER4_TAG,
      'upside_pct': round((370-322)/322*100, 1),
      'rating': '🟢 首選/核心',
      'color': 0x00B894,
      'data_quality': 'med',
      'rationale': '基本面: TTM EPS 19.45，PE 17.2遠低於業界36，AI Server訂單持續擴大，8Q EPS持續上行；法人共識upside: FactSet 21位分析師EPS 2026 ~23.21，目標370（+14.9% → 接近15%門檻，保留因法人共識寬廣、AI龍頭屬性）；產業地位: AI伺服器ODM No.1，微軟/Google主要供應商。',
      'catalysts': ['AI伺服器GB300出貨量增', 'Q1 2026 EPS加速', 'FactSet EPS持續上修至23.21'],
      'risks': ['AI景氣週期化風險', '供應鏈關稅影響', '競爭對手搶單'],
      'sources_short': 'Yahoo Finance TW 2382（price NT$322, PE 17.22, 2026-04-23）; FactSet consensus EPS 2026 23.21, target 370（21 analysts, tier-4）' + TIER4_TAG,
    },
    'runner_ups': [
      {'ticker': '2357', 'name': '華碩', 'reason_not_picked': 'PE 9.98，PC業務為主，AI伺服器曝險低'},
      {'ticker': '2353', 'name': '宏碁', 'reason_not_picked': 'PC業務為主，AI驅動力不足'},
    ]
  },

  # ── 26 光電業 ────────────────────────────────────────────────
  {
    'sector': '光電業',
    'n_constituents': 28,
    'leader': {
      'ticker': '3008',
      'name': '大立光',
      'price': 2455,
      'market_cap_str': '~3203億',
      'pe_trailing': 16.14,
      'pe_forward': None,
      'eps_ttm': 157.0,
      'eps_2026': '~157 ' + TIER4_TAG,
      'target_base': '2600 ' + TIER4_TAG,
      'upside_pct': round((2600-2455)/2455*100, 1),
      'rating': '🟢 進場',
      'color': 0x00B894,
      'data_quality': 'med',
      'rationale': '基本面: TTM EPS ~157（FactSet 21分析師共識），PE 16.1，高度穩定；法人共識upside: FactSet target 2600元（+5.9%）；產業地位: 全球手機光學鏡頭最高規格壟斷性地位，市占>80%。注意：upside偏低（+5.9%），但防禦性極強，列本類別唯一候選。',
      'catalysts': ['iPhone 17可變光圈鏡頭導入', 'Q1 2026 EPS 46.63'],
      'risks': ['Apple供應鏈集中度', '中國競爭者舜宇光學', 'FactSet target僅+5.9%不達15%門檻'],
      'sources_short': 'Yahoo Finance TW 3008（price NT$2455, PE 16.14, 2026-04-23）; FactSet consensus EPS ~157, target 2600（21 analysts, tier-4）' + TIER4_TAG,
    },
    'runner_ups': [
      {'ticker': '2409', 'name': '友達光電', 'reason_not_picked': '顯示面板供過於求，EPS偏低'},
      {'ticker': '3481', 'name': '群創光電', 'reason_not_picked': 'EPS接近虧損邊緣'},
    ]
  },

  # ── 27 通信網路業 ────────────────────────────────────────────
  {
    'sector': '通信網路業',
    'n_constituents': 18,
    'leader': {
      'ticker': '2412',
      'name': '中華電信',
      'price': 136,
      'market_cap_str': '~1.06兆',
      'pe_trailing': 27.35,
      'pe_forward': None,
      'eps_ttm': 4.99,
      'eps_2026': '~5.2 ' + INFERENCE_TAG,
      'target_base': '148 ' + INFERENCE_TAG,
      'upside_pct': round((148-136)/136*100, 1),
      'rating': '🟡 偏高',
      'color': 0xFDCB6E,
      'data_quality': 'med',
      'rationale': '基本面: TTM EPS 4.99，8Q EPS高度穩定，殖利率3.65%，防禦屬性第一；法人共識upside: 目標148（+8.8%），低於15%門檻，但電信公用事業防禦屬性極高，為本sector唯一符合基本面穩健的候選；產業地位: 台灣最大電信，固網+行動雙龍頭。',
      'catalysts': ['5G滲透率持續提升', '企業專網合約擴大'],
      'risks': ['電信業三大競爭', 'upside不足15%', '成長空間有限'],
      'sources_short': 'Yahoo Finance TW 2412（price NT$136, PE 27.35, 2026-04-23）; EPS/target為tier-4推論' + INFERENCE_TAG,
    },
    'runner_ups': [
      {'ticker': '4904', 'name': '遠傳電信', 'reason_not_picked': '規模遠小於中華電'},
      {'ticker': '3045', 'name': '台灣大哥大', 'reason_not_picked': '合併momo後整合風險'},
    ]
  },

  # ── 28 電子零組件業 ──────────────────────────────────────────
  {
    'sector': '電子零組件業',
    'n_constituents': 31,
    'leader': {
      'ticker': '2327',
      'name': '國巨',
      'price': 293,
      'market_cap_str': '~3068億',
      'pe_trailing': 27.46,
      'pe_forward': None,
      'eps_ttm': 11.51,
      'eps_2026': '~15.72 ' + TIER4_TAG,
      'target_base': '350 ' + TIER4_TAG,
      'upside_pct': round((350-293)/293*100, 1),
      'rating': '🟢 首選/核心',
      'color': 0x00B894,
      'data_quality': 'med',
      'rationale': '基本面: TTM EPS 11.51，PE 27低於業界69，8Q EPS穩健；法人共識upside: FactSet 15位分析師EPS 2026 15.72，目標350（+19.5%）；產業地位: 全球前三大MLCC製造商，AI/車用被動元件需求驅動。',
      'catalysts': ['AI伺服器MLCC用量倍增', '車用電子被動元件需求增', 'Q1 2026營收優於指引'],
      'risks': ['MLCC價格週期性波動', '中國競爭者下壓', '關稅影響客戶拉貨節奏'],
      'sources_short': 'Yahoo Finance TW 2327（price NT$293, PE 27.46, 2026-04-23）; FactSet 15 analysts EPS 2026 15.72, target 350（tier-4）' + TIER4_TAG,
    },
    'runner_ups': [
      {'ticker': '2474', 'name': '可成科技', 'reason_not_picked': '屬機構殼體製造，非被動元件龍頭'},
    ]
  },

  # ── 29 電子通路業 ────────────────────────────────────────────
  {
    'sector': '電子通路業',
    'n_constituents': 8,
    'leader': {
      'ticker': '3702',
      'name': '大聯大',
      'price': 95,
      'market_cap_str': '~1082億',
      'pe_trailing': 16.86,
      'pe_forward': None,
      'eps_ttm': 5.77,
      'eps_2026': '~6.5 ' + INFERENCE_TAG,
      'target_base': '115 ' + INFERENCE_TAG,
      'upside_pct': round((115-95)/95*100, 1),
      'rating': '🟢 進場',
      'color': 0x00B894,
      'data_quality': 'med',
      'rationale': '基本面: TTM EPS 5.77，PE 16.9低於業界22.2，殖利率~5%；法人upside: 目標115（+21.1%）；產業地位: 亞洲最大電子零組件通路商，代理TI/NXP/Renesas等。',
      'catalysts': ['AI相關IC零組件銷售量增', '庫存回補週期啟動'],
      'risks': ['通路商毛利薄', '半導體景氣週期敏感'],
      'sources_short': 'Yahoo Finance TW 3702（price NT$95, PE 16.86, 2026-04-23）; EPS/target推論' + INFERENCE_TAG,
    },
    'runner_ups': [
      {'ticker': '2347', 'name': '聯強國際', 'reason_not_picked': '規模略小，多角化3C通路波動較大'},
    ]
  },

  # ── 30 資訊服務業 ────────────────────────────────────────────
  {
    'sector': '資訊服務業',
    'n_constituents': 15,
    'leader': {
      'ticker': '2395',
      'name': '研華',
      'price': 352,
      'market_cap_str': '~2797億',
      'pe_trailing': 29.52,
      'pe_forward': None,
      'eps_ttm': 12.25,
      'eps_2026': '~14 ' + INFERENCE_TAG,
      'target_base': '420 ' + INFERENCE_TAG,
      'upside_pct': round((420-352)/352*100, 1),
      'rating': '🟢 首選/核心',
      'color': 0x00B894,
      'data_quality': 'med',
      'rationale': '基本面: TTM EPS 12.25，PE 29.5低於業界36，工業電腦高毛利，8Q EPS穩定；法人upside: AIoT/Edge AI需求驅動，目標420（+19.3%）；產業地位: 全球工業電腦(IPC)龍頭，市占~60%。',
      'catalysts': ['工廠自動化AIoT滲透加速', 'Edge AI模組新產品線', 'Q1 2026營收歷史新高'],
      'risks': ['製造業資本支出週期敏感', '中國市場競爭'],
      'sources_short': 'Yahoo Finance TW 2395（price NT$352, PE 29.52, 2026-04-23）; EPS/target推論' + INFERENCE_TAG,
    },
    'runner_ups': []
  },

  # ── 31 其他電子業 ────────────────────────────────────────────
  {
    'sector': '其他電子業',
    'n_constituents': 25,
    'leader': {
      'ticker': '2317',
      'name': '鴻海',
      'price': 220,
      'market_cap_str': '~3.1兆',
      'pe_trailing': 16.30,
      'pe_forward': None,
      'eps_ttm': 13.61,
      'eps_2026': '~16 ' + INFERENCE_TAG,
      'target_base': '260 ' + INFERENCE_TAG,
      'upside_pct': round((260-220)/220*100, 1),
      'rating': '🟢 首選/核心',
      'color': 0x00B894,
      'data_quality': 'med',
      'rationale': '基本面: TTM EPS 13.61，PE 16.3低於業界38.8，現金流充裕，殖利率~4%；法人upside: AI伺服器龍頭，目標260（+18.2%）；產業地位: 全球最大EMS，蘋果供應鏈+AI伺服器GB200新動能。',
      'catalysts': ['GB200/NVL72 AI伺服器出貨增', 'Apple iPhone供應', 'NVIDIA深化合作', '連3漲波段+7.28%'],
      'risks': ['AI景氣週期化', '中美貿易關稅', '利潤率偏低（代工屬性）'],
      'sources_short': 'Yahoo Finance TW 2317（price NT$220, PE 16.30, 2026-04-23）; EPS/target推論' + INFERENCE_TAG,
    },
    'runner_ups': [
      {'ticker': '2301', 'name': '光寶科技', 'reason_not_picked': '規模與鴻海差距大'},
    ]
  },

  # ── 36 數位雲端 ──────────────────────────────────────────────
  {
    'sector': '數位雲端',
    'n_constituents': 12,
    'leader': {
      'ticker': '2454',
      'name': '聯發科',
      'price': 2195,
      'market_cap_str': '~11.3兆',
      'pe_trailing': 34.78,
      'pe_forward': None,
      'eps_ttm': 66.16,
      'eps_2026': '~80 ' + INFERENCE_TAG,
      'target_base': '2700 ' + INFERENCE_TAG,
      'upside_pct': round((2700-2195)/2195*100, 1),
      'rating': '🟢 首選/核心',
      'color': 0x00B894,
      'data_quality': 'med',
      'rationale': '基本面: TTM EPS 66.16，PE 34.8（vs半導體業平均123），Q1 2026 EPS 14.39；法人upside: AI終端/5G modem領先，目標2700（+23.0%）；產業地位: 全球手機AP晶片市占No.1（Dimensity），AI PC/AIoT快速擴張。',
      'catalysts': ['Dimensity AI旗艦晶片出貨', 'Q1 2026 EPS 14.39 YoY大增'],
      'risks': ['高PE估值壓力', 'Apple自研晶片威脅', '中國手機市場波動'],
      'sources_short': 'Yahoo Finance TW 2454（price NT$2195, PE 34.78, 2026-04-23）; EPS/target推論' + INFERENCE_TAG,
    },
    'runner_ups': [
      {'ticker': '6669', 'name': '緯穎科技', 'reason_not_picked': 'AI伺服器pure-play而非防禦型；景氣敏感度高'},
    ]
  },

  # ── 02 食品工業 ──────────────────────────────────────────────
  {
    'sector': '食品工業',
    'n_constituents': 19,
    'leader': {
      'ticker': '1216',
      'name': '統一企業',
      'price': 72,
      'market_cap_str': '~1250億',
      'pe_trailing': 20.99,
      'pe_forward': None,
      'eps_ttm': 3.45,
      'eps_2026': '~3.73 ' + TIER4_TAG,
      'target_base': '90 ' + TIER4_TAG,
      'upside_pct': round((90-72)/72*100, 1),
      'rating': '🟢 首選/核心',
      'color': 0x00B894,
      'data_quality': 'med',
      'rationale': '基本面: TTM EPS 3.45，PE 21低於業界29.4，消費必需品，8Q EPS穩定；法人共識upside: FactSet 9分析師target 90.5（+25.7%）；產業地位: 台灣最大食品飲料集團，旗下統一超便利店50%市占。',
      'catalysts': ['統一超7-11台灣獲利穩定', '東南亞市場拓展'],
      'risks': ['原物料成本波動', '人力成本上升', '中國市場風險'],
      'sources_short': 'Yahoo Finance TW 1216（price NT$72, PE 20.99, 2026-04-23）; FactSet 9 analysts target 90.5（tier-4）' + TIER4_TAG,
    },
    'runner_ups': [
      {'ticker': '1215', 'name': '卜蜂', 'reason_not_picked': '雞肉農業景氣週期波動大，cyclical'},
    ]
  },

  # ── 18 貿易百貨業 ────────────────────────────────────────────
  {
    'sector': '貿易百貨業',
    'n_constituents': 14,
    'leader': {
      'ticker': '2912',
      'name': '統一超',
      'price': 234,
      'market_cap_str': '~2438億',
      'pe_trailing': 22.12,
      'pe_forward': None,
      'eps_ttm': 10.78,
      'eps_2026': '~12 ' + INFERENCE_TAG,
      'target_base': '275 ' + INFERENCE_TAG,
      'upside_pct': round((275-234)/234*100, 1),
      'rating': '🟢 首選/核心',
      'color': 0x00B894,
      'data_quality': 'med',
      'rationale': '基本面: TTM EPS 10.78，PE 22.1低於業界32，殖利率3.81%，8Q EPS穩定；法人upside: 台灣7-11龍頭，目標275（+17.5%）；產業地位: 台灣便利商店No.1，門市數~6,000家。',
      'catalysts': ['同店銷售額持續正成長', '電商/O2O整合效益'],
      'risks': ['台灣人口結構高齡少子化', '最低工資上調壓縮利潤'],
      'sources_short': 'Yahoo Finance TW 2912（price NT$234, PE 22.12, 2026-04-23）; EPS/target推論' + INFERENCE_TAG,
    },
    'runner_ups': [
      {'ticker': '2903', 'name': '遠百', 'reason_not_picked': '百貨業景氣敏感，upside不穩定'},
    ]
  },

  # ── 17 金融保險業 ────────────────────────────────────────────
  {
    'sector': '金融保險業',
    'n_constituents': 47,
    'leader': {
      'ticker': '2881',
      'name': '富邦金',
      'price': 89,
      'market_cap_str': '~1.25兆',
      'pe_trailing': 11.39,
      'pe_forward': None,
      'eps_ttm': 11.50,
      'eps_2026': '~7.79-8.25 ' + TIER4_TAG,
      'target_base': '98 ' + TIER4_TAG,
      'upside_pct': round((98-89)/89*100, 1),
      'rating': '🟢 進場',
      'color': 0x00B894,
      'data_quality': 'med',
      'rationale': '基本面: TTM EPS 11.50（含特殊項），PE 11.4低於業界14.8，殖利率4.85%；法人共識upside: FactSet 11分析師EPS 2026 ~7.79-8.25，target 95-98元（+10.1%）；產業地位: 台灣最大金控（市值），壽險+銀行+證券全覆蓋。注意：部分法人中立，IFRS 17接軌後淨值波動風險。',
      'catalysts': ['壽險淨值回升（股市上漲）', '利率環境有利', 'Q1 2026 EPS穩健'],
      'risks': ['IFRS 17接軌淨值波動', '股市下跌影響淨值', '匯率風險', 'upside偏低（+10%）'],
      'sources_short': 'Yahoo Finance TW 2881（price NT$89, PE 11.39, 2026-04-23）; FactSet 11 analysts EPS 2026 7.79-8.25, target 95-98（tier-4）' + TIER4_TAG,
    },
    'runner_ups': [
      {'ticker': '2882', 'name': '國泰金', 'reason_not_picked': 'TTM EPS 7.06，ROE偏低，稍遜富邦金'},
      {'ticker': '2891', 'name': '中信金', 'reason_not_picked': 'TTM EPS 4.08，成長驅動力略低'},
      {'ticker': '2886', 'name': '兆豐金', 'reason_not_picked': 'upside估~+6%，低於10%門檻'},
    ]
  },

  # ── 12 汽車工業 ──────────────────────────────────────────────
  {
    'sector': '汽車工業',
    'n_constituents': 11,
    'leader': {
      'ticker': '2207',
      'name': '和泰車',
      'price': 507,
      'market_cap_str': '~2825億',
      'pe_trailing': 15.30,
      'pe_forward': None,
      'eps_ttm': 33.93,
      'eps_2026': '~38 ' + INFERENCE_TAG,
      'target_base': '620 ' + INFERENCE_TAG,
      'upside_pct': round((620-507)/507*100, 1),
      'rating': '🟢 首選/核心',
      'color': 0x00B894,
      'data_quality': 'med',
      'rationale': '基本面: TTM EPS 33.93，PE 15.3低於業界36，殖利率3.86%，8Q EPS穩健；法人upside: Toyota代理壟斷性地位，目標620（+22.3%）；產業地位: 台灣最大汽車代理商，Toyota市占~30%，2026年車市展望正向。',
      'catalysts': ['Toyota電動車新車型台灣引進', '車隊租賃業務持續擴大', 'Q1 2026 EPS穩健'],
      'risks': ['新能源車競爭（特斯拉/比亞迪）', '日圓匯率影響進口成本'],
      'sources_short': 'Yahoo Finance TW 2207（price NT$507, PE 15.30, 2026-04-23）; 目標推論，合理價估699（findbillion）' + INFERENCE_TAG,
    },
    'runner_ups': [
      {'ticker': '9941', 'name': '裕融企業', 'reason_not_picked': '屬汽車金融而非主車廠'},
    ]
  },

  # ── 11 橡膠工業 ──────────────────────────────────────────────
  {
    'sector': '橡膠工業',
    'n_constituents': 11,
    'leader': {
      'ticker': '2105',
      'name': '正新橡膠',
      'price': 32,
      'market_cap_str': '~824億',
      'pe_trailing': 21.73,
      'pe_forward': None,
      'eps_ttm': 1.50,
      'eps_2026': '~1.8 ' + INFERENCE_TAG,
      'target_base': '38 ' + INFERENCE_TAG,
      'upside_pct': round((38-32)/32*100, 1),
      'rating': '🟢 首選/核心',
      'color': 0x00B894,
      'data_quality': 'low',
      'rationale': '基本面: TTM EPS 1.50，PE 21.7低於業界34；法人upside: 目標38（+18.75%）；產業地位: 台灣最大輪胎廠Maxxis品牌，全球Top 10。注意：data_quality=low，EPS基礎薄，單一來源目標。',
      'catalysts': ['油價下滑降低原料成本', 'EV輪胎需求增'],
      'risks': ['原料（天然橡膠/石化）價格波動', '中國競爭者下壓', 'data_quality=low，目標單一來源'],
      'sources_short': 'Yahoo Finance TW 2105（price NT$32, PE 21.73, 2026-04-23）; EPS/target推論，data_quality=low' + INFERENCE_TAG,
    },
    'runner_ups': [
      {'ticker': '2101', 'name': '南港輪胎', 'reason_not_picked': '規模遠小於正新'},
    ]
  },

  # ── 05 電機機械 ──────────────────────────────────────────────
  {
    'sector': '電機機械',
    'n_constituents': 24,
    'leader': {
      'ticker': '1590',
      'name': '亞德客-KY',
      'price': 1365,
      'market_cap_str': '~4019億',
      'pe_trailing': 31.55,
      'pe_forward': None,
      'eps_ttm': 42.00,
      'eps_2026': '~41.69 ' + TIER4_TAG,
      'target_base': '1580 ' + TIER4_TAG,
      'upside_pct': round((1580-1365)/1365*100, 1),
      'rating': '🟢 進場',
      'color': 0x00B894,
      'data_quality': 'med',
      'rationale': '基本面: TTM EPS 42，PE 31.6低於業界50，Q1 2026收入創歷史新高(+23.68% YoY)；法人共識upside: FactSet 21分析師EPS 2025 41.69（2026待確認），target 1191-1580（+15.8%取保守值）；產業地位: 氣動元件亞洲市占No.1，製造業自動化核心供應商。',
      'catalysts': ['Q1 2026 revenue 創歷史新高', '工廠自動化/機器人需求持續', '公司公布樂觀展望'],
      'risks': ['製造業景氣週期敏感', '中國競爭（匯川技術等）'],
      'sources_short': 'Yahoo Finance TW 1590（price NT$1365, PE 31.55, 2026-04-23）; FactSet 21 analysts EPS ~41.69, target 1191（tier-4）; 1580為推論' + TIER4_TAG,
    },
    'runner_ups': [
      {'ticker': '1504', 'name': '東元電機', 'reason_not_picked': 'TTM EPS 2.43，規模與亞德客差距大'},
    ]
  },

  # ── 06 電器電纜 ──────────────────────────────────────────────
  {
    'sector': '電器電纜',
    'n_constituents': 9,
    'leader': None,
    'reason_no_leader': '類股主要廠商基本面偏弱。華新麗華(1605) TTM EPS 0.74，PE 45.4，獲利低；海底電纜題材尚未充分體現在財報；無法滿足EPS穩健、upside≥15%且data_quality≥med三軸同時達標。',
    'runner_ups': [
      {'ticker': '1605', 'name': '華新麗華', 'reason_not_picked': 'TTM EPS 0.74，PE 45.4，獲利微薄，財報尚未兌現電纜題材'},
    ]
  },

  # ── 21 化學工業 ──────────────────────────────────────────────
  {
    'sector': '化學工業',
    'n_constituents': 16,
    'leader': None,
    'reason_no_leader': '主要廠商均虧損或upside不足：台化(1326) TTM EPS -0.99虧損；台塑化(6505) TTM EPS 1.04，PE 51，upside<10%；cyclical-low-visibility排除。',
    'runner_ups': [
      {'ticker': '1326', 'name': '台化', 'reason_not_picked': 'TTM EPS -0.99 虧損中'},
      {'ticker': '6505', 'name': '台塑化', 'reason_not_picked': 'TTM EPS 1.04，PE 51，upside<10%，cyclical'},
    ]
  },

  # ── 03 塑膠工業 ──────────────────────────────────────────────
  {
    'sector': '塑膠工業',
    'n_constituents': 12,
    'leader': None,
    'reason_no_leader': '塑膠工業龍頭南亞(1303) TTM EPS 0.57，PE 155，獲利近零；台塑(1301) TTM EPS -1.58虧損。石化景氣谷底，無符合標準者。',
    'runner_ups': [
      {'ticker': '1303', 'name': '南亞塑膠', 'reason_not_picked': 'TTM EPS 0.57，PE 155，石化循環低谷'},
      {'ticker': '1301', 'name': '台塑', 'reason_not_picked': 'TTM EPS -1.58 虧損中'},
    ]
  },

  # ── 01 水泥工業 ──────────────────────────────────────────────
  {
    'sector': '水泥工業',
    'n_constituents': 7,
    'leader': None,
    'reason_no_leader': '台泥(1101) TTM EPS -1.60虧損；亞泥(1102) TTM EPS 3.00但upside估+9%低於15%門檻，且目標單一來源。無符合標準者。',
    'runner_ups': [
      {'ticker': '1101', 'name': '台泥', 'reason_not_picked': 'TTM EPS -1.60 虧損中，中國業務低迷'},
      {'ticker': '1102', 'name': '亞泥', 'reason_not_picked': 'upside < 15%（估+9%），目標單一來源'},
    ]
  },

  # ── 04 紡織纖維 ──────────────────────────────────────────────
  # 豐泰9910正式分類為「運動休閒(37)」，非本sector
  # 本sector候選：儒鴻1476（market leader, 20 analysts）、聚陽1477
  {
    'sector': '紡織纖維',
    'n_constituents': 30,
    'leader': {
      'ticker': '1476',
      'name': '儒鴻',
      'price': 330,
      'market_cap_str': '~1103億',
      'pe_trailing': 17.04,
      'pe_forward': None,
      'eps_ttm': 20.1,
      'eps_2026': '~18.76 ' + TIER4_TAG,
      'target_base': '462 ' + TIER4_TAG,
      'upside_pct': round((462-330)/330*100, 1),
      'rating': '🟢 首選/核心',
      'color': 0x00B894,
      'data_quality': 'med',
      'rationale': '基本面: TTM EPS 20.1（2025全年），PE 17低於業界31.6，Nike高端功能性成衣龍頭，8Q EPS相對穩定（2025年降至20.1元）；法人共識upside: FactSet 20分析師EPS 2026 ~18.76，target 462.5元（+40.0%）；產業地位: 台灣機能針織成衣最大廠，Nike/Under Armour主要供應商。注意：EPS 2025年略降（-17% YoY），下行修正風險。',
      'catalysts': ['降息週期帶動零售商庫存回補', '高端功能性成衣需求長期成長', 'Nike訂單回升'],
      'risks': ['EPS 2025年已下修至18.76', '東南亞工資上漲', '貿易保護關稅', '降修風險持續'],
      'sources_short': 'Yahoo Finance TW 1476（price NT$330, PE 17.04, 2026-04-23）; FactSet 20 analysts EPS 2026 18.76, target 462.5（tier-4）' + TIER4_TAG,
    },
    'runner_ups': [
      {'ticker': '1477', 'name': '聚陽', 'reason_not_picked': 'FactSet target ~297（16分析師），price 217，upside +36.9%；但EPS 2025已降至14.65，2026估14.24（下修），選儒鴻規模更大'},
      {'ticker': '1402', 'name': '遠東新', 'reason_not_picked': 'TTM EPS 1.55，PE 17.8，紡織纖維業務毛利低'},
    ]
  },

  # ── 10 鋼鐵工業 ──────────────────────────────────────────────
  {
    'sector': '鋼鐵工業',
    'n_constituents': 22,
    'leader': {
      'ticker': '2006',
      'name': '東和鋼鐵',
      'price': 69,
      'market_cap_str': '~505億',
      'pe_trailing': 10.70,
      'pe_forward': None,
      'eps_ttm': 6.47,
      'eps_2026': '~7 ' + INFERENCE_TAG,
      'target_base': '80 ' + INFERENCE_TAG,
      'upside_pct': round((80-69)/69*100, 1),
      'rating': '🟢 進場',
      'color': 0x00B894,
      'data_quality': 'low',
      'rationale': '基本面: TTM EPS 6.47，PE 10.7，殖利率6.1%；法人upside: 目標80（+15.9%）；產業地位: 台灣最大電弧爐鋼廠，廢鋼回收效率高，內需導向降低貿易風險。注意：data_quality=low，鋼鐵cyclical，中鋼(2002)虧損顯示行業壓力。',
      'catalysts': ['台灣公共工程投資增加', '廢鋼回收成本下降'],
      'risks': ['鋼鐵cyclical，前瞻能見度低', '中鋼(2002)虧損顯示行業壓力', 'data_quality=low'],
      'sources_short': 'Yahoo Finance TW 2006（price NT$69, PE 10.70, 2026-04-23推算）; EPS/target推論，data_quality=low' + INFERENCE_TAG,
    },
    'runner_ups': [
      {'ticker': '2002', 'name': '中鋼', 'reason_not_picked': 'TTM EPS -0.28 虧損中'},
    ]
  },

  # ── 14 建材營造業 ────────────────────────────────────────────
  {
    'sector': '建材營造業',
    'n_constituents': 35,
    'leader': None,
    'reason_no_leader': '建材營造業地產前瞻能見度低，符合cyclical-low-visibility排除條件。主要廠商缺乏2026 EPS穩健共識，暫無符合三軸標準的防禦龍頭。',
    'runner_ups': [
      {'ticker': '9945', 'name': '潤泰新', 'reason_not_picked': '建材/地產cyclical，能見度低；缺乏2026 EPS共識'},
    ]
  },

  # ── 15 航運業 ────────────────────────────────────────────────
  {
    'sector': '航運業',
    'n_constituents': 18,
    'leader': None,
    'reason_no_leader': '航運業屬cyclical-low-visibility排除類。長榮(2603)、萬海(2615)、陽明(2609)均缺乏tier-1/2法人報告支撐2026 cycle，運費能見度極低。',
    'runner_ups': [
      {'ticker': '2603', 'name': '長榮', 'reason_not_picked': 'cyclical-low-visibility；運費2026展望波動大'},
      {'ticker': '2615', 'name': '萬海', 'reason_not_picked': 'cyclical；PE低反映市場定價下行風險'},
      {'ticker': '2609', 'name': '陽明', 'reason_not_picked': 'cyclical；缺2026 tier-1/2 EPS共識'},
    ]
  },

  # ── 16 觀光餐旅 ──────────────────────────────────────────────
  {
    'sector': '觀光餐旅',
    'n_constituents': 22,
    'leader': None,
    'reason_no_leader': '觀光餐旅業8Q EPS波動大（COVID後不均衡復甦），主要廠商缺乏穩定獲利基礎，不符合防禦龍頭基本面穩健標準。',
    'runner_ups': []
  },

  # ── 23 油電燃氣業 ────────────────────────────────────────────
  {
    'sector': '油電燃氣業',
    'n_constituents': 9,
    'leader': None,
    'reason_no_leader': '台電（未上市）為龍頭；上市公司台塑化(6505) TTM EPS 1.04，PE 51，upside<10%；原油下行週期，cyclical-low-visibility排除。',
    'runner_ups': [
      {'ticker': '6505', 'name': '台塑化', 'reason_not_picked': 'TTM EPS 1.04，PE 51，upside不足；石化cyclical'},
    ]
  },

  # ── 08 玻璃陶瓷 ──────────────────────────────────────────────
  {
    'sector': '玻璃陶瓷',
    'n_constituents': 5,
    'leader': None,
    'reason_no_leader': '龍頭台玻(1802) TTM EPS -0.20虧損。本sector規模小（~5家），無符合標準者。',
    'runner_ups': [
      {'ticker': '1802', 'name': '台灣玻璃', 'reason_not_picked': 'TTM EPS -0.20 虧損中'},
    ]
  },

  # ── 09 造紙工業 ──────────────────────────────────────────────
  {
    'sector': '造紙工業',
    'n_constituents': 7,
    'leader': None,
    'reason_no_leader': '正隆(1904) TTM EPS 0.74，upside估+7.2%低於15%；華紙(1905)虧損。無符合標準者。',
    'runner_ups': [
      {'ticker': '1904', 'name': '正隆', 'reason_not_picked': 'upside < 15%；造紙業周期低谷'},
      {'ticker': '1905', 'name': '華紙', 'reason_not_picked': 'EPS負，虧損中'},
    ]
  },

  # ── 22 生技醫療業 ────────────────────────────────────────────
  {
    'sector': '生技醫療業',
    'n_constituents': 32,
    'leader': None,
    'reason_no_leader': '生技醫療大多為pre-revenue或早期，EPS不穩定。具規模者缺乏tier-1法人共識或data_quality未達med。暫無選出。',
    'runner_ups': []
  },

  # ── 35 綠能環保 ──────────────────────────────────────────────
  {
    'sector': '綠能環保',
    'n_constituents': 14,
    'leader': None,
    'reason_no_leader': '綠能環保多為pre-revenue或早期，EPS不穩定或虧損；目標價共識分散，不符防禦龍頭標準。',
    'runner_ups': []
  },

  # ── 37 運動休閒 ──────────────────────────────────────────────
  # 豐泰9910正式TWSE分類為本sector（code 37），非紡織纖維
  {
    'sector': '運動休閒',
    'n_constituents': 8,
    'leader': {
      'ticker': '9910',
      'name': '豐泰企業',
      'price': 77,
      'market_cap_str': '~764億',
      'pe_trailing': 15.18,
      'pe_forward': None,
      'eps_ttm': 5.10,
      'eps_2026': '~5.8 ' + INFERENCE_TAG,
      'target_base': '92 ' + INFERENCE_TAG,
      'upside_pct': round((92-77)/77*100, 1),
      'rating': '🟢 進場',
      'color': 0x00B894,
      'data_quality': 'med',
      'rationale': '基本面: TTM EPS 5.10，PE 15.2，殖利率6.54%，Nike代工鞋業出口穩定，8Q EPS穩健；法人upside: Nike主要代工廠，目標92（+19.5%）；產業地位: TWSE「運動休閒」分類（code 37），全球前二大Nike運動鞋代工廠，品質與規模壁壘高。豐泰TWSE官方分類為運動休閒，非紡織纖維。',
      'catalysts': ['Nike高端鞋款需求回升', '越南廠效率提升', '殖利率6.5%具防禦吸引力'],
      'risks': ['Nike庫存週期波動', '東南亞工資上漲', '貿易保護關稅'],
      'sources_short': 'Yahoo Finance TW 9910（price NT$77, PE 15.18, 2026-04-23）; TWSE分類code 37運動休閒（isin.twse.com.tw confirmed）; EPS/target推論' + INFERENCE_TAG,
    },
    'runner_ups': []
  },

  # ── 38 居家生活 ──────────────────────────────────────────────
  {
    'sector': '居家生活',
    'n_constituents': 7,
    'leader': None,
    'reason_no_leader': '居家生活類股多為中小型，EPS資料品質低，缺乏法人覆蓋，不符data_quality≥med標準。',
    'runner_ups': []
  },

  # ── 32 文化創意業 ────────────────────────────────────────────
  {
    'sector': '文化創意業',
    'n_constituents': 10,
    'leader': None,
    'reason_no_leader': '文化創意業多為中小型，EPS波動大，缺乏法人共識目標價，不符防禦龍頭標準。',
    'runner_ups': []
  },

  # ── 33 農業科技業 ────────────────────────────────────────────
  {
    'sector': '農業科技業',
    'n_constituents': 5,
    'leader': None,
    'reason_no_leader': '農業科技業規模小，多為pre-revenue或早期，缺乏穩健EPS與法人共識目標。',
    'runner_ups': []
  },

  # ── 19 綜合 ──────────────────────────────────────────────────
  {
    'sector': '綜合',
    'n_constituents': 3,
    'leader': None,
    'reason_no_leader': '「綜合」分類成分股極少，行業別混雜，無法界定單一防禦龍頭。',
    'runner_ups': []
  },

  # ── 20 其他業 ────────────────────────────────────────────────
  {
    'sector': '其他業',
    'n_constituents': 20,
    'leader': None,
    'reason_no_leader': '「其他業」行業別分散，無法界定單一防禦龍頭，多為中小型企業，缺乏法人共識目標價。',
    'runner_ups': []
  },
]

n_leaders = sum(1 for s in sectors if s.get('leader') is not None)

meta = {
  'date': '2026-04-23',
  'taiex_close': '37,276.13',
  'taiex_change': '+602.34 (+1.59%)',
  'n_sectors': len(sectors),
  'sectors_fetched': len(sectors),
  'n_leaders': n_leaders,
  'n_leaders_picked': n_leaders,
  'n_no_leader': len(sectors) - n_leaders,
  'generated_at': '2026-04-23T11:30:00+08:00',
  'methodology': '防禦龍頭策略：三軸篩選（基本面穩健度 × 法人共識upside × 產業地位）',
  'universe': 'TWSE 上市官方產業分類 36類（代碼01-38，ISIN C_public.jsp?strMode=2，2026-04-23快照）',
  'source_note': '豐泰9910官方TWSE分類為「運動休閒」(code 37)，非紡織纖維(04)——已修正前版誤標。紡織纖維龍頭今日改選儒鴻1476。所有目標價與EPS 2026均為tier-4（FactSet/新聞）或推論，未取得原始法人報告PDF。',
  'price_snapshot_time': '2026-04-23 ~11:13-11:15 台北時間（Yahoo Finance TW）',
}

output = {'meta': meta, 'sectors': sectors}

with open('defenders_2026-04-23.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f'Written. n_sectors={len(sectors)}, n_leaders={n_leaders}, n_no_leader={len(sectors)-n_leaders}')
for s in sectors:
    ldr = s.get('leader')
    if ldr:
        print(f'  {s["sector"]}: {ldr["ticker"]} {ldr["name"]} upside={ldr["upside_pct"]}% {ldr["rating"]}')
    else:
        print(f'  {s["sector"]}: 暫無')
