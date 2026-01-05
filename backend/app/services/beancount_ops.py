import os
from datetime import datetime
from typing import List, Dict
from beancount import loader
from beancount.core import data
from beancount.core.amount import Amount
from beancount.core.number import D
from ..config import settings

class BeancountService:
    def __init__(self):
        self.main_path = settings.BEANCOUNT_MAIN_PATH
        self.transaction_path = settings.BEANCOUNT_TRANSACTION_PATH
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        # 确保交易文件目录存在
        os.makedirs(os.path.dirname(self.transaction_path), exist_ok=True)
        if not os.path.exists(self.transaction_path):
            with open(self.transaction_path, 'w', encoding='utf-8') as f:
                f.write(f"; 交易记录\n")
                f.write(f"; 创建时间: {datetime.now().strftime('%Y-%m-%d')}\n\n")

    def get_accounts(self) -> List[str]:
        try:
            entries, errors, options = loader.load_file(self.main_path)
            accounts = set()
            for entry in entries:
                if isinstance(entry, data.Open):
                    accounts.add(entry.account)
            return sorted(list(accounts))
        except:
            return []

    def get_balances(self) -> Dict[str, float]:
        try:
            entries, errors, options = loader.load_file(self.main_path)
            from beancount.core import realization
            real_root = realization.realize(entries)

            balances = {}
            for account in realization.iter_children(real_root):
                if account.account:
                    balance = account.balance
                    if balance:
                        for pos in balance:
                            if pos.units.currency == 'CNY':
                                balances[account.account] = float(pos.units.number)
            return balances
        except:
            return {}

    def append_transaction(self,
                          date: str,
                          amount: float,
                          merchant: str,
                          payment_method: str,
                          bank_name: str = "",
                          card_last_four: str = "",
                          transaction_type: str = "expense",
                          category: str = "",
                          description: str = "") -> bool:
        try:
            # 构建账户名称
            if transaction_type == "expense":
                from_account = self._get_asset_account(payment_method, bank_name, card_last_four)
                to_account = self._get_expense_account(category)
            else:  # income
                from_account = self._get_income_account(category)
                to_account = self._get_asset_account(payment_method, bank_name, card_last_four)

            # 构建交易记录
            payee = merchant if merchant else ""
            narration = description if description else merchant

            transaction_text = f'\n{date} * "{payee}" "{narration}"\n'
            transaction_text += f'  {to_account}  {amount:.2f} CNY\n'
            transaction_text += f'  {from_account}  -{amount:.2f} CNY\n'

            # 追加到交易文件
            with open(self.transaction_path, 'a', encoding='utf-8') as f:
                f.write(transaction_text)

            return True
        except Exception as e:
            print(f"Error appending transaction: {e}")
            return False

    def _get_asset_account(self, payment_method: str, bank_name: str = "", card_last_four: str = "") -> str:
        """
        根据支付方式、银行名称和卡号后四位获取资产账户
        
        银行卡账户映射规则：
        - CCB (建设银行): 0388, 0349
        - BOC (中国银行): 8735, 1969, 7870, 3469
        - ICBC (工商银行): 4969
        """
        if payment_method == "银行卡" and bank_name and card_last_four:
            # 尝试精确匹配银行+卡号后四位
            bank_card_map = {
                ("CCB", "0388"): "Assets:Bank:CCB:0388",
                ("CCB", "0349"): "Assets:Bank:CCB:0349",
                ("BOC", "8735"): "Assets:Bank:BOC:8735",
                ("BOC", "1969"): "Assets:Bank:BOC:1969",
                ("BOC", "7870"): "Assets:Bank:BOC:7870",
                ("BOC", "3469"): "Assets:Bank:BOC:3469",
                ("ICBC", "4969"): "Assets:Bank:ICBC:4969",
            }
            account = bank_card_map.get((bank_name.upper(), card_last_four))
            if account:
                return account
            
            # 如果没有精确匹配，但有银行名称，返回该银行的第一个账户
            bank_default = {
                "CCB": "Assets:Bank:CCB:0388",
                "BOC": "Assets:Bank:BOC:8735",
                "ICBC": "Assets:Bank:ICBC:4969",
            }
            return bank_default.get(bank_name.upper(), "Assets:Bank:Other")
        
        # 非银行卡支付方式
        method_map = {
            "支付宝": "Assets:Cash:Alipay",
            "微信": "Assets:Cash:WeChat",
            "现金": "Assets:Cash:CNY"
        }
        return method_map.get(payment_method, "Assets:Other")

    def _get_expense_account(self, category: str) -> str:
        """
        根据分类获取支出账户，严格匹配accounts.beancount中的账户层级
        """
        category_map = {
            # 餐饮类
            "餐饮": "Expenses:Food:Lunch",
            "早餐": "Expenses:Food:Breakfast",
            "午餐": "Expenses:Food:Lunch",
            "晚餐": "Expenses:Food:Dinner",
            "零食": "Expenses:Food:Snacks",
            "水果": "Expenses:Food:Snacks",
            "买菜": "Expenses:Food:Groceries",
            
            # 交通类
            "交通": "Expenses:Transport:Public",
            "公交": "Expenses:Transport:Public",
            "地铁": "Expenses:Transport:Public",
            "打车": "Expenses:Transport:Taxi",
            "出租车": "Expenses:Transport:Taxi",
            "加油": "Expenses:Transport:Fuel",
            "充电": "Expenses:Transport:Fuel",
            
            # 住房类
            "房租": "Expenses:Housing:Rent",
            "水电": "Expenses:Housing:Utilities",
            "水电煤": "Expenses:Housing:Utilities",
            "宽带": "Expenses:Housing:Internet",
            "话费": "Expenses:Housing:Internet",
            
            # 购物类
            "购物": "Expenses:Shopping:Daily",
            "衣服": "Expenses:Shopping:Clothing",
            "鞋子": "Expenses:Shopping:Clothing",
            "数码": "Expenses:Shopping:Electronics",
            "电子产品": "Expenses:Shopping:Electronics",
            "日用品": "Expenses:Shopping:Daily",
            
            # 娱乐类
            "娱乐": "Expenses:Entertainment:Social",
            "电影": "Expenses:Entertainment:Movies",
            "游戏": "Expenses:Entertainment:Games",
            "聚餐": "Expenses:Entertainment:Social",
            
            # 医疗类
            "医疗": "Expenses:Health:Hospital",
            "药品": "Expenses:Health:Medicine",
            "看病": "Expenses:Health:Hospital",
            
            # 其他
            "红包": "Expenses:Other:Gifts",
            "礼物": "Expenses:Other:Gifts",
        }
        return category_map.get(category, "Expenses:Other:Misc")

    def _get_income_account(self, category: str) -> str:
        category_map = {
            "工资": "Income:Salary",
            "奖金": "Income:Bonus",
            "投资": "Income:Investment"
        }
        return category_map.get(category, "Income:Other")

    def get_account_config(self) -> Dict:
        """
        获取账户配置，包括支付方式、分类等
        这些配置与 accounts.beancount 严格对应
        """
        return {
            "payment_methods": [
                {"value": "支付宝", "label": "支付宝", "account": "Assets:Cash:Alipay"},
                {"value": "微信", "label": "微信", "account": "Assets:Cash:WeChat"},
                {"value": "银行卡", "label": "银行卡", "account": "Assets:Bank"},
                {"value": "现金", "label": "现金", "account": "Assets:Cash:CNY"},
            ],
            "bank_cards": [
                {"bank": "CCB", "bank_name": "建设银行", "last_four": "0388", "account": "Assets:Bank:CCB:0388"},
                {"bank": "CCB", "bank_name": "建设银行", "last_four": "0349", "account": "Assets:Bank:CCB:0349"},
                {"bank": "BOC", "bank_name": "中国银行", "last_four": "8735", "account": "Assets:Bank:BOC:8735"},
                {"bank": "BOC", "bank_name": "中国银行", "last_four": "1969", "account": "Assets:Bank:BOC:1969"},
                {"bank": "BOC", "bank_name": "中国银行", "last_four": "7870", "account": "Assets:Bank:BOC:7870"},
                {"bank": "BOC", "bank_name": "中国银行", "last_four": "3469", "account": "Assets:Bank:BOC:3469"},
                {"bank": "ICBC", "bank_name": "工商银行", "last_four": "4969", "account": "Assets:Bank:ICBC:4969"},
            ],
            "expense_categories": [
                # 餐饮类
                {"value": "早餐", "label": "早餐", "account": "Expenses:Food:Breakfast", "group": "餐饮"},
                {"value": "午餐", "label": "午餐", "account": "Expenses:Food:Lunch", "group": "餐饮"},
                {"value": "晚餐", "label": "晚餐", "account": "Expenses:Food:Dinner", "group": "餐饮"},
                {"value": "零食", "label": "零食水果", "account": "Expenses:Food:Snacks", "group": "餐饮"},
                {"value": "买菜", "label": "买菜买肉", "account": "Expenses:Food:Groceries", "group": "餐饮"},
                
                # 交通类
                {"value": "公交", "label": "公交地铁", "account": "Expenses:Transport:Public", "group": "交通"},
                {"value": "打车", "label": "打车", "account": "Expenses:Transport:Taxi", "group": "交通"},
                {"value": "加油", "label": "加油/充电", "account": "Expenses:Transport:Fuel", "group": "交通"},
                
                # 住房类
                {"value": "房租", "label": "房租", "account": "Expenses:Housing:Rent", "group": "住房"},
                {"value": "水电", "label": "水电煤气", "account": "Expenses:Housing:Utilities", "group": "住房"},
                {"value": "宽带", "label": "宽带话费", "account": "Expenses:Housing:Internet", "group": "住房"},
                
                # 购物类
                {"value": "衣服", "label": "衣物鞋包", "account": "Expenses:Shopping:Clothing", "group": "购物"},
                {"value": "数码", "label": "数码电子", "account": "Expenses:Shopping:Electronics", "group": "购物"},
                {"value": "日用品", "label": "日用品", "account": "Expenses:Shopping:Daily", "group": "购物"},
                
                # 娱乐类
                {"value": "电影", "label": "电影娱乐", "account": "Expenses:Entertainment:Movies", "group": "娱乐"},
                {"value": "游戏", "label": "游戏", "account": "Expenses:Entertainment:Games", "group": "娱乐"},
                {"value": "聚餐", "label": "社交聚餐", "account": "Expenses:Entertainment:Social", "group": "娱乐"},
                
                # 医疗类
                {"value": "药品", "label": "药品", "account": "Expenses:Health:Medicine", "group": "医疗"},
                {"value": "看病", "label": "医疗挂号", "account": "Expenses:Health:Hospital", "group": "医疗"},
                
                # 其他
                {"value": "红包", "label": "随礼红包", "account": "Expenses:Other:Gifts", "group": "其他"},
                {"value": "其他", "label": "其他杂项", "account": "Expenses:Other:Misc", "group": "其他"},
            ],
            "income_categories": [
                {"value": "工资", "label": "工资", "account": "Income:Salary"},
                {"value": "奖金", "label": "奖金", "account": "Income:Bonus"},
                {"value": "投资", "label": "投资收益", "account": "Income:Investment"},
            ],
            "liability_accounts": [
                {"value": "花呗", "label": "花呗", "account": "Liabilities:Credit:花呗"},
                {"value": "先用后付", "label": "先用后付", "account": "Liabilities:Credit:先用后付"},
            ]
        }
