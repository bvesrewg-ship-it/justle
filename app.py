from flask import Flask, jsonify, request
import datetime
import os

app = Flask(__name__)

# =====================================================================
# 1. قاعدة بيانات اليوزرات المحاكية (تم حقن اليوزر والباص الخاص بك)
# =====================================================================
USERS_DATABASE = {
    "0176436959603": {
        "password": "2442668892", 
        "expiry": "2027-06-18", 
        "max_connections": 1
    }
}

# =====================================================================
# 2. باقات وقنوات السيرفر المحاكي
# =====================================================================
LIVE_STREAMS_SOURCE = [
    {
        "stream_id": 1035137, 
        "name": "beIN SPORTS 1 HD",
        "category_id": "1",
        "url": "http://103.211.103.13:2095/live/stream1.ts" 
    },
    {
        "stream_id": 1035138,
        "name": "SSC SPORTS 1 HD",
        "category_id": "2",
        "url": "http://217.60.15.202:2095/live/ssc1.ts"
    }
]

CATEGORIES_SOURCE = [
    {"category_id": "1", "category_name": "beIN Sports Pack"},
    {"category_id": "2", "category_name": "SSC Sports Pack"}
]

# =====================================================================
# 3. دالة التحقق من الهوية
# =====================================================================
def authenticate(username, password):
    if username in USERS_DATABASE and USERS_DATABASE[username]["password"] == password:
        return USERS_DATABASE[username]
    return None

# =====================================================================
# 4. محرك الـ API الرئيسي لـ Xtream Codes
# =====================================================================
@app.route('/player_api.php')
def player_api():
    username = request.args.get('username')
    password = request.args.get('password')
    action = request.args.get('action')
    stream_id = request.args.get('stream_id')
    
    user_info = authenticate(username, password)
    if not user_info:
        return jsonify({"user_info": {"auth": 0, "status": "Invalid"}})
        
    exp_timestamp = int(datetime.datetime.strptime(user_info["expiry"], "%Y-%m-%d").timestamp())
    
    if not action:
        return jsonify({
            "user_info": {
                "auth": 1, 
                "status": "Active", 
                "username": username, 
                "exp_date": str(exp_timestamp), 
                "max_connections": str(user_info["max_connections"])
            },
            "server_info": {"url": request.host, "port": "80", "timezone": "Asia/Kuwait"}
        })
        
    elif action == "get_live_categories":
        return jsonify(CATEGORIES_SOURCE)
        
    elif action == "get_live_streams":
        return jsonify([
            {
                "num": s["stream_id"], 
                "name": s["name"], 
                "stream_id": s["stream_id"], 
                "category_id": s["category_id"], 
                "stream_type": "live", 
                "container_extension": "ts"
            } for s in LIVE_STREAMS_SOURCE
        ])
        
    elif action == "get_short_epg":
        return jsonify({
            "epg_listings": [
                {
                    "id": "1",
                    "stream_id": stream_id,
                    "title": "LIVE MATCH",
                    "start": "2026-06-18 00:00:00",
                    "end": "2026-06-18 23:59:59",
                    "description": "بث محاكي يعمل بنجاح"
                }
            ]
        })
        
    return jsonify([])

# =====================================================================
# 5. التوجيه الذكي للبث المباشر (302 Redirect)
# =====================================================================
@app.route('/live/<username>/<password>/<int:stream_id>.ts')
def stream_video(username, password, stream_id):
    if not authenticate(username, password): 
        return "Unauthorized", 401
    for stream in LIVE_STREAMS_SOURCE:
        if stream["stream_id"] == stream_id:
            return "", 302, {"Location": stream["url"]}
    return "Not Found", 404

# تشغيل السيرفر تلقائياً على المنصة الجديدة
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
