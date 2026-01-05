from ..utils.datetime_utils import get_beijing_date_str


def get_image_parse_prompt() -> str:
    current_date = get_beijing_date_str()
    return f"""请分析账单截图，严格按照以下JSON格式返回。

### 核心规则（违反将导致记账失败）：
1. **分类唯一性**：`category` 必须【百分之百】匹配下方列表。禁止返回“餐饮美食”、“交通出行”等列表外词汇。
2. **逻辑推断**：如果商家是“肯德基”且时间在11:00-14:00，category="午餐"；若无时间，默认选“午餐”。
3. **输出格式**：只返回纯JSON字符串，严禁包含任何Markdown标签（如 ```json）或解释性文字。

{{
  "date": "YYYY-MM-DD",
  "amount": 0.0,
  "merchant": "",
  "payment_method": "支付宝/微信/银行卡/现金",
  "bank_name": "CCB/BOC/ICBC/NONE",
  "card_last_four": "XXXX",
  "transaction_type": "expense/income",
  "category": "必须从预设列表中选择",
  "description": ""
}}

### 预设分类白名单（禁止超出此范围）：
- 餐饮类：早餐, 午餐, 晚餐, 零食, 买菜
- 交通类：公交, 打车, 加油
- 住房类：房租, 水电, 宽带
- 购物类：衣服, 数码, 日用品
- 娱乐类：电影, 游戏, 聚餐
- 医疗类：药品, 看病
- 其他类：红包, 其他
- 收入类：工资, 奖金, 投资

### 银行卡识别：
- 建设银行/CCB -> "CCB", 中国银行/BOC -> "BOC", 工商银行/ICBC -> "ICBC"
- 若非银行卡支付，bank_name填"NONE"，card_last_four填"0000"

### 强制映射示例：
- 识别到商家“美团外卖” -> 检查时间 -> 返回 "午餐" (不可返回"外卖")
- 识别到商家“全家便利店” -> 返回 "零食" (不可返回"便利店")
- 识别到商家“滴滴” -> 返回 "打车" (不可返回"交通出行")

今天日期是：{current_date}"""


def get_text_parse_prompt() -> str:
    """生成文本解析prompt，包含当前日期"""
    current_date = get_beijing_date_str()
    return f"""请解析用户的记账文本，提取以下信息并以JSON格式返回。

当前北京时间（UTC+8）：{current_date}

返回格式：
{{
  "date": "YYYY-MM-DD格式的日期（如果用户没提供，使用今天{current_date}）",
  "amount": 金额（数字），
  "merchant": "商家名称或描述",
  "payment_method": "支付方式（支付宝/微信/现金/银行卡）",
  "bank_name": "银行简称（CCB/BOC/ICBC）",
  "card_last_four": "银行卡后四位数字",
  "transaction_type": "expense或income",
  "category": "精确分类（见下方列表）",
  "description": "简短描述"
}}

【支付方式识别规则】
1. 支付宝/宝 → payment_method="支付宝"
2. 微信/wx → payment_method="微信"
3. 现金 → payment_method="现金"
4. 银行卡/建行/中行/工行/带卡号 → payment_method="银行卡"
   - 建设银行/建行/CCB/建 → bank_name="CCB"
   - 中国银行/中行/BOC/中 → bank_name="BOC"
   - 工商银行/工行/ICBC/工 → bank_name="ICBC"
   - 识别4位数字作为card_last_four，如"0388"、"8735"

【支出分类列表】必须从以下选项中选择
餐饮：早餐、午餐、晚餐、零食、买菜
交通：公交、打车、加油
住房：房租、水电、宽带
购物：衣服、数码、日用品
娱乐：电影、游戏、聚餐
医疗：药品、看病
其他：红包、其他

【收入分类】
工资、奖金、投资

【智能分类规则】
- 早饭/早点/包子/豆浆 → 早餐
- 午饭/午餐/外卖 → 午餐
- 晚饭/晚餐/夜宵 → 晚餐
- 零食/饮料/奶茶/水果/咖啡 → 零食
- 菜市场/超市买菜/盒马 → 买菜
- 地铁/公交/公共交通 → 公交
- 滴滴/打车/出租车/taxi → 打车
- 加油/充电/中石化/中石油 → 加油
- 房租/租金 → 房租
- 水费/电费/燃气/水电费 → 水电
- 话费/流量/宽带/网费 → 宽带
- 衣服/鞋/裤子/外套 → 衣服
- 手机/电脑/耳机/数码产品 → 数码
- 洗发水/牙膏/日化/生活用品 → 日用品
- 看电影/电影票/影院 → 电影
- 游戏/充值/steam → 游戏
- 聚餐/请客/饭局 → 聚餐
- 药/药店/买药 → 药品
- 挂号/医院/看病 → 看病
- 红包/礼金/随礼 → 红包

【解析示例】
输入："午餐 25 微信"
输出：{{"date": "{current_date}", "amount": 25, "merchant": "午餐", "payment_method": "微信", "bank_name": "", "card_last_four": "", "transaction_type": "expense", "category": "午餐", "description": "午餐"}}

输入："工资 8000 建行0388"
输出：{{"date": "{current_date}", "amount": 8000, "merchant": "工资", "payment_method": "银行卡", "bank_name": "CCB", "card_last_four": "0388", "transaction_type": "income", "category": "工资", "description": "工资"}}

输入："滴滴打车 35 中行8735"
输出：{{"date": "{current_date}", "amount": 35, "merchant": "滴滴打车", "payment_method": "银行卡", "bank_name": "BOC", "card_last_four": "8735", "transaction_type": "expense", "category": "打车", "description": "滴滴打车"}}

输入："买菜 68.5 支付宝"
输出：{{"date": "{current_date}", "amount": 68.5, "merchant": "买菜", "payment_method": "支付宝", "bank_name": "", "card_last_four": "", "transaction_type": "expense", "category": "买菜", "description": "买菜"}}

输入："星巴克 45 工行4969"
输出：{{"date": "{current_date}", "amount": 45, "merchant": "星巴克", "payment_method": "银行卡", "bank_name": "ICBC", "card_last_four": "4969", "transaction_type": "expense", "category": "零食", "description": "星巴克"}}

【重要要求】
1. category必须从列表中选择，优先选择最精确的分类
2. 银行卡支付必须识别bank_name和card_last_four
3. 智能推断：如果用户没说支付方式，根据常识推断（如工资通常是银行卡）
4. 只返回纯JSON对象，不要markdown代码块，不要其他文字"""
