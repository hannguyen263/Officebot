# ð¼ `office-user-bot`

[![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)](https://forthebadge.com)

## ð ç¨ Telegram bot åå»º Office è´¦å·

![](readme/ea7870bb.png)
![](readme/adeff432.png)

### ð¥¼ ç¯å¢

```
python 3.6+
```

### ð¢ ç¨æ³

#### 1. å¨ @botfather æ°å»º bot

#### 2. ä¸è½½é¡¹ç®

```
git clone https://github.com/zayabighead/office-user-bot.git
cd office-user-bot
pip install -r requirements.txt
```

#### 3. åç®å½ä¸æ°å»º `config.json` å¹¶å¦ä¸ç¼è¾

```
{
  "bot": {
    "admin": bot ç®¡çåï¼å¡« tg çç¨æ· id,
    "notify": true / false æ¯å¦æ¥åæ°å»ºè´¦å·æ¶çæ¨é,
    "token": "bot ç tokenï¼ä» botfather è·å"
  },
  "aad": {
    "clientId": "aad app ç client id",
    "clientSecret": "aad app ç client secret",
    "tenantId": "aad app ç tenant id"
  },
  "office": {
    "subscriptions": [
      {
        "name": "è®¢éæ¾ç¤ºåç§°",
        "sku": "è®¢é id"
      }
    ],
    "domains": [
      {
        "display": "@******.org ä»ä¾æ¾ç¤ºåå",
        "value": "@abcde.org å®éåå"
      }
    ]
  },
  "banned": {
    "tgId": [è¦æé»ç tg ç¨æ·ç id],
    "officeUsername": [
      "admin",
      "ç¨æ·åé»åå"
    ]
  }
}
```

#### 4. è¿è¡

```
python bot.py
```

è¾å¥ä»»ææ¶æ¯ bot å³ä¼åå¤

çæçæ¿æ´»ç ä¿å­å¨åç®å½ä¸ç `codes.json`